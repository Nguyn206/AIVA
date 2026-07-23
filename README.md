# AIVA Project Management CLI

Sprint 14 adds commands for inspecting and resuming saved video projects.

Install the updated command entry points:

```powershell
pip install -e ".[dev]"
```

List projects:

```powershell
aiva-project list
```

Check one project:

```powershell
aiva-project status video_abc123
```

Resume with offline providers:

```powershell
aiva-project resume video_abc123 --mode mock
```

Resume with real providers:

```powershell
aiva-project resume video_abc123 --mode real
```

Use a different output directory:

```powershell
aiva-project --output-root D:\AIVA_Output list
```
