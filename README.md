# AIVA

**AIVA — AI Video Advertiser Platform**

AIVA is being built as a workflow-driven platform for researching products,
planning advertising content, generating media assets, and rendering complete
affiliate marketing videos.

## Current milestone

Sprint 1 — Foundation

Included:

- Environment-based settings
- Central logging
- Generic result type
- Initial package structure
- Automated tests

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Copy the environment template:

```powershell
Copy-Item .env.example .env
```

Run the application:

```powershell
python app.py
```

Run tests:

```powershell
pytest
```

Run code checks:

```powershell
ruff check .
```
