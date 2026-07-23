import pytest

from providers.models import (
    LLMRequest,
    LLMResponse,
    TokenUsage,
)


def test_llm_request_validates_prompt() -> None:
    with pytest.raises(ValueError):
        LLMRequest(prompt=" ")


def test_llm_request_validates_temperature() -> None:
    with pytest.raises(ValueError):
        LLMRequest(prompt="Create a script", temperature=3)


def test_llm_response_requires_text() -> None:
    with pytest.raises(ValueError):
        LLMResponse(
            text=" ",
            provider="mock",
            model="mock-model",
        )


def test_token_usage_rejects_negative_values() -> None:
    with pytest.raises(ValueError):
        TokenUsage(input_tokens=-1)
