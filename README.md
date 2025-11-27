# LARI — LLM Artifact Removal Initiative  
### Profile-Based Rewriting for Natural, Human-Readable Text

![Project](https://img.shields.io/badge/Project-LARI-blueviolet)
![HumanMode](https://img.shields.io/badge/HumanMode-Profiles-green)
![CGPTSAO](https://img.shields.io/badge/CGPTSAO-Approved-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

# Overview

LARI rewrites text using profile-driven instructions that guide tone, rhythm, and clarity.  
The goal is to produce writing that feels natural and readable, without the repetitive or mechanical patterns common in AI-generated text.

LARI runs locally with **Ollama as the default engine**, requiring no API keys.  
Cloud engines (OpenAI and Anthropic) are available as optional backends.

---

# Installation

You can install LARI with or without a virtual environment.

### Clone the project
```bash
git clone https://github.com/anasec/LARI
cd LARI
```

### (Optional) Create a virtual environment

macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate.bat
```

### Install dependencies
```bash
pip install -r requirements.txt
```

---

# Local Model Setup (Ollama)

Ollama allows LARI to run fully offline with a local LLM.

### Install Ollama  
Download from:  
https://ollama.com/download

### Pull a model
```bash
ollama pull llama3
```

### Start the service
```bash
ollama serve
```

LARI will use Ollama automatically when `default_engine` is set to `"ollama"` in `config/config.json`.

---

# Basic Usage

LARI is a single-command tool controlled through options.

### Rewrite inline text
```bash
python lari.py --text "Rewrite this sentence to feel more natural."
```

### Rewrite using a specific profile
```bash
python lari.py --text "text here" --profile=linkedin
```

### Rewrite from a file
```bash
python lari.py --file=input.txt --profile=technical
```

### Pipe input via stdin
```bash
cat draft.txt | python lari.py --profile=casual
```

### Write output to a file
```bash
python lari.py --file=input.txt --out=output.txt --profile=academic
```

During processing, a small spinner appears showing progress.

---

# HumanMode Profiles

Profiles control the rewriting style and live in:
```
config/profiles/
```

A profile can contain:

- explicit `system` and `user` prompts  
**or**
- structured fields like `name`, `description`, `style_instructions`, and `artifact_rules`

LARI converts these definitions into the prompts sent to the chosen engine.

### Use a profile
```bash
python lari.py --text "text" --profile=academic
```

### Create a new profile
1. Add a new JSON file in `config/profiles/`  
2. Define prompts or structured fields  
3. Use `--profile=<name>` with the filename (without `.json`)

---

# Engines

LARI supports four engines:

| Engine   | Backend                  | Offline | Notes                         |
|----------|--------------------------|---------|-------------------------------|
| ollama   | Local Ollama server      | Yes     | Default engine                |
| openai   | OpenAI Chat Completions  | No      | Requires API key              |
| anthropic| Claude Messages API      | No      | Requires API key              |
| dry-run  | No model                 | Yes     | Performs light artifact cleanup |

### Choose an engine explicitly
```bash
python lari.py --text "text" --engine=ollama
python lari.py --text "text" --engine=openai
python lari.py --text "text" --engine=anthropic
python lari.py --text "text" --engine=dry-run
```

If `--engine` is omitted, LARI uses `default_engine` from the config file.  
If that key is missing, it falls back to `ollama`.

---

# Optional Cloud Engines (OpenAI / Anthropic)

Cloud engines require API keys.  
They are optional and not needed for local usage.

### macOS/Linux
```bash
export OPENAI_API_KEY="yourkey"
export ANTHROPIC_API_KEY="yourkey"
```

### Windows PowerShell
```powershell
setx OPENAI_API_KEY "yourkey"
setx ANTHROPIC_API_KEY "yourkey"
```

Example usage:
```bash
python lari.py --text "text" --engine=openai
python lari.py --text "text" --engine=anthropic
```

Models are configured in `config/config.json`.

---

# Dry-Run Scrubber

For quick cleanup without using a model:
```bash
python lari.py --text "as an AI, I think we should leverage this" --engine=dry-run
```

Dry-run removes a small set of common artifacts and normalizes some punctuation.

---

# Configuration

LARI reads settings from:
```
config/config.json
```

A recommended configuration:

```json
{
  "default_engine": "ollama",
  "default_model": "gpt-4.1-mini",
  "profiles_path": "./config/profiles",
  "default_profile": "linkedin",
  "temperature": 0.6,
  "max_tokens": 1500,
  "openai_api_key_env": "OPENAI_API_KEY",
  "anthropic_api_key_env": "ANTHROPIC_API_KEY",
  "ollama": {
    "base_url": "http://localhost:11434",
    "model": "llama3"
  },
  "anthropic_model": "claude-3-sonnet-20240229"
}
```

Adjust the Ollama model name if you pulled a different one (for example, `"llama3.1"`).

---

# Prompt Packs

The `prompt-packs/` directory contains large, copy-paste-ready prompts designed for users who prefer pasting into ChatGPT, Claude, or Gemini instead of running the CLI.

Each pack:

- describes a HumanMode profile  
- contains a full prompt you can paste into any LLM  
- accepts your draft text when you paste it afterward  

Usage:

1. Open any `.txt` file in `prompt-packs/`  
2. Copy all text  
3. Paste into your LLM session  
4. Then paste your draft text  

This makes LARI usable for non-technical users without installing Python.

---

# Development Roadmap

Planned improvements:

- Output-to-file for batch workloads  
- Directory processing mode  
- Clipboard integration  
- Extended dry-run cleaning  
- More HumanMode profiles  
- More prompt packs  
- VS Code and browser integrations  
- Simple GUI wrapper  

---

# Contributing

Contributions are welcome.

Areas to help:

- Improving the overall code or revamping it completely... the goal is to get rid of all the AI sounding language that suffocates true human voice
- Creating new profiles  
- Improving documentation  
- Extending engine support  
- Adding prompt packs  

Open a pull request or issue at any time.

---

# License

LARI is released under the MIT License.  
See the `LICENSE` file for the full terms.

