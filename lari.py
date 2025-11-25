#!/usr/bin/env python3
import json
import typer
from rich import print
from rich.console import Console
import requests
import os

app = typer.Typer(help="LARI — LLM Artifact Removal Initiative")

console = Console()

# ---------------------------------------------------------
# Load config
# ---------------------------------------------------------

def load_config():
    with open("config/config.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ---------------------------------------------------------
# Load profile
# ---------------------------------------------------------

def load_profile(profile_name, config):
    profile_path = os.path.join(config["profiles_path"], f"{profile_name}.json")
    if not os.path.exists(profile_path):
        console.print(f"[red]Profile not found:[/red] {profile_name}")
        raise typer.Exit()
    with open(profile_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---------------------------------------------------------
# Engine: OpenAI
# ---------------------------------------------------------

def rewrite_with_openai(text, profile, config):
    import openai

    api_key = os.getenv(config["openai_api_key_env"])
    if not api_key:
        console.print("[red]Missing OPENAI_API_KEY environment variable.[/red]")
        raise typer.Exit()

    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=config["default_model"],
        temperature=config["temperature"],
        max_tokens=config["max_tokens"],
        messages=[
            {"role": "system", "content": profile["system"]},
            {"role": "user", "content": profile["user"] + "\n\n" + text},
        ],
    )

    return response.choices[0].message.content.strip()


# ---------------------------------------------------------
# Engine: Anthropic
# ---------------------------------------------------------

def rewrite_with_anthropic(text, profile, config):
    import anthropic

    api_key = os.getenv(config["anthropic_api_key_env"])
    if not api_key:
        console.print("[red]Missing ANTHROPIC_API_KEY environment variable.[/red]")
        raise typer.Exit()

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        system=profile["system"],
        messages=[{"role": "user", "content": profile["user"] + "\n\n" + text}],
    )

    return response.content[0].text.strip()


# ---------------------------------------------------------
# Engine: Ollama (offline)
# ---------------------------------------------------------

def rewrite_with_ollama(text, profile, config):
    url = f'{config["ollama"]["base_url"]}/api/generate'
    model = config["ollama"]["model"]

    payload = {
        "model": model,
        "prompt": profile["system"] + "\n\n" + profile["user"] + "\n\n" + text,
        "temperature": config["temperature"]
    }

    resp = requests.post(url, json=payload)
    if resp.status_code != 200:
        console.print(f"[red]Ollama request failed:[/red] {resp.text}")
        raise typer.Exit()

    return resp.json().get("response", "").strip()


# ---------------------------------------------------------
# Main rewrite function
# ---------------------------------------------------------

def rewrite(text, engine, profile, config, dry_run=False):

    # Dry run mode — regex style cleaning
    if dry_run:
        cleaned = (
            text.replace("—", "-")
            .replace("–", "-")
            .replace("in conclusion", "")
            .replace("as an AI", "")
            .replace("leveraging", "using")
            .replace("dive deeper", "look into")
            .replace("furthermore", "")
        )
        return cleaned.strip()

    # Normal engine mode
    if engine == "openai":
        return rewrite_with_openai(text, profile, config)

    elif engine == "anthropic":
        return rewrite_with_anthropic(text, profile, config)

    elif engine == "ollama":
        return rewrite_with_ollama(text, profile, config)

    else:
        console.print(f"[red]Unknown engine:[/red] {engine}")
        raise typer.Exit()


# ---------------------------------------------------------
# CLI Command
# ---------------------------------------------------------

@app.command()
def run(
    text: str = typer.Argument(None, help="Text to rewrite. Leave blank to read from STDIN."),
    profile: str = typer.Option("linkedin", help="Profile to use."),
    engine: str = typer.Option(None, help="Engine: openai | anthropic | ollama | dry-run"),
    file: str = typer.Option(None, help="Input file path"),
):
    """
    LARI rewrite engine.
    """

    config = load_config()
    engine = engine or config["default_engine"]
    profile_data = load_profile(profile, config)

    # Load input
    if file:
        with open(file, "r", encoding="utf-8") as f:
            text_input = f.read()
    elif text is None:
        text_input = typer.get_text_stream("stdin").read()
    else:
        text_input = text

    result = rewrite(
        text_input,
        engine,
        profile_data,
        config,
        dry_run=(engine == "dry-run"),
    )

    print("\n[bold green]=== LARI OUTPUT ===[/bold green]\n")
    print(result)


if __name__ == "__main__":
    app()
