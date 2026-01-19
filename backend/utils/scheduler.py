from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from backend.api import broadcast_realtime_stats
from backend.services.cache_service import redis_service
from backend.models import get_db, Session as SessionModel, PageView
from sqlalchemy import func, and_
import json

scheduler = AsyncIOScheduler()

async def update_online_users():
    if not redis_service.is_available():
        return
    
    db = next(get_db())
    try:
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        active_sessions = db.query(func.count(func.distinct(SessionModel.session_id))).filter(
            SessionModel.start_time >= five_minutes_ago
        ).scalar()
        
        redis_service.set("stats:online_users", active_sessions, expire=300)
    finally:
        db.close()

async def update_daily_unique_visitors():
    if not redis_service.is_available():
        return
    
    db = next(get_db())
    try:
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        
        unique_visitors = db.query(func.count(func.distinct(PageView.session_id))).filter(
            and_(
                PageView.timestamp >= datetime.combine(today, datetime.min.time()),
                PageView.timestamp < datetime.combine(tomorrow, datetime.min.time())
            )
        ).scalar()
        
        redis_service.set("stats:unique_visitors_today", unique_visitors, expire=86400)
    finally:
        db.close()

async def calculate_avg_duration():
    if not redis_service.is_available():
        return
    
    db = next(get_db())
    try:
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        
        avg_duration = db.query(func.avg(SessionModel.duration)).filter(
            SessionModel.start_time >= datetime.combine(today, datetime.min.time())
        ).scalar()
        
        redis_service.set("stats:avg_duration_today", avg_duration or 0, expire=86400)
    finally:
        db.close()

async def broadcast_stats_update():
    await broadcast_realtime_stats()

def start_scheduler():
    scheduler.add_job(
        update_online_users,
        trigger=IntervalTrigger(minutes=1),
        id='update_online_users',
        replace_existing=True
    )
    
    scheduler.add_job(
        update_daily_unique_visitors,
        trigger=IntervalTrigger(minutes=5),
        id='update_daily_unique_visitors',
        replace_existing=True
    )
    
    scheduler.add_job(
        calculate_avg_duration,
        trigger=IntervalTrigger(minutes=10),
        id='calculate_avg_duration',
        replace_existing=True
    )
    
    scheduler.add_job(
        broadcast_stats_update,
        trigger=IntervalTrigger(seconds=5),
        id='broadcast_stats_update',
        replace_existing=True
    )
    
    scheduler.start()
