# Tessera – AfCFTA rules of origin pre-check (prototype)

**Synthetic data – prototype – indicative only.**
Prototype of the flagship service of a government-supported AI Adoption and Innovation Centre in Ghana
(BI Norwegian Business School, AI for Business, Autumn 2026, Group 10).
It gives formally registered food manufacturers an indicative pre-check of whether a product of **HS heading 19.01**
(e.g. malt extract, millet porridge mix) is likely to meet the AfCFTA rules of origin, and what is missing.
GRA Customs and the National AfCFTA Approval Committee make the official decision.

## What is where

| Folder | Content |
|---|---|
| `rules/` | `rules.json` (71 entries: verbatim text, source file, page, provision, date, legal status, engine behaviour), `build_rules.py`, `validate.py` |
| `engine/` | Deterministic rule engine – pure Python standard library, exact `Decimal` arithmetic. The same files run in the browser (Pyodide). |
| `adapter/` | Language-model adapter: `stub.py` (shown as "Tessera prototype") and `live.py` (optional Google Gemini free tier, run locally). Prompts in `adapter/prompts/`. |
| `generator/` | Seeded synthetic SME generator, defect library, handwriting-style image renderer. |
| `answer_key/` | `fixed_key.json` (hand-derived, five required tests, checker fields blank) and `derive.py` (independent expectations for the evaluation set). |
| `cases/` | Generated cases (`fixed/`, `eval/`), readable versions (`readable/`), images, `manifest.json`, `recorded/` (live runs). |
| `pipeline/` | Glue: documents → adapter → engine → citation check → comparison with the answer key; writes the website data and the test log. |
| `tests/` | pytest suite (rules, engine, boundaries, case pack) and `tests/js/pyodide_parity.mjs`. |
| `web/` | Static website (Vite + React + TypeScript + Tailwind, hash routing). Pages: Overview, Navigator (tabs: Upload, 1 Inputs, 2 AI task, 3 Model, 4 Adviser view, 5 SME view), Monitoring, Test log, Show the logic, Credits. |
| `docs/` | Plan, revision log, test log, assumptions, Appendix B draft, demo script, screenshot list, run snapshots. |

Generator, engine, adapter and answer key never import each other's logic (enforced by `tests/test_boundaries_and_generator.py`).

## Run locally

Python 3.12+ and Node 20+.

```bash
pip install -r requirements-dev.txt
python rules/validate.py                 # rules.json schema + source check
python -m generator.build                # cases (seed 2026) – optional, already committed
python -m generator.render               # handwriting-style images – optional
python -m answer_key.derive              # evaluation answer key
python -m pipeline.run_cases             # stub -> engine on every case -> web/public/data
python -m pipeline.test_log              # Appendix A test log + metrics
python -m pytest -q                      # 54 tests

cd web && npm ci && npm run dev          # http://localhost:5173
```

### Optional live model (free)
The website never contains an API key. Live runs are made locally:

```bash
export GEMINI_API_KEY=...                # from Google AI Studio (free tier); never commit it
python -m adapter.run --case T5a --live  # writes cases/recorded/T5a_<date>.json (model, version, date, prompt hash)
```
Free-tier inputs may be used by Google to improve its products – send synthetic data only.
A recorded run is labelled "recorded live run"; its explanation is checked against `rules.json` and flagged if it cites anything else.

## Deploy to GitHub Pages (manual)
1. Create a new **public** repository on GitHub (any name).
2. Upload the whole folder (GitHub web: *Add file → Upload files*, or `git init && git add . && git commit -m "prototype" && git branch -M main && git remote add origin <url> && git push -u origin main`).
3. In the repository: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. The workflow `.github/workflows/pages.yml` validates `rules.json`, checks that the generator is deterministic, runs the pipeline and pytest, checks engine parity under Pyodide, builds the site and deploys it. The URL appears under *Actions → latest run → deploy*: `https://<user>.github.io/<repo>/`.

The site uses a relative base path and hash routing, so it works under any repository name.

## Link or embed from Adobe
- **Adobe Portfolio** accepts `<iframe>` embed code (Add content → Embed). Use:
  ```html
  <iframe src="https://<user>.github.io/<repo>/#/navigator/T3c/sme" title="Tessera (prototype)"
          width="100%" height="900" style="border:0" loading="lazy"></iframe>
  ```
  Also add a normal link "Open full screen" to `https://<user>.github.io/<repo>/`.
- **Adobe Express** web pages do not accept arbitrary embed code; add a **button or linked image** to `https://<user>.github.io/<repo>/`.
- The in-browser Python engine loads Pyodide from cdn.jsdelivr.net. If that is blocked, the site switches to precomputed results and says so.

## Status labels used everywhere
- 19.01 rule: Appendix IV, approved December 2023.
- 15% tolerance and FOB basis: annex to a **draft** decision (EX.CL/1329(XL), January 2022) – adoption not confirmed in the attached sources; value tolerance also listed as outstanding in Annex 2 Art. 42(1)(e).
- Ex-Chapter 19 wheat condition: **not applied – group decision**.
- Operation map for Article 7: **group interpretation**.
