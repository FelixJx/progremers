# 🚀 AI Agent开发团队 - 启动指南

## 🎯 端口说明

系统已自动检测并配置了可用端口：
- **后端API**: http://localhost:8080
- **前端界面**: http://localhost:3000
- **API文档**: http://localhost:8080/docs

## 💡 三种启动方式

### 方式1: 智能启动 (推荐)
```bash
python smart_start.py
```
✅ **优点**: 自动检测端口、更新配置、处理依赖  
✅ **适用**: 开发和测试环境

### 方式2: Docker部署 (生产推荐)
```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d --build

# 停止服务
docker-compose down
```
✅ **优点**: 一键部署、环境隔离、生产就绪  
✅ **适用**: 生产环境和团队协作

### 方式3: 手动启动
```bash
# 检查端口
python check_ports.py

# 启动后端
python api_server.py

# 启动前端 (新终端)
cd frontend
npm install
npm run dev
```
✅ **优点**: 完全控制、方便调试  
✅ **适用**: 开发调试

## 🔧 端口被占用解决方案

### 自动解决 (推荐)
```bash
# 检查并获取可用端口
python check_ports.py

# 强制停止占用端口的进程
python check_ports.py --kill

# 智能启动会自动使用可用端口
python smart_start.py
```

### 手动解决
```bash
# 查看占用8080端口的进程
lsof -ti :8080

# 停止进程 (替换PID)
kill -9 <PID>

# 或停止所有常用端口
sudo pkill -f "8000|8080|3000"
```

## 🐳 Docker快速部署

### 最简单启动
```bash
# 一行命令启动整个系统
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f ai-agent-backend
```

### 服务访问地址
- **前端界面**: http://localhost:3000
- **项目启动台**: http://localhost:3000/launchpad  
- **后端API**: http://localhost:8080
- **API文档**: http://localhost:8080/docs
- **Redis**: localhost:6379
- **PostgreSQL**: localhost:5432

## 🎯 快速开始

### 1. 启动系统
选择任一方式启动后，访问：http://localhost:3000

### 2. 创建您的第一个项目
1. 点击 **"项目启动台"** 或直接访问: http://localhost:3000/launchpad
2. 点击 **"创建新项目"**
3. 填写项目信息：
   - 项目名称: "我的电商App"
   - 项目描述: "用户友好的在线购物平台"
   - 项目类型: "移动应用"
   - 核心需求: ["用户注册", "商品浏览", "购物车", "支付系统"]
4. 选择AI团队成员
5. 确认创建

### 3. 监控AI团队工作
- 在 **仪表板** 查看系统总览
- 在 **Agent监控** 查看5个AI Agent的实时状态
- 在 **任务分析** 查看项目进展

## 🛠️ 故障排除

### 常见问题

**Q: 端口被占用怎么办？**
```bash
python check_ports.py --kill
python smart_start.py
```

**Q: 前端无法访问后端API？**
检查CORS配置和端口配置是否正确

**Q: Docker启动失败？**
```bash
# 清理Docker资源
docker-compose down -v
docker system prune -f

# 重新构建
docker-compose up --build
```

**Q: npm安装依赖失败？**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 日志查看
```bash
# 智能启动日志
tail -f logs/app.log

# Docker日志
docker-compose logs -f ai-agent-backend
docker-compose logs -f ai-agent-frontend
```

## 🎉 功能亮点

### 🚀 项目启动台 (核心功能)
- 一键创建新的app项目
- 自动分配5个AI Agent团队
- 实时监控项目进展
- 支持多项目并行开发

### 🤖 AI Agent团队
- **PM-Agent**: 需求分析和产品规划
- **Architect-Agent**: 系统架构设计
- **Developer-Agent**: 代码开发实现
- **QA-Agent**: 质量保证测试
- **Manager-Agent**: 项目管理协调

### 📊 系统特色
- **自我评估**: 8.1/10系统评分
- **Context-Rot技术**: 先进的上下文管理
- **MCP集成**: 实际操作能力
- **实时监控**: 完整的团队协作可视化

## 🔗 重要链接

启动后访问这些地址：

- 🏠 **主页**: http://localhost:3000
- 🚀 **项目启动台**: http://localhost:3000/launchpad
- 🤖 **Agent监控**: http://localhost:3000/agents  
- 📊 **系统评估**: http://localhost:3000/evaluation
- ⚙️ **系统设置**: http://localhost:3000/settings
- 📚 **API文档**: http://localhost:8080/docs

---

## 🎯 立即开始

选择您喜欢的启动方式，开始您的AI驱动开发之旅！

```bash
# 最简单的方式
python smart_start.py
```

然后访问: http://localhost:3000/launchpad 创建您的第一个项目！