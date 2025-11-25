# Configuration Guide for LARI  
**LLM Artifact Removal Initiative**

This folder contains the configuration files that control how LARI behaves, which engines it uses, and which HumanMode profiles are loaded.

LARI can run in **three modes**:

1. **Offline Scrub Mode** (no internet, no API keys)  
2. **Online HumanMode Rewrite** (OpenAI or Anthropic)  
3. **Local LLM HumanMode Rewrite** using **Ollama** (no API keys)

This guide explains how to set up each mode.

---

## 📄 `config.json`  
This is the active configuration file.  
It must be valid JSON with **no comments**.

You can start by copying the provided example:

```bash
cp config/config.example.json config/config.json
