# AI Agent开发团队系统 - Docker镜像

# 使用多阶段构建
FROM node:18-alpine AS frontend-builder

# 构建前端
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ ./
RUN npm run build

# Python后端镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制Python依赖文件
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ ./src/
COPY *.py ./
COPY PROJECT_EVALUATION_REPORT.md ./
COPY FINAL_SYSTEM_SUMMARY.md ./

# 复制前端构建结果
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# 创建静态文件服务
RUN mkdir -p static
COPY --from=frontend-builder /app/frontend/dist/* ./static/

# 设置环境变量
ENV PYTHONPATH=/app
ENV PORT=8080
ENV FRONTEND_PORT=3000

# 暴露端口
EXPOSE 8080

# 创建启动脚本
RUN echo '#!/bin/bash\n\
echo "🚀 启动AI Agent开发团队系统..."\n\
echo "后端API: http://localhost:8080"\n\
echo "API文档: http://localhost:8080/docs"\n\
python api_server.py\n\
' > start.sh && chmod +x start.sh

# 启动命令
CMD ["./start.sh"]