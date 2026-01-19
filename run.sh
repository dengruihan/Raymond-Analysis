#!/bin/bash

# Raymond Analysis 启动脚本

echo "正在启动 Raymond Analysis..."

# 检查虚拟环境
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "警告：未检测到 conda 虚拟环境"
    echo "请先激活虚拟环境: conda activate raymond"
    echo "继续启动可能使用系统 Python..."
fi

# 创建数据目录
mkdir -p data

# 检查并启动 Redis（可选）
if command -v redis-cli &> /dev/null; then
    if ! redis-cli ping &> /dev/null; then
        echo "Redis 未运行，尝试启动 Redis..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew services start redis 2>/dev/null || echo "请手动启动 Redis: brew services start redis"
        else
            sudo systemctl start redis 2>/dev/null || echo "请手动启动 Redis: sudo systemctl start redis"
        fi
    else
        echo "Redis 正在运行"
    fi
else
    echo "Redis 未安装，部分功能将受限（实时缓存）"
fi

# 启动应用
echo "启动 FastAPI 应用..."
python backend/app.py
