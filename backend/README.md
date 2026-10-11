# Backend

FastAPI backend for detecting and correcting ambiguous software requirements.

Run all commands from the `backend/` folder.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your own values
```

## Run the server

```bash
uvicorn app.main:app --reload
```

- Health check: http://127.0.0.1:8000/health
- API docs: http://127.0.0.1:8000/docs

## Run the tests

```bash
pytest
```
