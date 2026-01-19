class Dashboard {
    constructor() {
        this.charts = {};
        this.ws = null;
        this.init();
    }

    async init() {
        await this.initCharts();
        await this.loadInitialData();
        this.connectWebSocket();
        this.startPeriodicUpdates();
    }

    async initCharts() {
        this.charts.pageViews = echarts.init(document.getElementById('page-views-chart'));
        this.charts.visitors = echarts.init(document.getElementById('visitors-chart'));
        this.charts.hourly = echarts.init(document.getElementById('hourly-chart'));
        this.charts.devices = echarts.init(document.getElementById('devices-chart'));
        this.charts.topPages = echarts.init(document.getElementById('top-pages-chart'));
        this.charts.referrers = echarts.init(document.getElementById('referrers-chart'));
        this.charts.events = echarts.init(document.getElementById('events-chart'));

        window.addEventListener('resize', () => {
            Object.values(this.charts).forEach(chart => chart.resize());
        });
    }

    async loadInitialData() {
        await Promise.all([
            this.updateRealtimeStats(),
            this.loadPageViewsTrend(),
            this.loadVisitorsTrend(),
            this.loadHourlyDistribution(),
            this.loadDeviceStats(),
            this.loadTopPages(),
            this.loadReferrers(),
            this.loadEventStats()
        ]);
    }

    async updateRealtimeStats() {
        try {
            const response = await fetch('/api/stats/realtime');
            const data = await response.json();

            document.getElementById('online-users').textContent = data.online_users || 0;
            document.getElementById('page-views-today').textContent = data.page_views_today || 0;
            document.getElementById('unique-visitors-today').textContent = data.unique_visitors_today || 0;
            document.getElementById('avg-duration').textContent = Math.round(data.avg_duration_today || 0) + 's';
        } catch (error) {
            console.error('Failed to load realtime stats:', error);
        }
    }

    async loadPageViewsTrend() {
        try {
            const response = await fetch('/api/stats/page-views/trend?days=7');
            const data = await response.json();

            const option = {
                title: {
                    text: '近7天页面浏览量'
                },
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: 'category',
                    data: data.map(d => d.date)
                },
                yAxis: {
                    type: 'value'
                },
                series: [{
                    name: '浏览量',
                    type: 'line',
                    data: data.map(d => d.views),
                    smooth: true,
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(102, 126, 234, 0.8)' },
                            { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
                        ])
                    },
                    itemStyle: {
                        color: '#667eea'
                    }
                }]
            };

            this.charts.pageViews.setOption(option);
        } catch (error) {
            console.error('Failed to load page views trend:', error);
        }
    }

    async loadVisitorsTrend() {
        try {
            const response = await fetch('/api/stats/visitors/trend?days=7');
            const data = await response.json();

            const option = {
                title: {
                    text: '近7天访客数量'
                },
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: 'category',
                    data: data.map(d => d.date)
                },
                yAxis: {
                    type: 'value'
                },
                series: [{
                    name: '访客数',
                    type: 'bar',
                    data: data.map(d => d.visitors),
                    itemStyle: {
                        color: '#764ba2'
                    }
                }]
            };

            this.charts.visitors.setOption(option);
        } catch (error) {
            console.error('Failed to load visitors trend:', error);
        }
    }

    async loadHourlyDistribution() {
        try {
            const response = await fetch('/api/stats/hourly?days=1');
            const data = await response.json();

            const option = {
                title: {
                    text: '24小时访问分布'
                },
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: 'category',
                    data: data.map(d => d.hour + ':00')
                },
                yAxis: {
                    type: 'value'
                },
                series: [{
                    name: '访问量',
                    type: 'line',
                    data: data.map(d => d.views),
                    smooth: true,
                    itemStyle: {
                        color: '#10b981'
                    },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(16, 185, 129, 0.8)' },
                            { offset: 1, color: 'rgba(16, 185, 129, 0.1)' }
                        ])
                    }
                }]
            };

            this.charts.hourly.setOption(option);
        } catch (error) {
            console.error('Failed to load hourly distribution:', error);
        }
    }

    async loadDeviceStats() {
        try {
            const response = await fetch('/api/stats/devices');
            const data = await response.json();

            const option = {
                title: {
                    text: '设备分布',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: '{a} <br/>{b}: {c} ({d}%)'
                },
                series: [{
                    name: '设备类型',
                    type: 'pie',
                    radius: ['40%', '70%'],
                    avoidLabelOverlap: false,
                    itemStyle: {
                        borderRadius: 10,
                        borderColor: '#fff',
                        borderWidth: 2
                    },
                    label: {
                        show: true,
                        formatter: '{b}: {d}%'
                    },
                    data: [
                        { value: data.desktop.count, name: '桌面端' },
                        { value: data.mobile.count, name: '移动端' },
                        { value: data.tablet.count, name: '平板' }
                    ]
                }]
            };

            this.charts.devices.setOption(option);
        } catch (error) {
            console.error('Failed to load device stats:', error);
        }
    }

    async loadTopPages() {
        try {
            const response = await fetch('/api/stats/top-pages?limit=10');
            const data = await response.json();

            const option = {
                title: {
                    text: '热门页面 TOP 10'
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'value'
                },
                yAxis: {
                    type: 'category',
                    data: data.map(d => d.url).reverse()
                },
                series: [{
                    name: '浏览量',
                    type: 'bar',
                    data: data.map(d => d.views).reverse(),
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                            { offset: 0, color: '#667eea' },
                            { offset: 1, color: '#764ba2' }
                        ])
                    }
                }]
            };

            this.charts.topPages.setOption(option);
        } catch (error) {
            console.error('Failed to load top pages:', error);
        }
    }

    async loadReferrers() {
        try {
            const response = await fetch('/api/stats/referrers?limit=10');
            const data = await response.json();

            const option = {
                title: {
                    text: '流量来源'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c} ({d}%)'
                },
                series: [{
                    name: '来源',
                    type: 'pie',
                    radius: '70%',
                    data: data.map(d => ({
                        value: d.views,
                        name: d.referrer || '直接访问'
                    }))
                }]
            };

            this.charts.referrers.setOption(option);
        } catch (error) {
            console.error('Failed to load referrers:', error);
        }
    }

    async loadEventStats() {
        try {
            const response = await fetch('/api/stats/events?days=7');
            const data = await response.json();

            const option = {
                title: {
                    text: '事件统计'
                },
                tooltip: {
                    trigger: 'axis'
                },
                xAxis: {
                    type: 'category',
                    data: data.map(d => d.event_name)
                },
                yAxis: {
                    type: 'value'
                },
                series: [{
                    name: '事件次数',
                    type: 'bar',
                    data: data.map(d => d.count),
                    itemStyle: {
                        color: '#f59e0b'
                    }
                }]
            };

            this.charts.events.setOption(option);
        } catch (error) {
            console.error('Failed to load event stats:', error);
        }
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/ws/realtime`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus(true);
            this.ws.send('stats');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'stats_update') {
                this.updateRealtimeStats();
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateConnectionStatus(false);
            setTimeout(() => this.connectWebSocket(), 5000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus(false);
        };
    }

    updateConnectionStatus(connected) {
        const indicator = document.getElementById('status-indicator');
        const text = document.getElementById('status-text');

        if (connected) {
            indicator.className = 'status-dot connected';
            text.textContent = '已连接';
        } else {
            indicator.className = 'status-dot disconnected';
            text.textContent = '连接断开';
        }
    }

    startPeriodicUpdates() {
        setInterval(() => {
            this.updateRealtimeStats();
        }, 30000);

        setInterval(() => {
            this.loadTopPages();
            this.loadDeviceStats();
        }, 60000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});
