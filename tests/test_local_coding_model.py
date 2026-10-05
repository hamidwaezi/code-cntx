import asyncio
from pathlib import Path

import pytest

from code_cntx.domain.contracts import DeveloperRequest, Evidence
from code_cntx.models.local import LocalCodingModel


class QueueInferenceClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.prompts: list[str] = []

    async def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


def test_local_model_builds_task_plan_from_structured_output() -> None:
    client = QueueInferenceClient(
        [
            """
            {
              "summary": "Inspect RichCandle aggregation and callers.",
              "retrieval_queries": [
                {
                  "symbol": "RichCandle",
                  "relative_path": "src/market",
                  "include_references": true
                }
              ]
            }
            """
        ]
    )
    model = LocalCodingModel(client)

    plan = asyncio.run(
        model.plan(
            DeveloperRequest(
                text="Modify RichCandle aggregation.",
                repository=Path("/repos/ig.com"),
            )
        )
    )

    assert plan.summary == "Inspect RichCandle aggregation and callers."
    assert plan.retrieval_queries[0].symbol == "RichCandle"
    assert plan.retrieval_queries[0].relative_path == "src/market"
    assert plan.retrieval_queries[0].include_references is True
    assert "Do not propose the final implementation yet." in client.prompts[0]


def test_local_model_builds_proposal_from_evidence() -> None:
    client = QueueInferenceClient(
        [
            """
            {
              "analysis": "RichCandle owns aggregation behaviour.",
              "proposed_solution": "Reuse stored base candles for larger intervals.",
              "affected_files": ["src/market/domain/entities/rich_candle.py"],
              "risks": ["Boundary alignment may be wrong."],
              "suggested_tests": ["test_aggregation_from_base_candles"]
            }
            """
        ]
    )
    model = LocalCodingModel(client)

    proposal = asyncio.run(
        model.analyse(
            DeveloperRequest(
                text="Modify RichCandle aggregation.",
                repository=Path("/repos/ig.com"),
            ),
            [
                Evidence(
                    source="serena:find_symbol:RichCandle",
                    content="class RichCandle: ...",
                    symbol="RichCandle",
                )
            ],
        )
    )

    assert proposal.analysis == "RichCandle owns aggregation behaviour."
    assert proposal.affected_files == (
        "src/market/domain/entities/rich_candle.py",
    )
    assert proposal.suggested_tests == ("test_aggregation_from_base_candles",)
    assert "class RichCandle: ..." in client.prompts[0]


def test_local_model_rejects_invalid_json() -> None:
    model = LocalCodingModel(QueueInferenceClient(["not-json"]))

    with pytest.raises(ValueError, match="invalid JSON"):
        asyncio.run(
            model.plan(
                DeveloperRequest(
                    text="Inspect code.",
                    repository=Path("/repo"),
                )
            )
        )
