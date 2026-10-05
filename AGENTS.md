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
6. External I/O boundaries are asynchronous.
7. Serena-specific MCP tool names and argument formats stay inside the Serena retrieval adapter.
8. Serena receives retrieval intent from a provider-neutral `TaskPlan`; the domain does not know Serena tool names.
9. Keep the MVP small. Do not introduce custom parsers, vector databases, inference engines, MCP implementations, or multi-agent frameworks unless justified by measured need.

## Initial layers

- `domain`: provider-neutral data structures and interfaces.
- `orchestration`: coordinates planning, retrieval, and analysis.
- `retrieval`: repository evidence adapters, including Serena.
- `models`: local and cloud model adapters.
- `context`: context-package construction.
- `metrics`: token, size, latency, and quality measurements.

## Current retrieval boundary

```text
DeveloperRequest
    -> TaskPlanner
    -> TaskPlan / RetrievalQuery
    -> CodeRetriever
    -> SerenaCodeRetriever
    -> Serena MCP
    -> Evidence[]
```

Serena output is stored as evidence and must not be silently replaced by a model-generated summary.

## Change discipline

When architecture boundaries change, update this file and the affected tests.
