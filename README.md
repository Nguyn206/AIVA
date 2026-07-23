# AIVA Project Dashboard and Downloads

Sprint 17 adds:

- a browser project dashboard,
- project asset listing,
- secure asset downloads,
- direct final-video downloads.

New endpoints:

```text
GET /api/projects/{project_id}/assets
GET /api/projects/{project_id}/assets/{asset_path}/download
GET /api/projects/{project_id}/video
```

Run:

```powershell
pip install -e ".[dev]"
aiva-web
```

Then open:

```text
http://127.0.0.1:8000
```
