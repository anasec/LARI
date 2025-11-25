# Contributing to LARI — LLM Artifact Removal Initiative

Thanks for your interest in contributing.

## How to contribute

1. Fork the repository.
2. Create a feature branch from `main`.
3. Make your changes in small, focused commits.
4. Add or update documentation if behavior changes.
5. Open a pull request against `main`.

## Profiles

When adding a new HumanMode profile:

- Place JSON files in `config/profiles/`.
- Use a clear `name`, `description`, and `style_instructions`.
- Add `artifact_rules.remove_phrases` only for phrases that are clearly LLM artifacts.
- Do not copy private or proprietary instructions.

## Prompts

When adding prompts under `prompts/`:

- Keep them short and direct.
- Avoid marketing tone.
- Ensure they do not encourage harmful or deceptive use.

## Code style

- Keep the CLI simple and explicit.
- Use type hints where reasonable.
- Prefer clarity over cleverness.

## Security

Do not commit API keys or secrets.  
Use environment variables as described in the README.

By submitting a pull request, you agree that your contributions may be used, modified, and distributed under the MIT License.
