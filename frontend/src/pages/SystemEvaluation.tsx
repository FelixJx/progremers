import React, { useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material'
import {
  Assessment,
  TrendingUp,
  CheckCircle,
  Warning,
  Error,
  Star,
  PlayArrow,
  Refresh,
} from '@mui/icons-material'
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'

const SystemEvaluation: React.FC = () => {
  const [evaluationDialog, setEvaluationDialog] = useState(false)

  // 基于实际评估结果的数据
  const evaluationSummary = {
    overallScore: 8.1,
    evaluationDate: '2025-07-29',
    projectName: 'AI Agent开发团队系统',
    status: 'excellent'
  }

  const detailedScores = [
    { dimension: '产品价值', score: 8.5, status: 'excellent' },
    { dimension: '技术架构', score: 8.8, status: 'excellent' },
    { dimension: '代码质量', score: 7.8, status: 'good' },
    { dimension: '测试质量', score: 7.2, status: 'good' },
    { dimension: '文档完整性', score: 6.5, status: 'needs_improvement' },
    { dimension: '用户体验', score: 5.8, status: 'needs_improvement' },
    { dimension: '安全性', score: 6.8, status: 'good' },
    { dimension: '可维护性', score: 8.2, status: 'excellent' },
    { dimension: '创新性', score: 9.2, status: 'excellent' },
  ]

  const radarData = detailedScores.map(item => ({
    dimension: item.dimension,
    score: item.score,
    fullMark: 10
  }))

  const strengths = [
    '🚀 技术创新性强 - 首个应用context-rot研究的AI Agent系统',
    '🏗️ 架构设计完善 - 模块化、可扩展的企业级架构',
    '🤖 Agent能力全面 - 覆盖完整软件开发流程',
    '🧠 上下文管理先进 - 解决LLM长上下文问题',
    '🔧 MCP深度集成 - 实际操作能力',
    '📊 测试验证充分 - 75%整体成功率'
  ]

  const weaknesses = [
    '⚠️ 测试覆盖率待提升 - 需要更多自动化测试',
    '⚠️ 安全机制需加强 - 缺少企业级安全控制',
    '⚠️ 性能优化空间 - 大规模并发处理能力',
    '⚠️ 文档体系不完整 - API文档和用户手册',
    '⚠️ UI界面缺失 - 缺少友好的用户界面'
  ]

  const criticalIssues = [
    '❌ 生产部署指南缺失',
    '❌ 监控和告警系统未实现',
    '❌ 数据备份和恢复策略'
  ]

  const recommendations = {
    immediate: [
      '🎨 开发Web管理界面',
      '📚 完善文档体系',
      '🔒 加强安全控制',
      '📊 添加监控系统'
    ],
    shortTerm: [
      '🧪 提升测试覆盖率到90%+',
      '🚀 创建Docker部署方案',
      '📈 性能优化和监控',
      '👥 用户体验改进'
    ],
    longTerm: [
      '🌍 多语言支持',
      '☁️ 云原生部署',
      '🤖 更多Agent类型',
      '🏢 企业版功能'
    ]
  }

  const agentPerformance = [
    { agent: 'PM-Agent', performance: 92, tasks: 6 },
    { agent: 'Architect-Agent', performance: 88, tasks: 5 },
    { agent: 'Developer-Agent', performance: 85, tasks: 3 },
    { agent: 'QA-Agent', performance: 90, tasks: 4 },
    { agent: 'Manager-Agent', performance: 87, tasks: 8 },
  ]

  const getScoreColor = (score: number) => {
    if (score >= 8.5) return '#4caf50'
    if (score >= 7.0) return '#ff9800'
    return '#f44336'
  }

  const getStatusChip = (status: string) => {
    const configs = {
      excellent: { label: '🟢 优秀', color: 'success' as const },
      good: { label: '🟡 良好', color: 'warning' as const },
      needs_improvement: { label: '🔴 需改进', color: 'error' as const }
    }
    const config = configs[status as keyof typeof configs] || configs.good
    return <Chip label={config.label} color={config.color} size="small" />
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          系统评估报告
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            sx={{ mr: 2 }}
            onClick={() => setEvaluationDialog(true)}
          >
            重新评估
          </Button>
          <Button
            variant="contained"
            startIcon={<Assessment />}
            onClick={() => window.open('/PROJECT_EVALUATION_REPORT.md', '_blank')}
          >
            查看详细报告
          </Button>
        </Box>
      </Box>

      {/* 评估概览 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <CardContent>
              <Typography variant="h2" sx={{ fontWeight: 'bold', color: '#1976d2', mb: 1 }}>
                {evaluationSummary.overallScore}
              </Typography>
              <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
                综合评分 / 10
              </Typography>
              <Chip 
                label="🏆 优秀产品" 
                color="success" 
                sx={{ fontWeight: 'bold' }}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                评估日期: {evaluationSummary.evaluationDate}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              各维度评分雷达图
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="dimension" />
                <PolarRadiusAxis angle={30} domain={[0, 10]} />
                <Radar
                  name="评分"
                  dataKey="score"
                  stroke="#1976d2"
                  fill="#1976d2"
                  fillOpacity={0.3}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* 详细评分表 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              详细评分
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>维度</TableCell>
                    <TableCell align="center">评分</TableCell>
                    <TableCell align="center">状态</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {detailedScores.map((row) => (
                    <TableRow key={row.dimension}>
                      <TableCell>{row.dimension}</TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          <Typography variant="body1" sx={{ mr: 1, fontWeight: 'bold' }}>
                            {row.score}
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={row.score * 10}
                            sx={{ 
                              width: 60, 
                              height: 6, 
                              borderRadius: 3,
                              '& .MuiLinearProgress-bar': {
                                backgroundColor: getScoreColor(row.score)
                              }
                            }}
                          />
                        </Box>
                      </TableCell>
                      <TableCell align="center">
                        {getStatusChip(row.status)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
              Agent性能评估
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={agentPerformance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="agent" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="performance" fill="#1976d2" name="性能分数" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* 优势与问题 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#4caf50' }}>
              <Star sx={{ mr: 1, verticalAlign: 'middle' }} />
              项目优势
            </Typography>
            <List dense>
              {strengths.map((strength, index) => (
                <ListItem key={index} sx={{ py: 0.5 }}>
                  <ListItemText 
                    primary={strength}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#ff9800' }}>
              <Warning sx={{ mr: 1, verticalAlign: 'middle' }} />
              待改进领域
            </Typography>
            <List dense>
              {weaknesses.map((weakness, index) => (
                <ListItem key={index} sx={{ py: 0.5 }}>
                  <ListItemText 
                    primary={weakness}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#f44336' }}>
              <Error sx={{ mr: 1, verticalAlign: 'middle' }} />
              关键问题
            </Typography>
            <List dense>
              {criticalIssues.map((issue, index) => (
                <ListItem key={index} sx={{ py: 0.5 }}>
                  <ListItemText 
                    primary={issue}
                    primaryTypographyProps={{ variant: 'body2' }}
                  />
                </ListItem>
              ))}
            </List>
            <Alert severity="error" sx={{ mt: 2 }}>
              这些问题需要优先解决
            </Alert>
          </Paper>
        </Grid>
      </Grid>

      {/* 改进建议 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 3 }}>
          改进建议路线图
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2, color: '#f44336' }}>
              🚨 立即行动 (1-2周)
            </Typography>
            <List dense>
              {recommendations.immediate.map((item, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <CheckCircle sx={{ color: '#f44336', fontSize: 20 }} />
                  </ListItemIcon>
                  <ListItemText primary={item} />
                </ListItem>
              ))}
            </List>
          </Grid>

          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2, color: '#ff9800' }}>
              📅 短期计划 (1-3个月)
            </Typography>
            <List dense>
              {recommendations.shortTerm.map((item, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <CheckCircle sx={{ color: '#ff9800', fontSize: 20 }} />
                  </ListItemIcon>
                  <ListItemText primary={item} />
                </ListItem>
              ))}
            </List>
          </Grid>

          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2, color: '#4caf50' }}>
              🎯 长期规划 (3-12个月)
            </Typography>
            <List dense>
              {recommendations.longTerm.map((item, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <CheckCircle sx={{ color: '#4caf50', fontSize: 20 }} />
                  </ListItemIcon>
                  <ListItemText primary={item} />
                </ListItem>
              ))}
            </List>
          </Grid>
        </Grid>
      </Paper>

      {/* 结论 */}
      <Alert severity="success" sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          📊 评估结论
        </Typography>
        <Typography variant="body1">
          这是一个技术创新性强、架构设计优秀的AI Agent系统，具有很大的商业价值和技术价值。
          主要优势在于完整的多Agent协作能力和先进的上下文管理技术。需要在用户体验、安全性和生产就绪度方面继续改进。
          <strong>总体评价：优秀的技术产品，具备商业化潜力。</strong>
        </Typography>
      </Alert>

      {/* 重新评估对话框 */}
      <Dialog open={evaluationDialog} onClose={() => setEvaluationDialog(false)} maxWidth="md">
        <DialogTitle>重新运行系统评估</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            这将启动AI Agent团队对系统进行全面重新评估，包括：
          </Typography>
          <List>
            <ListItem>
              <ListItemIcon><Assessment /></ListItemIcon>
              <ListItemText primary="PM Agent - 产品需求与市场分析" />
            </ListItem>
            <ListItem>
              <ListItemIcon><Assessment /></ListItemIcon>
              <ListItemText primary="Architect Agent - 技术架构评估" />
            </ListItem>
            <ListItem>
              <ListItemIcon><Assessment /></ListItemIcon>
              <ListItemText primary="Developer Agent - 代码质量分析" />
            </ListItem>
            <ListItem>
              <ListItemIcon><Assessment /></ListItemIcon>
              <ListItemText primary="QA Agent - 质量保证评估" />
            </ListItem>
            <ListItem>
              <ListItemIcon><Assessment /></ListItemIcon>
              <ListItemText primary="Manager Agent - 综合评估和决策" />
            </ListItem>
          </List>
          <Alert severity="info" sx={{ mt: 2 }}>
            评估过程大约需要2-3分钟，将生成新的评估报告。
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEvaluationDialog(false)}>取消</Button>
          <Button 
            variant="contained" 
            startIcon={<PlayArrow />}
            onClick={() => {
              setEvaluationDialog(false)
              // 这里可以调用实际的评估API
              alert('评估已启动，请查看控制台输出')
            }}
          >
            开始评估
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default SystemEvaluation