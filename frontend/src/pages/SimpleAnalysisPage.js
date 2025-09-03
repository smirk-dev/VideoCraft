import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert
} from '@mui/material';
import {
  Analytics,
  Mood,
  VolumeUp,
  Timeline,
  SmartToy
} from '@mui/icons-material';
import { API_CONFIG } from '../config/api';

const SimpleAnalysisPage = () => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('🚀 Starting simple analysis...');
      
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/analyze/analyze-filename`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: 'test_video.mp4' })
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Analysis result:', result);
      
      if (result.success) {
        // Use the data directly without complex transformation
        setAnalysisData({
          emotions: result.analysis.emotion_detection?.emotion_timeline || [],
          scenes: result.analysis.scene_analysis || [],
          suggestions: result.recommendations || [],
          processingTime: result.analysis.processing_time_seconds || 0
        });
      } else {
        setError('Analysis failed');
      }
      
    } catch (err) {
      console.error('Analysis error:', err);
      setError(`Failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Auto-run analysis on page load
  useEffect(() => {
    runAnalysis();
  }, []);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        📊 Simple Video Analysis
      </Typography>
      
      {loading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <LinearProgress sx={{ mb: 2 }} />
          <Typography>Analyzing video...</Typography>
        </Paper>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
          <Button onClick={runAnalysis} sx={{ ml: 2 }}>
            Retry
          </Button>
        </Alert>
      )}
      
      {analysisData && (
        <Grid container spacing={3}>
          {/* Video Metrics */}
          <Grid item xs={12}>
            <Grid container spacing={2}>
              <Grid item xs={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">Duration</Typography>
                    <Typography variant="h4" color="primary">2:05</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">Resolution</Typography>
                    <Typography variant="h4" color="primary">1920x1080</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">Frame Rate</Typography>
                    <Typography variant="h4" color="primary">30 FPS</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">Processing Time</Typography>
                    <Typography variant="h4" color="primary">{analysisData.processingTime.toFixed(1)}s</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Grid>

          {/* Emotions */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                😊 Emotions Detected
              </Typography>
              <List>
                {analysisData.emotions.map((emotion, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <Mood color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={emotion.emotion}
                      secondary={
                        <Box>
                          <Typography variant="body2">
                            At {emotion.timestamp} • {(emotion.intensity * 100).toFixed(0)}% confidence
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={emotion.intensity * 100} 
                            sx={{ mt: 1 }}
                          />
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* Scenes */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                🎬 Scene Analysis
              </Typography>
              <List>
                {analysisData.scenes.map((scene, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <Timeline color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={scene.scene}
                      secondary={
                        <Box>
                          <Typography variant="body2">
                            {scene.timestamp} • {(scene.confidence * 100).toFixed(0)}% confidence
                          </Typography>
                          <Typography variant="body2">
                            {scene.description}
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={scene.confidence * 100} 
                            sx={{ mt: 1 }}
                          />
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* AI Suggestions */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                🤖 AI Suggestions
              </Typography>
              <List>
                {analysisData.suggestions.map((suggestion, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <SmartToy color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={suggestion.type}
                      secondary={
                        <Box>
                          <Typography variant="body2">
                            {suggestion.suggestion}
                          </Typography>
                          <Typography variant="caption">
                            Platform: {suggestion.platform} • {(suggestion.confidence * 100).toFixed(0)}% confidence
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* Manual Trigger */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<Analytics />}
                onClick={runAnalysis}
                disabled={loading}
              >
                Run Analysis Again
              </Button>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default SimpleAnalysisPage;
