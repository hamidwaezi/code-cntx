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
- GitHub Actions test workflow

The Serena adapter starts Serena against the target repository and uses semantic tools such as `find_symbol` and `find_referencing_symbols`.

The first test repository will be `ig.com`.

Not implemented yet:

- concrete local inference adapter (for example Ollama)
- cloud reviewer
- context-size controls
- token/cost metrics
- caching or smart routing
