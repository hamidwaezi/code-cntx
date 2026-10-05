from __future__ import annotations

from collections.abc import Sequence

from code_cntx.domain.contracts import DeveloperRequest, Evidence


class FakeCodeRetriever:
    """Deterministic retriever used to develop the orchestration boundary."""

    def __init__(self, evidence: Sequence[Evidence]) -> None:
        self._evidence = tuple(evidence)

    def retrieve(self, request: DeveloperRequest) -> tuple[Evidence, ...]:
        del request
        return self._evidence
