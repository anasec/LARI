# LARI — LLM Artifact Removal Initiative  
### Humanizing AI-generated text through profile-driven rewriting

![Project](https://img.shields.io/badge/Project-LARI-blueviolet)
![HumanMode](https://img.shields.io/badge/HumanMode-Profiles-green)
![CGPTSAO](https://img.shields.io/badge/CGPTSAO-Approved-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🧩 Overview

**LARI (LLM Artifact Removal Initiative)** is a lightweight, open-source toolkit designed to rewrite AI-generated text so it reads more human.

It removes common AI artifacts, applies configurable "HumanMode" writing profiles, and supports multiple LLM providers.  
LARI is built for **quality**, **clarity**, and **authenticity**, not impersonation.

---

## 🚀 Features

### ✔ HumanMode Profiles  
Rewrite text using human-oriented styles:
- Technical  
- Academic  
- LinkedIn  
- Casual  
- Multilingual (EN / ES / ZH / HI)

### ✔ Artifact Scrubber  
Automatically strips:
- Repetitive LLM sentence forms  
- Hedging language  
- Robotic symmetry and transitions  
- Over-formatted structure  
- Predictable GPT-style phrasing

### ✔ Multi-Model Support  
Compatible with:
- OpenAI  
- Anthropic  
- Groq  
- LM Studio  
- Any model with an API endpoint

### ✔ CLI Tool  
Use LARI from the terminal:

```bash
lari input.txt --profile=linkedin --model=openai
```

### ✔ Extensible Profiles & Prompts  
Add or customize writing styles easily.

---

## 📁 Repository Structure

```
LARI/
│
├── README.md
├── LICENSE
├── lari.py
│
├── config/
│   ├── config.example.json
│   └── profiles/
│       ├── technical.json
│       ├── academic.json
│       ├── linkedin.json
│       ├── casual.json
│       └── multilingual/
│           ├── english.json
│           ├── spanish.json
│           ├── mandarin.json
│           └── hindi.json
│
├── prompts/
│   ├── technical.md
│   ├── academic.md
│   ├── linkedin.md
│   ├── casual.md
│   └── stealth.md
│
└── scripts/
    └── installer.sh
```

---

## ⚙️ Installation

### Clone the repository
```bash
git clone https://github.com/anasec/LARI.git
cd LARI
pip install -r requirements.txt
```

---

## 🛠 Usage

### Basic usage
```bash
python lari.py input.txt --profile=technical
```

### Specify model
```bash
python lari.py input.txt --profile=linkedin --model=openai
```

### Output to file
```bash
python lari.py input.txt --profile=casual --out=cleaned.txt
```

---

## 🧠 HumanMode Profiles

Each profile defines:
- sentence variation rules  
- tone shaping  
- artifact removal  
- personal writing quirks  
- disallowed LLM phrases

Profiles are stored under `config/profiles/`.

To create your own:
1. Copy an existing `.json` file  
2. Adjust tone, rules, and patterns  
3. Select it with `--profile=yourname`

---

## 🔒 Safety & Ethics

LARI focuses on:
- removing artificial language artifacts  
- improving clarity  
- enhancing authenticity  

LARI **does not** attempt to impersonate specific individuals  
and **does not** bypass model safety features.

---

## 📅 Roadmap

- [ ] LARI v1.1 — GUI mode  
- [ ] LARI Web Service  
- [ ] Contributor profiles  
- [ ] Language expansion (JP, FR, DE)  
- [ ] GitHub Action plugin  
- [ ] VS Code extension  
- [ ] “Batch rewrite” mode for entire folders

---

## 🤝 Contributing

Pull requests are welcome — whether you're:
- adding new HumanMode profiles  
- refining artifact rules  
- improving documentation  
- expanding multilingual coverage  

See `CONTRIBUTING.md` for guidelines.

---

## 📄 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## 🧭 Why LARI Exists

If you want your writing to sound human while still using AI tools, LARI gives you the middle ground:  
**AI-assisted writing with human-level authenticity.**

Happy writing. Stay human.
