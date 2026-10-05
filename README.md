# code-cntx

Standalone orchestration layer for building compact, high-quality repository context for AI coding models.

## Core idea

code-cntx sits outside target repositories.

```text
code-cntx ---> target repository
target repository -X-> code-cntx
```

The initial architecture separates:

- repository evidence
- local model analysis
- cloud model review

Evidence is treated as source material. Model analysis is treated as a proposal.

## MVP flow

```text
Developer request
    -> local planner
    -> repository retrieval
    -> repository evidence
    -> local analysis
    -> context package
    -> cloud review
    -> final result
```

The first test repository will be `ig.com`.

## Current phase

Only package boundaries and architecture contracts are being established.

No Serena, Ollama, OpenAI, Anthropic, Gemini, cache, vector database, or agent framework integration is included yet.
