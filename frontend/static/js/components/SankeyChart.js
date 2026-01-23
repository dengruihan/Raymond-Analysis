class SankeyChart {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.chart = echarts.init(this.container);
        this.data = null;
    }

    setData(data) {
        if (data.entry_pages && Object.keys(data.entry_pages).length > 0) {
            const entryPages = data.entry_pages;
            const newNodes = [];
            const newLinks = [...data.links];
            
            for (const [page, count] of Object.entries(entryPages)) {
                const entryNodeName = page + ' (入口)';
                newNodes.push({ name: entryNodeName });
                newLinks.push({
                    source: entryNodeName,
                    target: page,
                    value: count
                });
            }
            
            newNodes.push(...data.nodes.map(n => ({ name: n.name })));
            
            this.data = {
                nodes: newNodes,
                links: newLinks
            };
        } else {
            this.data = data;
        }
        this.render();
    }

    resize() {
        this.chart && this.chart.resize();
    }

    showEmptyMessage(message) {
        if (this.chart) {
            this.chart.dispose();
            this.chart = null;
        }
        this.container.innerHTML = `<div style="display: flex; justify-content: center; align-items: center; height: 400px; color: #999;">${message}</div>`;
    }

    removeCycles(nodes, links) {
        const nodeNames = nodes.map(n => n.name);
        const nodeIndex = new Map(nodeNames.map((name, i) => [name, i]));
        
        const graph = nodeNames.map(() => []);
        links.forEach(link => {
            const sourceIdx = nodeIndex.get(link.source);
            const targetIdx = nodeIndex.get(link.target);
            if (sourceIdx !== undefined && targetIdx !== undefined) {
                graph[sourceIdx].push({ target: targetIdx, link });
            }
        });
        
        const inDegree = nodeNames.map(() => 0);
        graph.forEach(edges => {
            edges.forEach(edge => {
                inDegree[edge.target]++;
            });
        });
        
        const queue = [];
        nodeNames.forEach((_, i) => {
            if (inDegree[i] === 0) {
                queue.push(i);
            }
        });
        
        const validNodes = new Set();
        while (queue.length > 0) {
            const node = queue.shift();
            validNodes.add(node);
            
            for (const edge of graph[node]) {
                inDegree[edge.target]--;
                if (inDegree[edge.target] === 0) {
                    queue.push(edge.target);
                }
            }
        }
        
        const filteredLinks = links.filter(link => {
            const sourceIdx = nodeIndex.get(link.source);
            const targetIdx = nodeIndex.get(link.target);
            return validNodes.has(sourceIdx) && validNodes.has(targetIdx);
        });
        
        const removedCount = links.length - filteredLinks.length;
        if (removedCount > 0) {
            console.log(`Removed ${removedCount} cycle links`);
        }
        
        return filteredLinks;
    }

    render() {
        console.log('Sankey data:', this.data);
        
        if (!this.data || !this.data.nodes || !this.data.links) {
            console.warn('Sankey data is invalid');
            this.showEmptyMessage('数据无效');
            return;
        }
        
        if (this.data.nodes.length === 0) {
            console.warn('Sankey has no nodes');
            this.showEmptyMessage('暂无数据');
            return;
        }
        
        const filteredLinks = this.removeCycles(this.data.nodes, this.data.links);
        console.log('Filtered links:', filteredLinks);
        
        if (filteredLinks.length === 0) {
            console.warn('Sankey has no valid links after removing cycles');
            this.showEmptyMessage('暂无有效流转数据');
            return;
        }
        
        if (!this.chart) {
            this.container.innerHTML = '';
            this.chart = echarts.init(this.container);
        }
        
        this.container.style.height = '500px';
        this.chart.resize();
        
        const option = {
            tooltip: {
                trigger: 'item',
                triggerOn: 'mousemove'
            },
            series: [{
                type: 'sankey',
                data: this.data.nodes.map(node => ({
                    name: node.name
                })),
                links: filteredLinks.map(link => ({
                    source: link.source,
                    target: link.target,
                    value: link.value
                })),
                itemStyle: {
                    color: '#6366f1',
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    color: '#333',
                    fontSize: 13,
                    fontWeight: 'bold'
                },
                lineStyle: {
                    color: 'source',
                    curveness: 0.5,
                    opacity: 0.4
                },
                left: '10%',
                right: '10%',
                top: '5%',
                bottom: '5%',
                nodeWidth: 30,
                nodeGap: 20,
                draggable: true
            }]
        };

        console.log('Sankey option:', option);
        this.chart.setOption(option, true);
    }
}
