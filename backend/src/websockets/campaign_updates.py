"""
WebSocket endpoint for real-time campaign analytics updates.
Sends periodic ticks (and optional summary) to clients to drive live refresh.
"""
import asyncio
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..database.connection import AsyncSessionLocal
from ..services.analytics_service import AnalyticsService


router = APIRouter()


@router.websocket("/ws/campaign-updates")
async def campaign_updates(websocket: WebSocket):
    await websocket.accept()

    # Optional filters from query params
    qp = websocket.query_params
    campaign_id: Optional[str] = qp.get("campaign_id")
    start_date: Optional[str] = qp.get("start_date")
    end_date: Optional[str] = qp.get("end_date")

    try:
        while True:
            # Compute summary (best-effort) and send a tick to trigger UI update
            try:
                async with AsyncSessionLocal() as session:
                    analytics = AnalyticsService(session)
                    summary = await analytics.get_analytics_summary(
                        start_date=start_date, end_date=end_date, campaign_id=campaign_id
                    )
                await websocket.send_json({
                    "type": "summary",
                    "summary": summary,
                    "campaign_id": campaign_id,
                })
            except Exception:
                # If summary computation fails, still send a tick
                await websocket.send_json({"type": "tick", "campaign_id": campaign_id})

            await asyncio.sleep(5)
    except WebSocketDisconnect:
        # Client disconnected
        return

