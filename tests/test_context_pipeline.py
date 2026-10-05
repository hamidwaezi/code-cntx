import asyncio
from pathlib import Path

from code_cntx.domain.contracts import (
    DeveloperRequest,
    Evidence,
    LocalProposal,
    RetrievalQuery,
    TaskPlan,
)
from code_cntx.models.fake import FakeLocalModel, FakeTaskPlanner
from code_cntx.orchestration.pipeline import ContextPipeline
from code_cntx.retrieval.fake import FakeCodeRetriever


def test_pipeline_builds_context_from_evidence_and_local_proposal() -> None:
    request = DeveloperRequest(
        text="Modify RichCandle aggregation.",
        repository=Path("/repos/ig.com"),
    )
    plan = TaskPlan(
        summary="Inspect RichCandle and its callers.",
        retrieval_queries=(RetrievalQuery(symbol="RichCandle"),),
    )
    evidence = Evidence(
        source="src/market/domain/entities/rich_candle.py",
        content="class RichCandle: ...",
        symbol="RichCandle",
    )
    proposal = LocalProposal(
        analysis="The aggregation boundary needs review.",
        proposed_solution="Aggregate stored base candles into larger intervals.",
        affected_files=("src/market/domain/entities/rich_candle.py",),
        suggested_tests=("test_rich_candle_aggregation",),
    )

    pipeline = ContextPipeline(
        planner=FakeTaskPlanner(plan),
        retriever=FakeCodeRetriever([evidence]),
        local_model=FakeLocalModel(proposal),
    )

    context = asyncio.run(pipeline.build_context(request))

    assert context.request is request
    assert context.evidence == (evidence,)
    assert context.local_proposal is proposal


def test_pipeline_does_not_replace_raw_evidence_with_model_analysis() -> None:
    evidence = Evidence(
        source="src/example.py",
        content="SOURCE_OF_TRUTH = True",
    )
    proposal = LocalProposal(
        analysis="My interpretation may be wrong.",
        proposed_solution="Review the source before changing it.",
    )
    pipeline = ContextPipeline(
        planner=FakeTaskPlanner(
            TaskPlan(
                summary="Inspect source.",
                retrieval_queries=(RetrievalQuery(symbol="SOURCE_OF_TRUTH"),),
            )
        ),
        retriever=FakeCodeRetriever([evidence]),
        local_model=FakeLocalModel(proposal),
    )

    context = asyncio.run(
        pipeline.build_context(
            DeveloperRequest(text="Review this code.", repository=Path("/repo"))
        )
    )

    assert context.evidence[0].content == "SOURCE_OF_TRUTH = True"
    assert context.local_proposal.analysis == "My interpretation may be wrong."
