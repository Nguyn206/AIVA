# AIVA Real Mode Preflight

Sprint 18 prevents real video jobs from starting with incomplete local
configuration.

The web interface can now check:

- whether `OPENAI_API_KEY` exists,
- whether FFmpeg is available,
- whether the output directory is writable,
- whether provider model names are configured.

New endpoint:

```text
GET /api/preflight/real
```

Run:

```powershell
pip install -e ".[dev]"
aiva-web
```

Open:

```text
http://127.0.0.1:8000
```
