(function(window) {
    if (window.raymond) {
        return;
    }

    const COOKIE_NAME = 'ra_user_id';
    const SESSION_COOKIE = 'ra_session_id';
    const COOKIE_EXPIRY = 365 * 24 * 60 * 60 * 1000; // 1 year

    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    function setCookie(name, value, days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = `expires=${date.toUTCString()}`;
        document.cookie = `${name}=${value}; ${expires}; path=/; SameSite=Lax`;
    }

    function getUserID() {
        let userID = getCookie(COOKIE_NAME);
        if (!userID) {
            userID = generateUUID();
            setCookie(COOKIE_NAME, userID, 365);
        }
        return userID;
    }

    function getSessionID() {
        let sessionID = getCookie(SESSION_COOKIE);
        if (!sessionID) {
            sessionID = generateUUID();
            setCookie(SESSION_COOKIE, sessionID, 1); // 1 day session
        }
        return sessionID;
    }

    function sendData(endpoint, data) {
        try {
            const img = new Image(1, 1);
            const params = new URLSearchParams(data).toString();
            img.src = `http://localhost:5500/api/pixel?${params}`;
            img.onload = function() {
                console.log('[RA] Tracking data sent successfully');
            };
            img.onerror = function() {
                console.warn('[RA] Failed to send tracking data');
            };
        } catch (e) {
            console.error('[RA] Error sending tracking data:', e);
        }
    }

    const raymond = {
        userID: getUserID(),
        sessionID: getSessionID(),

        init: function() {
            console.log('[RA] Tracker initialized for user:', this.userID);
            this.trackPageView();
        },

        trackPageView: function() {
            const data = {
                type: 'pageview',
                page_url: window.location.href,
                page_title: document.title,
                referrer: document.referrer || '',
                user_id: this.userID,
                session_id: this.sessionID,
                screen_width: window.screen.width,
                screen_height: window.screen.height,
                language: navigator.language
            };
            sendData('pixel', data);
        },

        trackEvent: function(eventType, eventName, properties) {
            const data = {
                type: 'event',
                event_type: eventType,
                event_name: eventName,
                page_url: window.location.href,
                user_id: this.userID,
                session_id: this.sessionID,
                properties: JSON.stringify(properties || {})
            };
            sendData('pixel', data);
        },

        updateSessionDuration: function(duration) {
            const data = {
                type: 'duration',
                session_id: this.sessionID,
                duration: duration
            };
            sendData('pixel', data);
        }
    };

    window.raymond = raymond;
    
    // 初始化跟踪器
    raymond.init();

    // 监听页面卸载，发送会话持续时间
    let startTime = Date.now();
    window.addEventListener('beforeunload', function() {
        const duration = (Date.now() - startTime) / 1000;
        raymond.updateSessionDuration(duration);
    });

})(window);
