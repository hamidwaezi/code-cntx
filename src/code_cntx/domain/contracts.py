from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence


@dataclass(frozen=True, slots=True)
class DeveloperRequest:
    text: str
    repository: Path


@dataclass(frozen=True, slots=True)
class RetrievalQuery:
    symbol: str
    relative_path: str | None = None
    include_references: bool = False


@dataclass(frozen=True, slots=True)
class TaskPlan:
    summary: str
    retrieval_queries: tuple[RetrievalQuery, ...]


@dataclass(frozen=True, slots=True)
class Evidence:
    source: str
    content: str
    symbol: str | None = None
    start_line: int | None = None
    end_line: int | None = None


@dataclass(frozen=True, slots=True)
class LocalProposal:
    analysis: str
    proposed_solution: str
    affected_files: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    suggested_tests: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ContextPackage:
    request: DeveloperRequest
    evidence: tuple[Evidence, ...]
    local_proposal: LocalProposal


class TaskPlanner(Protocol):
    async def plan(self, request: DeveloperRequest) -> TaskPlan:
        ...


class CodeRetriever(Protocol):
    async def retrieve(
        self,
        request: DeveloperRequest,
        plan: TaskPlan,
    ) -> Sequence[Evidence]:
        ...


class LocalModel(Protocol):
    async def analyse(
        self,
        request: DeveloperRequest,
        evidence: Sequence[Evidence],
    ) -> LocalProposal:
        ...


class CloudReviewer(Protocol):
    async def review(self, context: ContextPackage) -> str:
        ...
