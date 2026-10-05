from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Protocol
from urllib import error, request

from code_cntx.models.inference import InferenceProviderError


class JsonTransport(Protocol):
    async def post(
        self,
        url: str,
        payload: dict,
        headers: dict[str, str],
    ) -> dict:
        ...


class UrllibJsonTransport:
    async def post(
        self,
        url: str,
        payload: dict,
        headers: dict[str, str],
    ) -> dict:
        return await asyncio.to_thread(
            self._post_sync,
            url,
            payload,
            headers,
        )

    @staticmethod
    def _post_sync(
        url: str,
        payload: dict,
        headers: dict[str, str],
    ) -> dict:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url,
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=120) as response:
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = str(exc)
            raise InferenceProviderError(
                f"Remote provider HTTP {exc.code}: {detail}"
            ) from exc
        except (error.URLError, TimeoutError, OSError) as exc:
            raise InferenceProviderError(
                f"Remote provider request failed: {exc}"
            ) from exc

        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise InferenceProviderError(
                "Remote provider returned invalid JSON"
            ) from exc

        if not isinstance(result, dict):
            raise InferenceProviderError(
                "Remote provider response must be a JSON object"
            )

        return result


@dataclass(frozen=True, slots=True)
class OpenAICompatibleConfig:
    name: str
    model: str
    base_url: str
    api_key: str
    extra_headers: dict[str, str] = field(default_factory=dict)


class OpenAICompatibleProvider:
    """Remote inference provider using the OpenAI chat-completions shape."""

    def __init__(
        self,
        config: OpenAICompatibleConfig,
        transport: JsonTransport | None = None,
    ) -> None:
        self._config = config
        self._transport = transport or UrllibJsonTransport()

    @property
    def name(self) -> str:
        return f"{self._config.name}:{self._config.model}"

    async def complete(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "Content-Type": "application/json",
            **self._config.extra_headers,
        }

        result = await self._transport.post(
            f"{self._config.base_url.rstrip('/')}/chat/completions",
            {
                "model": self._config.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "stream": False,
            },
            headers,
        )

        try:
            content = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise InferenceProviderError(
                "Remote provider returned an unexpected response shape"
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise InferenceProviderError(
                "Remote provider returned no response text"
            )

        return content
