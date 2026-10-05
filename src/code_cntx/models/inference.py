from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


class InferenceClient(Protocol):
    async def complete(self, prompt: str) -> str:
        ...


class InferenceProvider(Protocol):
    @property
    def name(self) -> str:
        ...

    async def complete(self, prompt: str) -> str:
        ...


class InferenceProviderError(RuntimeError):
    """A provider failed to complete a request."""


@dataclass(frozen=True, slots=True)
class ProviderAttempt:
    provider: str
    error: str


class AllProvidersFailed(InferenceProviderError):
    def __init__(self, attempts: Sequence[ProviderAttempt]) -> None:
        self.attempts = tuple(attempts)
        details = "; ".join(
            f"{attempt.provider}: {attempt.error}" for attempt in self.attempts
        )
        super().__init__(f"All inference providers failed: {details}")


class RoutedInferenceClient:
    """Tries inference providers in configured priority order."""

    def __init__(self, providers: Sequence[InferenceProvider]) -> None:
        if not providers:
            raise ValueError("At least one inference provider is required")
        self._providers = tuple(providers)

    async def complete(self, prompt: str) -> str:
        attempts: list[ProviderAttempt] = []

        for provider in self._providers:
            try:
                return await provider.complete(prompt)
            except InferenceProviderError as exc:
                attempts.append(
                    ProviderAttempt(
                        provider=provider.name,
                        error=str(exc),
                    )
                )

        raise AllProvidersFailed(attempts)
