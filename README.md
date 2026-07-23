# AIVA Background Jobs

Sprint 16 moves long-running video generation out of the HTTP request thread.

The browser now:

1. submits a video job,
2. receives a job ID immediately,
3. polls the job-status endpoint,
4. displays progress and the final video path.

Run:

```powershell
pip install -e ".[dev]"
aiva-web
```

Endpoints:

```text
POST /api/jobs/videos
GET  /api/jobs/{job_id}
```

The original synchronous `POST /api/videos` endpoint remains available.
