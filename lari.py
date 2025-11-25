#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from typing import Optional

import requests
import typer
from rich import print
from rich.console import Console

app = typer.Typer(help="LARI — LLM Artifact Removal Initiative (v2.0)")

console = Console()

# ---------------------------------------------------------
# Config helpers
# ---------------------------------------------------------


def load_config() -> dict:
    config_path = Path("config") / "config.json"
    if not config_path.exists():
        console.print(
            f"[red]Config file not found:[/red] {config_path}\n"
            "Create it (you can start from config/config.example.json)."
        )
        raise typer.Exit(code=1)

    try:
        with config_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Failed to load config:[/red] {e}")
        raise typer.Exit(code=1)


def load_profile(profile_name: str, config: dict) -> dict:
    profiles_path = Path(config.get("profiles_path", "config/profiles"))
    profile_path = profiles_path / f"{profile_name}.json"

    if not profile_path.exists():
        console.print(
            f"[red]Profile not found:[/red] {profile_name}\n"
            f"Expected at: [cyan]{profile_path}[/cyan]"
        )
        raise typer.Exit(code=1)

    try:
        with profile_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Failed to load profile '{profile_name}':[/red] {e}")
        raise typer.Exit(code=1)


# ---------------------------------------------------------
# Engines
# ---------------------------------------------------------


def rewrite_with_openai(text: str, profile: dict, config: dict) -> str:
    import openai

    env_var = config.get("openai_api_key_env", "OPENAI_API_KEY")
    api_key = os.getenv(env_var)
    if not api_key:
        console.print(
            f"[red]Missing OpenAI API key.[/red]\n"
            f"Set environment variable [cyan]{env_var}[/cyan]."
        )
        raise typer.Exit(code=1)

    client = openai.OpenAI(api_key=api_key)

    model = config.get("default_model", "gpt-4o-mini")
    temperature = config.get("temperature", 0.4)
    max_tokens = config.get("max_tokens", 4096)

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": profile["system"]},
                {
                    "role": "user",
                    "content": profile["user"] + "\n\n" + text,
                },
            ],
        )
    except Exception as e:
        console.print(f"[red]OpenAI request failed:[/red] {e}")
        raise typer.Exit(code=1)

    return response.choices[0].message.content.strip()


def rewrite_with_anthropic(text: str, profile: dict, config: dict) -> str:
    import anthropic

    env_var = config.get("anthropic_api_key_env", "ANTHROPIC_API_KEY")
    api_key = os.getenv(env_var)
    if not api_key:
        console.print(
            f"[red]Missing Anthropic API key.[/red]\n"
            f"Set environment variable [cyan]{env_var}[/cyan]."
        )
        raise typer.Exit(code=1)

    client = anthropic.Anthropic(api_key=api_key)

    model = config.get("anthropic_model", "claude-3-sonnet-20240229")
    temperature = config.get("temperature", 0.4)
    max_tokens = config.get("max_tokens", 4096)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=profile["system"],
            messages=[
                {"role": "user", "content": profile["user"] + "\n\n" + text}
            ],
        )
    except Exception as e:
        console.print(f"[red]Anthropic request failed:[/red] {e}")
        raise typer.Exit(code=1)

    # anthropic response.content is a list of blocks
    return "".join(block.text for block in response.content if hasattr(block, "text")).strip()


def rewrite_with_ollama(text: str, profile: dict, config: dict) -> str:
    ollama_cfg = config.get("ollama", {})
    base_url = ollama_cfg.get("base_url", "http://localhost:11434")
    model = ollama_cfg.get("model", "llama3")

    url = f"{base_url.rstrip('/')}/api/generate"

    payload = {
        "model": model,
        "prompt": profile["system"] + "\n\n" + profile["user"] + "\n\n" + text,
        "temperature": config.get("temperature", 0.4),
        "stream": False,  # important: get a single JSON response
    }

    try:
        resp = requests.post(url, json=payload, timeout=120)
    except Exception as e:
        console.print(f"[red]Failed to reach Ollama at {base_url}:[/red] {e}")
        raise typer.Exit(code=1)

    if resp.status_code != 200:
        console.print(f"[red]Ollama request failed:[/red] {resp.text}")
        raise typer.Exit(code=1)

    data = resp.json()
    return data.get("response", "").strip()


