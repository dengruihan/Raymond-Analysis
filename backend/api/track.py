from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.services.tracking_service import tracking_service
import uuid

router = APIRouter(prefix="/api/track", tags=["tracking"])

class PageViewData(BaseModel):
    page_url: str
    page_title: Optional[str] = None
    referrer: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    language: Optional[str] = None
    duration: Optional[float] = None

class EventData(BaseModel):
    event_type: str
    event_name: str
    page_url: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Optional[dict] = None

@router.post("/pageview")
async def track_page_view(data: PageViewData, request: Request):
    try:
        session_id = data.session_id or str(uuid.uuid4())
        
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        tracking_data = {
            "session_id": session_id,
            "user_id": data.user_id,
            "page_url": data.page_url,
            "page_title": data.page_title,
            "referrer": data.referrer,
            "ip_address": client_host,
            "user_agent": user_agent,
            "screen_width": data.screen_width,
            "screen_height": data.screen_height,
            "language": data.language,
            "duration": data.duration
        }
        
        result = tracking_service.track_page_view(tracking_data)
        
        return {
            **result,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/event")
async def track_event(data: EventData, request: Request):
    try:
        session_id = data.session_id or str(uuid.uuid4())
        
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        tracking_data = {
            "session_id": session_id,
            "user_id": data.user_id,
            "event_type": data.event_type,
            "event_name": data.event_name,
            "page_url": data.page_url,
            "ip_address": client_host,
            "user_agent": user_agent,
            "properties": data.properties
        }
        
        result = tracking_service.track_event(tracking_data)
        
        return {
            **result,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/duration")
async def update_session_duration(session_id: str, duration: float):
    try:
        tracking_service.update_session_duration(session_id, duration)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
