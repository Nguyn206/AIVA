from providers.image.mock import MockImageProvider
from providers.image.models import ImageGenerationRequest


def test_mock_image_provider_creates_files(tmp_path) -> None:
    provider = MockImageProvider()

    result = provider.generate(
        ImageGenerationRequest(
            prompt="Cinematic product image",
            count=2,
        ),
        output_directory=tmp_path,
    )

    response = result.unwrap()
    assert len(response.images) == 2
    assert all(image.path.exists() for image in response.images)
    assert len(provider.requests) == 1
