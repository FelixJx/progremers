import React, { useState } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
} from '@mui/material'
import {
  Add,
  Edit,
  Delete,
  Visibility,
  PlayArrow,
  Pause,
  CheckCircle,
  Schedule,
  Warning,
  Folder,
  Code,
  BugReport,
  Assignment,
} from '@mui/icons-material'

const ProjectManagement: React.FC = () => {
  const [createProjectOpen, setCreateProjectOpen] = useState(false)
  const [selectedProject, setSelectedProject] = useState<any>(null)
  const [projectDetailsOpen, setProjectDetailsOpen] = useState(false)

  const projects = [
    {
      id: 'proj-001',
      name: '电商平台重构',
      status: 'active',
      progress: 75,
      priority: 'high',
      startDate: '2025-01-15',
      endDate: '2025-03-15',
      description: '基于微服务架构的电商平台重构项目',
      techStack: ['React', 'Node.js', 'PostgreSQL', 'Docker'],
      teamSize: 5,
      assignedAgents: ['PM-Agent', 'Architect-Agent', 'Developer-Agent', 'QA-Agent'],
      currentPhase: '开发阶段',
      completedTasks: 45,
      totalTasks: 60,
      budget: 500000,
      spent: 375000,
    },
    {
      id: 'proj-002',
      name: 'AI客服系统',
      status: 'planning',
      progress: 25,
      priority: 'medium',
      startDate: '2025-02-01',
      endDate: '2025-04-30',
      description: '基于大模型的智能客服系统开发',
      techStack: ['Python', 'FastAPI', 'Redis', 'LangChain'],
      teamSize: 3,
      assignedAgents: ['PM-Agent', 'Developer-Agent'],
      currentPhase: '需求分析',
      completedTasks: 8,
      totalTasks: 32,
      budget: 300000,
      spent: 75000,
    },
    {
      id: 'proj-003',
      name: '数据分析平台',
      status: 'completed',
      progress: 100,
      priority: 'low',
      startDate: '2024-10-01',
      endDate: '2024-12-31',
      description: '企业数据分析和可视化平台',
      techStack: ['Vue.js', 'Python', 'ClickHouse', 'Kubernetes'],
      teamSize: 4,
      assignedAgents: ['PM-Agent', 'Architect-Agent', 'Developer-Agent', 'QA-Agent'],
      currentPhase: '已完成',
      completedTasks: 42,
      totalTasks: 42,
      budget: 400000,
      spent: 380000,
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#4caf50'
      case 'planning': return '#ff9800'
      case 'paused': return '#f44336'
      case 'completed': return '#2196f3'
      default: return '#9e9e9e'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '进行中'
      case 'planning': return '规划中'
      case 'paused': return '已暂停'
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

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'high': return '高'
      case 'medium': return '中'
      case 'low': return '低'
      default: return '未知'
    }
  }

  const getAgentIcon = (agentName: string) => {
    switch (agentName) {
      case 'PM-Agent': return <Assignment />
      case 'Architect-Agent': return <Code />
      case 'Developer-Agent': return <Code />
      case 'QA-Agent': return <BugReport />
      default: return <Assignment />
    }
  }

  const handleProjectView = (project: any) => {
    setSelectedProject(project)
    setProjectDetailsOpen(true)
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          项目管理
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateProjectOpen(true)}
        >
          创建新项目
        </Button>
      </Box>

      {/* 项目概览卡片 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Folder sx={{ color: '#1976d2', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#1976d2' }}>
                  总项目数
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {projects.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <PlayArrow sx={{ color: '#4caf50', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#4caf50' }}>
                  进行中
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {projects.filter(p => p.status === 'active').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Schedule sx={{ color: '#ff9800', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#ff9800' }}>
                  规划中
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {projects.filter(p => p.status === 'planning').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircle sx={{ color: '#2196f3', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#2196f3' }}>
                  已完成
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {projects.filter(p => p.status === 'completed').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 项目列表 */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 3 }}>
          项目列表
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>项目名称</TableCell>
                <TableCell>状态</TableCell>
                <TableCell>优先级</TableCell>
                <TableCell>进度</TableCell>
                <TableCell>分配的Agents</TableCell>
                <TableCell>截止日期</TableCell>
                <TableCell>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {projects.map((project) => (
                <TableRow key={project.id} hover>
                  <TableCell>
                    <Box>
                      <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                        {project.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {project.currentPhase}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusText(project.status)}
                      size="small"
                      sx={{
                        bgcolor: getStatusColor(project.status),
                        color: 'white',
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getPriorityText(project.priority)}
                      size="small"
                      variant="outlined"
                      sx={{
                        borderColor: getPriorityColor(project.priority),
                        color: getPriorityColor(project.priority),
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="body2" sx={{ mr: 1, minWidth: 40 }}>
                        {project.progress}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={project.progress}
                        sx={{ 
                          flexGrow: 1, 
                          height: 6, 
                          borderRadius: 3,
                          maxWidth: 100,
                        }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      {project.assignedAgents.slice(0, 3).map((agent, index) => (
                        <Avatar
                          key={index}
                          sx={{
                            width: 24,
                            height: 24,
                            bgcolor: '#1976d2',
                            fontSize: '0.75rem',
                          }}
                        >
                          {getAgentIcon(agent)}
                        </Avatar>
                      ))}
                      {project.assignedAgents.length > 3 && (
                        <Avatar
                          sx={{
                            width: 24,
                            height: 24,
                            bgcolor: '#9e9e9e',
                            fontSize: '0.75rem',
                          }}
                        >
                          +{project.assignedAgents.length - 3}
                        </Avatar>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {project.endDate}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <IconButton 
                      size="small" 
                      onClick={() => handleProjectView(project)}
                    >
                      <Visibility />
                    </IconButton>
                    <IconButton size="small">
                      <Edit />
                    </IconButton>
                    <IconButton size="small">
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* 创建项目对话框 */}
      <Dialog open={createProjectOpen} onClose={() => setCreateProjectOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>创建新项目</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="项目名称"
                variant="outlined"
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>优先级</InputLabel>
                <Select label="优先级" defaultValue="medium">
                  <MenuItem value="high">高</MenuItem>
                  <MenuItem value="medium">中</MenuItem>
                  <MenuItem value="low">低</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="项目描述"
                variant="outlined"
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="开始日期"
                type="date"
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="截止日期"
                type="date"
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>分配Agents</InputLabel>
                <Select label="分配Agents" multiple value={[]}>
                  <MenuItem value="PM-Agent">PM-Agent</MenuItem>
                  <MenuItem value="Architect-Agent">Architect-Agent</MenuItem>
                  <MenuItem value="Developer-Agent">Developer-Agent</MenuItem>
                  <MenuItem value="QA-Agent">QA-Agent</MenuItem>
                  <MenuItem value="Manager-Agent">Manager-Agent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateProjectOpen(false)}>取消</Button>
          <Button variant="contained">创建项目</Button>
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
                  <Typography variant="h6" sx={{ mb: 2 }}>项目详情</Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    {selectedProject.description}
                  </Typography>
                  
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                    技术栈
                  </Typography>
                  <Box sx={{ mb: 3 }}>
                    {selectedProject.techStack.map((tech: string, index: number) => (
                      <Chip key={index} label={tech} size="small" sx={{ mr: 1, mb: 1 }} />
                    ))}
                  </Box>

                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                    分配的Agents
                  </Typography>
                  <List dense>
                    {selectedProject.assignedAgents.map((agent: string, index: number) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          {getAgentIcon(agent)}
                        </ListItemIcon>
                        <ListItemText primary={agent} />
                      </ListItem>
                    ))}
                  </List>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Typography variant="h6" sx={{ mb: 2 }}>项目指标</Typography>
                  
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                      整体进度
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {selectedProject.progress}%
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={selectedProject.progress} 
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                      任务完成情况
                    </Typography>
                    <Typography variant="h6">
                      {selectedProject.completedTasks} / {selectedProject.totalTasks}
                    </Typography>
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                      预算使用
                    </Typography>
                    <Typography variant="h6">
                      ¥{selectedProject.spent.toLocaleString()} / ¥{selectedProject.budget.toLocaleString()}
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={(selectedProject.spent / selectedProject.budget) * 100} 
                      sx={{ height: 6, borderRadius: 3, mt: 1 }}
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      项目周期
                    </Typography>
                    <Typography variant="body1">
                      {selectedProject.startDate} 至 {selectedProject.endDate}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      团队规模
                    </Typography>
                    <Typography variant="body1">
                      {selectedProject.teamSize} 人
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setProjectDetailsOpen(false)}>关闭</Button>
              <Button variant="outlined">编辑项目</Button>
              <Button variant="contained">管理任务</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  )
}

export default ProjectManagement