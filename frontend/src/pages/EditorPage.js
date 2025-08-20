import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Button,
  Alert,
  Tabs,
  Tab,
  Divider,
  CircularProgress
} from '@mui/material';
import {
  Save,
  Download,
  Upload,
  Info,
  GetApp
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useVideo } from '../context/VideoContext';
import VideoPlayer from '../components/editor/VideoPlayer';
import Timeline from '../components/editor/Timeline';
import EditingControls from '../components/editor/EditingControls';
import FilterControls from '../components/editor/FilterControls';
import ExportDialog from '../components/export/ExportDialog';
import SaveProjectDialog from '../components/common/SaveProjectDialog';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 2 }}>{children}</Box>}
    </div>
  );
}

const EditorPage = () => {
  const navigate = useNavigate();
  const {
    hasVideo,
    currentVideo,
    videoUrl,
    videoMetadata,
    editingData,
    updateEditingData,
    addTrimPoint,
    addCut,
    removeCut,
    addFilter,
    removeFilter,
    isProcessing,
    currentProject,
    saveProject,
    error
  } = useVideo();

  const [currentTab, setCurrentTab] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [saveProjectDialogOpen, setSaveProjectDialogOpen] = useState(false);

  // Initialize editing data when video loads
  useEffect(() => {
    if (hasVideo() && videoMetadata && editingData.trimEnd === null) {
      updateEditingData({
        trimEnd: videoMetadata.duration
      });
    }
  }, [hasVideo, videoMetadata, editingData.trimEnd, updateEditingData]);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const handleTimeUpdate = useCallback((time) => {
    setCurrentTime(time);
  }, []);

  const handlePlayPause = useCallback((isPlaying) => {
    setPlaying(isPlaying);
  }, []);

  const handleSeek = useCallback((time) => {
    setCurrentTime(time);
  }, []);

  const handleTrimChange = useCallback((start, end) => {
    addTrimPoint(start, end);
  }, [addTrimPoint]);

  const handleAddCut = useCallback((time) => {
    addCut(time);
  }, [addCut]);

  const handleRemoveCut = useCallback((time) => {
    removeCut(time);
  }, [removeCut]);

  const handleClearAllCuts = useCallback(() => {
    editingData.cuts.forEach(cut => removeCut(cut));
  }, [editingData.cuts, removeCut]);

  const handleFiltersChange = useCallback((filters) => {
    updateEditingData({ filters });
  }, [updateEditingData]);

  const getDuration = () => {
    return videoMetadata?.duration || 0;
  };

  // Handle export functions
  const handleExportClick = () => {
    setExportDialogOpen(true);
  };

  const handleExportClose = () => {
    setExportDialogOpen(false);
  };

  // Handle save project functions
  const handleSaveProjectClick = () => {
    setSaveProjectDialogOpen(true);
  };

  const handleSaveProjectClose = () => {
    setSaveProjectDialogOpen(false);
  };

  const handleSaveProject = async (projectName, description, status) => {
    const result = await saveProject(projectName, description);
    return result;
  };

  // Prepare video data for export
  const getVideoData = () => ({
    filename: currentVideo,
    url: videoUrl,
    metadata: videoMetadata,
    editingData: editingData,
    timeline: {
      duration: getDuration(),
      currentTime: currentTime,
      trimStart: editingData.trimStart,
      trimEnd: editingData.trimEnd,
      cuts: editingData.cuts
    }
  });

  // If no video is loaded, show upload prompt
  if (!hasVideo()) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h4" gutterBottom>
            🎬 Video Editor
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            No video loaded. Please upload a video to start editing.
          </Typography>
          <Button
            variant="contained"
            startIcon={<Upload />}
            onClick={() => navigate('/upload')}
            size="large"
          >
            Upload Video
          </Button>
        </Paper>
      </Container>
    );
  }

  // Show loading state
  if (isProcessing) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography variant="h6">Processing video...</Typography>
        </Paper>
      </Container>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, bgcolor: 'background.default', minHeight: '100vh' }}>
      <Container maxWidth="xl" sx={{ py: 2 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            🎬 Video Editor
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Editing: <strong>{currentVideo}</strong> • {videoMetadata && `${Math.round(videoMetadata.duration)}s • ${videoMetadata.width}x${videoMetadata.height}`}
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {/* Main Editor Area */}
          <Grid item xs={12} lg={8}>
            {/* Video Player */}
            <Box sx={{ mb: 3 }}>
              <VideoPlayer
                videoUrl={videoUrl}
                currentTime={currentTime}
                onTimeUpdate={handleTimeUpdate}
                playing={playing}
                onPlayPause={handlePlayPause}
                trimStart={editingData.trimStart}
                trimEnd={editingData.trimEnd}
                cuts={editingData.cuts}
                filters={editingData.filters}
              />
            </Box>

            {/* Timeline */}
            <Box sx={{ mb: 3 }}>
              <Timeline
                duration={getDuration()}
                currentTime={currentTime}
                onSeek={handleSeek}
                trimStart={editingData.trimStart}
                trimEnd={editingData.trimEnd}
                onTrimChange={handleTrimChange}
                cuts={editingData.cuts}
                onAddCut={handleAddCut}
                onRemoveCut={handleRemoveCut}
              />
            </Box>

            {/* Export Controls */}
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Export & Save
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  startIcon={<Save />}
                  variant="contained"
                  onClick={handleSaveProjectClick}
                  disabled={isProcessing}
                >
                  {currentProject ? 'Update Project' : 'Save Project'}
                </Button>
                <Button
                  startIcon={<GetApp />}
                  variant="contained"
                  color="primary"
                  onClick={handleExportClick}
                >
                  Export Video & Reports
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/analysis')}
                >
                  Analyze Video
                </Button>
              </Box>
              {currentProject && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    <strong>Current Project:</strong> {currentProject.name}
                    <br />
                    <strong>Last Modified:</strong> {new Date(currentProject.date_modified).toLocaleString()}
                  </Typography>
                </Alert>
              )}
            </Paper>
          </Grid>

          {/* Right Sidebar */}
          <Grid item xs={12} lg={4}>
            {/* Tools Panel */}
            <Paper sx={{ mb: 2 }}>
              <Tabs value={currentTab} onChange={handleTabChange} variant="fullWidth">
                <Tab label="Edit" />
                <Tab label="Filters" />
                <Tab label="Info" />
              </Tabs>

              <TabPanel value={currentTab} index={0}>
                <EditingControls
                  currentTime={currentTime}
                  duration={getDuration()}
                  trimStart={editingData.trimStart}
                  trimEnd={editingData.trimEnd}
                  cuts={editingData.cuts}
                  onTrimChange={handleTrimChange}
                  onAddCut={handleAddCut}
                  onRemoveCut={handleRemoveCut}
                  onClearAllCuts={handleClearAllCuts}
                  videoName={currentVideo}
                  videoUrl={videoUrl}
                  videoMetadata={videoMetadata}
                  editingData={editingData}
                />
              </TabPanel>

              <TabPanel value={currentTab} index={1}>
                <FilterControls
                  filters={editingData.filters}
                  onFiltersChange={handleFiltersChange}
                />
              </TabPanel>

              <TabPanel value={currentTab} index={2}>
                {/* Video Information */}
                <Typography variant="h6" gutterBottom>
                  Video Information
                </Typography>
                
                {videoMetadata && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      <strong>File:</strong> {currentVideo}
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      <strong>Duration:</strong> {Math.round(videoMetadata.duration)}s
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      <strong>Resolution:</strong> {videoMetadata.width}x{videoMetadata.height}
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      <strong>Size:</strong> {(videoMetadata.size / (1024 * 1024)).toFixed(2)} MB
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      <strong>Type:</strong> {videoMetadata.type}
                    </Typography>
                  </Box>
                )}

                <Divider sx={{ my: 2 }} />

                <Typography variant="h6" gutterBottom>
                  Editing Summary
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>Trim Range:</strong> {editingData.trimStart.toFixed(1)}s - {(editingData.trimEnd || getDuration()).toFixed(1)}s
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>Cut Points:</strong> {editingData.cuts.length}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>Filters Applied:</strong> {editingData.filters.length}
                </Typography>

                <Divider sx={{ my: 2 }} />

                {/* Instructions */}
                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    <strong>Quick Tips:</strong><br/>
                    • Use the timeline to navigate<br/>
                    • Double-click timeline to add cuts<br/>
                    • Drag trim handles to adjust range<br/>
                    • Apply filters in real-time<br/>
                    • Save your project regularly
                  </Typography>
                </Alert>
              </TabPanel>
            </Paper>
          </Grid>
        </Grid>

        {/* Export Dialog */}
        <ExportDialog
          open={exportDialogOpen}
          onClose={handleExportClose}
          videoData={getVideoData()}
        />

        {/* Save Project Dialog */}
        <SaveProjectDialog
          open={saveProjectDialogOpen}
          onClose={handleSaveProjectClose}
          onSave={handleSaveProject}
          currentProject={currentProject}
          isProcessing={isProcessing}
          error={error}
        />
      </Container>
    </Box>
  );
};

export default EditorPage;
