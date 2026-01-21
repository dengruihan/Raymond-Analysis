class SankeyChart {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            width: options.width || 800,
            height: options.height || 500,
            nodeWidth: options.nodeWidth || 25,
            nodePadding: options.nodePadding || 30,
            nodeMinHeight: options.nodeMinHeight || 5,
            colors: options.colors || [
                '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e',
                '#f97316', '#eab308', '#22c55e', '#06b6d4',
                '#0ea5e9', '#3b82f6'
            ],
            linkOpacity: options.linkOpacity || 0.35,
            linkHoverOpacity: options.linkHoverOpacity || 0.6,
            nodeCornerRadius: options.nodeCornerRadius || 6,
            ...options
        };
        this.data = null;
        this.links = [];
        this.nodes = [];
        this.nodeMap = {};
        this.svg = null;
    }

    setData(data) {
        this.data = data;
        this.processData();
        this.render();
        this.addInteractions();
    }

    processData() {
        this.nodes = [];
        this.links = [];
        this.nodeMap = {};

        this.data.nodes.forEach((node, index) => {
            this.nodes.push({
                ...node,
                index: index,
                value: 0,
                x: 0,
                y: 0
            });
            this.nodeMap[node.name] = index;
        });

        this.data.links.forEach(link => {
            const sourceIndex = this.nodeMap[link.source];
            const targetIndex = this.nodeMap[link.target];

            if (sourceIndex !== undefined && targetIndex !== undefined) {
                this.links.push({
                    source: sourceIndex,
                    target: targetIndex,
                    value: link.value,
                    dy: 0
                });
                this.nodes[sourceIndex].value += link.value;
                this.nodes[targetIndex].value += link.value;
            }
        });

        this.calculatePositions();
    }

    calculatePositions() {
        const { width, height, nodePadding, nodeWidth, nodeMinHeight } = this.options;
        const columns = {};

        this.nodes.forEach(node => {
            const column = this.getNodeColumn(node.name);
            if (!columns[column]) {
                columns[column] = [];
            }
            columns[column].push(node);
        });

        const columnKeys = Object.keys(columns).sort((a, b) => parseInt(a) - parseInt(b));
        const numColumns = columnKeys.length;
        const columnWidth = numColumns > 1 ? (width - nodeWidth) / (numColumns - 1) : 0;

        columnKeys.forEach((key, colIndex) => {
            const columnNodes = columns[key].sort((a, b) => b.value - a.value);
            const totalValue = columnNodes.reduce((sum, n) => sum + n.value, 0);
            const totalHeight = columnNodes.reduce((sum, n) => sum + Math.max(n.value * 0.6, nodeMinHeight) + nodePadding, 0) - nodePadding;
            let yOffset = (height - totalHeight) / 2;

            columnNodes.forEach(node => {
                node.x = numColumns > 1 ? colIndex * columnWidth : width / 2 - nodeWidth / 2;
                node.y = yOffset + Math.max(node.value * 0.6, nodeMinHeight) / 2;
                yOffset += Math.max(node.value * 0.6, nodeMinHeight) + nodePadding;
            });
        });

        this.links.forEach(link => {
            const sourceNode = this.nodes[link.source];
            const targetNode = this.nodes[link.target];
            link.x1 = sourceNode.x + nodeWidth;
            link.y1 = sourceNode.y;
            link.x2 = targetNode.x;
            link.y2 = targetNode.y;
            link.sourceHeight = Math.max(sourceNode.value * 0.6, nodeMinHeight);
            link.targetHeight = Math.max(targetNode.value * 0.6, nodeMinHeight);
            link.dy = Math.min(link.value * 1.2, Math.min(link.sourceHeight, link.targetHeight));
        });
    }

    getNodeColumn(pageName) {
        if (pageName === '首页') return '0';
        if (pageName.includes('登录')) return '1';
        if (pageName.includes('搜索')) return '1';
        if (pageName.includes('WiFi模型')) return '2';
        if (pageName.includes('提交')) return '3';
        return '2';
    }

    render() {
        const { width, height, colors } = this.options;

        const svg = `
            <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
                <defs>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                        <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                    <filter id="shadow">
                        <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.2"/>
                    </filter>
                </defs>
                ${this.renderLinks()}
                ${this.renderNodes()}
            </svg>
        `;

        this.container.innerHTML = svg;
        this.svg = this.container.querySelector('svg');
    }

    renderLinks() {
        return this.links.map(link => {
            const sourceNode = this.nodes[link.source];
            const targetNode = this.nodes[link.target];
            const colorIndex = this.nodes[link.source].index % this.options.colors.length;
            const color = this.options.colors[colorIndex];
            const { linkOpacity } = this.options;

            return `
                <path
                    class="sankey-link"
                    d="M ${link.x1} ${link.y1}
                       C ${(link.x1 + link.x2) / 2} ${link.y1},
                         ${(link.x1 + link.x2) / 2} ${link.y2},
                         ${link.x2} ${link.y2}"
                    fill="none"
                    stroke="${color}"
                    stroke-width="${link.dy}"
                    stroke-opacity="${linkOpacity}"
                    data-value="${link.value}"
                    style="transition: stroke-opacity 0.3s ease, stroke-width 0.3s ease;"
                >
                    <title>${this.nodes[link.source].name} → ${this.nodes[link.target].name}: ${link.value} 次访问</title>
                </path>
            `;
        }).join('');
    }

    renderNodes() {
        const { nodeWidth, nodeCornerRadius, colors } = this.options;

        return this.nodes.map(node => {
            const colorIndex = node.index % colors.length;
            const color = colors[colorIndex];
            const height = Math.max(node.value * 0.6, this.options.nodeMinHeight);

            return `
                <g class="sankey-node" data-name="${node.name}">
                    <rect
                        x="${node.x - nodeWidth / 2}"
                        y="${node.y - height / 2}"
                        width="${nodeWidth}"
                        height="${height}"
                        fill="${color}"
                        stroke="#fff"
                        stroke-width="2"
                        rx="${nodeCornerRadius}"
                        filter="url(#shadow)"
                        style="transition: transform 0.3s ease, filter 0.3s ease;"
                    >
                        <title>${node.name}: ${node.value} 次访问</title>
                    </rect>
                    <text
                        x="${node.x - nodeWidth / 2 - 10}"
                        y="${node.y}"
                        text-anchor="end"
                        dominant-baseline="middle"
                        font-size="13"
                        font-weight="500"
                        fill="#374151"
                    >${node.name}</text>
                    <text
                        x="${node.x + nodeWidth / 2 + 10}"
                        y="${node.y}"
                        text-anchor="start"
                        dominant-baseline="middle"
                        font-size="11"
                        font-weight="600"
                        fill="#6b7280"
                    >${node.value}</text>
                </g>
            `;
        }).join('');
    }

    addInteractions() {
        const links = this.svg.querySelectorAll('.sankey-link');
        const nodes = this.svg.querySelectorAll('.sankey-node');

        links.forEach(link => {
            link.addEventListener('mouseenter', () => {
                link.style.strokeOpacity = this.options.linkHoverOpacity;
                link.style.strokeWidth = parseFloat(link.getAttribute('stroke-width')) * 1.3 + 'px';
            });

            link.addEventListener('mouseleave', () => {
                link.style.strokeOpacity = this.options.linkOpacity;
                link.style.strokeWidth = parseFloat(link.getAttribute('stroke-width')) / 1.3 + 'px';
            });
        });

        nodes.forEach(nodeGroup => {
            const rect = nodeGroup.querySelector('rect');
            
            nodeGroup.addEventListener('mouseenter', () => {
                rect.style.filter = 'url(#glow) url(#shadow)';
                rect.style.transform = 'scale(1.05)';
                rect.style.transformOrigin = 'center';
            });

            nodeGroup.addEventListener('mouseleave', () => {
                rect.style.filter = 'url(#shadow)';
                rect.style.transform = 'scale(1)';
            });
        });
    }
}
