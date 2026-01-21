from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models import PageView, Event, Session as SessionModel, get_db
from backend.services.cache_service import redis_service
import json

class TrackingService:
    
    def track_page_view(self, data: dict):
        db = next(get_db())
        try:
            session = db.query(SessionModel).filter(
                SessionModel.session_id == data.get('session_id')
            ).first()
            
            if not session:
                session = SessionModel(
                    session_id=data.get('session_id'),
                    user_id=data.get('user_id'),
                    ip_address=data.get('ip_address'),
                    user_agent=data.get('user_agent'),
                    referrer=data.get('referrer'),
                    start_time=datetime.utcnow()
                )
                db.add(session)
            else:
                session.page_views += 1
                session.end_time = datetime.utcnow()
            
            db.flush()
            
            page_view = PageView(
                session_id=data.get('session_id'),
                user_id=data.get('user_id'),
                page_url=data.get('page_url'),
                page_title=data.get('page_title'),
                referrer=data.get('referrer'),
                ip_address=data.get('ip_address'),
                user_agent=data.get('user_agent'),
                screen_width=data.get('screen_width'),
                screen_height=data.get('screen_height'),
                language=data.get('language'),
                duration=data.get('duration')
            )
            db.add(page_view)
            db.commit()
            
            self._update_realtime_stats(data.get('page_url'))
            
            return {"status": "success", "page_view_id": page_view.id}
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def track_event(self, data: dict):
        db = next(get_db())
        try:
            properties_json = json.dumps(data.get('properties', {})) if data.get('properties') else None
            
            event = Event(
                session_id=data.get('session_id'),
                user_id=data.get('user_id'),
                event_type=data.get('event_type'),
                event_name=data.get('event_name'),
                properties=properties_json,
                page_url=data.get('page_url'),
                ip_address=data.get('ip_address'),
                user_agent=data.get('user_agent')
            )
            db.add(event)
            db.commit()
            
            self._update_event_stats(data.get('event_type'))
            
            return {"status": "success", "event_id": event.id}
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def _update_realtime_stats(self, page_url: str):
        if not redis_service.is_available():
            return
        
        today = datetime.utcnow().date().isoformat()
        
        redis_service.hincrby(f"daily_stats:{today}", "page_views")
        redis_service.incr("stats:page_views_today")
        redis_service.zincrby("stats:top_pages", 1, page_url)
    
    def _update_event_stats(self, event_type: str):
        if not redis_service.is_available():
            return
        
        today = datetime.utcnow().date().isoformat()
        redis_service.hincrby(f"daily_events:{today}", event_type)
    
    def update_session_duration(self, session_id: str, duration: float):
        db = next(get_db())
        try:
            session = db.query(SessionModel).filter(
                SessionModel.session_id == session_id
            ).first()
            
            if session:
                session.duration = duration
                session.end_time = datetime.utcnow()
                db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_sessions_by_days(self, days: int):
        db = next(get_db())
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            sessions = db.query(SessionModel).filter(
                SessionModel.start_time >= start_date
            ).all()
            
            return [{
                'session_id': s.session_id,
                'user_id': s.user_id,
                'start_time': s.start_time.isoformat() if s.start_time else None,
                'end_time': s.end_time.isoformat() if s.end_time else None,
                'page_views': s.page_views,
                'duration': s.duration
            } for s in sessions]
        finally:
            db.close()
    
    def get_session_pageviews(self, session_id: str):
        db = next(get_db())
        try:
            pageviews = db.query(PageView).filter(
                PageView.session_id == session_id
            ).order_by(PageView.timestamp).all()
            
            return [{
                'id': pv.id,
                'page_url': pv.page_url,
                'page_title': pv.page_title,
                'created_at': pv.timestamp.timestamp() if pv.timestamp else 0
            } for pv in pageviews]
        finally:
            db.close()

tracking_service = TrackingService()