def dry_run_scrub(text: str) -> str:
    """
    Very lightweight artifact removal.
    Intentionally simple and conservative.
    """
    cleaned = text

    # normalize dashes
    cleaned = cleaned.replace("—", "-").replace("–", "-")

    # lower-cased copy for phrase stripping
    # but we remove from original via simple replace to avoid over-mangling
    to_strip = [
        "in conclusion",
        "as an ai",
        "furthermore",
    ]
    for phrase in to_strip:
        cleaned = cleaned.replace(phrase, "")
        cleaned = cleaned.replace(phrase.capitalize(), "")

    replacements = {
        "leveraging": "using",
        "Leveraging": "Using",
        "dive deeper": "look into",
        "Dive deeper": "Look into",
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    return cleaned.strip()


# ---------------------------------------------------------
# Main rewrite dispatcher
# ---------------------------------------------------------


def rewrite(text: str, engine: str, profile: dict, config: dict) -> str:
    if engine == "dry-run":
        return dry_run_scrub(text)
    elif engine == "openai":
        return rewrite_with_openai(text, profile, config)
    elif engine == "anthropic":
        return rewrite_with_anthropic(text, profile, config)
    elif engine == "ollama":
        return rewrite_with_ollama(text, profile, config)
    else:
        console.print(
            f"[red]Unknown engine:[/red] {engine}\n"
            "Use one of: [cyan]openai[/cyan], [cyan]anthropic[/cyan], "
            "[cyan]ollama[/cyan], [cyan]dry-run[/cyan]."
        )
        raise typer.Exit(code=1)


# ---------------------------------------------------------
# CLI Command
# ---------------------------------------------------------


@app.command()
def run(
    text: Optional[str] = typer.Option(
        None,
        "--text",
        "-t",
        help="Inline text to rewrite.",
    ),
    file: Optional[Path] = typer.Option(
        None,
        "--file",
        "-f",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to input file.",
    ),
    out: Optional[Path] = typer.Option(
        None,
        "--out",
        "-o",
        help="Write output to this file (single input).",
    ),
    profile: str = typer.Option(
        "linkedin",
        "--profile",
        "-p",
        help="Profile name (JSON in config/profiles without .json).",
    ),
    engine: Optional[str] = typer.Option(
        None,
        "--engine",
        "-e",
        help="Engine: openai | anthropic | ollama | dry-run. Defaults to config.default_engine.",
    ),
):
    """
    LARI rewrite engine.
    Provide --text, --file, or pipe content via stdin.
    """
    config = load_config()
    engine_to_use = engine or config.get("default_engine", "openai")
    profile_data = load_profile(profile, config)

    # Determine input source
    input_text: Optional[str] = None

    if text is not None and file is not None:
        console.print("[red]Use either --text OR --file, not both.[/red]")
        raise typer.Exit(code=1)

    if text is not None:
        input_text = text
    elif file is not None:
        try:
            input_text = file.read_text(encoding="utf-8")
        except Exception as e:
            console.print(f"[red]Failed to read file:[/red] {e}")
            raise typer.Exit(code=1)
    else:
        # check stdin
        if not sys.stdin.isatty():
            input_text = sys.stdin.read()
        else:
            console.print(
                "[red]No input provided.[/red]\n"
                "Use [cyan]--text[/cyan], [cyan]--file[/cyan], or pipe data via stdin."
            )
            raise typer.Exit(code=1)

    result = rewrite(input_text, engine_to_use, profile_data, config)

    if out:
        try:
            out.write_text(result, encoding="utf-8")
        except Exception as e:
            console.print(f"[red]Failed to write output file:[/red] {e}")
            raise typer.Exit(code=1)
        console.print(f"[green]Wrote output to:[/green] {out}")
    else:
        print("\n[bold green]=== LARI OUTPUT ===[/bold green]\n")
        print(result)


if __name__ == "__main__":
    app()
