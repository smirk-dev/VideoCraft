import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import { VideoProvider } from './context/VideoContext';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import UploadPage from './pages/UploadPage';
import EditorPage from './pages/EditorPage';
import AnalysisPage from './pages/AnalysisPage';
import ProjectsPage from './pages/ProjectsPage';
import RecommendationsPage from './pages/RecommendationsPage';
import DebugPage from './pages/DebugPage';
import SimpleAnalysisPage from './pages/SimpleAnalysisPage';

function App() {
  return (
    <VideoProvider>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Navbar />
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/editor" element={<EditorPage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
            <Route path="/debug" element={<DebugPage />} />
            <Route path="/simple" element={<SimpleAnalysisPage />} />
          </Routes>
        </Box>
      </Box>
    </VideoProvider>
  );
}

export default App;
