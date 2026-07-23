# AIVA

AIVA creates a complete AI-generated product video.

## Modes

### Offline validation

```powershell
aiva --mode mock `
  --name "Smart Lamp" `
  --description "Adaptive desk lamp" `
  --target-market "Home workers"
```

### Real video generation

Real mode uses OpenAI for planning, images, and narration. FFmpeg turns
the AI-generated images into animated scene clips and renders the final MP4.

1. Install FFmpeg and ensure `ffmpeg --version` works.
2. Copy `.env.example` to `.env`.
3. Add your real `OPENAI_API_KEY`.
4. Run:

```powershell
aiva --mode real `
  --name "Smart Lamp" `
  --description "Adaptive desk lamp for home workers" `
  --target-market "Home workers" `
  --feature "Adaptive brightness"
```

Output:

```text
output/video_<id>/final.mp4
```
