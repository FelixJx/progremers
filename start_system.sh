#!/bin/bash

# AI Agent开发团队系统启动脚本

echo "🚀 启动AI Agent开发团队系统..."
echo "=================================="

# 检查Python依赖
echo "📦 检查Python依赖..."
pip install fastapi uvicorn

# 检查前端依赖
echo "📦 检查前端依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo "安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

echo "🌟 系统组件启动中..."

# 启动后端API服务器
echo "🔧 启动后端API服务器 (端口: 8000)..."
python api_server.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端开发服务器
echo "🎨 启动前端开发服务器 (端口: 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ 系统启动完成！"
echo "=================================="
echo "🌐 前端界面: http://localhost:3000"
echo "📡 API服务: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "🎯 功能亮点："
echo "  • 🏠 仪表板 - 系统总览和实时监控"
echo "  • 🚀 项目启动台 - 一键启动多个app项目"
echo "  • 🤖 Agent监控 - 5个AI Agent实时状态"
echo "  • 📊 系统评估 - 8.1/10评分和改进建议"
echo "  • ⚙️ 系统设置 - LLM配置和Agent管理"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "=================================="

# 等待用户中断
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait