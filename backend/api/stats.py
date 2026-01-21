from fastapi import APIRouter, Query
from typing import Optional
from backend.services.stats_service import stats_service

router = APIRouter(prefix="/api/stats", tags=["stats"])

@router.get("/realtime")
async def get_realtime_stats():
    return stats_service.get_realtime_stats()

@router.get("/page-views/trend")
async def get_page_views_trend(
    days: int = Query(7, ge=1, le=30, description="天数范围")
):
    return stats_service.get_page_views_trend(days)

@router.get("/visitors/trend")
async def get_unique_visitors_trend(
    days: int = Query(7, ge=1, le=30, description="天数范围")
):
    return stats_service.get_unique_visitors_trend(days)

@router.get("/hourly")
async def get_hourly_distribution(
    days: int = Query(1, ge=1, le=30, description="天数范围")
):
    return stats_service.get_hourly_distribution(days)

@router.get("/top-pages")
async def get_top_pages(
    limit: int = Query(10, ge=1, le=50, description="返回数量")
):
    return stats_service.get_top_pages(limit)

@router.get("/hourly")
async def get_hourly_distribution(
    days: int = Query(1, ge=1, le=7, description="天数范围")
):
    return stats_service.get_hourly_distribution(days)

@router.get("/referrers")
async def get_referrers(
    limit: int = Query(10, ge=1, le=50, description="返回数量")
):
    return stats_service.get_referrers(limit)

@router.get("/devices")
async def get_device_stats():
    return stats_service.get_device_stats()

@router.get("/browsers")
async def get_browser_stats():
    return stats_service.get_browser_stats()

@router.get("/events")
async def get_event_stats(
    event_type: Optional[str] = Query(None, description="事件类型筛选"),
    days: int = Query(7, ge=1, le=30, description="天数范围")
):
    return stats_service.get_event_stats(event_type, days)
