from __future__ import annotations

import json
from collections.abc import Sequence
from code_cntx.domain.contracts import (
    DeveloperRequest,
    Evidence,
    LocalProposal,
    RetrievalQuery,
    TaskPlan,
)
from code_cntx.models.inference import InferenceClient


class LocalCodingModel:
    """Uses a lightweight inference backend for planning and repository analysis."""

    def __init__(self, client: InferenceClient) -> None:
        self._client = client

    async def plan(self, request: DeveloperRequest) -> TaskPlan:
        raw = await self._client.complete(self._planning_prompt(request))
        payload = self._parse_json(raw)

        queries = tuple(
            RetrievalQuery(
                symbol=item["symbol"],
                relative_path=item.get("relative_path"),
                include_references=bool(item.get("include_references", False)),
            )
            for item in payload.get("retrieval_queries", [])
        )

        return TaskPlan(
            summary=payload["summary"],
            retrieval_queries=queries,
        )

    async def analyse(
        self,
        request: DeveloperRequest,
        evidence: Sequence[Evidence],
    ) -> LocalProposal:
        raw = await self._client.complete(self._analysis_prompt(request, evidence))
        payload = self._parse_json(raw)

        return LocalProposal(
            analysis=payload["analysis"],
            proposed_solution=payload["proposed_solution"],
            affected_files=tuple(payload.get("affected_files", [])),
            risks=tuple(payload.get("risks", [])),
            suggested_tests=tuple(payload.get("suggested_tests", [])),
        )

    @staticmethod
    def _parse_json(raw: str) -> dict:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("Local model returned invalid JSON") from exc

        if not isinstance(payload, dict):
            raise ValueError("Local model response must be a JSON object")

        return payload

    @staticmethod
    def _planning_prompt(request: DeveloperRequest) -> str:
        return f"""You are planning repository retrieval for a coding task.

Developer request:
{request.text}

Repository:
{request.repository}

Return JSON only with this shape:
{{
  "summary": "short task interpretation",
  "retrieval_queries": [
    {{
      "symbol": "symbol or name path to inspect",
      "relative_path": "optional repository-relative path",
      "include_references": false
    }}
  ]
}}

Request the minimum sufficient repository evidence needed to understand the task.
Do not propose the final implementation yet.
"""

    @staticmethod
    def _analysis_prompt(
        request: DeveloperRequest,
        evidence: Sequence[Evidence],
    ) -> str:
        rendered_evidence = "\n\n".join(
            (
                f"SOURCE: {item.source}\n"
                f"SYMBOL: {item.symbol or ''}\n"
                f"CONTENT:\n{item.content}"
            )
            for item in evidence
        )

        return f"""You are analysing repository evidence for a coding task.

Developer request:
{request.text}

Repository evidence:
{rendered_evidence}

Treat the evidence as source material. Do not invent repository facts that are
not supported by it.

Return JSON only with this shape:
{{
  "analysis": "what the evidence shows",
  "proposed_solution": "initial implementation approach",
  "affected_files": [],
  "risks": [],
  "suggested_tests": []
}}
"""
