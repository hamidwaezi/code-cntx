# AGENTS.md

## Purpose

code-cntx is a standalone AI coding context orchestration tool.

It must remain independent from target repositories.

## Dependency direction

Allowed:

```text
code-cntx -> target repository
```

Forbidden:

```text
target repository -> code-cntx
```

Application repositories must not import, configure, or otherwise depend on code-cntx.

## Architectural rules

1. Repository evidence and model analysis are separate concepts.
2. Retrieved source evidence must remain available to the final reviewer.
3. Local model output is a proposal, never authoritative evidence.
4. Provider-specific integrations must stay behind interfaces.
5. Domain contracts must not depend on Serena, Ollama, OpenAI, Anthropic, Gemini, or another concrete provider.
6. Keep the MVP small. Do not introduce custom parsers, vector databases, inference engines, MCP implementations, or multi-agent frameworks unless justified by measured need.

## Initial layers

- `domain`: provider-neutral data structures and interfaces.
- `orchestration`: coordinates the workflow.
- `retrieval`: repository evidence adapters.
- `models`: local and cloud model adapters.
- `context`: context-package construction.
- `metrics`: token, size, latency, and quality measurements.

## Change discipline

When architecture boundaries change, update this file and the affected tests.
