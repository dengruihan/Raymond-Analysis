from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import func, and_
from backend.models import PageView, Event, Session, get_db
from backend.services.cache_service import redis_service

class StatsService:
    
    def get_realtime_stats(self) -> Dict[str, Any]:
        stats = {
            "online_users": 0,
            "page_views_today": 0,
            "unique_visitors_today": 0,
            "avg_duration_today": 0,
            "top_pages": []
        }
        
        if redis_service.is_available():
            stats["online_users"] = int(redis_service.get("stats:online_users") or 0)
            stats["page_views_today"] = int(redis_service.get("stats:page_views_today") or 0)
            stats["unique_visitors_today"] = int(redis_service.get("stats:unique_visitors_today") or 0)
            stats["avg_duration_today"] = float(redis_service.get("stats:avg_duration_today") or 0)
            
            top_pages = redis_service.zrevrange("stats:top_pages", 0, 9, withscores=True)
            stats["top_pages"] = [{"url": url, "views": int(score)} for url, score in top_pages]
        
        return stats
    
    def get_page_views_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        db = next(get_db())
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            results = db.query(
                func.date(PageView.timestamp).label('date'),
                func.count(PageView.id).label('views')
            ).filter(
                PageView.timestamp >= start_date
            ).group_by(
                func.date(PageView.timestamp)
            ).order_by(
                func.date(PageView.timestamp)
            ).all()
            
            return [
                {"date": str(r.date), "views": r.views}
                for r in results
            ]
        finally:
            db.close()
    
    def get_unique_visitors_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        db = next(get_db())
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            results = db.query(
                func.date(PageView.timestamp).label('date'),
                func.count(func.distinct(PageView.session_id)).label('visitors')
            ).filter(
                PageView.timestamp >= start_date
            ).group_by(
                func.date(PageView.timestamp)
            ).order_by(
                func.date(PageView.timestamp)
            ).all()
            
            return [
                {"date": str(r.date), "visitors": r.visitors}
                for r in results
            ]
        finally:
            db.close()
    
    def get_top_pages(self, limit: int = 10) -> List[Dict[str, Any]]:
        db = next(get_db())
        try:
            results = db.query(
                PageView.page_url,
                func.count(PageView.id).label('views')
            ).group_by(
                PageView.page_url
            ).order_by(
                func.count(PageView.id).desc()
            ).limit(limit).all()
            
            return [
                {"url": r.page_url, "views": r.views}
                for r in results
            ]
        finally:
            db.close()
    
    def get_hourly_distribution(self, days: int = 1) -> List[Dict[str, Any]]:
        db = next(get_db())
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            results = db.query(
                func.extract('hour', PageView.timestamp).label('hour'),
                func.count(PageView.id).label('views')
            ).filter(
                PageView.timestamp >= start_date
            ).group_by(
                func.extract('hour', PageView.timestamp)
            ).order_by(
                func.extract('hour', PageView.timestamp)
            ).all()
            
            hourly_data = {i: 0 for i in range(24)}
            for r in results:
                hourly_data[int(r.hour)] = r.views
            
            return [
                {"hour": hour, "views": views}
                for hour, views in hourly_data.items()
            ]
        finally:
            db.close()
    
    def get_referrers(self, limit: int = 10) -> List[Dict[str, Any]]:
        db = next(get_db())
        try:
            results = db.query(
                PageView.referrer,
                func.count(PageView.id).label('views')
            ).filter(
                PageView.referrer.isnot(None),
                PageView.referrer != ""
            ).group_by(
                PageView.referrer
            ).order_by(
                func.count(PageView.id).desc()
            ).limit(limit).all()
            
            return [
                {"referrer": r.referrer, "views": r.views}
                for r in results
            ]
        finally:
            db.close()
    
    def get_device_stats(self) -> Dict[str, Any]:
        db = next(get_db())
        try:
            results = db.query(
                PageView.screen_width,
                func.count(PageView.id).label('count')
            ).filter(
                PageView.screen_width.isnot(None)
            ).group_by(
                PageView.screen_width
            ).all()
            
            mobile = sum(r.count for r in results if r.screen_width < 768)
            tablet = sum(r.count for r in results if 768 <= r.screen_width < 1024)
            desktop = sum(r.count for r in results if r.screen_width >= 1024)
            
            total = mobile + tablet + desktop
            
            return {
                "mobile": {"count": mobile, "percentage": mobile / total * 100 if total > 0 else 0},
                "tablet": {"count": tablet, "percentage": tablet / total * 100 if total > 0 else 0},
                "desktop": {"count": desktop, "percentage": desktop / total * 100 if total > 0 else 0}
            }
        finally:
            db.close()
    
    def get_event_stats(self, event_type: str = None, days: int = 7) -> List[Dict[str, Any]]:
        db = next(get_db())
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = db.query(
                Event.event_name,
                func.count(Event.id).label('count')
            ).filter(
                Event.timestamp >= start_date
            )
            
            if event_type:
                query = query.filter(Event.event_type == event_type)
            
            results = query.group_by(
                Event.event_name
            ).order_by(
                func.count(Event.id).desc()
            ).all()
            
            return [
                {"event_name": r.event_name, "count": r.count}
                for r in results
            ]
        finally:
            db.close()

stats_service = StatsService()
