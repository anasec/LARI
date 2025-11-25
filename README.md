# LARI — LLM Artifact Removal Initiative  
### Humanizing AI-generated text through profile-driven rewriting

![Project](https://img.shields.io/badge/Project-LARI-blueviolet)
![HumanMode](https://img.shields.io/badge/HumanMode-Profiles-green)
![CGPTSAO](https://img.shields.io/badge/CGPTSAO-Approved-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🧩 Overview

**LARI (LLM Artifact Removal Initiative)** is a lightweight, profile-driven rewriting tool that cleans AI-generated text and rewrites it through OpenAI, Anthropic, or Ollama.

It supports:

- HumanMode rewriting profiles  
- A simple “dry-run” artifact scrubber  
- CLI-driven text, file, or stdin input  

LARI is designed for **clarity** and **authenticity**, not impersonation or bypassing safety features.

---

## 🚀 Features

### ✔ HumanMode Profiles

Profiles are stored as JSON under:

```
config/profiles/
```

Each profile contains:

```json
{
  "system": "System-level instructions for the model.",
  "user": "User-level rewrite instructions before the actual text."
}
```

You select a profile with the `--profile` option:

```bash
python lari.py run "Rewrite this text." --profile=linkedin
```

If no profile is provided, the default is:

```bash
--profile=linkedin
```

---

### ✔ Supported Engines

LARI supports exactly **four** engines, controlled by `--engine`:

| Engine      | Backend                     | Offline? | Notes                                                  |
|-------------|-----------------------------|----------|--------------------------------------------------------|
| `openai`    | OpenAI Chat Completions     | No       | Model name from `config["default_model"]`             |
| `anthropic` | Claude Messages API         | No       | Model is currently fixed to `claude-3-sonnet-20240229` |
| `ollama`    | Local Ollama instance       | Yes      | Uses `config["ollama"]["base_url"]` and `["model"]`   |
| `dry-run`   | No model (regex-style scrub)| Yes      | Applies simple string replacements only               |

If `--engine` is omitted, LARI uses:

```json
"default_engine": "openai"
```

(from `config/config.json`)

Examples:

```bash
# OpenAI
python lari.py run "input text" --profile=technical --engine=openai

# Anthropic (Claude 3 Sonnet)
python lari.py run "input text" --profile=linkedin --engine=anthropic

# Ollama (local model)
python lari.py run "input text" --profile=casual --engine=ollama

# Dry-run scrub only
python lari.py run "as an AI, in conclusion— leveraging this…" --engine=dry-run
```

---

### ✔ Dry-run Artifact Scrubber

When you choose `--engine=dry-run`, LARI does **not** call any model.  
Instead, it applies a simple set of replacements:

- Replace `—` and `–` with `-`
- Remove `"in conclusion"`
- Remove `"as an AI"`
- Replace `"leveraging"` → `"using"`
- Replace `"dive deeper"` → `"look into"`
- Remove `"furthermore"`

Example:

```bash
python lari.py run "as an AI, I think we should leverage this— in conclusion." --engine=dry-run
```

---

### ✔ Input Options

The `run` command supports three ways to feed text:

1. **Positional argument**

   ```bash
   python lari.py run "Rewrite this text to sound more human." --profile=linkedin
   ```

2. **File input**

   ```bash
   python lari.py run --file=notes.txt --profile=academic
   ```

3. **STDIN (pipe)**  
   If the `text` argument is omitted and `--file` is not set, LARI reads from stdin:

   ```bash
   cat draft.txt | python lari.py run --profile=technical
   ```

The function signature in `lari.py`:

```python
@app.command()
def run(
    text: str = typer.Argument(
        None,
        help="Text to rewrite. Leave blank to read from STDIN."
    ),
    profile: str = typer.Option("linkedin", help="Profile to use."),
    engine: str = typer.Option(
        None,
        help="Engine: openai | anthropic | ollama | dry-run"
    ),
    file: str = typer.Option(None, help="Input file path"),
):
    ...
```

There is **no** `--out`, `--dir`, `--clipboard`, or `--pipe` flag implemented in `lari.py`.


Notes:

- `config/config.json` is the **actual** config file used by the code.  
- `config/config.example.json` is a template you can copy/modify.  
- `prompt-packs/` and `prompts/` are **for humans**, not consumed by `lari.py` directly.

---

## ⚙️ Configuration

LARI loads:

```python
with open("config/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
```

A minimal working `config/config.json` might look like:

```json
{
  "profiles_path": "config/profiles",

  "openai_api_key_env": "OPENAI_API_KEY",
  "anthropic_api_key_env": "ANTHROPIC_API_KEY",

  "default_engine": "openai",
  "default_model": "gpt-4o-mini",

  "temperature": 0.4,
  "max_tokens": 4096,

  "ollama": {
    "base_url": "http://localhost:11434",
    "model": "llama3"
  }
}
```

Set your API keys via environment variables:

```bash
export OPENAI_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
```

The Anthropic engine currently uses a fixed model:

```python
model="claude-3-sonnet-20240229"
```

If you want a different Claude model, you edit `lari.py`.

---

## 🧠 Profiles (HumanMode)

Each JSON profile in `config/profiles/` defines how LARI rewrites text:

- System-level instructions (`system`)
- User-level instructions (`user`)

Example usage:

```bash
python lari.py run --file=blog.txt --profile=technical --engine=openai
python lari.py run "Make this sound less robotic." --profile=casual --engine=ollama
```

To add a new profile:

1. Create `config/profiles/myprofile.json`
2. Define `"system"` and `"user"` fields
3. Run:

   ```bash
   python lari.py run --file=input.txt --profile=myprofile
   ```

---

## 📦 Prompt Packs (for non-technical users)

The **`prompt-packs/` folder** is for people who **don’t want to run the CLI at all**.

It contains ready-made prompt files:

- `HUMANMODE_Academic.txt`
- `HUMANMODE_Casual.txt`
- `HUMANMODE_LinkedIn.txt`
- `HUMANMODE_Master.txt`
- `HUMANMODE_Technical.txt`

Each file:

- Explains how to use a HumanMode style  
- Includes a long-form, copy-pasteable prompt  
- Works directly in ChatGPT, Claude, Gemini, or any other LLM UI  

**How to use (no coding required):**

1. Open any `HUMANMODE_*.txt` file
2. Copy the entire contents
3. Paste it into your chatbot of choice (ChatGPT, Claude, etc.)
4. Paste or upload your draft text when the model asks

This gives non-technical teammates access to LARI’s HumanMode concepts without touching Python or config files.

---

## 🛠 Installation

From the repo root:

```bash
git clone https://github.com/anasec/LARI.git
cd LARI
pip install -r requirements.txt
```

Make sure `config/config.json` exists (you can copy `config/config.example.json` and modify it).

---

## 🔒 Safety Notes

LARI is meant to:

- Reduce robotic phrasing  
- Remove obvious AI “tells”  
- Improve readability and tone  

LARI does **not**:

- Impersonate specific people  
- Bypass safety systems  
- Guarantee undetectability  
- Strip forensic or watermark signals  

It is a writing-quality tool, not an evasion tool.

---

## 📅 Roadmap (code-level)

Planned / logical next features:

- [ ] Optional output file support (`--out`)
- [ ] Directory batch mode (`--dir`)
- [ ] Clipboard mode
- [ ] Stronger dry-run artifact cleaner
- [ ] More built-in profiles and prompt packs

---

## 🤝 Contributing

You can contribute by:

- Adding new profiles under `config/profiles/`  
- Extending engine support  
- Improving documentation  
- Expanding prompt-packs for different audiences  

See `CONTRIBUTING.md` for guidelines. Pull requests are welcome.

---

## 📄 License

This project is licensed under the **MIT License**.  
See the `LICENSE` file for full details.

---

## 🧭 Philosophy

LARI exists for people who like the speed of AI, but not the way AI usually sounds. 
LLMs aren't going anywhere, and the amount of AI text flooding the world is only going to get worse. This project aims to keep us a little bit more human.

Stay human.  
Happy writing.
