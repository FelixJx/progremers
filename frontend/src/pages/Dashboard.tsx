import React from 'react'
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
} from '@mui/material'
import {
  TrendingUp,
  Assignment,
  Group,
  Code,
  CheckCircle,
  Warning,
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

const Dashboard: React.FC = () => {
  // 模拟数据
  const systemStats = {
    totalProjects: 3,
    activeAgents: 5,
    completedTasks: 247,
    successRate: 85.2,
  }

  const agentPerformance = [
    { name: 'PM-Agent', tasks: 45, success: 92 },
    { name: 'Architect', tasks: 38, success: 88 },
    { name: 'Developer', tasks: 67, success: 85 },
    { name: 'QA-Agent', tasks: 52, success: 90 },
    { name: 'Manager', tasks: 45, success: 87 },
  ]

  const projectDistribution = [
    { name: 'Web应用', value: 40, color: '#8884d8' },
    { name: 'API服务', value: 30, color: '#82ca9d' },
    { name: '数据处理', value: 20, color: '#ffc658' },
    { name: '其他', value: 10, color: '#ff7300' },
  ]

  const weeklyTrend = [
    { day: '周一', tasks: 24 },
    { day: '周二', tasks: 13 },
    { day: '周三', tasks: 35 },
    { day: '周四', tasks: 28 },
    { day: '周五', tasks: 42 },
    { day: '周六', tasks: 18 },
    { day: '周日', tasks: 12 },
  ]

  const recentActivities = [
    {
      agent: 'Developer-Agent',
      action: '完成用户认证模块开发',
      time: '2分钟前',
      status: 'success',
    },
    {
      agent: 'QA-Agent',
      action: '执行自动化测试套件',
      time: '5分钟前',
      status: 'success',
    },
    {
      agent: 'PM-Agent',
      action: '创建新用户故事',
      time: '8分钟前',
      status: 'info',
    },
    {
      agent: 'Architect-Agent',
      action: '更新系统架构文档',
      time: '12分钟前',
      status: 'success',
    },
    {
      agent: 'Manager-Agent',
      action: '协调团队日常站会',
      time: '15分钟前',
      status: 'warning',
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return '#4caf50'
      case 'warning': return '#ff9800'
      case 'error': return '#f44336'
      default: return '#2196f3'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle sx={{ color: '#4caf50' }} />
      case 'warning': return <Warning sx={{ color: '#ff9800' }} />
      default: return <SmartToy sx={{ color: '#2196f3' }} />
    }
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        仪表板
      </Typography>
      
      {/* 统计卡片 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ backgroundColor: '#e3f2fd' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Assignment sx={{ color: '#1976d2', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#1976d2' }}>
                  活跃项目
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {systemStats.totalProjects}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                +1 本周新增
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ backgroundColor: '#e8f5e8' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Group sx={{ color: '#4caf50', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#4caf50' }}>
                  在线Agents
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {systemStats.activeAgents}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                全部在线运行
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ backgroundColor: '#fff3e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Code sx={{ color: '#ff9800', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#ff9800' }}>
                  完成任务
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {systemStats.completedTasks}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                +23 今日新增
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ backgroundColor: '#f3e5f5' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp sx={{ color: '#9c27b0', mr: 1 }} />
                <Typography variant="h6" sx={{ color: '#9c27b0' }}>
                  成功率
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {systemStats.successRate}%
              </Typography>
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={systemStats.successRate} 
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Agent性能图表 */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              Agent任务执行性能
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={agentPerformance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="tasks" fill="#1976d2" name="任务数量" />
                <Bar dataKey="success" fill="#4caf50" name="成功率%" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* 项目类型分布 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              项目类型分布
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={projectDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {projectDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* 周任务趋势 */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              本周任务完成趋势
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={weeklyTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="tasks" 
                  stroke="#1976d2" 
                  strokeWidth={3}
                  dot={{ fill: '#1976d2', strokeWidth: 2, r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* 最近活动 */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              最近活动
            </Typography>
            <List>
              {recentActivities.map((activity, index) => (
                <React.Fragment key={index}>
                  <ListItem sx={{ px: 0 }}>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'transparent' }}>
                        {getStatusIcon(activity.status)}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box>
                          <Chip 
                            label={activity.agent} 
                            size="small" 
                            sx={{ mb: 0.5 }}
                          />
                          <Typography variant="body2">
                            {activity.action}
                          </Typography>
                        </Box>
                      }
                      secondary={activity.time}
                    />
                  </ListItem>
                  {index < recentActivities.length - 1 && <Divider variant="inset" />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard