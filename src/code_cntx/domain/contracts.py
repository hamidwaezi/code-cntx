from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence


@dataclass(frozen=True, slots=True)
class DeveloperRequest:
    text: str
    repository: Path


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


class CodeRetriever(Protocol):
    def retrieve(self, request: DeveloperRequest) -> Sequence[Evidence]:
        ...


class LocalModel(Protocol):
    def analyse(
        self,
        request: DeveloperRequest,
        evidence: Sequence[Evidence],
    ) -> LocalProposal:
        ...


class CloudReviewer(Protocol):
    def review(self, context: ContextPackage) -> str:
        ...
