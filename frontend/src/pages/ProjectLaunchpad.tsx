import React, { useState } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemButton,
  Avatar,
  LinearProgress,
  Fab,
  Tooltip,
  Alert,
  Divider,
  Tabs,
  Tab,
  IconButton,
} from '@mui/material'
import {
  Add,
  RocketLaunch,
  Upload,
  Assignment,
  Code,
  Architecture,
  BugReport,
  SmartToy,
  Person,
  PlayArrow,
  Pause,
  Visibility,
  Edit,
  Delete,
  CheckCircle,
  Schedule,
  Warning,
  Folder,
  CloudUpload,
  GitHub,
  Description,
  Settings,
} from '@mui/icons-material'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && <Box>{children}</Box>}
    </div>
  )
}

const ProjectLaunchpad: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const [createProjectOpen, setCreateProjectOpen] = useState(false)
  const [importProjectOpen, setImportProjectOpen] = useState(false)
  const [projectDetailsOpen, setProjectDetailsOpen] = useState(false)
  const [selectedProject, setSelectedProject] = useState<any>(null)
  const [activeStep, setActiveStep] = useState(0)

  // 用户的多个app项目
  const userProjects = [
    {
      id: 'user-proj-001',
      name: '智能股票分析平台',
      type: 'Web应用',
      status: 'in_progress',
      priority: 'high',
      description: '基于AI的股票市场分析和预测平台，提供实时数据分析和投资建议',
      techStack: ['React', 'Python', 'FastAPI', 'PostgreSQL', 'Redis'],
      progress: 65,
      estimatedCompletion: '2025-03-15',
      assignedAgents: ['PM-Agent', 'Architect-Agent', 'Developer-Agent', 'QA-Agent'],
      currentPhase: '核心功能开发',
      requirements: [
        '实时股票数据获取和处理',
        'AI驱动的价格预测算法',
        '用户投资组合管理',
        '风险评估和警报系统',
        '移动端响应式设计'
      ],
      lastUpdate: '2小时前',
      budget: 800000,
      spent: 520000,
    },
    {
      id: 'user-proj-002',
      name: '企业CRM系统',
      type: '企业应用',
      status: 'planning',
      priority: 'medium',
      description: '全功能企业客户关系管理系统，支持销售流程自动化和客户数据分析',
      techStack: ['Vue.js', 'Node.js', 'MongoDB', 'Docker'],
      progress: 15,
      estimatedCompletion: '2025-05-30',
      assignedAgents: ['PM-Agent'],
      currentPhase: '需求收集',
      requirements: [
        '客户信息管理',
        '销售漏斗追踪',
        '自动化营销活动',
        '数据分析和报表',
        '移动端应用'
      ],
      lastUpdate: '1天前',
      budget: 600000,
      spent: 90000,
    },
    {
      id: 'user-proj-003',
      name: '在线教育平台',
      type: '移动应用',
      status: 'pending',
      priority: 'medium',
      description: '面向K12的在线教育平台，包含课程管理、在线考试和学习分析功能',
      techStack: ['React Native', 'Python', 'Django', 'MySQL'],
      progress: 0,
      estimatedCompletion: '2025-07-01',
      assignedAgents: [],
      currentPhase: '等待启动',
      requirements: [
        '课程内容管理系统',
        '在线视频播放',
        '互动考试系统',
        '学习进度跟踪',
        '家长监控功能'
      ],
      lastUpdate: '3天前',
      budget: 450000,
      spent: 0,
    },
    {
      id: 'user-proj-004',
      name: '智能物流管理',
      type: 'IoT应用',
      status: 'completed',
      priority: 'low',
      description: '基于IoT的智能物流管理系统，实现货物追踪和路径优化',
      techStack: ['Angular', 'Java', 'Spring Boot', 'Oracle'],
      progress: 100,
      estimatedCompletion: '2024-12-31',
      assignedAgents: ['PM-Agent', 'Architect-Agent', 'Developer-Agent', 'QA-Agent'],
      currentPhase: '已完成',
      requirements: [
        'RFID货物追踪',
        '路径优化算法',
        '实时位置监控',
        '库存管理系统',
        '数据分析报表'
      ],
      lastUpdate: '1周前',
      budget: 700000,
      spent: 680000,
    },
  ]

  const projectCreationSteps = [
    '项目基本信息',
    '技术需求分析',
    'AI团队分配',
    '项目启动确认'
  ]

  const availableAgents = [
    { id: 'pm', name: 'PM-Agent', role: '产品经理', icon: <Person />, color: '#1976d2' },
    { id: 'arch', name: 'Architect-Agent', role: '系统架构师', icon: <Architecture />, color: '#4caf50' },
    { id: 'dev', name: 'Developer-Agent', role: '开发工程师', icon: <Code />, color: '#ff9800' },
    { id: 'qa', name: 'QA-Agent', role: '质量保证', icon: <BugReport />, color: '#9c27b0' },
    { id: 'mgr', name: 'Manager-Agent', role: '项目管理', icon: <SmartToy />, color: '#f44336' },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in_progress': return '#4caf50'
      case 'planning': return '#ff9800'
      case 'pending': return '#2196f3'
      case 'completed': return '#9c27b0'
      default: return '#9e9e9e'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'in_progress': return '进行中'
      case 'planning': return '规划中'
      case 'pending': return '待启动'
      case 'completed': return '已完成'
      default: return '未知'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#f44336'
      case 'medium': return '#ff9800'
      case 'low': return '#4caf50'
      default: return '#9e9e9e'
    }
  }

  const handleProjectLaunch = (projectId: string) => {
    // 启动项目的逻辑
    alert(`正在为项目 ${projectId} 分配AI团队...`)
  }

  const handleProjectView = (project: any) => {
    setSelectedProject(project)
    setProjectDetailsOpen(true)
  }

  const handleCreateProject = () => {
    setCreateProjectOpen(true)
    setActiveStep(0)
  }

  const handleNextStep = () => {
    setActiveStep(prev => prev + 1)
  }

  const handleBackStep = () => {
    setActiveStep(prev => prev - 1)
  }

  return (
    <Box>
      {/* 页面标题和操作 */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
            🚀 项目启动台
          </Typography>
          <Typography variant="body1" color="text.secondary">
            让AI团队高效推进您的多个app项目
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Upload />}
            onClick={() => setImportProjectOpen(true)}
          >
            导入项目
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleCreateProject}
            sx={{ bgcolor: '#1976d2' }}
          >
            创建新项目
          </Button>
        </Box>
      </Box>

      {/* 快速统计 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6">总项目数</Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {userProjects.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6">进行中</Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {userProjects.filter(p => p.status === 'in_progress').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6">待启动</Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {userProjects.filter(p => p.status === 'pending').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h6">已完成</Typography>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {userProjects.filter(p => p.status === 'completed').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 标签页 */}
      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={tabValue} 
          onChange={(e, newValue) => setTabValue(newValue)}
          variant="fullWidth"
        >
          <Tab icon={<Folder />} label="所有项目" />
          <Tab icon={<PlayArrow />} label="进行中" />
          <Tab icon={<Schedule />} label="待启动" />
          <Tab icon={<CheckCircle />} label="已完成" />
        </Tabs>
      </Paper>

      {/* 项目列表 */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {userProjects.map((project) => (
            <Grid item xs={12} md={6} lg={4} key={project.id}>
              <Card 
                sx={{ 
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'all 0.3s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 6,
                  }
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  {/* 项目标题和状态 */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 'bold', flex: 1 }}>
                      {project.name}
                    </Typography>
                    <Chip
                      label={getStatusText(project.status)}
                      size="small"
                      sx={{
                        bgcolor: getStatusColor(project.status),
                        color: 'white',
                        ml: 1,
                      }}
                    />
                  </Box>

                  {/* 项目类型和优先级 */}
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip label={project.type} variant="outlined" size="small" />
                    <Chip 
                      label={`优先级: ${project.priority}`} 
                      size="small"
                      sx={{
                        bgcolor: getPriorityColor(project.priority),
                        color: 'white',
                      }}
                    />
                  </Box>

                  {/* 项目描述 */}
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {project.description}
                  </Typography>

                  {/* 进度条 */}
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="caption">项目进度</Typography>
                      <Typography variant="caption">{project.progress}%</Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={project.progress}
                      sx={{ 
                        height: 8, 
                        borderRadius: 4,
                        '& .MuiLinearProgress-bar': {
                          bgcolor: getStatusColor(project.status)
                        }
                      }}
                    />
                  </Box>

                  {/* 分配的Agents */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      分配的AI Agents ({project.assignedAgents.length})
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                      {project.assignedAgents.slice(0, 4).map((agentName, index) => {
                        const agent = availableAgents.find(a => agentName.includes(a.name.split('-')[0]))
                        return (
                          <Tooltip key={index} title={agentName}>
                            <Avatar
                              sx={{
                                width: 24,
                                height: 24,
                                bgcolor: agent?.color || '#9e9e9e',
                                fontSize: '0.75rem',
                              }}
                            >
                              {agent?.icon}
                            </Avatar>
                          </Tooltip>
                        )
                      })}
                      {project.assignedAgents.length > 4 && (
                        <Avatar
                          sx={{
                            width: 24,
                            height: 24,
                            bgcolor: '#9e9e9e',
                            fontSize: '0.75rem',
                          }}
                        >
                          +{project.assignedAgents.length - 4}
                        </Avatar>
                      )}
                    </Box>
                  </Box>

                  {/* 预算信息 */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      预算使用: ¥{project.spent.toLocaleString()} / ¥{project.budget.toLocaleString()}
                    </Typography>
                  </Box>

                  {/* 最后更新 */}
                  <Typography variant="caption" color="text.secondary">
                    最后更新: {project.lastUpdate}
                  </Typography>
                </CardContent>

                {/* 操作按钮 */}
                <Box sx={{ p: 2, pt: 0 }}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<Visibility />}
                      onClick={() => handleProjectView(project)}
                    >
                      查看详情
                    </Button>
                    {project.status === 'pending' ? (
                      <Button
                        size="small"
                        variant="contained"
                        startIcon={<RocketLaunch />}
                        onClick={() => handleProjectLaunch(project.id)}
                        sx={{ bgcolor: '#4caf50' }}
                      >
                        启动项目
                      </Button>
                    ) : project.status === 'in_progress' ? (
                      <Button
                        size="small"
                        variant="contained"
                        startIcon={<Settings />}
                        color="primary"
                      >
                        管理项目
                      </Button>
                    ) : (
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<Edit />}
                      >
                        编辑项目
                      </Button>
                    )}
                  </Box>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          {userProjects.filter(p => p.status === 'in_progress').map((project) => (
            <Grid item xs={12} md={6} key={project.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{project.name}</Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {project.currentPhase}
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={project.progress}
                    sx={{ mb: 2 }}
                  />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Button variant="outlined" size="small">管理</Button>
                    <Button variant="contained" size="small">查看详情</Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          {userProjects.filter(p => p.status === 'pending').map((project) => (
            <Grid item xs={12} md={6} key={project.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{project.name}</Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {project.description}
                  </Typography>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    该项目等待AI团队分配
                  </Alert>
                  <Button 
                    variant="contained" 
                    startIcon={<RocketLaunch />}
                    fullWidth
                    onClick={() => handleProjectLaunch(project.id)}
                  >
                    立即启动
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          {userProjects.filter(p => p.status === 'completed').map((project) => (
            <Grid item xs={12} md={6} key={project.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{project.name}</Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    完成时间: {project.estimatedCompletion}
                  </Typography>
                  <Chip label="项目成功完成" color="success" sx={{ mb: 2 }} />
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button variant="outlined" size="small">查看报告</Button>
                    <Button variant="outlined" size="small">复制项目</Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* 创建项目对话框 */}
      <Dialog open={createProjectOpen} onClose={() => setCreateProjectOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>创建新App项目</DialogTitle>
        <DialogContent>
          <Stepper activeStep={activeStep} orientation="vertical">
            {projectCreationSteps.map((label, index) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
                <StepContent>
                  {index === 0 && (
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <TextField fullWidth label="项目名称" required />
                      </Grid>
                      <Grid item xs={12}>
                        <TextField 
                          fullWidth 
                          label="项目描述" 
                          multiline 
                          rows={3} 
                          required 
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <FormControl fullWidth>
                          <InputLabel>项目类型</InputLabel>
                          <Select label="项目类型">
                            <MenuItem value="web">Web应用</MenuItem>
                            <MenuItem value="mobile">移动应用</MenuItem>
                            <MenuItem value="desktop">桌面应用</MenuItem>
                            <MenuItem value="api">API服务</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={6}>
                        <FormControl fullWidth>
                          <InputLabel>优先级</InputLabel>
                          <Select label="优先级">
                            <MenuItem value="high">高</MenuItem>
                            <MenuItem value="medium">中</MenuItem>
                            <MenuItem value="low">低</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                    </Grid>
                  )}
                  {index === 1 && (
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <TextField 
                          fullWidth 
                          label="核心功能需求" 
                          multiline 
                          rows={4}
                          placeholder="请列出项目的核心功能需求..."
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <TextField 
                          fullWidth 
                          label="技术栈偏好" 
                          placeholder="例如: React, Node.js, PostgreSQL"
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <TextField fullWidth label="预算" type="number" />
                      </Grid>
                      <Grid item xs={6}>
                        <TextField 
                          fullWidth 
                          label="期望完成时间" 
                          type="date"
                          InputLabelProps={{ shrink: true }}
                        />
                      </Grid>
                    </Grid>
                  )}
                  {index === 2 && (
                    <Box>
                      <Typography variant="h6" sx={{ mb: 2 }}>
                        选择AI团队成员
                      </Typography>
                      <Grid container spacing={2}>
                        {availableAgents.map((agent) => (
                          <Grid item xs={12} sm={6} key={agent.id}>
                            <Card 
                              sx={{ 
                                cursor: 'pointer',
                                border: '2px solid transparent',
                                '&:hover': { borderColor: agent.color }
                              }}
                            >
                              <CardContent>
                                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                  <Avatar sx={{ bgcolor: agent.color, mr: 2 }}>
                                    {agent.icon}
                                  </Avatar>
                                  <Box>
                                    <Typography variant="h6">{agent.name}</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                      {agent.role}
                                    </Typography>
                                  </Box>
                                </Box>
                              </CardContent>
                            </Card>
                          </Grid>
                        ))}
                      </Grid>
                    </Box>
                  )}
                  {index === 3 && (
                    <Box>
                      <Alert severity="success" sx={{ mb: 2 }}>
                        项目配置已完成，AI团队已准备就绪！
                      </Alert>
                      <Typography variant="body1" sx={{ mb: 2 }}>
                        确认创建项目后，AI团队将立即开始工作：
                      </Typography>
                      <List>
                        <ListItem>
                          <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                          <ListItemText primary="PM-Agent将进行需求分析" />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                          <ListItemText primary="Architect-Agent设计系统架构" />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                          <ListItemText primary="Developer-Agent开始编码实现" />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                          <ListItemText primary="QA-Agent确保质量标准" />
                        </ListItem>
                      </List>
                    </Box>
                  )}
                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="contained"
                      onClick={index === projectCreationSteps.length - 1 ? 
                        () => {
                          setCreateProjectOpen(false)
                          alert('项目创建成功！AI团队开始工作...')
                        } : 
                        handleNextStep
                      }
                      sx={{ mr: 1 }}
                    >
                      {index === projectCreationSteps.length - 1 ? '创建项目' : '下一步'}
                    </Button>
                    <Button
                      disabled={index === 0}
                      onClick={handleBackStep}
                    >
                      上一步
                    </Button>
                  </Box>
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </DialogContent>
      </Dialog>

      {/* 导入项目对话框 */}
      <Dialog open={importProjectOpen} onClose={() => setImportProjectOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>导入现有项目</DialogTitle>
        <DialogContent>
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <CloudUpload sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" sx={{ mb: 2 }}>
              选择导入方式
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<GitHub />}
                  sx={{ mb: 2 }}
                >
                  从GitHub导入
                </Button>
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Folder />}
                  sx={{ mb: 2 }}
                >
                  从本地文件夹导入
                </Button>
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Description />}
                >
                  从项目文档导入
                </Button>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImportProjectOpen(false)}>取消</Button>
        </DialogActions>
      </Dialog>

      {/* 项目详情对话框 */}
      <Dialog 
        open={projectDetailsOpen} 
        onClose={() => setProjectDetailsOpen(false)} 
        maxWidth="lg" 
        fullWidth
      >
        {selectedProject && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">{selectedProject.name}</Typography>
                <Chip
                  label={getStatusText(selectedProject.status)}
                  sx={{
                    bgcolor: getStatusColor(selectedProject.status),
                    color: 'white',
                  }}
                />
              </Box>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <Typography variant="h6" sx={{ mb: 2 }}>项目需求</Typography>
                  <List>
                    {selectedProject.requirements.map((req: string, index: number) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <CheckCircle color="primary" />
                        </ListItemIcon>
                        <ListItemText primary={req} />
                      </ListItem>
                    ))}
                  </List>
                  
                  <Typography variant="h6" sx={{ mb: 2, mt: 3 }}>技术栈</Typography>
                  <Box>
                    {selectedProject.techStack.map((tech: string, index: number) => (
                      <Chip key={index} label={tech} sx={{ mr: 1, mb: 1 }} />
                    ))}
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" sx={{ mb: 2 }}>项目信息</Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText 
                        primary="当前阶段" 
                        secondary={selectedProject.currentPhase} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="预计完成" 
                        secondary={selectedProject.estimatedCompletion} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="项目进度" 
                        secondary={`${selectedProject.progress}%`} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="预算状态" 
                        secondary={`¥${selectedProject.spent.toLocaleString()} / ¥${selectedProject.budget.toLocaleString()}`} 
                      />
                    </ListItem>
                  </List>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setProjectDetailsOpen(false)}>关闭</Button>
              <Button variant="outlined">编辑项目</Button>
              <Button variant="contained">管理团队</Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* 浮动操作按钮 */}
      <Fab
        color="primary"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
        }}
        onClick={handleCreateProject}
      >
        <Add />
      </Fab>
    </Box>
  )
}

export default ProjectLaunchpad