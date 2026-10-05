import asyncio

from code_cntx.models.ollama import OllamaConfig, OllamaProvider


class RecordingTransport:
    def __init__(self, response: dict) -> None:
        self.response = response
        self.calls: list[tuple[str, dict]] = []

    async def post(self, url: str, payload: dict) -> dict:
        self.calls.append((url, payload))
        return self.response


def test_ollama_provider_calls_generate_api_with_json_mode() -> None:
    transport = RecordingTransport({"response": "{\"summary\": \"ok\"}"})
    provider = OllamaProvider(
        OllamaConfig(model="qwen2.5-coder:7b"),
        transport=transport,
    )

    result = asyncio.run(provider.complete("plan this task"))

    assert result == '{"summary": "ok"}'
    assert transport.calls == [
        (
            "http://127.0.0.1:11434/api/generate",
            {
                "model": "qwen2.5-coder:7b",
                "prompt": "plan this task",
                "stream": False,
                "format": "json",
            },
        )
    ]
