import React, { useState } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
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
  Tabs,
  Tab,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
} from '@mui/material'
import {
  Assignment,
  TrendingUp,
  Schedule,
  CheckCircle,
  PlayArrow,
  Pause,
  Visibility,
  Add,
  Person,
  Architecture,
  Code,
  BugReport,
  SmartToy,
} from '@mui/icons-material'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts'

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
      id={`task-tabpanel-${index}`}
      aria-labelledby={`task-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const TaskAnalysis: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const [taskDetailsOpen, setTaskDetailsOpen] = useState(false)
  const [selectedTask, setSelectedTask] = useState<any>(null)
  const [createTaskOpen, setCreateTaskOpen] = useState(false)

  const taskStats = {
    totalTasks: 156,
    activeTasks: 23,
    completedTasks: 133,
    averageTime: '4.2小时',
  }

  const tasks = [
    {
      id: 'task-001',
      title: '用户认证系统开发',
      description: '实现基于JWT的用户认证和授权系统',
      status: 'in_progress',
      priority: 'high',
      assignedAgent: 'Developer-Agent',
      project: '电商平台重构',
      estimatedTime: '8小时',
      actualTime: '6小时',
      progress: 75,
      createdAt: '2025-01-28',
      dueDate: '2025-01-30',
      tags: ['认证', '安全', 'JWT'],
    },
    {
      id: 'task-002',
      title: '数据库架构设计',
      description: '设计电商平台的数据库表结构和关系',
      status: 'completed',
      priority: 'high',
      assignedAgent: 'Architect-Agent',
      project: '电商平台重构',
      estimatedTime: '12小时',
      actualTime: '10小时',
      progress: 100,
      createdAt: '2025-01-25',
      dueDate: '2025-01-27',
      tags: ['数据库', '架构', 'PostgreSQL'],
    },
    {
      id: 'task-003',
      title: '用户故事梳理',
      description: '梳理和完善用户购物流程的用户故事',
      status: 'pending',
      priority: 'medium',
      assignedAgent: 'PM-Agent',
      project: '电商平台重构',
      estimatedTime: '4小时',
      actualTime: '0小时',
      progress: 0,
      createdAt: '2025-01-29',
      dueDate: '2025-02-01',
      tags: ['需求', '用户故事', 'UX'],
    },
    {
      id: 'task-004',
      title: 'API接口测试',
      description: '对已开发的API接口进行自动化测试',
      status: 'in_progress',
      priority: 'medium',
      assignedAgent: 'QA-Agent',
      project: '电商平台重构',
      estimatedTime: '6小时',
      actualTime: '3小时',
      progress: 50,
      createdAt: '2025-01-28',
      dueDate: '2025-01-31',
      tags: ['测试', 'API', '自动化'],
    },
    {
      id: 'task-005',
      title: 'Sprint计划制定',
      description: '制定下个Sprint的开发计划和任务分配',
      status: 'completed',
      priority: 'high',
      assignedAgent: 'Manager-Agent',
      project: '电商平台重构',
      estimatedTime: '3小时',
      actualTime: '2.5小时',
      progress: 100,
      createdAt: '2025-01-26',
      dueDate: '2025-01-28',
      tags: ['计划', 'Sprint', '管理'],
    },
  ]

  const tasksByAgent = [
    { agent: 'Developer-Agent', tasks: 45, completed: 38, success: 84 },
    { agent: 'PM-Agent', tasks: 32, completed: 28, success: 88 },
    { agent: 'Architect-Agent', tasks: 28, completed: 25, success: 89 },
    { agent: 'QA-Agent', tasks: 35, completed: 31, success: 89 },
    { agent: 'Manager-Agent', tasks: 16, completed: 11, success: 69 },
  ]

  const taskPriorityDistribution = [
    { name: '高优先级', value: 35, color: '#f44336' },
    { name: '中优先级', value: 45, color: '#ff9800' },
    { name: '低优先级', value: 20, color: '#4caf50' },
  ]

  const dailyTaskTrend = [
    { day: '周一', created: 8, completed: 12 },
    { day: '周二', created: 6, completed: 9 },
    { day: '周三', created: 12, completed: 15 },
    { day: '周四', created: 9, completed: 11 },
    { day: '周五', created: 15, completed: 18 },
    { day: '周六', created: 3, completed: 5 },
    { day: '周日', created: 2, completed: 3 },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#4caf50'
      case 'in_progress': return '#ff9800'
      case 'pending': return '#2196f3'
      case 'cancelled': return '#f44336'
      default: return '#9e9e9e'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return '已完成'
      case 'in_progress': return '进行中'
      case 'pending': return '待开始'
      case 'cancelled': return '已取消'
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
      case 'PM-Agent': return <Person />
      case 'Architect-Agent': return <Architecture />
      case 'Developer-Agent': return <Code />
      case 'QA-Agent': return <BugReport />
      case 'Manager-Agent': return <SmartToy />
      default: return <Assignment />
    }
  }

  const getAgentColor = (agentName: string) => {
    switch (agentName) {
      case 'PM-Agent': return '#1976d2'
      case 'Architect-Agent': return '#4caf50'
      case 'Developer-Agent': return '#ff9800'
      case 'QA-Agent': return '#9c27b0'
      case 'Manager-Agent': return '#f44336'
      default: return '#9e9e9e'
    }
  }

  const handleTaskView = (task: any) => {
    setSelectedTask(task)
    setTaskDetailsOpen(true)
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          任务分析
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateTaskOpen(true)}
        >
          创建任务
        </Button>
      </Box>

      {/* 任务统计卡片 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Assignment sx={{ color: '#1976d2', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#1976d2' }}>
                  总任务数
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {taskStats.totalTasks}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <PlayArrow sx={{ color: '#ff9800', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#ff9800' }}>
                  进行中
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {taskStats.activeTasks}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircle sx={{ color: '#4caf50', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#4caf50' }}>
                  已完成
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {taskStats.completedTasks}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Schedule sx={{ color: '#9c27b0', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#9c27b0' }}>
                  平均耗时
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {taskStats.averageTime}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 任务分析图表 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              Agent任务执行统计
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={tasksByAgent}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="agent" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="tasks" fill="#1976d2" name="总任务" />
                <Bar dataKey="completed" fill="#4caf50" name="已完成" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              任务优先级分布
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={taskPriorityDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {taskPriorityDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* 任务趋势 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 3 }}>
          每日任务创建和完成趋势
        </Typography>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={dailyTaskTrend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="created" 
              stroke="#1976d2" 
              strokeWidth={3}
              name="创建任务"
            />
            <Line 
              type="monotone" 
              dataKey="completed" 
              stroke="#4caf50" 
              strokeWidth={3}
              name="完成任务"
            />
          </LineChart>
        </ResponsiveContainer>
      </Paper>

      {/* 任务列表标签页 */}
      <Paper sx={{ p: 0 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="所有任务" />
            <Tab label="进行中" />
            <Tab label="已完成" />
            <Tab label="待开始" />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>任务</TableCell>
                  <TableCell>状态</TableCell>
                  <TableCell>优先级</TableCell>
                  <TableCell>负责Agent</TableCell>
                  <TableCell>项目</TableCell>
                  <TableCell>截止日期</TableCell>
                  <TableCell>操作</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tasks.map((task) => (
                  <TableRow key={task.id} hover>
                    <TableCell>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          {task.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {task.description}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusText(task.status)}
                        size="small"
                        sx={{
                          bgcolor: getStatusColor(task.status),
                          color: 'white',
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getPriorityText(task.priority)}
                        size="small"
                        variant="outlined"
                        sx={{
                          borderColor: getPriorityColor(task.priority),
                          color: getPriorityColor(task.priority),
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Avatar
                          sx={{
                            bgcolor: getAgentColor(task.assignedAgent),
                            width: 32,
                            height: 32,
                            mr: 1,
                          }}
                        >
                          {getAgentIcon(task.assignedAgent)}
                        </Avatar>
                        <Typography variant="body2">
                          {task.assignedAgent}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{task.project}</TableCell>
                    <TableCell>{task.dueDate}</TableCell>
                    <TableCell>
                      <IconButton 
                        size="small"
                        onClick={() => handleTaskView(task)}
                      >
                        <Visibility />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <List>
            {tasks.filter(task => task.status === 'in_progress').map((task) => (
              <ListItem key={task.id}>
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: getAgentColor(task.assignedAgent) }}>
                    {getAgentIcon(task.assignedAgent)}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={task.title}
                  secondary={`${task.assignedAgent} | ${task.project}`}
                />
              </ListItem>
            ))}
          </List>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <List>
            {tasks.filter(task => task.status === 'completed').map((task) => (
              <ListItem key={task.id}>
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: getAgentColor(task.assignedAgent) }}>
                    {getAgentIcon(task.assignedAgent)}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={task.title}
                  secondary={`${task.assignedAgent} | 耗时: ${task.actualTime}`}
                />
              </ListItem>
            ))}
          </List>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <List>
            {tasks.filter(task => task.status === 'pending').map((task) => (
              <ListItem key={task.id}>
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: getAgentColor(task.assignedAgent) }}>
                    {getAgentIcon(task.assignedAgent)}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={task.title}
                  secondary={`${task.assignedAgent} | 预计: ${task.estimatedTime}`}
                />
              </ListItem>
            ))}
          </List>
        </TabPanel>
      </Paper>

      {/* 任务详情对话框 */}
      <Dialog open={taskDetailsOpen} onClose={() => setTaskDetailsOpen(false)} maxWidth="md" fullWidth>
        {selectedTask && (
          <>
            <DialogTitle>{selectedTask.title}</DialogTitle>
            <DialogContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    {selectedTask.description}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">状态</Typography>
                  <Chip
                    label={getStatusText(selectedTask.status)}
                    sx={{ bgcolor: getStatusColor(selectedTask.status), color: 'white' }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">优先级</Typography>
                  <Chip
                    label={getPriorityText(selectedTask.priority)}
                    variant="outlined"
                    sx={{ borderColor: getPriorityColor(selectedTask.priority), color: getPriorityColor(selectedTask.priority) }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">负责Agent</Typography>
                  <Typography variant="body1">{selectedTask.assignedAgent}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">所属项目</Typography>
                  <Typography variant="body1">{selectedTask.project}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">预计耗时</Typography>
                  <Typography variant="body1">{selectedTask.estimatedTime}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">实际耗时</Typography>
                  <Typography variant="body1">{selectedTask.actualTime}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">标签</Typography>
                  <Box sx={{ mt: 1 }}>
                    {selectedTask.tags.map((tag: string, index: number) => (
                      <Chip key={index} label={tag} size="small" sx={{ mr: 1, mb: 1 }} />
                    ))}
                  </Box>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setTaskDetailsOpen(false)}>关闭</Button>
              <Button variant="outlined">编辑任务</Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* 创建任务对话框 */}
      <Dialog open={createTaskOpen} onClose={() => setCreateTaskOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>创建新任务</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField fullWidth label="任务标题" variant="outlined" required />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="任务描述"
                variant="outlined"
                multiline
                rows={3}
                required
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>优先级</InputLabel>
                <Select label="优先级" defaultValue="medium">
                  <MenuItem value="high">高</MenuItem>
                  <MenuItem value="medium">中</MenuItem>
                  <MenuItem value="low">低</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>负责Agent</InputLabel>
                <Select label="负责Agent">
                  <MenuItem value="PM-Agent">PM-Agent</MenuItem>
                  <MenuItem value="Architect-Agent">Architect-Agent</MenuItem>
                  <MenuItem value="Developer-Agent">Developer-Agent</MenuItem>
                  <MenuItem value="QA-Agent">QA-Agent</MenuItem>
                  <MenuItem value="Manager-Agent">Manager-Agent</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="预计耗时"
                variant="outlined"
                placeholder="例如: 4小时"
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="截止日期"
                type="date"
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateTaskOpen(false)}>取消</Button>
          <Button variant="contained">创建任务</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default TaskAnalysis