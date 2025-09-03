import React, { useState, useRef, useCallback } from 'react';
import { API_CONFIG } from '../config/api';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
  CircularProgress,
  Card,
  CardContent
} from '@mui/material';
import {
  CloudUpload,
  VideoLibrary,
  AudioFile,
  CheckCircle,
  Error,
  Info
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { useVideo } from '../context/VideoContext';
import axios from 'axios';

const API_BASE_URL = API_CONFIG.BASE_URL;

const UploadPage = () => {
  const navigate = useNavigate();
  const { uploadVideo, isProcessing } = useVideo();
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    setUploading(true);
    setError(null);
    setSuccess(null);

    for (const file of acceptedFiles) {
      try {
        // For video files, use the global video context AND create project
        if (file.type.includes('video')) {
          const result = await uploadVideo(file);
          
          if (result.success) {
            // Create project record in backend
            try {
              const projectResponse = await axios.post(`${API_BASE_URL}/api/projects/`, {
                title: file.name.replace(/\.[^/.]+$/, ""),
                description: `Video project created from ${file.name}`,
                original_filename: file.name,
                video_path: result.url,
                video_metadata: result.metadata,
                editing_data: {
                  trimStart: 0,
                  trimEnd: result.metadata.duration,
                  cuts: [],
                  filters: []
                },
                tags: ['new'],
                category: 'video'
              });

              setSuccess(`${file.name} uploaded and project created successfully! Redirecting to editor...`);
            } catch (projectError) {
              console.warn('Project creation failed, but video upload succeeded:', projectError);
              setSuccess(`${file.name} loaded successfully! Redirecting to editor...`);
            }
            
            // Redirect to editor after a short delay
            setTimeout(() => {
              navigate('/editor');
            }, 1500);
            
            return; // Exit early for video files since we're redirecting
          } else {
            throw new Error(result.error);
          }
        }

        // For audio files, continue with the original upload logic
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', file.name);
        formData.append('description', `Uploaded ${file.type.includes('video') ? 'video' : 'audio'} file`);

        const endpoint = file.type.includes('video') ? '/api/upload/video' : '/api/upload/audio';
        
        const response = await axios.post(`${API_BASE_URL}${endpoint}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 10 * 60 * 1000, // 10 minutes timeout for large files
          onUploadProgress: (progressEvent) => {
            if (progressEvent.lengthComputable) {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              console.log(`Upload progress: ${percentCompleted}%`);
            }
          },
        });

        if (response.status === 201) {
          setUploadedFiles(prev => [...prev, {
            ...response.data.data,
            file: file,
            status: 'success'
          }]);
          setSuccess(`${file.name} uploaded successfully!`);
        }
      } catch (err) {
        console.error('Upload error:', err);
        setError(`Failed to upload ${file.name}: ${err.response?.data?.detail || err.message}`);
        setUploadedFiles(prev => [...prev, {
          original_filename: file.name,
          file: file,
          status: 'error',
          error: err.response?.data?.detail || err.message
        }]);
      }
    }

    setUploading(false);
  }, [uploadVideo, navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
      'audio/*': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a']
    },
    multiple: true,
    maxSize: 2 * 1024 * 1024 * 1024 // 2GB
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const supportedFormats = {
    video: ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv'],
    audio: ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a', '.wma', '.aiff', '.au']
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Upload Your Content
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload videos and audio files to start analyzing and editing with AI-powered tools.
        </Typography>
      </Box>

      {/* Upload Area */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          mb: 4,
          textAlign: 'center',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.400',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover'
          }
        }}
      >
        <input {...getInputProps()} />
        <CloudUpload sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h5" gutterBottom>
          {isDragActive ? 'Drop files here...' : 'Drag & drop files here'}
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          or click to select files
        </Typography>
        <Button variant="contained" disabled={uploading || isProcessing}>
          {(uploading || isProcessing) ? <CircularProgress size={24} /> : 'Choose Files'}
        </Button>
        <Typography variant="caption" display="block" sx={{ mt: 2 }}>
          Maximum file size: 2GB
        </Typography>
      </Paper>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Uploaded Files */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Uploaded Files ({uploadedFiles.length})
              </Typography>
              {uploadedFiles.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Info sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="body1" color="text.secondary">
                    No files uploaded yet. Drag and drop files above to get started.
                  </Typography>
                </Box>
              ) : (
                <List>
                  {uploadedFiles.map((file, index) => (
                    <ListItem key={index} divider>
                      <ListItemIcon>
                        {file.status === 'success' ? (
                          <CheckCircle color="success" />
                        ) : file.status === 'error' ? (
                          <Error color="error" />
                        ) : file.file?.type.includes('video') ? (
                          <VideoLibrary />
                        ) : (
                          <AudioFile />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={file.original_filename || file.file?.name}
                        secondary={
                          <Box>
                            {file.file && (
                              <Typography variant="caption" display="block">
                                Size: {formatFileSize(file.file.size)} • 
                                Type: {file.file.type || 'Unknown'}
                              </Typography>
                            )}
                            {file.status === 'error' && (
                              <Typography variant="caption" color="error" display="block">
                                Error: {file.error}
                              </Typography>
                            )}
                            {file.upload_time && (
                              <Typography variant="caption" color="text.secondary" display="block">
                                Uploaded: {new Date(file.upload_time).toLocaleString()}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                      {file.status === 'success' && (
                        <Chip 
                          label="Ready for Analysis" 
                          color="success" 
                          size="small" 
                        />
                      )}
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Supported Formats */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Supported Formats
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Video Formats
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {supportedFormats.video.map((format) => (
                    <Chip 
                      key={format} 
                      label={format} 
                      size="small" 
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>

              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Audio Formats
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {supportedFormats.audio.map((format) => (
                    <Chip 
                      key={format} 
                      label={format} 
                      size="small" 
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Next Steps
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText 
                    primary="1. Upload your files"
                    secondary="Drag and drop or click to select"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="2. Analyze content"
                    secondary="Use AI to analyze video and audio"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="3. Edit and enhance"
                    secondary="Apply AI-powered editing tools"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="4. Export results"
                    secondary="Download your enhanced content"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default UploadPage;
