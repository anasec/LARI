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
- Dry-run artifact scrubbing  
- CLI-driven text or file input  

LARI is designed for writing clarity and authenticity — not impersonation or bypassing safety features.

---

## 🚀 Features (Accurate to lari.py)

### ✔ HumanMode Profiles  
Profiles are stored as individual JSON files under:

```
config/profiles/
```

Each profile contains:
- `system` (system prompt)
- `user` (rewrite instructions)

Select with:

```bash
python lari.py "text here" --profile=linkedin
```

---

### ✔ Supported Engines

LARI supports exactly **four** engines:

| Engine      | Backend                   | Offline? | Notes |
|-------------|---------------------------|----------|-------|
| `openai`    | OpenAI Chat Completions   | No       | Uses env var for API key |
| `anthropic` | Claude Messages API       | No       | Uses env var for API key |
| `ollama`    | Local Ollama instance     | Yes      | Uses REST `/api/generate` |
| `dry-run`   | No model (regex scrub)    | Yes      | Simple artifact removal |

Example:

```bash
python lari.py "input text" --profile=technical --engine=openai
```

If `--engine` is omitted, LARI uses:

```
config["default_engine"]
```

---

### ✔ Dry-run Artifact Scrubber

`dry-run` applies a lightweight regex-style cleanup:

- Replaces em-dashes with hyphens  
- Removes phrases like “as an AI”, “in conclusion”, “furthermore”  
- Rewrites “leveraging” → “using”  
- Rewrites “dive deeper” → “look into”

Use:

```bash
python lari.py "text" --engine=dry-run
```

---

### ✔ CLI Input Options

LARI supports **two** input sources:

1. **Direct argument text**

```bash
python lari.py "Rewrite this text." --profile=linkedin
```

2. **File input**

```bash
python lari.py --file=notes.txt --profile=academic
```

3. **STDIN (pipe)**  
Triggered automatically when no text argument is supplied.

```bash
cat draft.txt | python lari.py --profile=casual
```

**Note:**  
There is **no `--pipe` option**, but STDIN works automatically.

---

## 📁 Repository Structure (Accurate)

```
LARI/
│
├── lari.py
├── README.md
├── LICENSE
│
├── config/
│   ├── config.json        ← Loaded at runtime
│   └── profiles/
│       ├── linkedin.json
│       ├── technical.json
│       ├── academic.json
│       ├── casual.json
│       └── (your custom profiles).json
│
└── prompts/ (optional documentation files)
```

**Important:**  
LARI loads only:

```
config/config.json
```

It does *not* use `config.example.json`, `keys.json`, or multilingual subfolders.

---

## ⚙️ Configuration

Your `config/config.json` must contain keys used by the code:

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

API keys must be stored as environment variables:

```bash
export OPENAI_API_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"
```

---

## 🛠 Usage Examples

### Rewrite using a profile
```bash
python lari.py --file=article.txt --profile=linkedin
```

### Choose an engine
```bash
python lari.py "text to rewrite" --profile=technical --engine=anthropic
```

### Offline use (Ollama)
```bash
python lari.py "local rewrite" --profile=casual --engine=ollama
```

### Dry-run cleanup
```bash
python lari.py "as an AI, I think— in conclusion…" --engine=dry-run
```

### Using STDIN
```bash
cat input.md | python lari.py --profile=academic
```

---

## 🧠 Profiles

Each profile JSON requires:

```json
{
  "system": "System instructions here.",
  "user": "Rewrite instructions here."
}
```

Create new profiles by dropping a `.json` file in:

```
config/profiles/
```

Use them via:

```bash
python lari.py --profile=myprofile
```

---

## 🔒 Safety Notes

LARI does *not*:
- impersonate specific individuals  
- bypass model safeguards  
- remove watermarking or forensic signals  

LARI *only* improves readability and reduces obvious AI artifacts.

---

## 📅 Roadmap (Grounded in Actual Code)

- [ ] Optional output file support (`--out`)
- [ ] Directory batch mode (`--dir`)
- [ ] Clipboard mode
- [ ] More robust dry-run cleaner
- [ ] Additional built-in profiles

---

## 🤝 Contributing

You can contribute by:
- Adding new profiles  
- Improving documentation  
- Extending engine support  
- Enhancing dry-run scrubbing  

Pull requests are welcomed.

---

## 📄 License

MIT License. See `LICENSE` for details.

---

## 🧭 Philosophy

LARI aims to preserve the usefulness of AI while removing its obvious artifacts, producing writing that feels clearer, calmer, and more human.

Stay human.  
Happy writing.
