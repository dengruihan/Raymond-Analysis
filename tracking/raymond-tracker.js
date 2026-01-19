(function(window) {
    'use strict';

    var RaymondTracker = function(config) {
        this.config = config || {};
        this.trackerUrl = config.trackerUrl || window.location.origin + '/api/track';
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
        var data = {
            page_url: pageUrl || window.location.href,
            page_title: pageTitle || document.title,
            referrer: document.referrer,
            user_id: this.userId,
            session_id: this.sessionId,
            screen_width: window.screen.width,
            screen_height: window.screen.height,
            language: navigator.language
        };

        this.sendRequest('/pageview', data);
        this.pageViewSent = true;
    };

    RaymondTracker.prototype.trackEvent = function(eventType, eventName, properties) {
        var data = {
            event_type: eventType || 'custom',
            event_name: eventName,
            page_url: window.location.href,
            user_id: this.userId,
            session_id: this.sessionId,
            properties: properties || {}
        };

        this.sendRequest('/event', data);
    };

    RaymondTracker.prototype.updateDuration = function() {
        if (!this.pageViewSent) return;

        var duration = (Date.now() - this.startTime) / 1000;
        var data = {
            session_id: this.sessionId,
            duration: duration
        };

        this.sendRequest('/session/duration', data);
    };

    RaymondTracker.prototype.sendRequest = function(endpoint, data) {
        var url = this.trackerUrl + endpoint;
        
        if (navigator.sendBeacon) {
            navigator.sendBeacon(url, JSON.stringify(data));
        } else {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', url, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify(data));
        }
    };

    RaymondTracker.prototype.init = function() {
        var self = this;

        this.trackPageView();

        document.addEventListener('click', function(e) {
            var target = e.target;
            var eventName = target.getAttribute('data-track-event') || 'click';
            var eventType = target.getAttribute('data-track-type') || 'interaction';
            
            self.trackEvent(eventType, eventName, {
                tag_name: target.tagName,
                id: target.id,
                class: target.className,
                text: target.textContent.substring(0, 100)
            });
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

    window.raymond = new RaymondTracker();
    
    if (document.readyState === 'complete') {
        window.raymond.init();
    } else {
        window.addEventListener('load', function() {
            window.raymond.init();
        });
    }

})(window);
