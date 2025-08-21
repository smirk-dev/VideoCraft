import React, { useState } from 'react';
import { 
  Container, 
  Typography, 
  Button, 
  Paper, 
  Box, 
  TextField,
  Alert,
  CircularProgress 
} from '@mui/material';
import { useVideo } from '../context/VideoContext';

const DebugPage = () => {
  const { currentVideo, videoMetadata, hasVideo } = useVideo();
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiUrl, setApiUrl] = useState('http://localhost:8002');

  const testBackendConnection = async () => {
    setLoading(true);
    setTestResult(null);
    
    try {
      console.log('🔧 Testing backend connection...');
      
      // Test basic connectivity
      const healthResponse = await fetch(`${apiUrl}/api/analyze/analyze-filename`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: currentVideo || 'test_video.mp4'
        })
      });
      
      console.log('Response received:', healthResponse.status);
      
      if (!healthResponse.ok) {
        throw new Error(`HTTP ${healthResponse.status}: ${healthResponse.statusText}`);
      }
      
      const result = await healthResponse.json();
      console.log('Analysis result:', result);
      
      setTestResult({
        success: true,
        status: healthResponse.status,
        data: result,
        timestamp: new Date().toISOString()
      });
      
    } catch (error) {
      console.error('❌ Backend test failed:', error);
      setTestResult({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  const testVideoContext = () => {
    const contextData = {
      currentVideo,
      videoMetadata,
      hasVideo: hasVideo(),
      apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8002'
    };
    
    console.log('Video Context Data:', contextData);
    alert(`Video Context:\n${JSON.stringify(contextData, null, 2)}`);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        🐛 Debug Dashboard
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Current State
        </Typography>
        <Paper sx={{ p: 2 }}>
          <Typography variant="body2">
            <strong>Current Video:</strong> {currentVideo || 'None'}
          </Typography>
          <Typography variant="body2">
            <strong>Has Video:</strong> {hasVideo() ? 'Yes' : 'No'}
          </Typography>
          <Typography variant="body2">
            <strong>Video Metadata:</strong> {videoMetadata ? 'Available' : 'None'}
          </Typography>
          {videoMetadata && (
            <Typography variant="body2" sx={{ ml: 2, fontSize: '0.8rem' }}>
              Duration: {videoMetadata.duration}s, Size: {videoMetadata.size} bytes
            </Typography>
          )}
        </Paper>
      </Box>

      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          API Testing
        </Typography>
        <Paper sx={{ p: 2 }}>
          <TextField
            fullWidth
            label="Backend URL"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            sx={{ mb: 2 }}
          />
          
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Button
              variant="contained"
              onClick={testBackendConnection}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              Test Analysis API
            </Button>
            
            <Button
              variant="outlined"
              onClick={testVideoContext}
            >
              Check Video Context
            </Button>
          </Box>
          
          {testResult && (
            <Alert 
              severity={testResult.success ? 'success' : 'error'}
              sx={{ mt: 2 }}
            >
              <Typography variant="h6">
                {testResult.success ? '✅ API Test Successful' : '❌ API Test Failed'}
              </Typography>
              
              {testResult.success ? (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2">
                    <strong>Status:</strong> {testResult.status}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Success:</strong> {testResult.data?.success ? 'Yes' : 'No'}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Analysis Data:</strong> {testResult.data?.analysis ? 'Present' : 'Missing'}
                  </Typography>
                  {testResult.data?.analysis && (
                    <Box sx={{ ml: 2, fontSize: '0.8rem' }}>
                      <Typography variant="body2">
                        • Scenes: {testResult.data.analysis.scenes?.length || 0}
                      </Typography>
                      <Typography variant="body2">
                        • Emotions: {testResult.data.analysis.emotions?.length || 0}
                      </Typography>
                      <Typography variant="body2">
                        • Audio Analysis: {testResult.data.analysis.audio_analysis ? 'Yes' : 'No'}
                      </Typography>
                      <Typography variant="body2">
                        • Recommendations: {testResult.data.recommendations?.length || 0}
                      </Typography>
                    </Box>
                  )}
                  <Typography variant="body2" sx={{ mt: 1, fontSize: '0.7rem' }}>
                    <strong>Raw Response:</strong>
                  </Typography>
                  <Box sx={{ 
                    mt: 1, 
                    p: 1, 
                    bgcolor: 'grey.100', 
                    borderRadius: 1,
                    fontSize: '0.7rem',
                    fontFamily: 'monospace',
                    maxHeight: 200,
                    overflow: 'auto'
                  }}>
                    {JSON.stringify(testResult.data, null, 2)}
                  </Box>
                </Box>
              ) : (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  <strong>Error:</strong> {testResult.error}
                </Typography>
              )}
              
              <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
                Test performed at: {testResult.timestamp}
              </Typography>
            </Alert>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default DebugPage;
