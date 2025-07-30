import React, { useState } from 'react'
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Chip,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  Divider,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Badge,
} from '@mui/material'
import {
  Message,
  Send,
  Group,
  TrendingUp,
  Schedule,
  Handshake,
  Person,
  Architecture,
  Code,
  BugReport,
  SmartToy,
  Circle,
  Notifications,
} from '@mui/icons-material'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts'

const TeamCollaboration: React.FC = () => {
  const [messageDialogOpen, setMessageDialogOpen] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)

  const agents = [
    {
      id: 'pm-001',
      name: 'PM-Agent',
      role: '产品经理',
      status: 'active',
      icon: <Person />,
      color: '#1976d2',
      currentTask: '需求分析',
      lastMessage: '已完成用户故事梳理',
      lastActive: '刚刚',
      collaborations: 12,
    },
    {
      id: 'arch-001',
      name: 'Architect-Agent',
      role: '系统架构师',
      status: 'active',
      icon: <Architecture />,
      color: '#4caf50',
      currentTask: '架构设计',
      lastMessage: '数据库设计方案已完成',
      lastActive: '2分钟前',
      collaborations: 8,
    },
    {
      id: 'dev-001',
      name: 'Developer-Agent',
      role: '开发工程师',
      status: 'busy',
      icon: <Code />,
      color: '#ff9800',
      currentTask: '代码开发',
      lastMessage: '用户认证模块开发中',
      lastActive: '5分钟前',
      collaborations: 15,
    },
    {
      id: 'qa-001',
      name: 'QA-Agent',
      role: '质量保证',
      status: 'active',
      icon: <BugReport />,
      color: '#9c27b0',
      currentTask: '测试执行',
      lastMessage: '自动化测试套件运行完毕',
      lastActive: '1分钟前',
      collaborations: 9,
    },
    {
      id: 'mgr-001',
      name: 'Manager-Agent',
      role: '项目管理',
      status: 'active',
      icon: <SmartToy />,
      color: '#f44336',
      currentTask: '团队协调',
      lastMessage: 'Sprint规划已更新',
      lastActive: '3分钟前',
      collaborations: 20,
    },
  ]

  const collaborationMetrics = {
    totalInteractions: 247,
    activeCollaborations: 12,
    avgResponseTime: '2.3分钟',
    successfulHandoffs: 89,
  }

  const recentActivities = [
    {
      id: 1,
      type: 'message',
      agent: 'Developer-Agent',
      target: 'QA-Agent',
      content: '用户认证模块已完成，请进行测试',
      timestamp: '2分钟前',
      status: 'sent',
    },
    {
      id: 2,
      type: 'handoff',
      agent: 'PM-Agent',
      target: 'Architect-Agent',
      content: '需求分析完成，请开始架构设计',
      timestamp: '15分钟前',
      status: 'completed',
    },
    {
      id: 3,
      type: 'collaboration',
      agent: 'Architect-Agent',
      target: 'Developer-Agent',
      content: '数据库设计评审',
      timestamp: '30分钟前',
      status: 'in_progress',
    },
    {
      id: 4,
      type: 'message',
      agent: 'QA-Agent',
      target: 'Manager-Agent',
      content: '测试覆盖率达到85%',
      timestamp: '45分钟前',
      status: 'acknowledged',
    },
    {
      id: 5,
      type: 'alert',
      agent: 'Manager-Agent',
      target: 'ALL',
      content: 'Sprint Review会议提醒',
      timestamp: '1小时前',
      status: 'broadcast',
    },
  ]

  const collaborationTrend = [
    { hour: '09:00', interactions: 5, handoffs: 2 },
    { hour: '10:00', interactions: 8, handoffs: 3 },
    { hour: '11:00', interactions: 12, handoffs: 4 },
    { hour: '12:00', interactions: 6, handoffs: 1 },
    { hour: '13:00', interactions: 4, handoffs: 1 },
    { hour: '14:00', interactions: 15, handoffs: 5 },
    { hour: '15:00', interactions: 18, handoffs: 6 },
    { hour: '16:00', interactions: 12, handoffs: 3 },
  ]

  const agentConnections = [
    { from: 'PM-Agent', to: 'Architect-Agent', weight: 8 },
    { from: 'Architect-Agent', to: 'Developer-Agent', weight: 12 },
    { from: 'Developer-Agent', to: 'QA-Agent', weight: 15 },
    { from: 'QA-Agent', to: 'Manager-Agent', weight: 6 },
    { from: 'Manager-Agent', to: 'PM-Agent', weight: 10 },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#4caf50'
      case 'busy': return '#ff9800'
      case 'idle': return '#2196f3'
      default: return '#9e9e9e'
    }
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'message': return <Message />
      case 'handoff': return <Handshake />
      case 'collaboration': return <Group />
      case 'alert': return <Notifications />
      default: return <Circle />
    }
  }

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'message': return '#1976d2'
      case 'handoff': return '#4caf50'
      case 'collaboration': return '#ff9800'
      case 'alert': return '#f44336'
      default: return '#9e9e9e'
    }
  }

  const handleSendMessage = (targetAgent: string) => {
    setSelectedAgent(targetAgent)
    setMessageDialogOpen(true)
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
        团队协作中心
      </Typography>

      {/* 协作指标 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Group sx={{ color: '#1976d2', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#1976d2' }}>
                  总交互数
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {collaborationMetrics.totalInteractions}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Handshake sx={{ color: '#4caf50', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#4caf50' }}>
                  活跃协作
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {collaborationMetrics.activeCollaborations}
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
                  响应时间
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {collaborationMetrics.avgResponseTime}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp sx={{ color: '#9c27b0', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#9c27b0' }}>
                  成功交接
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {collaborationMetrics.successfulHandoffs}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Agent状态面板 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 'fit-content' }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              Agent状态
            </Typography>
            <List>
              {agents.map((agent, index) => (
                <React.Fragment key={agent.id}>
                  <ListItem 
                    sx={{ 
                      px: 0,
                      cursor: 'pointer',
                      '&:hover': { bgcolor: 'action.hover' },
                      borderRadius: 1,
                    }}
                    onClick={() => handleSendMessage(agent.name)}
                  >
                    <ListItemAvatar>
                      <Badge
                        overlap="circular"
                        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                        badgeContent={
                          <Circle 
                            sx={{ 
                              fontSize: 12, 
                              color: getStatusColor(agent.status),
                            }} 
                          />
                        }
                      >
                        <Avatar sx={{ bgcolor: agent.color }}>
                          {agent.icon}
                        </Avatar>
                      </Badge>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                            {agent.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {agent.lastActive}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {agent.currentTask}
                          </Typography>
                          <Typography variant="caption" sx={{ fontStyle: 'italic' }}>
                            "{agent.lastMessage}"
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < agents.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* 协作趋势图 */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              今日协作趋势
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={collaborationTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Area 
                  type="monotone" 
                  dataKey="interactions" 
                  stackId="1" 
                  stroke="#1976d2" 
                  fill="#1976d2" 
                  name="交互次数"
                />
                <Area 
                  type="monotone" 
                  dataKey="handoffs" 
                  stackId="1" 
                  stroke="#4caf50" 
                  fill="#4caf50" 
                  name="任务交接"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* 最近活动时间轴 */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              最近协作活动
            </Typography>
            <Timeline>
              {recentActivities.map((activity, index) => (
                <TimelineItem key={activity.id}>
                  <TimelineSeparator>
                    <TimelineDot sx={{ bgcolor: getActivityColor(activity.type) }}>
                      {getActivityIcon(activity.type)}
                    </TimelineDot>
                    {index < recentActivities.length - 1 && <TimelineConnector />}
                  </TimelineSeparator>
                  <TimelineContent>
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Chip 
                          label={activity.agent} 
                          size="small" 
                          sx={{ mr: 1 }}
                        />
                        {activity.target !== 'ALL' && (
                          <>
                            <Typography variant="body2" sx={{ mx: 1 }}>→</Typography>
                            <Chip 
                              label={activity.target} 
                              size="small" 
                              variant="outlined"
                            />
                          </>
                        )}
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                          {activity.timestamp}
                        </Typography>
                      </Box>
                      <Typography variant="body2">
                        {activity.content}
                      </Typography>
                    </Box>
                  </TimelineContent>
                </TimelineItem>
              ))}
            </Timeline>
          </Paper>
        </Grid>

        {/* Agent连接强度 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              Agent协作强度
            </Typography>
            <List>
              {agentConnections.map((connection, index) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body2" sx={{ flex: 1 }}>
                          {connection.from}
                        </Typography>
                        <Typography variant="body2" sx={{ mx: 1 }}>
                          ↔
                        </Typography>
                        <Typography variant="body2" sx={{ flex: 1 }}>
                          {connection.to}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          协作次数: {connection.weight}
                        </Typography>
                        <Box
                          sx={{
                            width: '100%',
                            height: 4,
                            bgcolor: 'grey.300',
                            borderRadius: 2,
                            mt: 0.5,
                          }}
                        >
                          <Box
                            sx={{
                              width: `${(connection.weight / 20) * 100}%`,
                              height: '100%',
                              bgcolor: '#1976d2',
                              borderRadius: 2,
                            }}
                          />
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* 发送消息对话框 */}
      <Dialog open={messageDialogOpen} onClose={() => setMessageDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          发送消息给 {selectedAgent}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="消息内容"
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            placeholder="输入要发送的消息..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMessageDialogOpen(false)}>取消</Button>
          <Button 
            variant="contained" 
            startIcon={<Send />}
            onClick={() => {
              setMessageDialogOpen(false)
              // 这里可以添加发送消息的逻辑
            }}
          >
            发送
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default TeamCollaboration