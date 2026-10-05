from __future__ import annotations

from code_cntx.domain.contracts import (
    CodeRetriever,
    ContextPackage,
    DeveloperRequest,
    LocalModel,
)


class ContextPipeline:
    """Coordinates retrieval and local analysis without provider knowledge."""

    def __init__(self, retriever: CodeRetriever, local_model: LocalModel) -> None:
        self._retriever = retriever
        self._local_model = local_model

    def build_context(self, request: DeveloperRequest) -> ContextPackage:
        evidence = tuple(self._retriever.retrieve(request))
        proposal = self._local_model.analyse(request, evidence)

        return ContextPackage(
            request=request,
            evidence=evidence,
            local_proposal=proposal,
        )
