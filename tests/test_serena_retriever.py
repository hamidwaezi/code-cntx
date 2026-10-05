import asyncio
from pathlib import Path
from typing import Any

from code_cntx.domain.contracts import DeveloperRequest, RetrievalQuery, TaskPlan
from code_cntx.retrieval.serena import SerenaCodeRetriever


class RecordingSerenaClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        self.calls.append((name, arguments))
        return f"raw result from {name}"


def test_serena_retriever_uses_find_symbol_and_preserves_raw_output() -> None:
    client = RecordingSerenaClient()
    retriever = SerenaCodeRetriever(client)
    request = DeveloperRequest(
        text="Inspect RichCandle.",
        repository=Path("/repos/ig.com"),
    )
    plan = TaskPlan(
        summary="Inspect the RichCandle entity.",
        retrieval_queries=(
            RetrievalQuery(
                symbol="RichCandle",
                relative_path="src/market",
            ),
        ),
    )

    evidence = asyncio.run(retriever.retrieve(request, plan))

    assert client.calls == [
        (
            "find_symbol",
            {
                "name_path_pattern": "RichCandle",
                "include_body": True,
                "relative_path": "src/market",
            },
        )
    ]
    assert evidence[0].content == "raw result from find_symbol"
    assert evidence[0].source == "serena:find_symbol:RichCandle"


def test_serena_retriever_can_request_symbol_references() -> None:
    client = RecordingSerenaClient()
    retriever = SerenaCodeRetriever(client)
    plan = TaskPlan(
        summary="Inspect symbol and callers.",
        retrieval_queries=(
            RetrievalQuery(
                symbol="RichCandle",
                relative_path="src/market/domain/entities/rich_candle.py",
                include_references=True,
            ),
        ),
    )

    evidence = asyncio.run(
        retriever.retrieve(
            DeveloperRequest(text="Find callers.", repository=Path("/repos/ig.com")),
            plan,
        )
    )

    assert [name for name, _ in client.calls] == [
        "find_symbol",
        "find_referencing_symbols",
    ]
    assert len(evidence) == 2
    assert evidence[1].source == "serena:find_referencing_symbols:RichCandle"
