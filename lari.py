#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

import itertools
import threading
import time

import requests
import typer
from rich import print
from rich.console import Console

console = Console()

# ---------------------------------------------------------
# Spinner
# ---------------------------------------------------------


class Spinner:
    def __init__(self, message: str = "Generating", interval: float = 0.12):
        self.message = message
        self.interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def _spin(self):
        frames = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        while self._running:
            frame = next(frames)
            sys.stdout.write(f"\r{self.message} {frame}")
            sys.stdout.flush()
            time.sleep(self.interval)

    def stop(self):
        if not self._running:
            return
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        # Clear the spinner line
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()


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


def build_prompts(profile: dict) -> Tuple[str, str]:
    """
    Normalize profile structure so JSON files that only have
    name/description/style_instructions/artifact_rules still work.

    Returns: (system_prompt, user_prefix)
    """

    # If explicit prompts exist, just use them.
    if "system" in profile and "user" in profile:
        return profile["system"], profile["user"]

    name = profile.get("name", "HumanMode profile")
    desc = profile.get("description", "")
    style_instructions = profile.get("style_instructions", [])
    artifact_rules = profile.get("artifact_rules", {})
    remove_phrases = artifact_rules.get("remove_phrases", [])

    system_parts = [
        f"You are a rewriting assistant applying the '{name}' style.",
        "Your job is to rewrite text so it sounds human, natural, and authentic.",
        "Preserve the original meaning and technical accuracy.",
        "Do NOT talk about yourself, what you are doing, or how you rewrote the text.",
        "Do NOT introduce the rewrite (no 'here is a reworked version', "
        "'here is your rewritten text', or similar).",
        "Do NOT use bullet lists or markdown-style '-' lines unless the original "
        "text was already formatted as a list.",
        "Do NOT use dashes or hyphens as fake punctuation between clauses "
        "(no ' - ' or '--' between words).",
        "Prefer commas and periods instead of any kind of dash when breaking up thoughts.",
    ]
    if desc:
        system_parts.append(desc)

    if style_instructions:
        system_parts.append("Follow these style guidelines:")
        for s in style_instructions:
            system_parts.append(f"- {s}")

    if remove_phrases:
        system_parts.append("Avoid or remove these phrases when possible:")
        for p in remove_phrases:
            system_parts.append(f"- {p}")

    system_prompt = "\n".join(system_parts)

    user_prefix = (
        "Rewrite the following text according to the style guidelines above.\n"
        "Return ONLY the rewritten text, with no preface, no explanation, "
        "and no lines like 'Here is the revised version'.\n\n"
    )

    return system_prompt, user_prefix


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

    system_prompt, user_prefix = build_prompts(profile)

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_prefix + text,
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

    system_prompt, user_prefix = build_prompts(profile)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prefix + text}
            ],
        )
    except Exception as e:
        console.print(f"[red]Anthropic request failed:[/red] {e}")
        raise typer.Exit(code=1)

    # anthropic response.content is a list of blocks
    return "".join(
        block.text for block in response.content if hasattr(block, "text")
    ).strip()


def rewrite_with_ollama(text: str, profile: dict, config: dict) -> str:
    ollama_cfg = config.get("ollama", {})
    base_url = ollama_cfg.get("base_url", "http://localhost:11434")
    model = ollama_cfg.get("model", "llama3")

    url = f"{base_url.rstrip('/')}/api/generate"

    system_prompt, user_prefix = build_prompts(profile)

    payload = {
        "model": model,
        "prompt": system_prompt + "\n\n" + user_prefix + text,
        "temperature": config.get("temperature", 0.4),
        "stream": False,  # important: get a single JSON response
    }

    try:
        resp = requests.post(url, json=payload, timeout=300)
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
# Output post-processing
# ---------------------------------------------------------


def postprocess_output(text: str) -> str:
    """
    Strip common AI-ish wrappers and clean dash-y punctuation.
    """
    lines = [line.rstrip() for line in text.splitlines()]

    # Drop leading empty lines
    while lines and not lines[0].strip():
        lines.pop(0)

    # Strip typical intro lines
    if lines:
        first = lines[0].strip().lower()
        intro_starts = (
            "here's a reworked version",
            "here is a reworked version",
            "here's the revised version",
            "here is the revised version",
            "here's a revised version",
            "here is a revised version",
            "here's your rewritten text",
            "here is your rewritten text",
            "rewritten version:",
            "revised version:",
        )
        if any(first.startswith(p) for p in intro_starts):
            lines = lines[1:]

    # Strip "I'm ..." meta line if it's clearly about being an assistant / ai
    if lines:
        first = lines[0].strip().lower()
        if first.startswith("i'm ") or first.startswith("i am "):
            if "assistant" in first or "language model" in first:
                lines = lines[1:]

    # If the whole thing turned into bullet-y output, collapse it
    if any(line.lstrip().startswith("- ") for line in lines):
        bullet_lines = [
            l.lstrip()[2:] if l.lstrip().startswith("- ") else l for l in lines
        ]
        result = " ".join(bullet_lines)
        result = re.sub(r"\s+", " ", result).strip()
        # dash cleanup
        result = re.sub(r"(\w)\s*[-–—]{1,2}\s+(\w)", r"\1, \2", result)
        return result.strip()

    # Normal join
    result = "\n".join(lines).strip()

    # --- Dash cleanup: turn " - " / " -- " between words into commas ---
    # This keeps real minus signs and hyphenated words intact.
    result = re.sub(r"(\w)\s*[-–—]{1,2}\s+(\w)", r"\1, \2", result)

    return result.strip()


# ---------------------------------------------------------
# Main rewrite dispatcher
# ---------------------------------------------------------


def rewrite(text: str, engine: str, profile: dict, config: dict) -> str:
    if engine == "dry-run":
        result = dry_run_scrub(text)
    elif engine == "openai":
        result = rewrite_with_openai(text, profile, config)
    elif engine == "anthropic":
        result = rewrite_with_anthropic(text, profile, config)
    elif engine == "ollama":
        result = rewrite_with_ollama(text, profile, config)
    else:
        console.print(
            f"[red]Unknown engine:[/red] {engine}\n"
            "Use one of: [cyan]openai[/cyan], [cyan]anthropic[/cyan], "
            "[cyan]ollama[/cyan], [cyan]dry-run[/cyan]."
        )
        raise typer.Exit(code=1)

    return postprocess_output(result)


# ---------------------------------------------------------
# CLI (single-command)
# ---------------------------------------------------------


def main(
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
        help="Engine: openai | anthropic | ollama | dry-run. "
             "Defaults to config.default_engine.",
    ),
):
    """
    LARI rewrite engine.
    Use --text, --file, or pipe content via stdin.
    """
    config = load_config()
    # default to config.default_engine, falling back to ollama if missing
    engine_to_use = engine or config.get("default_engine", "ollama")
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
                "Use [cyan]--text[/cyan], [cyan]--file[/cyan], "
                "or pipe data via stdin."
            )
            raise typer.Exit(code=1)

    spinner = Spinner("Generating")
    spinner.start()
    try:
        result = rewrite(input_text, engine_to_use, profile_data, config)
    finally:
        spinner.stop()

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
    typer.run(main)
