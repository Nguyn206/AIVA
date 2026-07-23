import base64
from dataclasses import dataclass, field

from providers.image.models import ImageGenerationRequest
from providers.image.openai_provider import OpenAIImageProvider

_PIXEL = base64.b64encode(b"fake-image-data").decode("utf-8")


@dataclass
class FakeImage:
    b64_json: str = _PIXEL
    revised_prompt: str = "Revised prompt"


@dataclass
class FakeImageResponse:
    data: list[FakeImage] = field(
        default_factory=lambda: [FakeImage()]
    )
    _request_id: str = "image-request-123"


class FakeImages:
    def __init__(self) -> None:
        self.parameters = None

    def generate(self, **parameters):
        self.parameters = parameters
        return FakeImageResponse()


class FakeClient:
    def __init__(self) -> None:
        self.images = FakeImages()


def test_openai_image_provider_saves_base64_image(tmp_path) -> None:
    client = FakeClient()
    provider = OpenAIImageProvider(
        client=client,
        default_model="test-image-model",
    )

    result = provider.generate(
        ImageGenerationRequest(
            prompt="Advertising image",
            size="1024x1024",
        ),
        output_directory=tmp_path,
    )

    response = result.unwrap()
    assert response.images[0].path.read_bytes() == b"fake-image-data"
    assert client.images.parameters["prompt"] == "Advertising image"
    assert client.images.parameters["model"] == "test-image-model"
