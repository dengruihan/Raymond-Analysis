from fastapi import APIRouter, Query
from backend.services.tracking_service import tracking_service
from collections import defaultdict
import re

router = APIRouter(prefix="/api/stats", tags=["sankey"])

@router.get("/page-flow")
async def get_page_flow(days: int = Query(7, description="查询天数")):
    try:
        sessions = tracking_service.get_sessions_by_days(days)
        
        session_flows = defaultdict(list)
        
        for session in sessions:
            pageviews = tracking_service.get_session_pageviews(session['session_id'])
            sorted_pvs = sorted(pageviews, key=lambda x: x.get('created_at', 0))
            
            max_hops = min(3, len(sorted_pvs) - 1)
            for i in range(max_hops):
                current_page = normalize_page_url(sorted_pvs[i].get('page_url', ''))
                next_page = normalize_page_url(sorted_pvs[i+1].get('page_url', ''))
                
                if current_page and next_page and current_page != next_page:
                    session_flows[(current_page, next_page)].append(session['session_id'])
        
        nodes = set()
        links = []
        
        for (source, target), session_ids in session_flows.items():
            nodes.add(source)
            nodes.add(target)
            links.append({
                'source': source,
                'target': target,
                'value': len(session_ids)
            })
        
        nodes_list = [{'name': node} for node in sorted(nodes)]
        
        return {
            'nodes': nodes_list,
            'links': links
        }
    except Exception as e:
        return {'nodes': [], 'links': []}

def normalize_page_url(url):
    if not url:
        return '未知'
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path = parsed.path
        
        path = re.sub(r'/\d+$', '/:id', path)
        path = re.sub(r'/\d+/', '/:id/', path)
        
        if path == '/' or not path:
            return '首页'
        
        parts = path.strip('/').split('/')
        
        if len(parts) == 1:
            if parts[0] == 'login':
                return '登录页'
            elif parts[0] == 'register':
                return '注册页'
            elif parts[0] == 'search':
                return '搜索页'
            elif parts[0] == 'wifi-model':
                return 'WiFi模型详情'
            elif parts[0] == 'submit':
                return '提交页'
            else:
                return parts[0]
        else:
            return ' > '.join(parts[:3])
            
    except Exception:
        return '未知'
