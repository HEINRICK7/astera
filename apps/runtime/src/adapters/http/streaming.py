"""WebSocket streaming adapter."""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from apps.runtime.src.ports.outbound.streaming import StreamBrokerPort


def create_streaming_router(broker: StreamBrokerPort) -> APIRouter:
    router = APIRouter(tags=["Streaming"])

    @router.websocket("/api/v1/streaming/{stream_id}")
    async def stream(websocket: WebSocket, stream_id: str) -> None:
        await websocket.accept()
        try:
            async for event in broker.subscribe(stream_id):
                await websocket.send_json(event.to_dict())
        except WebSocketDisconnect:
            return

    @router.websocket("/api/v1/clinical-stream/{encounter_id}")
    async def clinical_stream(websocket: WebSocket, encounter_id: str) -> None:
        """Fan out clinical projections for an active encounter.

        Upstream transcription is owned by ``astera-live-transcriber``. This
        endpoint is intentionally read-only from Astera's perspective and
        exposes clinical state, facts, review and A2UI events only.
        """
        await websocket.accept()
        stream_id = encounter_id

        try:
            async for event in broker.subscribe(stream_id):
                await websocket.send_json(event.to_dict())
        except WebSocketDisconnect:
            return

    return router
