from __future__ import annotations

from collections.abc import Sequence

from code_cntx.domain.contracts import DeveloperRequest, Evidence, TaskPlan


class FakeCodeRetriever:
    """Deterministic retriever used to develop the orchestration boundary."""

    def __init__(self, evidence: Sequence[Evidence]) -> None:
        self._evidence = tuple(evidence)

    async def retrieve(
        self,
        request: DeveloperRequest,
        plan: TaskPlan,
    ) -> tuple[Evidence, ...]:
        del request, plan
        return self._evidence
