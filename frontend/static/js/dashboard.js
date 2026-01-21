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
        this.charts.browsers = echarts.init(document.getElementById('browsers-chart'));
        this.charts.topPages = echarts.init(document.getElementById('top-pages-chart'));
        this.charts.referrers = echarts.init(document.getElementById('referrers-chart'));
        this.charts.sankey = new SankeyChart('sankey-chart');

        window.addEventListener('resize', () => {
            Object.values(this.charts).forEach(chart => chart.resize && chart.resize());
        });
    }

    async loadInitialData() {
        await Promise.all([
            this.updateRealtimeStats(),
            this.loadPageViewsTrend(7),
            this.loadVisitorsTrend(7),
            this.loadHourlyDistribution(1),
            this.loadDeviceStats(),
            this.loadBrowserStats(),
            this.loadTopPages(),
            this.loadReferrers(),
            this.loadPageFlow()
        ]);
        this.initTimeRangeSelectors();
    }

    initTimeRangeSelectors() {
        document.getElementById('page-views-time-range').addEventListener('change', (e) => {
            this.loadPageViewsTrend(parseInt(e.target.value));
        });

        document.getElementById('visitors-time-range').addEventListener('change', (e) => {
            this.loadVisitorsTrend(parseInt(e.target.value));
        });

        document.getElementById('hourly-time-range').addEventListener('change', (e) => {
            this.loadHourlyDistribution(parseInt(e.target.value));
        });
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

    async loadPageViewsTrend(days = 7) {
        try {
            const response = await fetch(`/api/stats/page-views/trend?days=${days}`);
            const data = await response.json();

            let titleText = '页面浏览量';
            if (days === 1) titleText = '24小时页面浏览量';
            else if (days === 2) titleText = '48小时页面浏览量';
            else titleText = `近${days}天页面浏览量`;

            const option = {
                title: {
                    text: titleText
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

    async loadVisitorsTrend(days = 7) {
        try {
            const response = await fetch(`/api/stats/visitors/trend?days=${days}`);
            const data = await response.json();

            let titleText = '访客数量';
            if (days === 1) titleText = '24小时访客数量';
            else if (days === 2) titleText = '48小时访客数量';
            else titleText = `近${days}天访客数量`;

            const option = {
                title: {
                    text: titleText
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

    async loadHourlyDistribution(days = 1) {
        try {
            const response = await fetch(`/api/stats/hourly?days=${days}`);
            const data = await response.json();

            let titleText = '访问分布';
            if (days === 1) titleText = '24小时访问分布';
            else if (days === 2) titleText = '48小时访问分布';
            else titleText = `近${days}天访问分布`;

            const option = {
                title: {
                    text: titleText
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

            const osData = Object.entries(data).map(([name, stats]) => ({
                value: stats.count,
                name: name
            }));

            const option = {
                title: {
                    text: '操作系统分布',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: '{a} <br/>{b}: {c} ({d}%)'
                },
                series: [{
                    name: '操作系统',
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
                    data: osData
                }]
            };

            this.charts.devices.setOption(option);
        } catch (error) {
            console.error('Failed to load device stats:', error);
        }
    }

    async loadBrowserStats() {
        try {
            const response = await fetch('/api/stats/browsers');
            const data = await response.json();

            const browserData = Object.entries(data).map(([name, stats]) => ({
                value: stats.count,
                name: name
            }));

            const option = {
                title: {
                    text: '浏览器分布',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: '{a} <br/>{b}: {c} ({d}%)'
                },
                series: [{
                    name: '浏览器',
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
                    data: browserData
                }]
            };

            this.charts.browsers.setOption(option);
        } catch (error) {
            console.error('Failed to load browser stats:', error);
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
                    formatter: '{a} <br/>{b}: {c} ({d}%)'
                },
                series: [{
                    name: '来源',
                    type: 'pie',
                    radius: '70%',
                    data: data.map(d => ({
                        value: d.views,
                        name: d.referrer
                    }))
                }]
            };

            this.charts.referrers.setOption(option);
        } catch (error) {
            console.error('Failed to load referrers:', error);
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
            this.loadBrowserStats();
            this.loadPageFlow();
        }, 60000);
    }

    async loadPageFlow() {
        try {
            const response = await fetch('/api/stats/page-flow?days=7');
            const data = await response.json();

            if (data.nodes && data.links) {
                this.charts.sankey.setData(data);
            }
        } catch (error) {
            console.error('Failed to load page flow:', error);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});
