# LARI — LLM Artifact Removal Initiative  
### Profile-Based Rewriting for Natural, Human-Readable Text

![Project](https://img.shields.io/badge/Project-LARI-blueviolet)
![HumanMode](https://img.shields.io/badge/HumanMode-Profiles-green)
![CGPTSAO](https://img.shields.io/badge/CGPTSAO-Approved-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

# Overview

LARI rewrites text using profile-driven instructions that guide tone, rhythm, and clarity.  
The goal is to produce writing that feels natural and readable, without the mechanical patterns common in AI-generated content.

LARI runs locally with **Ollama by default**, requiring no API keys or cloud access.  
OpenAI and Anthropic engines remain available as optional backends.

---

# Installation

LARI can be installed with or without a virtual environment.

### Clone the project
```
git clone https://github.com/anasec/LARI
cd LARI
```

### (Optional) Create a virtual environment
This is recommended for clean dependency isolation.
```
python -m venv venv
```

Activate it:

macOS/Linux:
```
source venv/bin/activate
```

Windows:
```
venv\Scripts\activate.bat
```

### Install dependencies
```
pip install -r requirements.txt
```

---

# Default Local Setup (Ollama)

LARI uses Ollama as its default engine for offline rewriting.

### Install Ollama  
Download from:  
https://ollama.com/download

### Pull a model (recommended)
```
ollama pull llama3.1
```

### Start the service
```
ollama serve
```

LARI will automatically use the Ollama engine unless another engine is explicitly selected.

---

# Basic Usage

### Rewrite text directly
```
python lari.py run "Rewrite this text to feel more natural."
```

### Use a specific profile
```
python lari.py run "text here" --profile=linkedin
```

### Use file input
```
python lari.py run --file=input.txt --profile=technical
```

### Pipe from stdin
```
cat draft.txt | python lari.py run --profile=casual
```

If no text or file is provided, LARI listens for stdin.

---

# HumanMode Profiles

Profiles define rewrite behavior and live in:
```
config/profiles/
```

Each profile specifies system-level and user-level instructions that shape the result.  
To use a profile:
```
python lari.py run "text" --profile=academic
```

To create a new profile, add a JSON file in the profiles directory.

---

# Engines

LARI supports four engines:

| Engine | Backend | Offline | Notes |
|--------|---------|---------|-------|
| ollama | Local Ollama server | Yes | Default and recommended |
| openai | OpenAI Chat Completions | No | Requires API key |
| anthropic | Claude Messages API | No | Requires API key |
| dry-run | No model | Yes | Performs basic artifact cleanup |

Select an engine with:
```
python lari.py run "text" --engine=ollama
```

---

# Optional Cloud Engines (OpenAI and Anthropic)

These engines require API keys. They are entirely optional.

### macOS/Linux
```
export OPENAI_API_KEY="yourkey"
export ANTHROPIC_API_KEY="yourkey"
```

### Windows (PowerShell)
```
setx OPENAI_API_KEY "yourkey"
setx ANTHROPIC_API_KEY "yourkey"
```

Once set, you can run:
```
python lari.py run "text" --engine=openai
python lari.py run "text" --engine=anthropic
```

---

# Dry-Run Scrubber

The dry-run engine performs simple artifact cleanup without calling any model.

Example:
```
python lari.py run "as an AI, I think we should leverage this" --engine=dry-run
```

This mode removes common patterns and placeholders while preserving the original structure.

---

# Configuration

LARI reads from:
```
config/config.json
```

A typical configuration:
```json
{
  "profiles_path": "config/profiles",
  "openai_api_key_env": "OPENAI_API_KEY",
  "anthropic_api_key_env": "ANTHROPIC_API_KEY",
  "default_engine": "ollama",
  "default_model": "gpt-4o-mini",
  "temperature": 0.4,
  "max_tokens": 4096,
  "ollama": {
    "base_url": "http://localhost:11434",
    "model": "llama3.1"
  }
}
```

---

# Prompt Packs

The `prompt-packs/` folder provides ready-to-use prompt files for users who prefer using an LLM interface instead of the CLI.  

Each pack contains a complete, copy-paste prompt designed to reproduce a HumanMode style inside tools like ChatGPT, Claude, or Gemini.

Usage:
1. Open any `.txt` file in the folder  
2. Copy the entire contents  
3. Paste into the LLM of your choice  
4. Provide your draft text when requested  

This makes LARI accessible to non-technical users without installation.

---

# Development Roadmap

Planned improvements include:

• Output file support  
• Batch directory processing  
• Clipboard integration  
• Extended dry-run cleaning  
• Additional HumanMode profiles  
• GUI and editor extensions  

---

# Contributing

Contributions are welcome.  
You can add profiles, refine documentation, extend engines, or improve prompt packs.  
See `CONTRIBUTING.md` for guidelines.

---

# License

LARI is released under the MIT License.  
See the LICENSE file for full terms.

