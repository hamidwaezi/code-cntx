from __future__ import annotations

from collections.abc import Sequence

from code_cntx.domain.contracts import (
    DeveloperRequest,
    Evidence,
    LocalProposal,
    TaskPlan,
)


class FakeTaskPlanner:
    """Deterministic planner used before a real local planner exists."""

    def __init__(self, plan: TaskPlan) -> None:
        self._plan = plan

    async def plan(self, request: DeveloperRequest) -> TaskPlan:
        del request
        return self._plan


class FakeLocalModel:
    """Deterministic local model used before a real inference adapter exists."""

    def __init__(self, proposal: LocalProposal) -> None:
        self._proposal = proposal

    async def analyse(
        self,
        request: DeveloperRequest,
        evidence: Sequence[Evidence],
    ) -> LocalProposal:
        del request, evidence
        return self._proposal
