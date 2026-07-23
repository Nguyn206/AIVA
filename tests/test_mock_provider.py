from providers.mock import MockLLMProvider
from providers.models import LLMRequest


def test_mock_provider_generates_deterministic_response() -> None:
    provider = MockLLMProvider(response="Generated script")

    result = provider.generate(
        LLMRequest(prompt="Write a product video script")
    )

    response = result.unwrap()
    assert response.text == "Generated script"
    assert response.provider == "mock"
    assert response.usage.total_tokens > 0


def test_mock_provider_accepts_response_factory() -> None:
    provider = MockLLMProvider(
        response=lambda request: f"Echo: {request.prompt}"
    )

    result = provider.generate(LLMRequest(prompt="Camera"))

    assert result.unwrap().text == "Echo: Camera"
