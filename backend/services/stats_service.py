from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import func, and_
from backend.models import PageView, Event, Session, User, get_db
from backend.services.cache_service import redis_service

class StatsService:
    
    def _exclude_dashboard(self, query):
        return query.filter(~PageView.page_url.like('%localhost:5500%')).filter(~PageView.page_url.like('%/dashboard%'))
    
    def get_realtime_stats(self) -> Dict[str, Any]:
        stats = {
            "online_users": 0,
            "page_views_today": 0,
            "unique_visitors_today": 0,
            "avg_duration_today": 0,
            "top_pages": []
        }
        
        db = next(get_db())
        try:
            now = datetime.now()
            today = now.date()
            today_start = datetime.combine(today, datetime.min.time())
            yesterday_start = today_start - timedelta(days=1)
            
            stats["page_views_today"] = self._exclude_dashboard(db.query(func.count(PageView.id))).filter(
                PageView.timestamp >= today_start
            ).scalar() or 0
            
            stats["unique_visitors_today"] = self._exclude_dashboard(db.query(func.count(func.distinct(PageView.session_id)))).filter(
                PageView.timestamp >= today_start
            ).scalar() or 0
            
            result = db.query(func.avg(Session.duration)).filter(
                Session.start_time >= today_start,
                Session.duration.isnot(None),
                Session.duration > 0
            ).scalar()
            stats["avg_duration_today"] = float(result) if result else 0
            
            top_pages = self._exclude_dashboard(db.query(
                PageView.page_url,
                func.count(PageView.id).label('views')
            )).filter(
                PageView.timestamp >= today_start
            ).group_by(
                PageView.page_url
            ).order_by(
                func.count(PageView.id).desc()
            ).limit(10).all()
            
            stats["top_pages"] = [{"url": r.page_url, "views": r.views} for r in top_pages]
            
            result = db.query(func.count(func.distinct(Session.session_id))).filter(
                Session.end_time >= yesterday_start
            ).scalar()
            stats["online_users"] = result or 0
        finally:
            db.close()
        
        return stats
    
    def get_page_views_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        db = next(get_db())
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            if days <= 2:
                results = self._exclude_dashboard(db.query(
                    func.date(PageView.timestamp).label('date'),
                    func.extract('hour', PageView.timestamp).label('hour'),
                    func.count(PageView.id).label('views')
                )).filter(
                    PageView.timestamp >= start_date
                ).group_by(
                    func.date(PageView.timestamp),
                    func.extract('hour', PageView.timestamp)
                ).order_by(
                    func.date(PageView.timestamp),
                    func.extract('hour', PageView.timestamp)
                ).all()
                
                return [
                    {"date": str(r.date), "hour": int(r.hour), "views": r.views}
                    for r in results
                ]
            else:
                results = self._exclude_dashboard(db.query(
                    func.date(PageView.timestamp).label('date'),
                    func.count(PageView.id).label('views')
                )).filter(
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
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            results = self._exclude_dashboard(db.query(
                func.date(PageView.timestamp).label('date'),
                func.count(func.distinct(PageView.session_id)).label('visitors')
            )).filter(
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
            results = self._exclude_dashboard(db.query(
                PageView.page_url,
                func.count(PageView.id).label('views')
            )).group_by(
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
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            results = self._exclude_dashboard(db.query(
                func.extract('hour', PageView.timestamp).label('hour'),
                func.count(PageView.id).label('views')
            )).filter(
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
        from urllib.parse import urlparse
        
        def parse_referrer(referrer):
            if not referrer or referrer == "":
                return "直接访问"
            
            try:
                parsed = urlparse(referrer)
                domain = parsed.netloc.lower()
                
                if domain in ["localhost", "127.0.0.1", "::1"]:
                    return "直接访问"
                
                if "google" in domain:
                    return "Google"
                elif "baidu" in domain:
                    return "百度"
                elif "bing" in domain:
                    return "Bing"
                elif "yahoo" in domain:
                    return "Yahoo"
                elif "weibo" in domain:
                    return "微博"
                elif "zhihu" in domain:
                    return "知乎"
                elif "douyin" in domain or "tiktok" in domain:
                    return "抖音/TikTok"
                elif "bilibili" in domain:
                    return "B站"
                elif "github" in domain:
                    return "GitHub"
                else:
                    return domain
            except Exception:
                return "直接访问"
        
        db = next(get_db())
        try:
            results = db.query(
                PageView.referrer,
                func.count(PageView.id).label('views')
            ).all()
            
            referrer_counts = {}
            for r in results:
                ref_name = parse_referrer(r.referrer)
                if ref_name not in referrer_counts:
                    referrer_counts[ref_name] = 0
                referrer_counts[ref_name] += r.views
            
            sorted_referrers = sorted(referrer_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            total = sum(count for _, count in sorted_referrers)
            
            return [
                {"referrer": name, "views": count, "percentage": count / total * 100 if total > 0 else 0}
                for name, count in sorted_referrers
            ]
        finally:
            db.close()
    
    def get_device_stats(self) -> Dict[str, Any]:
        import re
        
        def parse_os(user_agent):
            if not user_agent:
                return '未知'
            user_agent = user_agent.lower()
            if 'mac os x' in user_agent or 'macintosh' in user_agent:
                return 'Mac OS'
            elif 'windows' in user_agent:
                return 'Windows'
            elif 'linux' in user_agent:
                return 'Linux'
            elif 'android' in user_agent:
                return 'Android'
            elif 'iphone' in user_agent or 'ipad' in user_agent or 'ios' in user_agent:
                return 'iOS'
            else:
                return '其他'
        
        db = next(get_db())
        try:
            results = db.query(
                PageView.user_agent,
                func.count(PageView.id).label('count')
            ).filter(
                PageView.user_agent.isnot(None)
            ).group_by(
                PageView.user_agent
            ).all()
            
            os_stats = {}
            for r in results:
                os_name = parse_os(r.user_agent)
                if os_name not in os_stats:
                    os_stats[os_name] = 0
                os_stats[os_name] += r.count
            
            total = sum(os_stats.values())
            
            return {
                os_name: {"count": count, "percentage": count / total * 100 if total > 0 else 0}
                for os_name, count in os_stats.items()
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

    def get_browser_stats(self) -> Dict[str, Any]:
        def parse_browser(user_agent):
            if not user_agent:
                return '未知'
            user_agent = user_agent.lower()
            if 'chrome' in user_agent and 'edg' not in user_agent:
                return 'Chrome'
            elif 'safari' in user_agent and 'chrome' not in user_agent:
                return 'Safari'
            elif 'firefox' in user_agent:
                return 'Firefox'
            elif 'edge' in user_agent or 'edg' in user_agent:
                return 'Edge'
            elif 'opera' in user_agent or 'opr' in user_agent:
                return 'Opera'
            else:
                return '其他'
        
        db = next(get_db())
        try:
            results = db.query(
                PageView.user_agent,
                func.count(PageView.id).label('count')
            ).filter(
                PageView.user_agent.isnot(None)
            ).group_by(
                PageView.user_agent
            ).all()
            
            browser_stats = {}
            for r in results:
                browser_name = parse_browser(r.user_agent)
                if browser_name not in browser_stats:
                    browser_stats[browser_name] = 0
                browser_stats[browser_name] += r.count
            
            total = sum(browser_stats.values())
            
            return {
                browser_name: {"count": count, "percentage": count / total * 100 if total > 0 else 0}
                for browser_name, count in browser_stats.items()
            }
        finally:
            db.close()
    
    def get_user_type_stats(self) -> Dict[str, Any]:
        """获取新老用户统计数据"""
        db = next(get_db())
        try:
            now = datetime.now()
            today = now.date()
            today_start = datetime.combine(today, datetime.min.time())
            
            # 获取总用户数
            total_users = db.query(func.count(User.id)).scalar() or 0
            
            # 获取新用户数（今天首次访问的用户）
            new_users = db.query(func.count(User.id)).filter(
                func.date(User.first_visit) == today
            ).scalar() or 0
            
            # 获取老用户数
            returning_users = total_users - new_users
            
            # 计算比例
            new_user_percentage = (new_users / total_users * 100) if total_users > 0 else 0
            returning_user_percentage = (returning_users / total_users * 100) if total_users > 0 else 0
            
            return {
                "total_users": total_users,
                "new_users": new_users,
                "returning_users": returning_users,
                "new_user_percentage": new_user_percentage,
                "returning_user_percentage": returning_user_percentage
            }
        finally:
            db.close()
    
    def get_user_type_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取新老用户趋势数据"""
        db = next(get_db())
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 生成日期范围
            date_range = []
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date)
                current_date += timedelta(days=1)
            
            # 获取每天的新用户数
            daily_new_users = db.query(
                func.date(User.first_visit).label('date'),
                func.count(User.id).label('new_users')
            ).filter(
                User.first_visit >= start_date
            ).group_by(
                func.date(User.first_visit)
            ).all()
            
            # 获取每天的活跃用户数（包含新老用户）
            daily_active_users = self._exclude_dashboard(db.query(
                func.date(PageView.timestamp).label('date'),
                func.count(func.distinct(PageView.user_id)).label('active_users')
            )).filter(
                PageView.timestamp >= start_date,
                PageView.user_id.isnot(None)
            ).group_by(
                func.date(PageView.timestamp)
            ).all()
            
            # 构建结果
            new_users_map = {str(r.date): r.new_users for r in daily_new_users}
            active_users_map = {str(r.date): r.active_users for r in daily_active_users}
            
            trend_data = []
            for date in date_range:
                date_str = str(date.date())
                new_users = new_users_map.get(date_str, 0)
                active_users = active_users_map.get(date_str, 0)
                returning_users = max(0, active_users - new_users)
                
                trend_data.append({
                    "date": date_str,
                    "new_users": new_users,
                    "returning_users": returning_users,
                    "total_active": active_users
                })
            
            return trend_data
        finally:
            db.close()

stats_service = StatsService()
