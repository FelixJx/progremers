import React, { useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Grid,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Divider,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
} from '@mui/material'
import {
  Save,
  Refresh,
  Delete,
  Add,
  Edit,
  Visibility,
  VisibilityOff,
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
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const Settings: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const [showApiKey, setShowApiKey] = useState(false)
  const [apiKeyDialogOpen, setApiKeyDialogOpen] = useState(false)

  const systemSettings = {
    maxContextTokens: 8000,
    autoSave: true,
    debugMode: false,
    notificationsEnabled: true,
    darkMode: false,
    language: 'zh-CN',
    autoRefreshInterval: 30,
  }

  const llmConfigs = [
    {
      name: 'DeepSeek',
      endpoint: 'https://api.deepseek.com',
      apiKey: 'sk-************************************',
      model: 'deepseek-chat',
      enabled: true,
      agents: ['PM-Agent', 'Developer-Agent', 'Manager-Agent'],
    },
    {
      name: 'Qwen-Max',
      endpoint: 'https://dashscope.aliyuncs.com',
      apiKey: 'sk-************************************',
      model: 'qwen-max',
      enabled: true,
      agents: ['Architect-Agent'],
    },
    {
      name: 'Qwen-72B',
      endpoint: 'https://dashscope.aliyuncs.com',
      apiKey: 'sk-************************************',
      model: 'qwen-72b-chat',
      enabled: true,
      agents: ['QA-Agent'],
    },
    {
      name: 'Local LM Studio',
      endpoint: 'http://localhost:1234',
      apiKey: 'not-needed',
      model: 'local-model',
      enabled: false,
      agents: [],
    },
  ]

  const agentSettings = [
    {
      id: 'pm-001',
      name: 'PM-Agent',
      enabled: true,
      llm: 'DeepSeek',
      maxTasks: 10,
      priority: 'high',
      autoAssign: true,
    },
    {
      id: 'arch-001',
      name: 'Architect-Agent',
      enabled: true,
      llm: 'Qwen-Max',
      maxTasks: 8,
      priority: 'high',
      autoAssign: true,
    },
    {
      id: 'dev-001',
      name: 'Developer-Agent',
      enabled: true,
      llm: 'DeepSeek',
      maxTasks: 15,
      priority: 'medium',
      autoAssign: true,
    },
    {
      id: 'qa-001',
      name: 'QA-Agent',
      enabled: true,
      llm: 'Qwen-72B',
      maxTasks: 12,
      priority: 'medium',
      autoAssign: true,
    },
    {
      id: 'mgr-001',
      name: 'Manager-Agent',
      enabled: true,
      llm: 'DeepSeek',
      maxTasks: 20,
      priority: 'high',
      autoAssign: true,
    },
  ]

  const handleSaveSettings = () => {
    // 保存设置逻辑
    alert('设置已保存')
  }

  const handleResetSettings = () => {
    // 重置设置逻辑
    if (confirm('确定要重置所有设置吗？')) {
      alert('设置已重置')
    }
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
        系统设置
      </Typography>

      <Paper sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="系统配置" />
            <Tab label="LLM配置" />
            <Tab label="Agent设置" />
            <Tab label="安全设置" />
          </Tabs>
        </Box>

        {/* 系统配置 */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    基础设置
                  </Typography>
                  
                  <Box sx={{ mb: 3 }}>
                    <FormControl fullWidth>
                      <InputLabel>界面语言</InputLabel>
                      <Select value={systemSettings.language} label="界面语言">
                        <MenuItem value="zh-CN">简体中文</MenuItem>
                        <MenuItem value="en-US">English</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <TextField
                      fullWidth
                      label="最大上下文Token数"
                      type="number"
                      value={systemSettings.maxContextTokens}
                      InputProps={{ inputProps: { min: 1000, max: 32000 } }}
                    />
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <TextField
                      fullWidth
                      label="自动刷新间隔(秒)"
                      type="number"
                      value={systemSettings.autoRefreshInterval}
                      InputProps={{ inputProps: { min: 10, max: 300 } }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    功能开关
                  </Typography>

                  <Box sx={{ mb: 2 }}>
                    <FormControlLabel
                      control={<Switch checked={systemSettings.autoSave} />}
                      label="自动保存"
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <FormControlLabel
                      control={<Switch checked={systemSettings.debugMode} />}
                      label="调试模式"
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <FormControlLabel
                      control={<Switch checked={systemSettings.notificationsEnabled} />}
                      label="通知提醒"
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <FormControlLabel
                      control={<Switch checked={systemSettings.darkMode} />}
                      label="深色模式"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Alert severity="info">
                修改系统设置后需要重启应用才能生效。
              </Alert>
            </Grid>
          </Grid>
        </TabPanel>

        {/* LLM配置 */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">LLM提供商配置</Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setApiKeyDialogOpen(true)}
              >
                添加LLM
              </Button>
            </Box>
            
            {llmConfigs.map((config, index) => (
              <Card key={index} sx={{ mb: 2 }}>
                <CardContent>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={2}>
                      <Typography variant="h6">{config.name}</Typography>
                      <Chip 
                        label={config.enabled ? '已启用' : '已禁用'} 
                        color={config.enabled ? 'success' : 'default'}
                        size="small"
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" color="text.secondary">
                        端点
                      </Typography>
                      <Typography variant="body1">
                        {config.endpoint}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12} md={2}>
                      <Typography variant="body2" color="text.secondary">
                        模型
                      </Typography>
                      <Typography variant="body1">
                        {config.model}
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" color="text.secondary">
                        分配的Agents
                      </Typography>
                      <Box>
                        {config.agents.map((agent, agentIndex) => (
                          <Chip 
                            key={agentIndex} 
                            label={agent} 
                            size="small" 
                            sx={{ mr: 0.5, mb: 0.5 }}
                          />
                        ))}
                      </Box>
                    </Grid>
                    
                    <Grid item xs={12} md={2}>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                        <IconButton 
                          size="small"
                          onClick={() => setShowApiKey(!showApiKey)}
                        >
                          {showApiKey ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                        <IconButton size="small" color="error">
                          <Delete />
                        </IconButton>
                      </Box>
                    </Grid>
                    
                    {showApiKey && (
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="API Key"
                          value={config.apiKey}
                          size="small"
                          InputProps={{ readOnly: true }}
                        />
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
            ))}
          </Box>
        </TabPanel>

        {/* Agent设置 */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Agent配置管理
          </Typography>
          
          <List>
            {agentSettings.map((agent, index) => (
              <React.Fragment key={agent.id}>
                <ListItem>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Typography variant="h6">{agent.name}</Typography>
                        <Chip 
                          label={agent.enabled ? '已启用' : '已禁用'} 
                          color={agent.enabled ? 'success' : 'default'}
                          size="small"
                        />
                        <Chip 
                          label={`优先级: ${agent.priority}`} 
                          variant="outlined"
                          size="small"
                        />
                      </Box>
                    }
                    secondary={
                      <Grid container spacing={2} sx={{ mt: 1 }}>
                        <Grid item xs={3}>
                          <Typography variant="caption" color="text.secondary">
                            LLM模型
                          </Typography>
                          <Typography variant="body2">
                            {agent.llm}
                          </Typography>
                        </Grid>
                        <Grid item xs={3}>
                          <Typography variant="caption" color="text.secondary">
                            最大任务数
                          </Typography>
                          <Typography variant="body2">
                            {agent.maxTasks}
                          </Typography>
                        </Grid>
                        <Grid item xs={3}>
                          <Typography variant="caption" color="text.secondary">
                            自动分配
                          </Typography>
                          <Typography variant="body2">
                            {agent.autoAssign ? '是' : '否'}
                          </Typography>
                        </Grid>
                      </Grid>
                    }
                  />
                  <ListItemSecondaryAction>
                    <IconButton edge="end">
                      <Edit />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
                {index < agentSettings.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </TabPanel>

        {/* 安全设置 */}
        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    访问控制
                  </Typography>
                  
                  <Box sx={{ mb: 3 }}>
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="启用API密钥验证"
                    />
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="启用IP白名单"
                    />
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <FormControlLabel
                      control={<Switch />}
                      label="启用访问日志"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    数据安全
                  </Typography>
                  
                  <Box sx={{ mb: 3 }}>
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="加密敏感数据"
                    />
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="定期备份数据"
                    />
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <FormControlLabel
                      control={<Switch />}
                      label="数据脱敏"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Alert severity="warning">
                安全设置的更改会影响系统的访问权限，请谨慎操作。
              </Alert>
            </Grid>
          </Grid>
        </TabPanel>

        {/* 操作按钮 */}
        <Box sx={{ p: 3, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSaveSettings}
            >
              保存设置
            </Button>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={handleResetSettings}
            >
              重置设置
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* 添加LLM对话框 */}
      <Dialog open={apiKeyDialogOpen} onClose={() => setApiKeyDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>添加LLM配置</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField fullWidth label="名称" variant="outlined" />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="API端点" variant="outlined" />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="API密钥" type="password" variant="outlined" />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="模型名称" variant="outlined" />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApiKeyDialogOpen(false)}>取消</Button>
          <Button variant="contained">添加</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Settings