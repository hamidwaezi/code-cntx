from pathlib import Path

from code_cntx.domain.contracts import (
    ContextPackage,
    DeveloperRequest,
    Evidence,
    LocalProposal,
)


def test_context_package_keeps_evidence_separate_from_local_proposal() -> None:
    request = DeveloperRequest(
        text="Explain RichCandle aggregation.",
        repository=Path("/tmp/ig.com"),
    )
    evidence = Evidence(
        source="src/market/domain/entities/rich_candle.py",
        content="class RichCandle: ...",
        symbol="RichCandle",
    )
    proposal = LocalProposal(
        analysis="Aggregation appears to belong in the market domain.",
        proposed_solution="Review aggregation responsibilities before implementation.",
    )

    package = ContextPackage(
        request=request,
        evidence=(evidence,),
        local_proposal=proposal,
    )

    assert package.evidence == (evidence,)
    assert package.local_proposal is proposal
