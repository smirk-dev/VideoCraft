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
  Upload,
  Link,
  Email,
  ContentCopy
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useVideo } from '../context/VideoContext';
import ExportButton from '../components/common/ExportButton';

const AnalysisPage = () => {
  const navigate = useNavigate();
  const { hasVideo, currentVideo, videoMetadata, videoUrl } = useVideo();
  
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Generate mock analysis data based on actual video
  const generateMockAnalysisData = () => {
    const duration = videoMetadata?.duration || 165; // fallback to 2:45
    const formatDuration = (seconds) => {
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return {
      videoMetrics: {
        duration: formatDuration(duration),
        resolution: `${videoMetadata?.width || 1920}x${videoMetadata?.height || 1080}`,
        fps: 30,
        fileSize: videoMetadata?.size ? `${(videoMetadata.size / (1024 * 1024)).toFixed(1)} MB` : '150 MB',
        bitrate: '8.5 Mbps',
      },
      emotions: [
        { emotion: 'Happy', confidence: 0.85, timestamp: '0:15' },
        { emotion: 'Neutral', confidence: 0.65, timestamp: formatDuration(duration * 0.25) },
        { emotion: 'Excited', confidence: 0.92, timestamp: formatDuration(duration * 0.5) },
        { emotion: 'Calm', confidence: 0.78, timestamp: formatDuration(duration * 0.8) },
      ],
      sceneChanges: [
        { timestamp: '0:00', confidence: 1.0, type: 'Cut' },
        { timestamp: formatDuration(duration * 0.2), confidence: 0.88, type: 'Fade' },
        { timestamp: formatDuration(duration * 0.45), confidence: 0.94, type: 'Cut' },
        { timestamp: formatDuration(duration * 0.75), confidence: 0.76, type: 'Dissolve' },
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
          timestamp: formatDuration(duration * 0.15),
          reason: 'Long pause detected',
          confidence: 0.82,
        },
        {
          type: 'Music Addition',
          timestamp: formatDuration(duration * 0.65),
          reason: 'Silent segment could benefit from background music',
          confidence: 0.75,
        },
        {
          type: 'Color Correction',
          timestamp: formatDuration(duration * 0.3),
          reason: 'Scene appears underexposed',
          confidence: 0.68,
        },
      ],
    };
  };

  const handleVideoAnalysis = async () => {
    setLoading(true);

    // Simulate API call with the existing video
    setTimeout(() => {
      setAnalysisData(generateMockAnalysisData());
      setLoading(false);
    }, 2000);
  };

  // Auto-analyze when component loads if video exists
  useEffect(() => {
    if (hasVideo() && !analysisData && !loading) {
      handleVideoAnalysis();
    }
  }, [hasVideo, analysisData, loading]);

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
            {hasVideo() 
              ? `Analyzing: ${currentVideo} • AI-powered content analysis and insights`
              : 'AI-powered video content analysis and insights'
            }
          </Typography>
        </Box>

        {!hasVideo() && (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Analytics sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No video loaded for analysis
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Please upload a video first to begin AI analysis
            </Typography>
            <Button
              variant="contained"
              size="large"
              startIcon={<Upload />}
              onClick={() => navigate('/upload')}
            >
              Upload Video
            </Button>
          </Paper>
        )}

        {hasVideo() && !analysisData && !loading && (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Analytics sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Ready to analyze: {currentVideo}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Our AI will analyze emotions, detect scenes, and provide intelligent suggestions
            </Typography>
            <Button
              variant="contained"
              size="large"
              startIcon={<Analytics />}
              onClick={handleVideoAnalysis}
            >
              Start Analysis
            </Button>
          </Paper>
        )}

        {loading && (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress size={60} sx={{ mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Analyzing {currentVideo}...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Processing video content • This may take a few moments
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
