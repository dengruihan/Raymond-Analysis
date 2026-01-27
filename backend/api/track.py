from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from backend.services.tracking_service import tracking_service
import uuid

router = APIRouter(prefix="/api", tags=["tracking"])

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

@router.get("/pixel")
async def pixel_tracking(
    request: Request,
    type: str = Query(...),
    page_url: Optional[str] = Query(None),
    page_title: Optional[str] = Query(None),
    referrer: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    screen_width: Optional[int] = Query(None),
    screen_height: Optional[int] = Query(None),
    language: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    event_name: Optional[str] = Query(None),
    element_id: Optional[str] = Query(None),
    properties: Optional[str] = Query(None),
    duration: Optional[float] = Query(None)
):
    try:
        sid = session_id or str(uuid.uuid4())
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        if type == "pageview":
            tracking_data = {
                "session_id": sid,
                "user_id": user_id,
                "page_url": page_url or request.headers.get("referer", ""),
                "page_title": page_title,
                "referrer": referrer,
                "ip_address": client_host,
                "user_agent": user_agent,
                "screen_width": screen_width,
                "screen_height": screen_height,
                "language": language
            }
            tracking_service.track_page_view(tracking_data)
            
        elif type == "event":
            import json
            props = json.loads(properties) if properties else {}
            tracking_data = {
                "session_id": sid,
                "user_id": user_id,
                "event_type": event_type or "custom",
                "event_name": event_name or "",
                "page_url": page_url or request.headers.get("referer", ""),
                "ip_address": client_host,
                "user_agent": user_agent,
                "properties": props
            }
            tracking_service.track_event(tracking_data)
            
        elif type == "duration":
            tracking_service.update_session_duration(sid, duration or 0.0)
        
        return Response(content=b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;', media_type='image/gif')
    except Exception as e:
        return Response(content=b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;', media_type='image/gif')

@router.post("/track/pageview")
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
            "session_id": session_id,
            "user_type": result.get("user_type", "unknown"),
            "is_new_user": result.get("is_new_user", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track/event")
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

@router.post("/track/session/duration")
async def update_session_duration(session_id: str, duration: float):
    try:
        tracking_service.update_session_duration(session_id, duration)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
