import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  CardActions,
  Chip,
  LinearProgress,
  IconButton,
  Tabs,
  Tab,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Stop,
  FastForward,
  FastRewind,
  VolumeUp,
  Fullscreen,
  Timeline,
  ContentCut,
  MovieFilter,
  ColorLens,
  MusicNote,
  Settings,
  Save,
  Download,
  Undo,
  Redo,
  ZoomIn,
  ZoomOut,
} from '@mui/icons-material';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const EditorPage = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(100);
  const [volume, setVolume] = useState(75);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <Box sx={{ flexGrow: 1, bgcolor: 'background.default', minHeight: '100vh' }}>
      <Container maxWidth="xl" sx={{ py: 2 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            🎬 Video Editor
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Professional timeline-based video editing with AI assistance
          </Typography>
        </Box>

        <Grid container spacing={2}>
          {/* Main Editor Area */}
          <Grid item xs={12} lg={9}>
            {/* Video Preview */}
            <Paper sx={{ mb: 2, p: 2 }}>
              <Box
                sx={{
                  bgcolor: 'black',
                  height: 400,
                  borderRadius: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mb: 2,
                }}
              >
                <Typography color="white" variant="h6">
                  Video Preview Area
                </Typography>
              </Box>

              {/* Video Controls */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <IconButton onClick={togglePlayPause}>
                  {isPlaying ? <Pause /> : <PlayArrow />}
                </IconButton>
                <IconButton>
                  <Stop />
                </IconButton>
                <IconButton>
                  <FastRewind />
                </IconButton>
                <IconButton>
                  <FastForward />
                </IconButton>
                <Box sx={{ flexGrow: 1, mx: 2 }}>
                  <LinearProgress
                    variant="determinate"
                    value={(currentTime / duration) * 100}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
                <Typography variant="body2" sx={{ minWidth: 80 }}>
                  {Math.floor(currentTime / 60)}:{(currentTime % 60).toString().padStart(2, '0')} / {Math.floor(duration / 60)}:{(duration % 60).toString().padStart(2, '0')}
                </Typography>
                <IconButton>
                  <VolumeUp />
                </IconButton>
                <IconButton>
                  <Fullscreen />
                </IconButton>
              </Box>
            </Paper>

            {/* Timeline */}
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Timeline sx={{ mr: 1 }} />
                <Typography variant="h6">Timeline</Typography>
                <Box sx={{ flexGrow: 1 }} />
                <IconButton size="small">
                  <ZoomOut />
                </IconButton>
                <Typography variant="body2" sx={{ mx: 1 }}>
                  100%
                </Typography>
                <IconButton size="small">
                  <ZoomIn />
                </IconButton>
              </Box>

              {/* Timeline Tracks */}
              <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1, minHeight: 200 }}>
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mt: 8 }}>
                  Timeline tracks will appear here
                  <br />
                  Drag and drop video files to start editing
                </Typography>
              </Box>
            </Paper>
          </Grid>

          {/* Right Sidebar */}
          <Grid item xs={12} lg={3}>
            {/* Tools Panel */}
            <Paper sx={{ mb: 2 }}>
              <Tabs value={currentTab} onChange={handleTabChange} variant="fullWidth">
                <Tab label="Tools" />
                <Tab label="Effects" />
                <Tab label="Audio" />
              </Tabs>

              <TabPanel value={currentTab} index={0}>
                {/* Editing Tools */}
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <ContentCut />
                    </ListItemIcon>
                    <ListItemText primary="Cut Tool" secondary="Split clips" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <Timeline />
                    </ListItemIcon>
                    <ListItemText primary="Trim Tool" secondary="Adjust clip length" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <MovieFilter />
                    </ListItemIcon>
                    <ListItemText primary="Transition" secondary="Add transitions" />
                  </ListItem>
                </List>

                <Divider sx={{ my: 2 }} />

                {/* AI Tools */}
                <Typography variant="subtitle2" gutterBottom>
                  🤖 AI Assistant
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemText primary="Auto Cut" secondary="AI-suggested cuts" />
                    <Button size="small" variant="outlined">
                      Analyze
                    </Button>
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Scene Detection" secondary="Find scene changes" />
                    <Button size="small" variant="outlined">
                      Detect
                    </Button>
                  </ListItem>
                </List>
              </TabPanel>

              <TabPanel value={currentTab} index={1}>
                {/* Effects */}
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <ColorLens />
                    </ListItemIcon>
                    <ListItemText primary="Color Correction" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <MovieFilter />
                    </ListItemIcon>
                    <ListItemText primary="Filters" />
                  </ListItem>
                </List>

                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                  🎨 AI Effects
                </Typography>
                <Button fullWidth variant="outlined" sx={{ mb: 1 }}>
                  Remove Background
                </Button>
                <Button fullWidth variant="outlined" sx={{ mb: 1 }}>
                  Enhance Quality
                </Button>
                <Button fullWidth variant="outlined">
                  Style Transfer
                </Button>
              </TabPanel>

              <TabPanel value={currentTab} index={2}>
                {/* Audio Tools */}
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <MusicNote />
                    </ListItemIcon>
                    <ListItemText primary="Add Music" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <VolumeUp />
                    </ListItemIcon>
                    <ListItemText primary="Audio Levels" />
                  </ListItem>
                </List>

                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                  🎵 AI Audio
                </Typography>
                <Button fullWidth variant="outlined" sx={{ mb: 1 }}>
                  Music Recommendations
                </Button>
                <Button fullWidth variant="outlined" sx={{ mb: 1 }}>
                  Remove Background Noise
                </Button>
                <Button fullWidth variant="outlined">
                  Audio Enhancement
                </Button>
              </TabPanel>
            </Paper>

            {/* Project Info */}
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Project Settings
              </Typography>
              
              <FormControlLabel
                control={<Switch defaultChecked />}
                label="Auto-save"
                sx={{ mb: 1 }}
              />
              <FormControlLabel
                control={<Switch />}
                label="AI Suggestions"
                sx={{ mb: 2 }}
              />

              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Button startIcon={<Undo />} size="small">
                  Undo
                </Button>
                <Button startIcon={<Redo />} size="small">
                  Redo
                </Button>
              </Box>

              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  startIcon={<Save />}
                  variant="contained"
                  size="small"
                  fullWidth
                >
                  Save
                </Button>
                <Button
                  startIcon={<Download />}
                  variant="outlined"
                  size="small"
                  fullWidth
                >
                  Export
                </Button>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default EditorPage;
