#!/bin/bash

# AI Agent开发团队 - 一键启动脚本

echo "🚀 AI Agent开发团队 - 一键启动"
echo "================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python"
    exit 1
fi

# 检查Node.js (用于前端)
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm 未安装，请先安装Node.js"
    exit 1
fi

echo "📋 选择启动方式:"
echo "1) 智能启动 (推荐)"
echo "2) Docker部署"
echo "3) 仅后端服务"
echo "4) 检查端口"

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo "🔧 智能启动模式..."
        python3 smart_start.py
        ;;
    2)
        echo "🐳 Docker部署模式..."
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker 未安装，请先安装Docker"
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            echo "❌ Docker Compose 未安装，请先安装Docker Compose"
            exit 1
        fi
        
        echo "构建并启动所有服务..."
        docker-compose up --build
        ;;
    3)
        echo "⚡ 仅启动后端服务..."
        python3 check_ports.py
        python3 api_server.py
        ;;
    4)
        echo "🔍 检查端口状态..."
        python3 check_ports.py
        echo ""
        echo "如需强制停止占用的进程，运行:"
        echo "python3 check_ports.py --kill"
        ;;
    *)
        echo "❌ 无效选择，请重新运行脚本"
        exit 1
        ;;
esac