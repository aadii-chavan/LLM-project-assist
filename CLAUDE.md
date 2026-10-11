# CLAUDE.md

## Project
**Automatic Detection and Correction of Ambiguous Software Requirements Using LLMs.**
A B.Tech (CS, Data Science) college project. The code must be clean, readable, and easy for the student to explain and defend. **Prefer simple over clever.**

## What the system does
Input: software requirements (pasted text, `.txt`/`.csv` file, or an SRS section).
For each requirement it:
1. Decides whether it is ambiguous.
2. Identifies the ambiguity type(s) and the exact words causing it.
3. Rewrites the requirement to be specific, measurable, and testable, and generates 1-3 clarifying questions for the stakeholder.

## Stack
- Backend: Python, FastAPI, Pydantic
- Frontend: Next.js, TypeScript, Tailwind
- Database: Supabase (Postgres)
- LLM: Anthropic Claude API via the official Python SDK. Model name and API key come from environment variables, never hardcoded.

## Backend pipeline
1. **Preprocess**: split input into individual requirements, assign IDs, clean text.
2. **Detect** (LLM call #1): structured JSON with `ambiguous` (bool), `types` (list), `spans` (list of offending words/phrases), `explanation` (str), `confidence` (0-1).
3. **Correct** (LLM call #2): runs ONLY if `ambiguous` is true. Returns `rewritten_text`, `clarifying_questions` (1-3), `assumptions` (list).
4. **Verify**: re-run detection on the rewritten text. If still ambiguous, retry correction up to 2 times. Log the number of attempts.
5. **Store and return**: save everything, return a before/after result.

Detection and correction are deliberately **separate** LLM calls. All LLM outputs are validated against Pydantic schemas. **Log every prompt and response** (needed for error analysis in the report).

## Ambiguity types
- `lexical`: a word with multiple meanings
- `syntactic`: unclear structure, unresolved pronouns, ambiguous "and/or"
- `semantic`: unclear who does what, or unclear meaning
- `vagueness`: non-measurable terms like "fast", "user-friendly", "secure"
- `incompleteness`: missing numbers, conditions, or actors

## API endpoints
- `POST /analyze`: analyze one requirement
- `POST /analyze/batch`: analyze a whole document
- `GET /results/{run_id}`: fetch past results
- `POST /evaluate`: run the pipeline on the labeled dataset and return metrics
- `GET /health`

## Database tables
- `projects`: id, name, created_at
- `requirements`: id, project_id, original_text
- `analyses`: id, requirement_id, ambiguity_types, spans, explanation, rewritten_text, questions, method, attempts, created_at

`method` stores which approach produced the result: `rule_based`, `zero_shot`, `few_shot`, `few_shot_verifier`. This allows comparing approaches in one table.

## Folder structure
```
backend/
  app/main.py            (FastAPI routes)
  app/schemas.py         (Pydantic models)
  app/config.py          (env/config loading)
  app/pipeline/          (preprocess, detect, correct, verify)
  app/prompts/           (prompt templates, kept as separate files)
  eval/                  (dataset loader, run_eval.py, metrics.py)
  tests/
frontend/
  app/                   (upload page, results page)
```

## Evaluation plan (later stages)
Compare 4 methods: (1) rule-based keyword baseline, (2) zero-shot LLM, (3) few-shot LLM, (4) few-shot + verification loop.
- Detection metrics: precision, recall, F1.
- Rewrite quality: clarity, testability, meaning preserved (manual rating + LLM judge).
- Dataset: public requirements documents such as PURE, ~200-300 requirements labeled by the student.

## Working rules
- Build in small stages. Only do what the current prompt asks. Don't add features, files, or abstractions that weren't requested.
- Follow the folder structure and schemas above exactly. If something should change, tell the user first instead of changing it.
- Never commit secrets. Use `.env`, and keep a `.env.example` with placeholder values.
- Add type hints and short docstrings. Keep functions small.
- After each stage, tell the user how to run and test what was built.
- Keep the "Current status" section below up to date at the end of every stage.

## Current status
- [x] Stage 0: `CLAUDE.md` and `.gitignore` created. No application code yet.
- [ ] Stage 1: backend scaffold (not started; waiting for the user's go-ahead)
