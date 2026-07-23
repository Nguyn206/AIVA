# AIVA

AIVA is a tool that automatically creates an AI-generated video from product
information.

Current end-to-end pipeline:

```text
Product input
→ AI product analysis
→ AI script
→ AI storyboard
→ AI images
→ AI scene clips
→ AI narration
→ subtitles
→ final MP4
```

## Offline end-to-end demo

Install the project:

```powershell
pip install -e ".[dev]"
```

Run the complete mock pipeline:

```powershell
aiva --mock `
  --name "Smart Lamp" `
  --description "Adaptive desk lamp for home workers" `
  --target-market "Home workers" `
  --feature "Adaptive brightness" `
  --feature "Energy efficient"
```

The output is written under:

```text
output/video_<generated-id>/final.mp4
```

Mock mode validates the complete workflow without using paid APIs.
