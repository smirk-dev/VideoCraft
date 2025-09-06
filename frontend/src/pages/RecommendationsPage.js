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
  Alert,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
  LinearProgress,
  Avatar,
  Tab,
  Tabs,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  AutoFixHigh,
  ContentCut,
  MusicNote,
  Psychology,
  FilterVintage,
  Speed,
  VolumeUp,
  ColorLens,
  Movie,
  TrendingUp,
  ExpandMore,
  PlayArrow,
  Add,
  CheckCircle,
  Schedule,
  Lightbulb,
  Analytics,
  Refresh,
  Share
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useVideo } from '../context/VideoContext';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ py: 2 }}>{children}</Box>}
    </div>
  );
}

const RecommendationsPage = () => {
  const navigate = useNavigate();
  const { hasVideo, currentVideo, videoMetadata } = useVideo();
  
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState(null);
  const [error, setError] = useState(null);
  const [currentTab, setCurrentTab] = useState(0);
  const [appliedRecommendations, setAppliedRecommendations] = useState(new Set());

  // Generate recommendations when component loads
  useEffect(() => {
    if (hasVideo() && currentVideo) {
      generateRecommendations();
    }
  }, [hasVideo, currentVideo]);

  // Debug recommendations state changes
  useEffect(() => {
    console.log('🎯 Recommendations state changed:', recommendations);
    console.log('🎯 Recommendations type:', typeof recommendations);
    if (recommendations) {
      console.log('🎯 Recommendations keys:', Object.keys(recommendations));
    }
  }, [recommendations]);

  const generateRecommendations = async () => {
    setLoading(true);
    setError(null);

    try {
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8003';
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const response = await fetch(`${API_BASE_URL}/api/recommendations/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: currentVideo,
          metadata: videoMetadata
        })
      });

      console.log('🎯 Recommendations API Response:', response.status, response.statusText);
      
      const result = await response.json();
      console.log('🎯 Recommendations Result:', result);
      console.log('🎯 Result type:', typeof result);
      console.log('🎯 Result keys:', Object.keys(result));
      
      if (result.success) {
        console.log('✅ Setting recommendations:', result.recommendations);
        console.log('🔍 Recommendations type:', typeof result.recommendations);
        console.log('🔍 Recommendations keys:', Object.keys(result.recommendations || {}));
        
        if (result.recommendations && result.recommendations.editing_recommendations) {
          const editing = result.recommendations.editing_recommendations;
          console.log('🔍 editing_recommendations keys:', Object.keys(editing));
          console.log('🔍 cuts length:', editing.cuts ? editing.cuts.length : 'undefined');
          console.log('🔍 music length:', editing.music ? editing.music.length : 'undefined');
          console.log('🔍 filters length:', editing.filters ? editing.filters.length : 'undefined');
        }
        
        setRecommendations(result.recommendations);
      } else {
        console.warn('❌ Recommendations failed:', result.error);
        throw new Error(result.error || 'Failed to generate recommendations');
      }
    } catch (err) {
      console.error('Failed to generate recommendations:', err);
      setError(err.message);
      // Fallback to mock data for demo
      setRecommendations(generateMockRecommendations());
    } finally {
      setLoading(false);
    }
  };

  const generateMockRecommendations = () => {
    return {
      overall_score: 78,
      sentiment: 'positive',
      editing_recommendations: {
        cuts: [
          {
            id: 'cut_1',
            timestamp: '0:15',
            reason: 'Scene transition detected - natural cut point',
            confidence: 0.92,
            type: 'scene_change',
            description: 'Strong visual transition from indoor to outdoor scene'
          },
          {
            id: 'cut_2',
            timestamp: '1:23',
            reason: 'Audio silence detected - remove dead space',
            confidence: 0.87,
            type: 'audio_silence',
            description: '2.3 seconds of silence that could be trimmed'
          },
          {
            id: 'cut_3',
            timestamp: '2:45',
            reason: 'Low engagement moment - consider cutting',
            confidence: 0.73,
            type: 'engagement',
            description: 'Static shot with minimal movement or interest'
          }
        ],
        music: [
          {
            id: 'music_1',
            genre: 'Upbeat Electronic',
            mood: 'Energetic',
            start_time: '0:00',
            end_time: '1:30',
            confidence: 0.89,
            description: 'High-energy music to match the dynamic opening sequence',
            suggested_tracks: ['Synth Pop Beat', 'Electronic Energy', 'Digital Pulse']
          },
          {
            id: 'music_2',
            genre: 'Ambient',
            mood: 'Calm',
            start_time: '1:30',
            end_time: '3:00',
            confidence: 0.82,
            description: 'Softer background music for dialogue-heavy section',
            suggested_tracks: ['Gentle Flow', 'Soft Ambience', 'Peaceful Waves']
          }
        ],
        filters: [
          {
            id: 'filter_1',
            name: 'Color Enhancement',
            type: 'color_correction',
            confidence: 0.85,
            description: 'Boost saturation by 15% to make colors more vibrant',
            settings: { saturation: 1.15, brightness: 1.05 }
          },
          {
            id: 'filter_2',
            name: 'Stabilization',
            type: 'video_stabilization',
            confidence: 0.91,
            description: 'Apply stabilization to reduce camera shake at 1:45-2:10',
            settings: { strength: 'medium', crop: 0.05 }
          }
        ],
        pacing: {
          overall_rating: 'good',
          slow_segments: [
            { start: '2:30', end: '2:55', suggestion: 'Speed up by 1.2x' },
            { start: '3:20', end: '3:45', suggestion: 'Consider trimming or adding cuts' }
          ],
          fast_segments: [
            { start: '0:45', end: '1:10', suggestion: 'Slow down by 0.9x for better comprehension' }
          ]
        }
      },
      sentiment_analysis: {
        overall_sentiment: 'positive',
        confidence: 0.84,
        emotional_peaks: [
          { timestamp: '0:30', emotion: 'excitement', intensity: 0.87 },
          { timestamp: '1:45', emotion: 'surprise', intensity: 0.72 },
          { timestamp: '2:20', emotion: 'satisfaction', intensity: 0.79 }
        ],
        recommended_tone: 'Keep the positive energy throughout. Consider adding more dynamic elements during the 2:30-3:00 segment.'
      },
      engagement_metrics: {
        predicted_retention: 0.76,
        hook_strength: 0.83,
        climax_timing: '1:45',
        recommended_length: '2:45',
        improvements: [
          'Add text overlay at key moments',
          'Include call-to-action at the end',
          'Consider thumbnail recommendations',
          'Optimize for mobile viewing'
        ]
      }
    };
  };

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const applyRecommendation = (recommendationId, type) => {
    setAppliedRecommendations(prev => new Set([...prev, recommendationId]));
    
    // Here you would integrate with the video editing functionality
    console.log(`Applying ${type} recommendation:`, recommendationId);
    
    // Navigate to editor with the recommendation applied
    // navigate('/editor', { state: { applyRecommendation: { id: recommendationId, type } } });
  };

  const formatTime = (timeStr) => {
    return timeStr;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return 'success';
      case 'negative': return 'error';
      case 'neutral': return 'info';
      default: return 'default';
    }
  };

  // If no video is loaded
  if (!hasVideo()) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h4" gutterBottom>
            🎯 AI Recommendations
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            No video loaded. Please upload a video to get AI-powered editing recommendations.
          </Typography>
          <Button
            variant="contained"
            onClick={() => navigate('/upload')}
            size="large"
          >
            Upload Video
          </Button>
        </Paper>
      </Container>
    );
  }

  // Loading state
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Analyzing your video...
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Our AI is examining your content to provide personalized editing recommendations
          </Typography>
          <LinearProgress sx={{ mt: 2, maxWidth: 400, mx: 'auto' }} />
        </Paper>
      </Container>
    );
  }

  // Error state
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={generateRecommendations} startIcon={<Refresh />}>
          Retry Analysis
        </Button>
      </Container>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, bgcolor: 'background.default', minHeight: '100vh' }}>
      <Container maxWidth="xl" sx={{ py: 2 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            🎯 AI Recommendations
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Intelligent editing suggestions for: <strong>{currentVideo}</strong>
          </Typography>
        </Box>

        {/* Overall Score */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h3" color="primary" gutterBottom>
                  {recommendations?.overall_score || 0}
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  Overall Score
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Chip 
                  label={recommendations?.sentiment || 'neutral'} 
                  color={getSentimentColor(recommendations?.sentiment)}
                  size="large"
                  icon={<Psychology />}
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  Content Sentiment
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h5" color="success.main" gutterBottom>
                  {appliedRecommendations.size}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Applied Recommendations
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Recommendations Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs 
            value={currentTab} 
            onChange={handleTabChange} 
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab icon={<ContentCut />} label="Cuts & Edits" />
            <Tab icon={<MusicNote />} label="Music & Audio" />
            <Tab icon={<FilterVintage />} label="Filters & Effects" />
            <Tab icon={<Psychology />} label="Sentiment Analysis" />
            <Tab icon={<TrendingUp />} label="Engagement" />
            <Tab icon={<Share />} label="Platform Optimization" />
          </Tabs>

          {/* Cuts & Edits Tab */}
          <TabPanel value={currentTab} index={0}>
            <Typography variant="h6" gutterBottom>
              Recommended Cuts & Edits
            </Typography>
            <Grid container spacing={2}>
              {recommendations?.editing_recommendations?.cuts?.map((cut) => (
                <Grid item xs={12} md={6} key={cut.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Typography variant="h6">
                          {formatTime(cut.timestamp)}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Chip 
                            label={cut.priority || 'medium'}
                            color={cut.priority === 'high' ? 'error' : cut.priority === 'medium' ? 'warning' : 'default'}
                            size="small"
                            variant="outlined"
                          />
                          <Chip 
                            label={`${Math.round(cut.confidence * 100)}%`}
                            color={getConfidenceColor(cut.confidence)}
                            size="small"
                          />
                        </Box>
                      </Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {cut.description}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Reason:</strong> {cut.reason}
                      </Typography>
                      {cut.expected_impact && (
                        <Typography variant="body2" sx={{ mb: 2, color: 'success.main' }}>
                          <strong>Expected Impact:</strong> {cut.expected_impact}
                        </Typography>
                      )}
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Chip label={cut.type} variant="outlined" size="small" />
                        {cut.priority && (
                          <Chip 
                            label={`${cut.priority} priority`} 
                            size="small"
                            color={cut.priority === 'high' ? 'error' : cut.priority === 'medium' ? 'warning' : 'default'}
                          />
                        )}
                      </Box>
                    </CardContent>
                    <CardActions>
                      <Button 
                        size="small" 
                        startIcon={<ContentCut />}
                        onClick={() => applyRecommendation(cut.id, 'cut')}
                        disabled={appliedRecommendations.has(cut.id)}
                      >
                        {appliedRecommendations.has(cut.id) ? 'Applied' : 'Apply Cut'}
                      </Button>
                      <Button size="small" startIcon={<PlayArrow />}>
                        Preview
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </TabPanel>

          {/* Music & Audio Tab */}
          <TabPanel value={currentTab} index={1}>
            <Typography variant="h6" gutterBottom>
              Music & Audio Recommendations
            </Typography>
            <Grid container spacing={2}>
              {recommendations?.editing_recommendations?.music?.map((music) => (
                <Grid item xs={12} md={6} key={music.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Typography variant="h6">
                          {music.genre || music.type}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Chip 
                            label={music.mood}
                            color="primary"
                            size="small"
                          />
                          <Chip 
                            label={`${Math.round(music.confidence * 100)}%`}
                            color={getConfidenceColor(music.confidence)}
                            size="small"
                          />
                        </Box>
                      </Box>
                      <Typography variant="body2" gutterBottom>
                        <strong>Timeline:</strong> {music.timestamp}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {music.reason}
                      </Typography>
                      
                      {/* Enhanced music details */}
                      <Grid container spacing={1} sx={{ mb: 2 }}>
                        {music.volume_level && (
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Volume: {music.volume_level}
                            </Typography>
                          </Grid>
                        )}
                        {music.content_type && (
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Type: {music.content_type}
                            </Typography>
                          </Grid>
                        )}
                        {music.fade_in && (
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Fade In: {music.fade_in}
                            </Typography>
                          </Grid>
                        )}
                        {music.fade_out && (
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">
                              Fade Out: {music.fade_out}
                            </Typography>
                          </Grid>
                        )}
                      </Grid>
                      
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Chip label={music.type} variant="outlined" size="small" />
                        <Chip label={music.priority || 'medium'} 
                              color={music.priority === 'high' ? 'error' : 'default'} 
                              size="small" variant="outlined" />
                      </Box>
                    </CardContent>
                    <CardActions>
                      <Button 
                        size="small" 
                        startIcon={<MusicNote />}
                        onClick={() => applyRecommendation(music.id, 'music')}
                        disabled={appliedRecommendations.has(music.id)}
                      >
                        {appliedRecommendations.has(music.id) ? 'Applied' : 'Add Music'}
                      </Button>
                      <Button size="small" startIcon={<VolumeUp />}>
                        Preview
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </TabPanel>

          {/* Filters & Effects Tab */}
          <TabPanel value={currentTab} index={2}>
            <Typography variant="h6" gutterBottom>
              Recommended Filters & Effects
            </Typography>
            <Grid container spacing={2}>
              {recommendations?.editing_recommendations?.filters?.map((filter) => (
                <Grid item xs={12} md={6} key={filter.id}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Typography variant="h6">
                          {filter.name}
                        </Typography>
                        <Chip 
                          label={`${Math.round(filter.confidence * 100)}%`}
                          color={getConfidenceColor(filter.confidence)}
                          size="small"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {filter.description}
                      </Typography>
                      <Chip label={filter.type} variant="outlined" size="small" />
                    </CardContent>
                    <CardActions>
                      <Button 
                        size="small" 
                        startIcon={<FilterVintage />}
                        onClick={() => applyRecommendation(filter.id, 'filter')}
                        disabled={appliedRecommendations.has(filter.id)}
                      >
                        {appliedRecommendations.has(filter.id) ? 'Applied' : 'Apply Filter'}
                      </Button>
                      <Button size="small" startIcon={<PlayArrow />}>
                        Preview
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>

            {/* Pacing Recommendations */}
            {recommendations?.editing_recommendations?.pacing && (
              <Box sx={{ mt: 4 }}>
                <Typography variant="h6" gutterBottom>
                  Pacing Adjustments
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="subtitle1" gutterBottom color="warning.main">
                          Slow Segments
                        </Typography>
                        {recommendations.editing_recommendations.pacing.slow_segments?.map((segment, index) => (
                          <Box key={index} sx={{ mb: 1 }}>
                            <Typography variant="body2">
                              {formatTime(segment.start)} - {formatTime(segment.end)}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {segment.suggestion}
                            </Typography>
                          </Box>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="subtitle1" gutterBottom color="info.main">
                          Fast Segments
                        </Typography>
                        {recommendations.editing_recommendations.pacing.fast_segments?.map((segment, index) => (
                          <Box key={index} sx={{ mb: 1 }}>
                            <Typography variant="body2">
                              {formatTime(segment.start)} - {formatTime(segment.end)}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {segment.suggestion}
                            </Typography>
                          </Box>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Box>
            )}
          </TabPanel>

          {/* Sentiment Analysis Tab */}
          <TabPanel value={currentTab} index={3}>
            <Typography variant="h6" gutterBottom>
              Sentiment Analysis
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Overall Sentiment
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Chip 
                        label={recommendations?.sentiment_analysis?.overall_sentiment || 'neutral'}
                        color={getSentimentColor(recommendations?.sentiment_analysis?.overall_sentiment)}
                        size="large"
                        icon={<Psychology />}
                      />
                      <Typography variant="body2" sx={{ ml: 2 }}>
                        {Math.round((recommendations?.sentiment_analysis?.confidence || 0) * 100)}% confidence
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {recommendations?.sentiment_analysis?.recommended_tone}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Emotional Peaks
                    </Typography>
                    {recommendations?.sentiment_analysis?.emotional_peaks?.map((peak, index) => (
                      <Box key={index} sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="body2">
                            {formatTime(peak.timestamp)} - {peak.emotion}
                          </Typography>
                          <Typography variant="caption">
                            {Math.round(peak.intensity * 100)}%
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={peak.intensity * 100} 
                          sx={{ mt: 0.5 }}
                        />
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Engagement Tab */}
          <TabPanel value={currentTab} index={4}>
            <Typography variant="h6" gutterBottom>
              Engagement Optimization
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Predicted Metrics
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Retention Rate: {Math.round((recommendations?.engagement_metrics?.predicted_retention || 0) * 100)}%
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={(recommendations?.engagement_metrics?.predicted_retention || 0) * 100}
                        color="success"
                      />
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Hook Strength: {Math.round((recommendations?.engagement_metrics?.hook_strength || 0) * 100)}%
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={(recommendations?.engagement_metrics?.hook_strength || 0) * 100}
                        color="primary"
                      />
                    </Box>
                    <Typography variant="body2">
                      <strong>Climax Timing:</strong> {recommendations?.engagement_metrics?.climax_timing}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Recommended Length:</strong> {recommendations?.engagement_metrics?.recommended_length}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Engagement Tips
                    </Typography>
                    <List>
                      {recommendations?.engagement_tips?.map((tip, index) => (
                        <ListItem key={index} sx={{ alignItems: 'flex-start' }}>
                          <ListItemIcon sx={{ mt: 0.5 }}>
                            <Lightbulb color="primary" />
                          </ListItemIcon>
                          <ListItemText 
                            primary={tip.split('(')[0].trim()} 
                            secondary={tip.includes('(') ? tip.split('(')[1].replace(')', '') : null}
                          />
                        </ListItem>
                      ))}
                      {recommendations?.quality_improvements?.map((improvement, index) => (
                        <ListItem key={`quality-${index}`} sx={{ alignItems: 'flex-start' }}>
                          <ListItemIcon sx={{ mt: 0.5 }}>
                            <AutoFixHigh color="secondary" />
                          </ListItemIcon>
                          <ListItemText 
                            primary={improvement.split('(')[0].trim()} 
                            secondary={improvement.includes('(') ? improvement.split('(')[1].replace(')', '') : null}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Platform Optimization Tab */}
          <TabPanel value={currentTab} index={5}>
            <Typography variant="h6" gutterBottom>
              Platform Optimization
            </Typography>
            <Grid container spacing={3}>
              {recommendations?.platform_optimization && Object.entries(recommendations.platform_optimization).map(([platform, data]) => (
                <Grid item xs={12} md={4} key={platform}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Avatar 
                          sx={{ 
                            bgcolor: data.recommended ? 'success.main' : 'grey.400',
                            mr: 2,
                            textTransform: 'capitalize'
                          }}
                        >
                          {platform.charAt(0).toUpperCase()}
                        </Avatar>
                        <Box>
                          <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                            {platform.replace(/_/g, ' ')}
                          </Typography>
                          <Chip 
                            label={data.recommended ? 'Recommended' : 'Not Optimal'}
                            color={data.recommended ? 'success' : 'default'}
                            size="small"
                          />
                        </Box>
                      </Box>
                      
                      {data.optimizations && data.optimizations.length > 0 && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Optimizations:
                          </Typography>
                          <List dense>
                            {data.optimizations.map((opt, index) => (
                              <ListItem key={index} sx={{ px: 0 }}>
                                <ListItemIcon>
                                  <CheckCircle color="success" fontSize="small" />
                                </ListItemIcon>
                                <ListItemText primary={opt} />
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}
                      
                      {data.content_tips && data.content_tips.length > 0 && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Content Tips:
                          </Typography>
                          <List dense>
                            {data.content_tips.map((tip, index) => (
                              <ListItem key={index} sx={{ px: 0 }}>
                                <ListItemIcon>
                                  <Lightbulb color="primary" fontSize="small" />
                                </ListItemIcon>
                                <ListItemText primary={tip} />
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}
                      
                      {data.strategy_tips && data.strategy_tips.length > 0 && (
                        <Box>
                          <Typography variant="subtitle2" gutterBottom>
                            Strategy Tips:
                          </Typography>
                          <List dense>
                            {data.strategy_tips.map((tip, index) => (
                              <ListItem key={index} sx={{ px: 0 }}>
                                <ListItemIcon>
                                  <Analytics color="info" fontSize="small" />
                                </ListItemIcon>
                                <ListItemText primary={tip} />
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </TabPanel>
        </Paper>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<Movie />}
            onClick={() => navigate('/editor')}
          >
            Apply to Editor
          </Button>
          <Button
            variant="outlined"
            size="large"
            startIcon={<Refresh />}
            onClick={generateRecommendations}
          >
            Regenerate
          </Button>
          <Button
            variant="outlined"
            size="large"
            startIcon={<Analytics />}
            onClick={() => navigate('/analysis')}
          >
            View Analysis
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default RecommendationsPage;
