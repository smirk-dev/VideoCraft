import React, { useCallback, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Avatar,
  Paper,
  Alert
} from '@mui/material';
import {
  VideoLibrary,
  AutoAwesome,
  MusicNote,
  RemoveRedEye,
  Edit,
  Analytics,
  CloudUpload
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { useVideo } from '../context/VideoContext';

const HomePage = () => {
  const navigate = useNavigate();
  const { uploadVideo } = useVideo();
  const [uploadMessage, setUploadMessage] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    const videoFile = acceptedFiles.find(file => file.type.includes('video'));
    
    if (videoFile) {
      setUploadError(null);
      setUploadMessage('Uploading video...');
      
      try {
        const result = await uploadVideo(videoFile);
        
        if (result.success) {
          setUploadMessage(`${videoFile.name} loaded successfully! Redirecting to editor...`);
          setTimeout(() => {
            navigate('/editor');
          }, 1500);
        } else {
          throw new Error(result.error);
        }
      } catch (error) {
        setUploadError(`Failed to upload ${videoFile.name}: ${error.message}`);
        setUploadMessage(null);
      }
    } else {
      setUploadError('Please upload a video file');
    }
  }, [uploadVideo, navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    },
    multiple: false,
    maxSize: 2 * 1024 * 1024 * 1024, // 2GB
    noClick: true // We'll handle clicks manually
  });

  const features = [
    {
      icon: <AutoAwesome />,
      title: "AI Video Analysis",
      description: "Automatic scene detection, object recognition, and intelligent content analysis powered by advanced AI models.",
      color: "#1976d2"
    },
    {
      icon: <RemoveRedEye />,
      title: "Emotion Detection",
      description: "Real-time emotion analysis using facial recognition and audio sentiment analysis for better storytelling.",
      color: "#9c27b0"
    },
    {
      icon: <MusicNote />,
      title: "Smart Music Recommendations",
      description: "Context-aware music suggestions based on video content, mood, and emotional tone.",
      color: "#f57c00"
    },
    {
      icon: <Edit />,
      title: "Background Removal",
      description: "AI-powered background removal and replacement with professional-grade accuracy.",
      color: "#388e3c"
    },
    {
      icon: <Analytics />,
      title: "Script Analysis",
      description: "NLP-powered script improvement suggestions and structure analysis for better content.",
      color: "#d32f2f"
    },
    {
      icon: <VideoLibrary />,
      title: "Timeline Editor",
      description: "Professional timeline-based video editing with real-time preview and AI suggestions.",
      color: "#7b1fa2"
    }
  ];

  const stats = [
    { label: "AI Models", value: "15+" },
    { label: "Video Formats", value: "10+" },
    { label: "Processing Speed", value: "5x Faster" },
    { label: "Accuracy", value: "95%" }
  ];

  return (
    <div {...getRootProps()} style={{ outline: 'none' }}>
      <input {...getInputProps()} />
      <Container maxWidth="lg">
        {/* Upload Messages */}
        {uploadMessage && (
          <Alert severity="info" sx={{ mb: 2 }}>
            {uploadMessage}
          </Alert>
        )}
        {uploadError && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setUploadError(null)}>
            {uploadError}
          </Alert>
        )}

        {/* Drag Overlay */}
        {isDragActive && (
          <Paper
            sx={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(33, 150, 243, 0.1)',
              border: '3px dashed #2196f3',
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexDirection: 'column'
            }}
          >
            <CloudUpload sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" color="primary">
              Drop your video here to start editing!
            </Typography>
          </Paper>
        )}

        {/* Hero Section */}
        <Box
          sx={{
            textAlign: 'center',
            py: 8,
            background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
            borderRadius: 2,
            mb: 6,
            color: 'white'
          }}
        >
          <Typography variant="h2" component="h1" gutterBottom fontWeight="bold">
            VideoCraft AI
          </Typography>
          <Typography variant="h5" component="p" sx={{ mb: 4, opacity: 0.9 }}>
            The Future of AI-Powered Video Editing
          </Typography>
          <Typography variant="body1" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
            Create, edit, and enhance videos with intelligent AI suggestions. 
            From automatic scene detection to emotion analysis and smart music recommendations.
          </Typography>
          <Typography variant="body2" sx={{ mb: 4, opacity: 0.8, fontStyle: 'italic' }}>
            💡 Tip: Drag and drop a video anywhere on this page to start editing immediately!
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<CloudUpload />}
              onClick={() => navigate('/upload')}
              sx={{ 
                backgroundColor: 'white', 
                color: '#1976d2',
                '&:hover': { backgroundColor: '#f5f5f5' }
              }}
            >
              Start Creating
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/editor')}
              sx={{ 
                borderColor: 'white', 
                color: 'white',
                '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' }
              }}
            >
              Try Editor
            </Button>
          </Box>
        </Box>

      {/* Stats Section */}
      <Box sx={{ mb: 6 }}>
        <Grid container spacing={3}>
          {stats.map((stat, index) => (
            <Grid item xs={6} md={3} key={index}>
              <Card sx={{ textAlign: 'center', py: 2 }}>
                <CardContent>
                  <Typography variant="h4" component="div" color="primary" fontWeight="bold">
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.label}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Features Section */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h3" component="h2" textAlign="center" gutterBottom>
          Powerful AI Features
        </Typography>
        <Typography 
          variant="body1" 
          textAlign="center" 
          color="text.secondary" 
          sx={{ mb: 4, maxWidth: 800, mx: 'auto' }}
        >
          Leverage cutting-edge AI technology to transform your video editing workflow. 
          Our intelligent features help you create professional content faster than ever.
        </Typography>
        
        <Grid container spacing={3}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <Card 
                sx={{ 
                  height: '100%',
                  transition: 'transform 0.2s',
                  '&:hover': { transform: 'translateY(-4px)' }
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar 
                      sx={{ 
                        backgroundColor: feature.color, 
                        mr: 2,
                        width: 48,
                        height: 48
                      }}
                    >
                      {feature.icon}
                    </Avatar>
                    <Typography variant="h6" component="h3">
                      {feature.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Technology Stack */}
      <Box sx={{ mb: 6, textAlign: 'center' }}>
        <Typography variant="h4" component="h2" gutterBottom>
          Powered by Advanced AI
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap', mt: 3 }}>
          {[
            'HuggingFace Transformers',
            'OpenCV',
            'PyTorch',
            'Whisper AI',
            'MediaPipe',
            'FastAPI',
            'React'
          ].map((tech) => (
            <Chip 
              key={tech} 
              label={tech} 
              variant="outlined"
              sx={{ m: 0.5 }}
            />
          ))}
        </Box>
      </Box>

      {/* Call to Action */}
      <Box
        sx={{
          textAlign: 'center',
          py: 6,
          backgroundColor: 'background.paper',
          borderRadius: 2,
          mb: 4
        }}
      >
        <Typography variant="h4" component="h2" gutterBottom>
          Ready to Transform Your Videos?
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Join thousands of creators using VideoCraft AI to produce stunning content.
        </Typography>
        <Button
          variant="contained"
          size="large"
          startIcon={<CloudUpload />}
          onClick={() => navigate('/upload')}
        >
          Upload Your First Video
        </Button>
      </Box>
    </Container>
    </div>
  );
};

export default HomePage;
