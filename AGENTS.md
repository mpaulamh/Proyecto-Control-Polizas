# AGENTS.md

## Repo basics
- **Python 3.11** is the target version (`.python-version`). Use it for any new scripts.
- Virtual environment lives at `.venv/` — activate it before running Python:
  `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows).
- No `pyproject.toml`, `requirements.txt`, `setup.py`, or `tox.ini` exist yet. Do not invent package managers or lockfiles.

## What this repo contains
- `Insumos_Control_Polizas/` — insurance policy PDFs (`polizas/`) and a client master Excel file (`Maestro_Clientes.xlsx`). This is primarily a data/inputs directory, not application source.
- No Python source files exist at the project root or inside `Insumos_Control_Polizas/`.

## Git / commit guardrails
- `.gitignore` only ignores `.DS_Store`. The `.venv/`, OS metadata, and large binaries are **not** ignored — double-check before `git add`/`git commit`.
- No branch, PR, or release conventions are defined in this repo.

## No test / lint / CI setup
- No test runner, linter, formatter, typechecker, or CI workflow is configured. Do not run `pytest`, `ruff`, `mypy`, etc. unless you add them first.
