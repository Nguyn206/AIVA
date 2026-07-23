from pathlib import Path

from engine.context import WorkflowContext
from providers.audio.models import GeneratedAudio
from providers.image.models import GeneratedImage
from providers.video.models import GeneratedVideo
from render.models import RenderResult
from schemas.subtitles import SubtitleCue, SubtitleTrack
from schemas.video_planning import ProductInput, Storyboard, VideoScript
from services.context_persistence import load_context, save_context
from services.image_generation import SceneImageAsset
from services.subtitle_generation import SubtitleAsset
from services.video_generation import SceneVideoAsset
from services.voice_generation import SceneNarrationAsset


def test_context_restores_pipeline_assets(tmp_path) -> None:
    image = GeneratedImage(
        path=tmp_path / "image.png",
        prompt="image prompt",
        provider="mock-image",
        model="mock-image-model",
    )
    video = GeneratedVideo(
        path=tmp_path / "clip.mp4",
        prompt="video prompt",
        provider="mock-video",
        model="mock-video-model",
        duration_seconds=3,
        source_image=image.path,
    )
    audio = GeneratedAudio(
        path=tmp_path / "audio.wav",
        provider="mock-voice",
        model="mock-voice-model",
        voice="alloy",
        text="Narration",
        response_format="wav",
    )
    track = SubtitleTrack(
        cues=(
            SubtitleCue(
                index=1,
                start_seconds=0,
                end_seconds=3,
                text="Narration",
            ),
        )
    )
    context = WorkflowContext(
        project_id="project-1",
        data={
            "product_input": ProductInput(
                name="Product",
                description="Description",
                target_market="Audience",
            ),
            "video_script": VideoScript.from_dict(
                {
                    "title": "Title",
                    "hook": "Hook",
                    "scenes": [{"scene": 1}],
                    "narration": "Narration",
                    "call_to_action": "Buy now",
                }
            ),
            "storyboard": Storyboard.from_dict(
                {
                    "scenes": [
                        {
                            "scene_number": 1,
                            "duration_seconds": 3,
                            "narration": "Narration",
                            "visual_description": "Visual",
                            "image_prompt": "Image",
                            "video_prompt": "Video",
                        }
                    ]
                }
            ),
            "scene_images": (
                SceneImageAsset(scene_number=1, image=image),
            ),
            "scene_videos": (
                SceneVideoAsset(scene_number=1, video=video),
            ),
            "scene_narration_audio": (
                SceneNarrationAsset(scene_number=1, audio=audio),
            ),
            "subtitle_asset": SubtitleAsset(
                track=track,
                srt_path=tmp_path / "subtitles.srt",
                vtt_path=tmp_path / "subtitles.vtt",
            ),
            "final_video": RenderResult(
                output_path=tmp_path / "final.mp4",
                scene_count=1,
                subtitle_burned=True,
                command=("ffmpeg",),
            ),
        },
    )

    path = save_context(context, tmp_path / "context.json")
    restored = load_context(path)

    assert isinstance(restored.require("product_input"), ProductInput)
    assert isinstance(restored.require("video_script"), VideoScript)
    assert isinstance(restored.require("storyboard"), Storyboard)
    assert isinstance(restored.require("scene_images")[0], SceneImageAsset)
    assert isinstance(restored.require("scene_videos")[0], SceneVideoAsset)
    assert isinstance(
        restored.require("scene_narration_audio")[0],
        SceneNarrationAsset,
    )
    assert isinstance(restored.require("subtitle_asset"), SubtitleAsset)
    assert isinstance(restored.require("final_video"), RenderResult)
    assert restored.require("final_video").output_path == Path(
        tmp_path / "final.mp4"
    )
