# AI Agent开发团队 - 前端管理界面

这是AI Agent开发团队系统的Web管理界面，提供了完整的可视化管理功能。

## 功能特性

### 🎯 核心功能
- **仪表板** - 系统总览、性能监控、实时数据展示
- **项目管理** - 项目创建、进度跟踪、资源分配
- **Agent监控** - Agent状态监控、性能分析、资源使用
- **任务分析** - 任务统计、执行分析、趋势图表
- **团队协作** - Agent间通信、协作流程、活动时间轴
- **系统评估** - 基于AI Agent团队自我评估的可视化报告
- **系统设置** - LLM配置、Agent设置、安全控制

### 🎨 界面特色
- **现代化设计** - Material-UI设计系统
- **响应式布局** - 适配各种屏幕尺寸
- **实时数据** - 动态更新的图表和指标
- **交互式图表** - 使用Recharts提供丰富的数据可视化
- **友好的用户体验** - 直观的导航和操作流程

## 技术栈

- **框架**: React 18 + TypeScript
- **UI库**: Material-UI (MUI) 5
- **图表**: Recharts
- **路由**: React Router v6
- **状态管理**: Zustand
- **数据获取**: React Query
- **构建工具**: Vite
- **样式**: Emotion (CSS-in-JS)

## 快速开始

### 1. 安装依赖
```bash
cd frontend
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```

应用将在 http://localhost:3000 启动

### 3. 构建生产版本
```bash
npm run build
```

### 4. 预览生产版本
```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 公共组件
│   │   ├── Navbar.tsx      # 顶部导航栏
│   │   └── Sidebar.tsx     # 侧边导航栏
│   ├── pages/              # 页面组件
│   │   ├── Dashboard.tsx   # 仪表板
│   │   ├── ProjectManagement.tsx  # 项目管理
│   │   ├── AgentMonitoring.tsx    # Agent监控
│   │   ├── TaskAnalysis.tsx       # 任务分析
│   │   ├── TeamCollaboration.tsx  # 团队协作
│   │   ├── SystemEvaluation.tsx   # 系统评估
│   │   └── Settings.tsx           # 系统设置
│   ├── App.tsx             # 主应用组件
│   └── main.tsx           # 应用入口点
├── public/                 # 静态资源
├── package.json           # 项目配置
├── vite.config.ts         # Vite配置
└── tsconfig.json          # TypeScript配置
```

## 页面功能详解

### 🏠 仪表板 (Dashboard)
- 系统关键指标概览
- Agent性能实时监控
- 项目分布和进度展示
- 最近活动时间轴
- 周任务完成趋势

### 📁 项目管理 (ProjectManagement)
- 项目列表和状态管理
- 创建和编辑项目
- 项目详情查看
- Agent分配管理
- 进度和预算跟踪

### 🤖 Agent监控 (AgentMonitoring)
- 5个Agent的实时状态
- 性能趋势图表
- 资源使用监控
- Agent详细信息面板
- 控制操作（暂停/重启）

### 📊 任务分析 (TaskAnalysis)
- 任务统计和分析
- Agent任务执行统计
- 任务优先级分布
- 每日任务趋势
- 任务详情管理

### 🤝 团队协作 (TeamCollaboration)
- Agent间通信监控
- 协作活动时间轴
- 协作强度分析
- 实时消息发送
- 团队状态面板

### 📈 系统评估 (SystemEvaluation)
- 基于AI Agent团队自我评估结果
- 综合评分展示 (8.1/10)
- 各维度雷达图分析
- 项目优势和待改进点
- 改进建议路线图
- 重新评估功能

### ⚙️ 系统设置 (Settings)
- 系统基础配置
- LLM提供商管理
- Agent参数设置
- 安全控制选项

## 数据模拟

当前版本使用模拟数据展示功能，主要包括：
- Agent状态和性能数据
- 项目进度和统计信息
- 任务分析和趋势数据
- 协作活动记录
- 系统评估结果（基于实际评估报告）

## API集成

前端预留了API集成接口，可以轻松连接到后端服务：
- 代理配置指向 `http://localhost:8000`
- 使用React Query进行数据管理
- 支持实时数据更新

## 开发说明

### 添加新页面
1. 在 `src/pages/` 创建新的页面组件
2. 在 `src/App.tsx` 中添加路由
3. 在 `src/components/Sidebar.tsx` 中添加导航项

### 自定义主题
主题配置在 `src/main.tsx` 中，可以修改颜色、字体等样式设置。

### 响应式设计
使用MUI的Grid系统和断点，确保在各种设备上的良好显示效果。

## 部署

### 开发环境
```bash
npm run dev
```

### 生产环境
```bash
npm run build
npm run preview
```

构建产物在 `dist/` 目录中，可以部署到任何静态文件服务器。

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 许可证

MIT License