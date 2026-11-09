# AGENTS.md

This is **not a software project**. There is no source code, no package manager, no build/test/lint/CI configuration, and no git repository. Do not look for `package.json`, `requirements.txt`, `Makefile`, test runners, or entrypoints — they do not exist.

## What is in this repo

- `Insumos_Control_Polizas/Maestro_Clientes.xlsx` — client master data (Excel).
- `Insumos_Control_Polizas/polizas/` — 21 insurance policy PDFs named `Poliza_<PREFIX>-2026-NNNN.pdf`.
  - Prefixes seen: `AIS` (5), `PCS` (9), `SPC` (6). All dated 2026.
- `.DS_Store` files at repo root and under `Insumos_Control_Polizas/` — macOS artifacts; ignore them, do not commit them.

## How to work here

- Treat files as read-only reference data unless told otherwise.
- There are no commands to run: no install, build, test, lint, or deploy steps.
- If version control is added later, track only `Maestro_Clientes.xlsx` and `polizas/`; exclude `.DS_Store`.

Nothing else in this repository affects how an agent should work. If you need to process these documents (e.g., extract policy data from the PDFs or Excel), that is a separate task — no tooling for it exists here yet.
