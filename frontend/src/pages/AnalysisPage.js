import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  ExpandMore,
  Analytics,
  Mood,
  MoodBad,
  SentimentSatisfied,
  Timeline,
  VolumeUp,
  Visibility,
  Speed,
  ColorLens,
  MusicNote,
  PersonRemove,
  SmartToy,
  TrendingUp,
  Assessment,
  Download,
  Share,
} from '@mui/icons-material';

const AnalysisPage = () => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  // Mock analysis data for demonstration
  const mockAnalysisData = {
    videoMetrics: {
      duration: '2:45',
      resolution: '1920x1080',
      fps: 30,
      fileSize: '150 MB',
      bitrate: '8.5 Mbps',
    },
    emotions: [
      { emotion: 'Happy', confidence: 0.85, timestamp: '0:15' },
      { emotion: 'Neutral', confidence: 0.65, timestamp: '0:45' },
      { emotion: 'Excited', confidence: 0.92, timestamp: '1:20' },
      { emotion: 'Calm', confidence: 0.78, timestamp: '2:10' },
    ],
    sceneChanges: [
      { timestamp: '0:00', confidence: 1.0, type: 'Cut' },
      { timestamp: '0:32', confidence: 0.88, type: 'Fade' },
      { timestamp: '1:15', confidence: 0.94, type: 'Cut' },
      { timestamp: '2:01', confidence: 0.76, type: 'Dissolve' },
    ],
    audioAnalysis: {
      avgVolume: 72,
      peakVolume: 95,
      silentSegments: 3,
      musicDetected: true,
      speechQuality: 'Good',
    },
    aiSuggestions: [
      {
        type: 'Cut Suggestion',
        timestamp: '0:23',
        reason: 'Long pause detected',
        confidence: 0.82,
      },
      {
        type: 'Music Addition',
        timestamp: '1:45',
        reason: 'Silent segment could benefit from background music',
        confidence: 0.75,
      },
      {
        type: 'Color Correction',
        timestamp: '0:45',
        reason: 'Scene appears underexposed',
        confidence: 0.68,
      },
    ],
  };

  const handleFileAnalysis = async (file) => {
    setLoading(true);
    setSelectedFile(file);

    // Simulate API call
    setTimeout(() => {
      setAnalysisData(mockAnalysisData);
      setLoading(false);
    }, 2000);
  };

  const getEmotionIcon = (emotion) => {
    switch (emotion.toLowerCase()) {
      case 'happy':
      case 'excited':
        return <Mood color="success" />;
      case 'sad':
      case 'angry':
        return <MoodBad color="error" />;
      default:
        return <SentimentSatisfied color="primary" />;
    }
  };

  const getEmotionColor = (emotion) => {
    switch (emotion.toLowerCase()) {
      case 'happy':
      case 'excited':
        return 'success';
      case 'sad':
      case 'angry':
        return 'error';
      case 'neutral':
      case 'calm':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ flexGrow: 1, bgcolor: 'background.default', minHeight: '100vh' }}>
      <Container maxWidth="xl" sx={{ py: 2 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            📊 Video Analysis
          </Typography>
          <Typography variant="body1" color="text.secondary">
            AI-powered video content analysis and insights
          </Typography>
        </Box>

        {!analysisData && !loading && (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Analytics sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Upload a video to start analysis
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Our AI will analyze emotions, detect scenes, and provide intelligent suggestions
            </Typography>
            <Button
              variant="contained"
              component="label"
              size="large"
              startIcon={<Analytics />}
            >
              Choose Video File
              <input
                type="file"
                accept="video/*"
                hidden
                onChange={(e) => {
                  if (e.target.files[0]) {
                    handleFileAnalysis(e.target.files[0]);
                  }
                }}
              />
            </Button>
          </Paper>
        )}

        {loading && (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress size={60} sx={{ mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Analyzing Video...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              This may take a few moments
            </Typography>
            <LinearProgress sx={{ mt: 2, maxWidth: 400, mx: 'auto' }} />
          </Paper>
        )}

        {analysisData && (
          <Grid container spacing={3}>
            {/* Overview Cards */}
            <Grid item xs={12}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Timeline color="primary" sx={{ mr: 1 }} />
                        <Typography variant="h6">Duration</Typography>
                      </Box>
                      <Typography variant="h4" color="primary">
                        {analysisData.videoMetrics.duration}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Visibility color="primary" sx={{ mr: 1 }} />
                        <Typography variant="h6">Resolution</Typography>
                      </Box>
                      <Typography variant="h4" color="primary">
                        {analysisData.videoMetrics.resolution}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Speed color="primary" sx={{ mr: 1 }} />
                        <Typography variant="h6">Frame Rate</Typography>
                      </Box>
                      <Typography variant="h4" color="primary">
                        {analysisData.videoMetrics.fps} FPS
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Assessment color="primary" sx={{ mr: 1 }} />
                        <Typography variant="h6">File Size</Typography>
                      </Box>
                      <Typography variant="h4" color="primary">
                        {analysisData.videoMetrics.fileSize}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Grid>

            {/* Detailed Analysis */}
            <Grid item xs={12} md={8}>
              {/* Emotion Analysis */}
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">
                    😊 Emotion Analysis
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {analysisData.emotions.map((emotion, index) => (
                      <Grid item xs={12} sm={6} key={index}>
                        <Card variant="outlined">
                          <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                              {getEmotionIcon(emotion.emotion)}
                              <Typography variant="h6" sx={{ ml: 1 }}>
                                {emotion.emotion}
                              </Typography>
                              <Chip
                                label={emotion.timestamp}
                                size="small"
                                sx={{ ml: 'auto' }}
                              />
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={emotion.confidence * 100}
                              color={getEmotionColor(emotion.emotion)}
                              sx={{ height: 8, borderRadius: 4 }}
                            />
                            <Typography variant="body2" sx={{ mt: 1 }}>
                              Confidence: {(emotion.confidence * 100).toFixed(1)}%
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </AccordionDetails>
              </Accordion>

              {/* Scene Detection */}
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">
                    🎬 Scene Detection
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Timestamp</TableCell>
                          <TableCell>Type</TableCell>
                          <TableCell>Confidence</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {analysisData.sceneChanges.map((scene, index) => (
                          <TableRow key={index}>
                            <TableCell>{scene.timestamp}</TableCell>
                            <TableCell>
                              <Chip label={scene.type} size="small" />
                            </TableCell>
                            <TableCell>
                              <LinearProgress
                                variant="determinate"
                                value={scene.confidence * 100}
                                sx={{ height: 6, borderRadius: 3, minWidth: 100 }}
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </AccordionDetails>
              </Accordion>

              {/* Audio Analysis */}
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">
                    🔊 Audio Analysis
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <List>
                        <ListItem>
                          <ListItemIcon>
                            <VolumeUp />
                          </ListItemIcon>
                          <ListItemText
                            primary="Average Volume"
                            secondary={`${analysisData.audioAnalysis.avgVolume}%`}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon>
                            <TrendingUp />
                          </ListItemIcon>
                          <ListItemText
                            primary="Peak Volume"
                            secondary={`${analysisData.audioAnalysis.peakVolume}%`}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon>
                            <Timeline />
                          </ListItemIcon>
                          <ListItemText
                            primary="Silent Segments"
                            secondary={`${analysisData.audioAnalysis.silentSegments} found`}
                          />
                        </ListItem>
                      </List>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <List>
                        <ListItem>
                          <ListItemIcon>
                            <MusicNote />
                          </ListItemIcon>
                          <ListItemText
                            primary="Music Detected"
                            secondary={analysisData.audioAnalysis.musicDetected ? 'Yes' : 'No'}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon>
                            <Assessment />
                          </ListItemIcon>
                          <ListItemText
                            primary="Speech Quality"
                            secondary={analysisData.audioAnalysis.speechQuality}
                          />
                        </ListItem>
                      </List>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* AI Suggestions */}
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  🤖 AI Suggestions
                </Typography>
                <List>
                  {analysisData.aiSuggestions.map((suggestion, index) => (
                    <div key={index}>
                      <ListItem>
                        <ListItemIcon>
                          <SmartToy color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary={suggestion.type}
                          secondary={
                            <Box>
                              <Typography variant="body2">
                                {suggestion.reason}
                              </Typography>
                              <Typography variant="caption">
                                At {suggestion.timestamp} • {(suggestion.confidence * 100).toFixed(0)}% confidence
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < analysisData.aiSuggestions.length - 1 && <Divider />}
                    </div>
                  ))}
                </List>

                <Box sx={{ mt: 3 }}>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<Download />}
                    sx={{ mb: 1 }}
                  >
                    Export Report
                  </Button>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Share />}
                  >
                    Share Analysis
                  </Button>
                </Box>
              </Paper>
            </Grid>
          </Grid>
        )}
      </Container>
    </Box>
  );
};

export default AnalysisPage;
