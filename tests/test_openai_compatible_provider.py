import asyncio

import pytest

from code_cntx.models.inference import InferenceProviderError
from code_cntx.models.openai_compatible import (
    OpenAICompatibleConfig,
    OpenAICompatibleProvider,
)


class RecordingTransport:
    def __init__(self, response: dict) -> None:
        self.response = response
        self.calls: list[tuple[str, dict, dict[str, str]]] = []

    async def post(
        self,
        url: str,
        payload: dict,
        headers: dict[str, str],
    ) -> dict:
        self.calls.append((url, payload, headers))
        return self.response


def test_provider_calls_chat_completions() -> None:
    transport = RecordingTransport(
        {
            "choices": [
                {
                    "message": {
                        "content": "{\"summary\": \"ok\"}"
                    }
                }
            ]
        }
    )
    provider = OpenAICompatibleProvider(
        OpenAICompatibleConfig(
            name="free-provider",
            model="coder-model",
            base_url="https://api.example.com/v1",
            api_key="TEST_KEY_PLACEHOLDER",
        ),
        transport=transport,
    )

    result = asyncio.run(provider.complete("plan this task"))

    assert result == '{"summary": "ok"}'
    url, payload, headers = transport.calls[0]
    assert url == "https://api.example.com/v1/chat/completions"
    assert payload["model"] == "coder-model"
    assert payload["messages"][0]["content"] == "plan this task"
    assert headers["Authorization"] == "Bearer TEST_KEY_PLACEHOLDER"


def test_provider_supports_extra_headers() -> None:
    transport = RecordingTransport(
        {"choices": [{"message": {"content": "result"}}]}
    )
    provider = OpenAICompatibleProvider(
        OpenAICompatibleConfig(
            name="provider",
            model="model",
            base_url="https://api.example.com/v1/",
            api_key="TEST_KEY_PLACEHOLDER",
            extra_headers={"X-App": "code-cntx"},
        ),
        transport=transport,
    )

    asyncio.run(provider.complete("prompt"))

    assert transport.calls[0][2]["X-App"] == "code-cntx"


def test_provider_rejects_bad_response_shape() -> None:
    provider = OpenAICompatibleProvider(
        OpenAICompatibleConfig(
            name="provider",
            model="model",
            base_url="https://api.example.com/v1",
            api_key="TEST_KEY_PLACEHOLDER",
        ),
        transport=RecordingTransport({"unexpected": True}),
    )

    with pytest.raises(InferenceProviderError, match="unexpected response shape"):
        asyncio.run(provider.complete("prompt"))
