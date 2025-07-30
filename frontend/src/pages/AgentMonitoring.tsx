import React, { useState } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Switch,
  FormControlLabel,
} from '@mui/material'
import {
  SmartToy,
  Person,
  Architecture,
  Code,
  BugReport,
  Settings,
  PlayArrow,
  Pause,
  Refresh,
  MoreVert,
  Circle,
} from '@mui/icons-material'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts'

const AgentMonitoring: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [agentDetailsOpen, setAgentDetailsOpen] = useState(false)

  const agents = [
    {
      id: 'pm-001',
      name: 'PM-Agent',
      role: '产品经理',
      status: 'active',
      llm: 'DeepSeek',
      icon: <Person />,
      color: '#1976d2',
      currentTask: '需求分析 - 用户认证系统',
      performance: 92,
      tasksCompleted: 156,
      averageTime: '2.3分钟',
      lastActive: '刚刚',
      capabilities: ['需求分析', '用户故事创建', 'PRD撰写'],
      memoryUsage: 45,
      cpuUsage: 23,
    },
    {
      id: 'arch-001',
      name: 'Architect-Agent',
      role: '系统架构师',
      status: 'active',
      llm: 'Qwen-Max',
      icon: <Architecture />,
      color: '#4caf50',
      currentTask: '架构设计 - 微服务拆分',
      performance: 88,
      tasksCompleted: 89,
      averageTime: '5.7分钟',
      lastActive: '2分钟前',
      capabilities: ['系统设计', '技术选型', '架构文档'],
      memoryUsage: 62,
      cpuUsage: 34,
    },
    {
      id: 'dev-001',
      name: 'Developer-Agent',
      role: '开发工程师',
      status: 'active',
      llm: 'DeepSeek + Local',
      icon: <Code />,
      color: '#ff9800',
      currentTask: '代码开发 - API接口实现',
      performance: 85,
      tasksCompleted: 234,
      averageTime: '8.1分钟',
      lastActive: '30秒前',
      capabilities: ['代码编写', 'MCP操作', '单元测试'],
      memoryUsage: 78,
      cpuUsage: 56,
    },
    {
      id: 'qa-001',
      name: 'QA-Agent',
      role: '质量保证',
      status: 'active',
      llm: 'Qwen-72B',
      icon: <BugReport />,
      color: '#9c27b0',
      currentTask: '测试执行 - 自动化测试套件',
      performance: 90,
      tasksCompleted: 178,
      averageTime: '4.2分钟',
      lastActive: '1分钟前',
      capabilities: ['测试设计', 'UI测试', '性能测试'],
      memoryUsage: 55,
      cpuUsage: 41,
    },
    {
      id: 'mgr-001',
      name: 'Manager-Agent',
      role: '项目管理',
      status: 'active',
      llm: 'DeepSeek',
      icon: <SmartToy />,
      color: '#f44336',
      currentTask: '团队协调 - Sprint规划',
      performance: 87,
      tasksCompleted: 203,
      averageTime: '3.5分钟',
      lastActive: '45秒前',
      capabilities: ['任务分配', '质量验证', '团队协调'],
      memoryUsage: 38,
      cpuUsage: 28,
    },
  ]

  // 性能趋势数据
  const performanceTrend = [
    { time: '09:00', pm: 90, arch: 85, dev: 82, qa: 88, mgr: 86 },
    { time: '10:00', pm: 92, arch: 87, dev: 84, qa: 89, mgr: 88 },
    { time: '11:00', pm: 88, arch: 89, dev: 86, qa: 91, mgr: 85 },
    { time: '12:00', pm: 94, arch: 88, dev: 85, qa: 90, mgr: 87 },
    { time: '13:00', pm: 91, arch: 90, dev: 87, qa: 92, mgr: 89 },
    { time: '14:00', pm: 93, arch: 88, dev: 89, qa: 88, mgr: 88 },
    { time: '15:00', pm: 92, arch: 88, dev: 85, qa: 90, mgr: 87 },
  ]

  const resourceUsage = [
    { time: '09:00', memory: 42, cpu: 25 },
    { time: '10:00', memory: 45, cpu: 28 },
    { time: '11:00', memory: 48, cpu: 32 },
    { time: '12:00', memory: 52, cpu: 35 },
    { time: '13:00', memory: 49, cpu: 31 },
    { time: '14:00', memory: 51, cpu: 33 },
    { time: '15:00', memory: 47, cpu: 29 },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#4caf50'
      case 'busy': return '#ff9800'
      case 'idle': return '#2196f3'
      case 'error': return '#f44336'
      default: return '#9e9e9e'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '活跃'
      case 'busy': return '繁忙'
      case 'idle': return '空闲'
      case 'error': return '错误'
      default: return '未知'
    }
  }

  const handleAgentClick = (agentId: string) => {
    setSelectedAgent(agentId)
    setAgentDetailsOpen(true)
  }

  const selectedAgentData = agents.find(agent => agent.id === selectedAgent)

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Agent监控中心
        </Typography>
        <Box>
          <IconButton>
            <Refresh />
          </IconButton>
          <IconButton>
            <Settings />
          </IconButton>
        </Box>
      </Box>

      {/* Agent状态卡片 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {agents.map((agent) => (
          <Grid item xs={12} sm={6} md={4} lg={2.4} key={agent.id}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: 4,
                }
              }}
              onClick={() => handleAgentClick(agent.id)}
            >
              <CardContent sx={{ textAlign: 'center', pb: '16px !important' }}>
                <Box sx={{ position: 'relative', mb: 2 }}>
                  <Avatar
                    sx={{
                      bgcolor: agent.color,
                      width: 56,
                      height: 56,
                      mx: 'auto',
                      mb: 1,
                    }}
                  >
                    {agent.icon}
                  </Avatar>
                  <Circle
                    sx={{
                      position: 'absolute',
                      top: 0,
                      right: 'calc(50% - 35px)',
                      fontSize: 16,
                      color: getStatusColor(agent.status),
                    }}
                  />
                </Box>
                
                <Typography variant="h6" sx={{ mb: 0.5 }}>
                  {agent.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {agent.role}
                </Typography>
                
                <Chip
                  label={getStatusText(agent.status)}
                  size="small"
                  sx={{
                    bgcolor: getStatusColor(agent.status),
                    color: 'white',
                    fontWeight: 'bold',
                    mb: 1,
                  }}
                />
                
                <Typography variant="body2" sx={{ mb: 1 }}>
                  性能: {agent.performance}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={agent.performance}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: agent.color,
                    },
                  }}
                />
                
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  {agent.lastActive}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* 性能趋势图 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              Agent性能趋势
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={[70, 100]} />
                <RechartsTooltip />
                <Line type="monotone" dataKey="pm" stroke="#1976d2" name="PM-Agent" strokeWidth={2} />
                <Line type="monotone" dataKey="arch" stroke="#4caf50" name="Architect" strokeWidth={2} />
                <Line type="monotone" dataKey="dev" stroke="#ff9800" name="Developer" strokeWidth={2} />
                <Line type="monotone" dataKey="qa" stroke="#9c27b0" name="QA-Agent" strokeWidth={2} />
                <Line type="monotone" dataKey="mgr" stroke="#f44336" name="Manager" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              系统资源使用
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={resourceUsage}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <RechartsTooltip />
                <Area type="monotone" dataKey="memory" stackId="1" stroke="#1976d2" fill="#1976d2" name="内存%" />
                <Area type="monotone" dataKey="cpu" stackId="1" stroke="#4caf50" fill="#4caf50" name="CPU%" />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Agent详细列表 */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 3 }}>
          Agent详细状态
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Agent</TableCell>
                <TableCell>状态</TableCell>
                <TableCell>当前任务</TableCell>
                <TableCell>LLM模型</TableCell>
                <TableCell>性能</TableCell>
                <TableCell>已完成任务</TableCell>
                <TableCell>平均耗时</TableCell>
                <TableCell>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {agents.map((agent) => (
                <TableRow key={agent.id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Avatar sx={{ bgcolor: agent.color, width: 32, height: 32, mr: 2 }}>
                        {agent.icon}
                      </Avatar>
                      <Box>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {agent.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {agent.role}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusText(agent.status)}
                      size="small"
                      sx={{
                        bgcolor: getStatusColor(agent.status),
                        color: 'white',
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {agent.currentTask}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={agent.llm} variant="outlined" size="small" />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="body2" sx={{ mr: 1 }}>
                        {agent.performance}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={agent.performance}
                        sx={{ width: 60, height: 4 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell>{agent.tasksCompleted}</TableCell>
                  <TableCell>{agent.averageTime}</TableCell>
                  <TableCell>
                    <Tooltip title="暂停">
                      <IconButton size="small">
                        <Pause />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="重启">
                      <IconButton size="small">
                        <Refresh />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="更多">
                      <IconButton size="small">
                        <MoreVert />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Agent详情对话框 */}
      <Dialog 
        open={agentDetailsOpen} 
        onClose={() => setAgentDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedAgentData && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: selectedAgentData.color, mr: 2 }}>
                  {selectedAgentData.icon}
                </Avatar>
                <Box>
                  <Typography variant="h6">{selectedAgentData.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedAgentData.role}
                  </Typography>
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                    基本信息
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText 
                        primary="状态" 
                        secondary={
                          <Chip 
                            label={getStatusText(selectedAgentData.status)} 
                            size="small"
                            sx={{ bgcolor: getStatusColor(selectedAgentData.status), color: 'white' }}
                          />
                        } 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="LLM模型" secondary={selectedAgentData.llm} />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="当前任务" secondary={selectedAgentData.currentTask} />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="最后活跃" secondary={selectedAgentData.lastActive} />
                    </ListItem>
                  </List>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                    性能指标
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText 
                        primary="整体性能" 
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                            <Typography variant="body2" sx={{ mr: 1 }}>
                              {selectedAgentData.performance}%
                            </Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={selectedAgentData.performance} 
                              sx={{ flexGrow: 1, height: 6 }}
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="内存使用" 
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                            <Typography variant="body2" sx={{ mr: 1 }}>
                              {selectedAgentData.memoryUsage}%
                            </Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={selectedAgentData.memoryUsage} 
                              sx={{ flexGrow: 1, height: 6 }}
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="CPU使用" 
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                            <Typography variant="body2" sx={{ mr: 1 }}>
                              {selectedAgentData.cpuUsage}%
                            </Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={selectedAgentData.cpuUsage} 
                              sx={{ flexGrow: 1, height: 6 }}
                            />
                          </Box>
                        }
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="已完成任务" secondary={`${selectedAgentData.tasksCompleted} 个`} />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="平均耗时" secondary={selectedAgentData.averageTime} />
                    </ListItem>
                  </List>
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                    核心能力
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {selectedAgentData.capabilities.map((capability, index) => (
                      <Chip 
                        key={index} 
                        label={capability} 
                        variant="outlined" 
                        size="small"
                      />
                    ))}
                  </Box>
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                    控制选项
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="自动任务分配"
                    />
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="性能监控"
                    />
                    <FormControlLabel
                      control={<Switch />}
                      label="调试模式"
                    />
                  </Box>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setAgentDetailsOpen(false)}>关闭</Button>
              <Button variant="outlined" startIcon={<Pause />}>
                暂停Agent
              </Button>
              <Button variant="contained" startIcon={<Refresh />}>
                重启Agent
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  )
}

export default AgentMonitoring