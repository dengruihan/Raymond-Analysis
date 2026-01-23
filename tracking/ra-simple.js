(function(w,d,s,id){
    w.RA_TRACKER_ID = id || 'default';
    
    var f=d.getElementsByTagName(s)[0],
        j=d.createElement(s);
    j.async=true;
    j.src='http://localhost:5500/tracker.js?site_id='+encodeURIComponent(w.RA_TRACKER_ID);
    j.onload=function(){
        console.log('[RA] 追踪器已加载');
    };
    j.onerror=function(){
        console.error('[RA] 追踪器加载失败，请检查服务器是否运行');
    };
    f.parentNode.insertBefore(j,f);
    
    w.ra_track = function(eventType, eventName, properties) {
        if (w.raymond) {
            w.raymond.trackEvent(eventType, eventName, properties);
        } else {
            console.warn('[RA] 追踪器尚未加载完成');
        }
    };
})(window,document,'script','default');
