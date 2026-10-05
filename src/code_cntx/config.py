from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from code_cntx.models.inference import InferenceProvider, RoutedInferenceClient
from code_cntx.models.ollama import OllamaConfig, OllamaProvider
from code_cntx.models.openai_compatible import (
    OpenAICompatibleConfig,
    OpenAICompatibleProvider,
)


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    kind: str
    name: str
    model: str
    base_url: str
    api_key_env: str | None = None


@dataclass(frozen=True, slots=True)
class AppConfig:
    providers: tuple[ProviderConfig, ...]


def load_config(path: Path) -> AppConfig:
    with path.open("rb") as file:
        raw = tomllib.load(file)

    providers_raw = raw.get("providers", [])
    if not isinstance(providers_raw, list):
        raise ValueError("'providers' must be a TOML array of tables")

    providers: list[ProviderConfig] = []

    for item in providers_raw:
        if not isinstance(item, dict):
            raise ValueError("Each provider entry must be a table")

        providers.append(
            ProviderConfig(
                kind=str(item["kind"]),
                name=str(item["name"]),
                model=str(item["model"]),
                base_url=str(item["base_url"]),
                api_key_env=(
                    str(item["api_key_env"])
                    if item.get("api_key_env") is not None
                    else None
                ),
            )
        )

    if not providers:
        raise ValueError("At least one provider must be configured")

    return AppConfig(providers=tuple(providers))


def build_inference_client(
    config: AppConfig,
    *,
    environ: dict[str, str] | None = None,
) -> RoutedInferenceClient:
    env = os.environ if environ is None else environ
    providers: list[InferenceProvider] = []

    for provider in config.providers:
        if provider.kind == "ollama":
            providers.append(
                OllamaProvider(
                    OllamaConfig(
                        model=provider.model,
                        base_url=provider.base_url,
                    )
                )
            )
            continue

        if provider.kind == "openai-compatible":
            if not provider.api_key_env:
                raise ValueError(
                    f"Provider '{provider.name}' requires api_key_env"
                )

            api_key = env.get(provider.api_key_env)
            if not api_key:
                raise ValueError(
                    f"Environment variable '{provider.api_key_env}' is not set"
                )

            providers.append(
                OpenAICompatibleProvider(
                    OpenAICompatibleConfig(
                        name=provider.name,
                        model=provider.model,
                        base_url=provider.base_url,
                        api_key=api_key,
                    )
                )
            )
            continue

        raise ValueError(f"Unsupported provider kind: {provider.kind}")

    return RoutedInferenceClient(providers)
