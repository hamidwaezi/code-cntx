from __future__ import annotations

from collections.abc import Sequence

from code_cntx.domain.contracts import DeveloperRequest, Evidence, LocalProposal


class FakeLocalModel:
    """Deterministic local model used before a real inference adapter exists."""

    def __init__(self, proposal: LocalProposal) -> None:
        self._proposal = proposal

    def analyse(
        self,
        request: DeveloperRequest,
        evidence: Sequence[Evidence],
    ) -> LocalProposal:
        del request, evidence
        return self._proposal
