import asyncio

import pytest

from code_cntx.models.inference import (
    AllProvidersFailed,
    InferenceProviderError,
    RoutedInferenceClient,
)


class FakeProvider:
    def __init__(
        self,
        name: str,
        *,
        response: str | None = None,
        error: str | None = None,
    ) -> None:
        self._name = name
        self._response = response
        self._error = error
        self.calls = 0

    @property
    def name(self) -> str:
        return self._name

    async def complete(self, prompt: str) -> str:
        self.calls += 1
        if self._error is not None:
            raise InferenceProviderError(self._error)
        assert self._response is not None
        return self._response


def test_router_uses_first_available_provider() -> None:
    first = FakeProvider("free-a", response="result-a")
    second = FakeProvider("ollama", response="result-local")
    router = RoutedInferenceClient([first, second])

    result = asyncio.run(router.complete("prompt"))

    assert result == "result-a"
    assert first.calls == 1
    assert second.calls == 0


def test_router_falls_back_to_next_provider() -> None:
    first = FakeProvider("free-a", error="rate limited")
    second = FakeProvider("ollama", response="result-local")
    router = RoutedInferenceClient([first, second])

    result = asyncio.run(router.complete("prompt"))

    assert result == "result-local"
    assert first.calls == 1
    assert second.calls == 1


def test_router_reports_all_provider_failures() -> None:
    router = RoutedInferenceClient(
        [
            FakeProvider("free-a", error="quota exceeded"),
            FakeProvider("ollama", error="not running"),
        ]
    )

    with pytest.raises(AllProvidersFailed) as exc_info:
        asyncio.run(router.complete("prompt"))

    assert [attempt.provider for attempt in exc_info.value.attempts] == [
        "free-a",
        "ollama",
    ]
