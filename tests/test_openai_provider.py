from dataclasses import dataclass, field

from providers.models import LLMRequest
from providers.openai_provider import OpenAIProvider


@dataclass
class FakeUsage:
    input_tokens: int = 12
    output_tokens: int = 8
    total_tokens: int = 20


@dataclass
class FakeResponse:
    output_text: str = "Generated advertising script"
    model: str = "test-model"
    usage: FakeUsage = field(default_factory=FakeUsage)
    _request_id: str = "request-123"


class FakeResponses:
    def __init__(self) -> None:
        self.parameters = None

    def create(self, **parameters):
        self.parameters = parameters
        return FakeResponse()


class FakeClient:
    def __init__(self) -> None:
        self.responses = FakeResponses()


def test_openai_provider_uses_responses_api() -> None:
    client = FakeClient()
    provider = OpenAIProvider(
        client=client,
        default_model="test-model",
    )

    result = provider.generate(
        LLMRequest(
            prompt="Create video script",
            system_instruction="You are a video advertiser.",
            max_output_tokens=500,
        )
    )

    response = result.unwrap()
    assert response.text == "Generated advertising script"
    assert response.request_id == "request-123"
    assert response.usage.total_tokens == 20
    assert client.responses.parameters == {
        "model": "test-model",
        "input": "Create video script",
        "instructions": "You are a video advertiser.",
        "max_output_tokens": 500,
    }


def test_openai_provider_requires_api_key_without_client() -> None:
    provider = OpenAIProvider(api_key=None)
    provider.api_key = None

    result = provider.generate(
        LLMRequest(prompt="Create video")
    )

    assert result.success is False
    assert result.error_type == "ProviderConfigurationError"
