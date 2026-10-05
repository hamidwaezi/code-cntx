from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Protocol
from urllib import error, request

from code_cntx.models.inference import InferenceProviderError


class JsonTransport(Protocol):
    async def post(self, url: str, payload: dict) -> dict:
        ...


class UrllibJsonTransport:
    async def post(self, url: str, payload: dict) -> dict:
        return await asyncio.to_thread(self._post_sync, url, payload)

    @staticmethod
    def _post_sync(url: str, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=120) as response:
                raw = response.read().decode("utf-8")
        except (error.URLError, TimeoutError, OSError) as exc:
            raise InferenceProviderError(f"Ollama request failed: {exc}") from exc

        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise InferenceProviderError("Ollama returned invalid JSON") from exc

        if not isinstance(result, dict):
            raise InferenceProviderError("Ollama response must be a JSON object")

        return result


@dataclass(frozen=True, slots=True)
class OllamaConfig:
    model: str
    base_url: str = "http://127.0.0.1:11434"


class OllamaProvider:
    def __init__(
        self,
        config: OllamaConfig,
        transport: JsonTransport | None = None,
    ) -> None:
        self._config = config
        self._transport = transport or UrllibJsonTransport()

    @property
    def name(self) -> str:
        return f"ollama:{self._config.model}"

    async def complete(self, prompt: str) -> str:
        result = await self._transport.post(
            f"{self._config.base_url.rstrip('/')}/api/generate",
            {
                "model": self._config.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
        )

        response = result.get("response")
        if not isinstance(response, str) or not response.strip():
            raise InferenceProviderError("Ollama returned no response text")

        return response
