"""First traceable Cognitive Agent composition."""
from __future__ import annotations

from packages.cognitive_sdk import CognitiveEvidence, CognitiveRequest, CognitiveResponse
from packages.embeddings_sdk import Embedder
from packages.llm_sdk import ChatMessage, CompletionRequest, LlmRouter
from packages.medical_knowledge_sdk import KnowledgeQuery, KnowledgeRetriever


class CognitiveAgent:
    """Ground model responses in retrieved evidence before generation."""

    def __init__(self, *, retriever: KnowledgeRetriever, router: LlmRouter) -> None:
        self._retriever = retriever
        self._router = router

    async def answer(self, request: CognitiveRequest) -> CognitiveResponse:
        evidence = list(
            self._retriever.retrieve(KnowledgeQuery(request.question, top_k=request.top_k))
        )
        context = "\n".join(
            f"[{item.source.source_id}:{item.chunk.document_id}:{item.chunk.chunk_id}] "
            f"{item.chunk.text}"
            for item in evidence
        )
        prompt = (
            "Answer using only the supplied evidence. If evidence is insufficient, say so.\n\n"
            f"Evidence:\n{context or '[no evidence retrieved]'}\n\n"
            f"Question: {request.question}"
        )
        completion = await self._router.complete(
            CompletionRequest(
                messages=(
                    ChatMessage(role="system", content="You are the Astera evidence agent."),
                    ChatMessage(role="user", content=prompt),
                ),
                model=request.model,
                metadata=request.metadata,
            )
        )
        return CognitiveResponse(
            request_id=request.request_id,
            answer=completion.content,
            provider=completion.provider,
            model=completion.model,
            evidence=tuple(
                CognitiveEvidence(
                    source_id=item.source.source_id,
                    document_id=item.chunk.document_id,
                    chunk_id=item.chunk.chunk_id,
                    title=item.title,
                    excerpt=item.chunk.text,
                    score=item.score,
                    version=item.version,
                )
                for item in evidence
            ),
        )
