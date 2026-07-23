from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class MessageRole(StrEnum):
    SYSTEM = "system"
    DEVELOPER = "developer"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True, slots=True)
class Message:
    role: MessageRole
    content: str

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Message content must not be empty.")


@dataclass(frozen=True, slots=True)
class LLMRequest:
    prompt: str
    system_instruction: str | None = None
    model: str | None = None
    temperature: float | None = None
    max_output_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.prompt.strip():
            raise ValueError("LLM prompt must not be empty.")
        if self.temperature is not None and not 0 <= self.temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2.")
        if self.max_output_tokens is not None and self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be greater than zero.")


@dataclass(frozen=True, slots=True)
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    def __post_init__(self) -> None:
        if min(
            self.input_tokens,
            self.output_tokens,
            self.total_tokens,
        ) < 0:
            raise ValueError("Token counts cannot be negative.")


@dataclass(frozen=True, slots=True)
class LLMResponse:
    text: str
    provider: str
    model: str
    request_id: str | None = None
    usage: TokenUsage = field(default_factory=TokenUsage)
    raw: Any = None

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("LLM response text must not be empty.")
        if not self.provider.strip():
            raise ValueError("Provider name must not be empty.")
        if not self.model.strip():
            raise ValueError("Model name must not be empty.")
