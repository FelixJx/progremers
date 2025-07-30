import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import ProjectLaunchpad from './pages/ProjectLaunchpad'
import ProjectManagement from './pages/ProjectManagement'
import AgentMonitoring from './pages/AgentMonitoring'
import TaskAnalysis from './pages/TaskAnalysis'
import TeamCollaboration from './pages/TeamCollaboration'
import SystemEvaluation from './pages/SystemEvaluation'
import Settings from './pages/Settings'

function App() {
  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <Sidebar />
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Navbar />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            overflow: 'auto',
            backgroundColor: '#f5f5f5',
          }}
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/launchpad" element={<ProjectLaunchpad />} />
            <Route path="/projects" element={<ProjectManagement />} />
            <Route path="/agents" element={<AgentMonitoring />} />
            <Route path="/tasks" element={<TaskAnalysis />} />
            <Route path="/collaboration" element={<TeamCollaboration />} />
            <Route path="/evaluation" element={<SystemEvaluation />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Box>
      </Box>
    </Box>
  )
}

export default App