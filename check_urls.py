from backend.models.database import SessionLocal, PageView
import sys

db = SessionLocal()
try:
    pageviews = db.query(PageView).all()
    
    unique_urls = set()
    url_counts = {}
    
    for pv in pageviews:
        url = pv.page_url
        unique_urls.add(url)
        url_counts[url] = url_counts.get(url, 0) + 1
    
    print(f"总共 {len(pageviews)} 条pageview记录")
    print(f"唯一URL数量: {len(unique_urls)}")
    print("\n所有URL及其出现次数:")
    for url, count in sorted(url_counts.items()):
        print(f"  {repr(url)}: {count}次")
    
    print("\n检查首页相关URL:")
    for url in unique_urls:
        if url in ['/', '', 'http://localhost:8000/', 'http://localhost:8000']:
            print(f"  首页URL: {repr(url)}")
finally:
    db.close()
