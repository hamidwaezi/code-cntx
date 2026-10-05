from __future__ import annotations

from code_cntx.domain.contracts import (
    CodeRetriever,
    ContextPackage,
    DeveloperRequest,
    LocalModel,
    TaskPlanner,
)


class ContextPipeline:
    """Coordinates planning, retrieval, and local analysis."""

    def __init__(
        self,
        planner: TaskPlanner,
        retriever: CodeRetriever,
        local_model: LocalModel,
    ) -> None:
        self._planner = planner
        self._retriever = retriever
        self._local_model = local_model

    async def build_context(self, request: DeveloperRequest) -> ContextPackage:
        plan = await self._planner.plan(request)
        evidence = tuple(await self._retriever.retrieve(request, plan))
        proposal = await self._local_model.analyse(request, evidence)

        return ContextPackage(
            request=request,
            evidence=evidence,
            local_proposal=proposal,
        )
