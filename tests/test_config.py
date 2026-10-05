from pathlib import Path

import pytest

from code_cntx.config import build_inference_client, load_config


def test_load_config_preserves_provider_order(tmp_path: Path) -> None:
    config_file = tmp_path / "code-cntx.toml"
    config_file.write_text(
        """
[[providers]]
kind = "openai-compatible"
name = "free-a"
model = "coder-a"
base_url = "https://api.example.com/v1"
api_key_env = "FREE_A_KEY"

[[providers]]
kind = "ollama"
name = "local"
model = "qwen2.5-coder:7b"
base_url = "http://127.0.0.1:11434"
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert [provider.name for provider in config.providers] == [
        "free-a",
        "local",
    ]


def test_build_inference_client_reads_remote_key_from_environment(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "code-cntx.toml"
    config_file.write_text(
        """
[[providers]]
kind = "openai-compatible"
name = "free-a"
model = "coder-a"
base_url = "https://api.example.com/v1"
api_key_env = "FREE_A_KEY"

[[providers]]
kind = "ollama"
name = "local"
model = "qwen2.5-coder:7b"
base_url = "http://127.0.0.1:11434"
""",
        encoding="utf-8",
    )

    config = load_config(config_file)
    client = build_inference_client(
        config,
        environ={"FREE_A_KEY": "TEST_KEY_PLACEHOLDER"},
    )

    assert client is not None


def test_build_inference_client_rejects_missing_remote_key(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "code-cntx.toml"
    config_file.write_text(
        """
[[providers]]
kind = "openai-compatible"
name = "free-a"
model = "coder-a"
base_url = "https://api.example.com/v1"
api_key_env = "FREE_A_KEY"
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    with pytest.raises(ValueError, match="FREE_A_KEY"):
        build_inference_client(config, environ={})
