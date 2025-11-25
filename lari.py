#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress
from openai import OpenAI

app = typer.Typer(help="LARI — LLM Artifact Removal Initiative CLI")
console = Console()

# -------------------- config loading -------------------- #

def load_config() -> Dict[str, Any]:
    config_path = Path("config/config.json")
    if not config_path.exists():
        console.print("[yellow]config/config.json not found. Using config/config.example.json[/yellow]")
        config_path = Path("config/config.example.json")
        if not config_path.exists():
            console.print("[red]No config file found. Create config/config.json or config/config.example.json[/red]")
            raise typer.Exit(1)
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_profile(config: Dict[str, Any], profile_name: str) -> Dict[str, Any]:
    profiles_path = Path(config.get("profiles_path", "./config/profiles"))
    profile_path = profiles_path / f"{profile_name}.json"
    if not profile_path.exists():
        console.print(f"[red]Profile not found:[/red] {profile_path}")
        raise typer.Exit(1)
    with profile_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_prompt(profile_name: str) -> str:
    prompts_path = Path("prompts")
    prompt_file = prompts_path / f"{profile_name}.md"
    if not prompt_file.exists():
        return (
            "You are LARI, rewriting AI-generated text so it reads like it was written by a real human. "
            "Preserve meaning, remove obvious AI artifacts, and keep the tone natural and slightly imperfect. "
            "Return only the rewritten text."
        )
    return prompt_file.read_text(encoding="utf-8")


# -------------------- artifact scrubbing -------------------- #

DEFAULT_ARTIFACT_PHRASES = [
    "as an ai language model",
    "as an ai",
    "in conclusion",
    "in summary",
    "furthermore",
    "moreover",
    "additionally",
    "in today's world",
    "ever-evolving landscape"
]


def scrub_artifacts(text: str, profile: Dict[str, Any]) -> str:
    """Simple rule-based scrubber that removes or softens obvious LLM artifacts and punctuation patterns."""
    import re

    phrases: List[str] = DEFAULT_ARTIFACT_PHRASES.copy()
    extra = profile.get("artifact_rules", {}).get("remove_phrases", [])
    phrases.extend(extra)

    cleaned = text

    # Remove phrases
    for phrase in phrases:
        cleaned = re.sub(re.escape(phrase), "", cleaned, flags=re.IGNORECASE)

    # Normalize dash types
    cleaned = cleaned.replace("—", "-")  # em dash
    cleaned = cleaned.replace("–", "-")  # en dash
    cleaned = re.sub(r"-{2,}", "-", cleaned)  # collapse multiple dashes

    # Remove bullet-like characters
    cleaned = cleaned.replace("•", "")

    # Remove weird unicode spacings
    cleaned = cleaned.replace("\u2009", " ")
    cleaned = cleaned.replace("\u202F", " ")
    cleaned = cleaned.replace("\u00A0", " ")

    # Remove corporate-style list bullets at line starts
    cleaned = re.sub(r"^\s*[-*]\s+", "", cleaned, flags=re.MULTILINE)

    # Collapse excessive whitespace
    cleaned = re.sub(r"\s{3,}", "  ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


# -------------------- LLM call -------------------- #

def get_openai_client(config: Dict[str, Any]) -> OpenAI:
    env_var = config.get("openai_api_key_env", "OPENAI_API_KEY")
    api_key = os.getenv(env_var)
    if not api_key:
        console.print(f"[red]Environment variable {env_var} is not set.[/red]")
        console.print("Export your key, e.g.:")
        console.print(f"[cyan]export {env_var}=your_api_key_here[/cyan]")
        raise typer.Exit(1)
    return OpenAI(api_key=api_key)


def rewrite_with_llm(
    config: Dict[str, Any],
    profile: Dict[str, Any],
    system_prompt: str,
    text: str,
) -> str:
    client = get_openai_client(config)
    model = config.get("default_model", "gpt-4.1-mini")
    temperature = float(config.get("temperature", 0.6))
    max_tokens = int(config.get("max_tokens", 1500))

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                "Profile description:\n"
                f"{profile.get('description', '')}\n\n"
                "Style instructions (apply these, but keep the content accurate):\n"
                + "\n".join(f"- {s}" for s in profile.get("style_instructions", []))
                + "\n\n"
                "Text to rewrite:\n"
                f"{text}"
            ),
        },
    ]

    with Progress() as progress:
        task = progress.add_task("[green]Calling LLM...", total=None)
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        progress.update(task, completed=1)

    content = resp.choices[0].message.content
    return content.strip()


# -------------------- IO helpers -------------------- #

def read_input_text(input_path: Optional[Path]) -> str:
    if input_path is None or str(input_path) == "-":
        console.print("[cyan]Reading from stdin. Press Ctrl+D (Linux/macOS) or Ctrl+Z then Enter (Windows) when done.[/cyan]")
        return sys.stdin.read()
    if not input_path.exists():
        console.print(f"[red]Input file not found:[/red] {input_path}")
        raise typer.Exit(1)
    return input_path.read_text(encoding="utf-8")


def write_output_text(output_path: Optional[Path], text: str) -> None:
    if output_path is None:
        console.print("\n[bold green]--- Rewritten Text ---[/bold green]\n")
        console.print(text)
    else:
        output_path.write_text(text, encoding="utf-8")
        console.print(f"[green]Written output to:[/green] {output_path}")


# -------------------- CLI command -------------------- #

@app.command()
def rewrite(
    input: Optional[Path] = typer.Argument(
        None,
        help="Input file path. Use '-' or omit to read from stdin."
    ),
    profile: str = typer.Option(
        None,
        help="Profile name (e.g. linkedin, technical, academic, casual). Defaults to config.default_profile."
    ),
    model: Optional[str] = typer.Option(
        None,
        help="Override model (defaults to config.default_model)."
    ),
    out: Optional[Path] = typer.Option(
        None,
        "--out",
        "-o",
        help="Optional output file path. If not set, prints to stdout."
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Only run local artifact scrubbing, skip LLM call."
    ),
):
    """
    Rewrite text using LARI to remove LLM artifacts and apply a HumanMode profile.
    """
    config = load_config()
    profile_name = profile or config.get("default_profile", "linkedin")
    prof = load_profile(config, profile_name)
    base_prompt = load_prompt(profile_name)

    if model is not None:
        config["default_model"] = model

    raw_text = read_input_text(input)
    if not raw_text.strip():
        console.print("[red]No input text provided.[/red]")
        raise typer.Exit(1)

    # Step 1: local scrub
    scrubbed = scrub_artifacts(raw_text, prof)

    # If dry-run: stop here
    if dry_run:
        write_output_text(out, scrubbed)
        raise typer.Exit(0)

    # Confirm if text is large
    if len(scrubbed) > 8000:
        ok = Confirm.ask(
            "[yellow]Text is long (>8000 chars). Continue and send to LLM?[/yellow]",
            default=False
        )
        if not ok:
            console.print("[red]Aborted by user.[/red]")
            raise typer.Exit(1)

    # Step 2: LLM rewrite
    rewritten = rewrite_with_llm(config, prof, base_prompt, scrubbed)
    write_output_text(out, rewritten)


@app.callback()
def main_callback():
    """
    LARI — LLM Artifact Removal Initiative
    """
    pass


if __name__ == "__main__":
    app()
