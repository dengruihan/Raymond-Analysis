(function(window) {
    'use strict';

    var RaymondTracker = function(config) {
        this.config = config || {};
        var script = document.querySelector('script[src*="tracker.js"], script[src*="ra.js"]');
        var scriptOrigin = script ? new URL(script.src).origin : 'http://localhost:5500';
        this.trackerUrl = config.trackerUrl || scriptOrigin + '/api/track';
        this.pixelUrl = config.pixelUrl || scriptOrigin + '/api/pixel';
        this.sessionId = this.getSessionId();
        this.userId = config.userId || null;
        this.startTime = Date.now();
        this.pageViewSent = false;
    };

    RaymondTracker.prototype.getSessionId = function() {
        var sessionId = localStorage.getItem('raymond_session_id');
        if (!sessionId) {
            sessionId = this.generateSessionId();
            localStorage.setItem('raymond_session_id', sessionId);
        }
        return sessionId;
    };

    RaymondTracker.prototype.generateSessionId = function() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0;
            var v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    };

    RaymondTracker.prototype.trackPageView = function(pageUrl, pageTitle) {
        var params = {
            type: 'pageview',
            page_url: pageUrl || window.location.href,
            page_title: pageTitle || document.title,
            referrer: document.referrer,
            user_id: this.userId,
            session_id: this.sessionId,
            screen_width: window.screen.width,
            screen_height: window.screen.height,
            language: navigator.language,
            timestamp: Date.now()
        };

        this.sendPixel(params);
        this.pageViewSent = true;
    };

    RaymondTracker.prototype.trackEvent = function(eventType, eventName, properties, elementId) {
        var params = {
            type: 'event',
            event_type: eventType || 'custom',
            event_name: eventName,
            page_url: window.location.href,
            user_id: this.userId,
            session_id: this.sessionId,
            element_id: elementId || null,
            properties: properties ? JSON.stringify(properties) : '{}',
            timestamp: Date.now()
        };

        this.sendPixel(params);
    };

    RaymondTracker.prototype.updateDuration = function() {
        if (!this.pageViewSent) {
            return;
        }

        var duration = (Date.now() - this.startTime) / 1000;
        var params = {
            type: 'duration',
            session_id: this.sessionId,
            duration: duration,
            timestamp: Date.now()
        };

        this.sendPixel(params);
    };

    RaymondTracker.prototype.sendPixel = function(params) {
        var url = this.pixelUrl + '?' + this.objectToQueryString(params);
        var img = new Image();
        img.onload = function() {
            console.log('[Raymond] 追踪数据已发送:', params);
        };
        img.onerror = function() {
            console.error('[Raymond] 追踪发送失败:', params);
        };
        img.src = url;
    };

    RaymondTracker.prototype.objectToQueryString = function(obj) {
        var str = [];
        for (var p in obj) {
            if (obj.hasOwnProperty(p)) {
                var k = encodeURIComponent(p);
                var v = encodeURIComponent(obj[p]);
                str.push(k + '=' + v);
            }
        }
        return str.join('&');
    };

    RaymondTracker.prototype.init = function() {
        var self = this;

        this.trackPageView();

        document.addEventListener('click', function(e) {
            var target = e.target;
            var eventName = target.getAttribute('data-track-event') || 'click';
            var eventType = target.getAttribute('data-track-type') || 'interaction';
            var elementId = target.id || target.getAttribute('data-id') || null;
            
            self.trackEvent(eventType, eventName, {
                tag_name: target.tagName,
                class: target.className,
                text: target.textContent ? target.textContent.substring(0, 100) : ''
            }, elementId);
        });

        window.addEventListener('beforeunload', function() {
            self.updateDuration();
        });

        window.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'hidden') {
                self.updateDuration();
            }
        });
    };

    window.RaymondTracker = RaymondTracker;

    var script = document.querySelector('script[src*="tracker.js"], script[src*="ra.js"]');
    var scriptOrigin = script ? new URL(script.src).origin : 'http://localhost:5500';
    
    window.raymond = new RaymondTracker({
        pixelUrl: scriptOrigin + '/api/pixel'
    });
    
    if (document.readyState === 'complete') {
        window.raymond.init();
    } else {
        window.addEventListener('load', function() {
            window.raymond.init();
        });
    }

})(window);
