# Raymond Analysis

一个类似 Google Analytics 的实时网站数据分析平台。

## 功能特性

- 实时数据收集（页面浏览量、用户行为、事件追踪）
- 实时监控仪表盘
- WebSocket 实时数据推送
- 数据可视化（ECharts 图表）
- 支持多种统计分析
- 高性能设计（支持 10万次/分钟）

## 技术栈

- 后端：FastAPI + SQLite + Redis
- 前端：原生 HTML/CSS/JavaScript + ECharts
- 实时通信：WebSocket

## 安装步骤

1. 创建并激活虚拟环境：
```bash
conda create -n raymond python=3.10 -y
conda activate raymond
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 启动 Redis（可选）：
```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt-get install redis-server
sudo systemctl start redis
```

## 运行项目

```bash
python backend/app.py
```

访问 http://localhost:8000 查看仪表盘。

## 使用追踪代码

在您的网站中添加以下代码：

```html
<script src="http://your-server:8000/tracker.js"></script>
```

## API 文档

启动服务后访问 http://localhost:8000/docs 查看 Swagger API 文档。

## 项目结构

```
RA/
├── backend/
│   ├── api/          # API 路由
│   ├── models/       # 数据库模型
│   ├── services/     # 业务逻辑
│   ├── utils/        # 工具函数
│   └── app.py        # FastAPI 应用入口
├── frontend/
│   ├── static/       # 静态资源
│   └── templates/    # HTML 模板
├── tracking/         # 追踪代码
├── data/            # 数据库文件
└── config/          # 配置文件
```
