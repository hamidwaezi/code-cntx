# code-cntx

Standalone orchestration layer for building compact, high-quality repository context for AI coding models.

## Core idea

code-cntx sits outside target repositories.

```text
code-cntx ---> target repository
target repository -X-> code-cntx
```

The architecture separates:

- repository evidence
- local model analysis
- cloud model review

Evidence is treated as source material. Model analysis is treated as a proposal.

## MVP flow

```text
Developer request
    -> local task planner
    -> Serena retrieval
    -> repository evidence
    -> local analysis
    -> context package
    -> cloud review
    -> final result
```

## Current state

Implemented:

- provider-neutral domain contracts
- async orchestration pipeline
- task plan and retrieval queries
- fake planner/retriever/local model for deterministic tests
- Serena MCP retrieval adapter
- provider-neutral local coding model for planning and analysis
- ordered multi-provider inference router with failover
- Ollama inference provider
- generic OpenAI-compatible remote inference provider
- TOML provider configuration + environment-based secrets
- GitHub Actions test workflow

The Serena adapter starts Serena against the target repository and uses semantic tools such as `find_symbol` and `find_referencing_symbols`.

The first test repository will be `ig.com`.

Not implemented yet:

- cloud reviewer
- context-size controls
- context-size controls
- token/cost metrics
- caching or smart routing


## Provider configuration

Provider priority is declared in `code-cntx.toml`-style configuration.

Example:

```toml
[[providers]]
kind = "openai-compatible"
name = "free-provider"
model = "your-model-name"
base_url = "https://api.example.com/v1"
api_key_env = "FREE_PROVIDER_API_KEY"

[[providers]]
kind = "ollama"
name = "local"
model = "qwen2.5-coder:7b"
base_url = "http://127.0.0.1:11434"
```

Real API keys are read from environment variables and must not be committed.
