from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from mcp import Client, StdioServerParameters
from mcp.types import TextContent

from code_cntx.domain.contracts import (
    DeveloperRequest,
    Evidence,
    RetrievalQuery,
    TaskPlan,
)


class SerenaToolClient(Protocol):
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        ...


@dataclass(frozen=True, slots=True)
class SerenaProcessConfig:
    command: str = "serena"
    context: str = "agent"


class McpSerenaClient:
    """Starts Serena as an MCP subprocess for one target repository."""

    def __init__(
        self,
        repository: Path,
        config: SerenaProcessConfig | None = None,
    ) -> None:
        self._repository = repository
        self._config = config or SerenaProcessConfig()

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        params = StdioServerParameters(
            command=self._config.command,
            args=[
                "start-mcp-server",
                "--context",
                self._config.context,
                "--project",
                str(self._repository),
            ],
        )

        async with Client(params) as client:
            result = await client.call_tool(name, arguments)

        chunks: list[str] = []
        for item in result.content:
            if isinstance(item, TextContent):
                chunks.append(item.text)

        if result.structured_content is not None:
            chunks.append(str(result.structured_content))

        return "\n".join(chunks).strip()


class SerenaCodeRetriever:
    """Retrieves repository evidence through Serena semantic tools."""

    def __init__(self, client: SerenaToolClient) -> None:
        self._client = client

    async def retrieve(
        self,
        request: DeveloperRequest,
        plan: TaskPlan,
    ) -> tuple[Evidence, ...]:
        del request
        evidence: list[Evidence] = []

        for query in plan.retrieval_queries:
            evidence.extend(await self._retrieve_query(query))

        return tuple(evidence)

    async def _retrieve_query(self, query: RetrievalQuery) -> list[Evidence]:
        arguments: dict[str, Any] = {
            "name_path_pattern": query.symbol,
            "include_body": True,
        }
        if query.relative_path:
            arguments["relative_path"] = query.relative_path

        symbol_result = await self._client.call_tool("find_symbol", arguments)
        results = [
            Evidence(
                source=f"serena:find_symbol:{query.symbol}",
                content=symbol_result,
                symbol=query.symbol,
            )
        ]

        if query.include_references:
            reference_arguments: dict[str, Any] = {
                "name_path": query.symbol,
                "relative_path": query.relative_path or "",
            }
            reference_result = await self._client.call_tool(
                "find_referencing_symbols",
                reference_arguments,
            )
            results.append(
                Evidence(
                    source=f"serena:find_referencing_symbols:{query.symbol}",
                    content=reference_result,
                    symbol=query.symbol,
                )
            )

        return results
