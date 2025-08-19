import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  IconButton,
  TextField,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert
} from '@mui/material';
import {
  ContentCut,
  Delete,
  Undo,
  Save,
  PlayArrow,
  Stop,
  Info
} from '@mui/icons-material';
import ExportButton from '../common/ExportButton';

const EditingControls = ({ 
  currentTime,
  duration,
  trimStart,
  trimEnd,
  cuts,
  onTrimChange,
  onAddCut,
  onRemoveCut,
  onClearAllCuts,
  videoName,
  videoUrl,
  videoMetadata,
  editingData
}) => {
  const [trimDialog, setTrimDialog] = useState(false);
  const [tempTrimStart, setTempTrimStart] = useState(trimStart);
  const [tempTrimEnd, setTempTrimEnd] = useState(trimEnd || duration);

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const parseTimeInput = (timeString) => {
    const parts = timeString.split(':');
    if (parts.length === 2) {
      const minutes = parseInt(parts[0]) || 0;
      const seconds = parseInt(parts[1]) || 0;
      return minutes * 60 + seconds;
    }
    return parseFloat(timeString) || 0;
  };

  // Prepare video data for export
  const getVideoData = () => {
    if (!videoName || !videoUrl) {
      return null;
    }
    
    return {
      filename: videoName,
      url: videoUrl,
      metadata: videoMetadata || {},
      editingData: editingData || {
        trimStart,
        trimEnd: trimEnd || duration,
        cuts,
        filters: []
      },
      timeline: {
        duration: duration || 0,
        currentTime: currentTime || 0,
        trimStart: trimStart || 0,
        trimEnd: trimEnd || duration || 0,
        cuts: cuts || []
      }
    };
  };

  const handleTrimToCurrentTime = () => {
    setTempTrimStart(0);
    setTempTrimEnd(currentTime);
    setTrimDialog(true);
  };

  const handleTrimFromCurrentTime = () => {
    setTempTrimStart(currentTime);
    setTempTrimEnd(duration);
    setTrimDialog(true);
  };

  const handleSetTrimStart = () => {
    onTrimChange(currentTime, trimEnd || duration);
  };

  const handleSetTrimEnd = () => {
    onTrimChange(trimStart, currentTime);
  };

  const handleApplyTrim = () => {
    const start = Math.max(0, Math.min(tempTrimStart, duration - 0.1));
    const end = Math.min(duration, Math.max(tempTrimEnd, start + 0.1));
    onTrimChange(start, end);
    setTrimDialog(false);
  };

  const handleAddCutAtCurrentTime = () => {
    onAddCut(currentTime);
  };

  const getTrimmedDuration = () => {
    return (trimEnd || duration) - trimStart;
  };

  const getFinalDuration = () => {
    let totalDuration = getTrimmedDuration();
    
    // Subtract cut segments (simplified calculation)
    // In a real implementation, this would calculate exact segments
    if (cuts.length > 0) {
      // Rough estimate: each cut removes about 0.1 seconds
      totalDuration -= cuts.length * 0.1;
    }
    
    return Math.max(0, totalDuration);
  };

  const getSegmentCount = () => {
    return cuts.length + 1;
  };

  return (
    <>
      <Paper elevation={2} sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Editing Controls
        </Typography>

        {/* Video Info */}
        <Box sx={{ mb: 3, p: 2, backgroundColor: '#ffffff', borderRadius: 1, border: '1px solid #e0e0e0' }}>
          <Typography variant="subtitle2" gutterBottom sx={{ color: '#333', fontWeight: 'medium' }}>
            Video: {videoName}
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" sx={{ color: '#333', fontWeight: 'medium' }}>
                Original Duration
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#222' }}>
                {formatTime(duration)}
              </Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" sx={{ color: '#333', fontWeight: 'medium' }}>
                Trimmed Duration
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#222' }}>
                {formatTime(getTrimmedDuration())}
              </Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" sx={{ color: '#333', fontWeight: 'medium' }}>
                Final Duration
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#222' }}>
                {formatTime(getFinalDuration())}
              </Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="caption" sx={{ color: '#333', fontWeight: 'medium' }}>
                Segments
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#222' }}>
                {getSegmentCount()}
              </Typography>
            </Grid>
          </Grid>
        </Box>

        {/* Trim Controls */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Trim Controls
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Button
                variant="outlined"
                fullWidth
                onClick={handleSetTrimStart}
                startIcon={<PlayArrow />}
              >
                Set Start Here ({formatTime(currentTime)})
              </Button>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Button
                variant="outlined"
                fullWidth
                onClick={handleSetTrimEnd}
                startIcon={<Stop />}
              >
                Set End Here ({formatTime(currentTime)})
              </Button>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Button
                variant="outlined"
                fullWidth
                onClick={handleTrimToCurrentTime}
              >
                Trim to Current Time
              </Button>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Button
                variant="outlined"
                fullWidth
                onClick={handleTrimFromCurrentTime}
              >
                Trim from Current Time
              </Button>
            </Grid>
          </Grid>

          {/* Current Trim Display */}
          <Box sx={{ mt: 2, p: 2, backgroundColor: '#f0f8ff', borderRadius: 1, border: '1px solid #2196f3' }}>
            <Typography variant="body2" sx={{ color: '#333', fontWeight: 'medium' }}>
              Current Trim: {formatTime(trimStart)} - {formatTime(trimEnd || duration)} 
              <Chip 
                label={`${formatTime(getTrimmedDuration())} remaining`} 
                size="small" 
                color="primary" 
                sx={{ ml: 1 }}
              />
            </Typography>
          </Box>
        </Box>

        {/* Cut Controls */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            Cut Controls
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Button
                variant="outlined"
                fullWidth
                onClick={handleAddCutAtCurrentTime}
                startIcon={<ContentCut />}
                color="warning"
              >
                Add Cut at {formatTime(currentTime)}
              </Button>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Button
                variant="outlined"
                fullWidth
                onClick={onClearAllCuts}
                startIcon={<Delete />}
                color="error"
                disabled={cuts.length === 0}
              >
                Clear All Cuts ({cuts.length})
              </Button>
            </Grid>
          </Grid>

          {/* Cut Points Display */}
          {cuts.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" sx={{ mb: 1, color: '#333', fontWeight: 'medium' }}>
                Cut Points:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {cuts.map((cutTime, index) => (
                  <Chip
                    key={index}
                    label={formatTime(cutTime)}
                    onDelete={() => onRemoveCut(cutTime)}
                    deleteIcon={<Delete />}
                    color="warning"
                    variant="outlined"
                    size="small"
                  />
                ))}
              </Box>
            </Box>
          )}
        </Box>

        {/* Instructions */}
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="body2">
            <strong>How to use:</strong><br/>
            • <strong>Trim:</strong> Set start/end points to remove unwanted sections from beginning/end<br/>
            • <strong>Cut:</strong> Add cut points to remove sections from the middle<br/>
            • <strong>Timeline:</strong> Double-click timeline to add cuts, drag handles to adjust trim
          </Typography>
        </Alert>

        {/* Quick Actions */}
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            startIcon={<Save />}
            size="small"
          >
            Save Project
          </Button>
          <Button
            variant="outlined"
            startIcon={<Undo />}
            size="small"
            onClick={() => {
              onTrimChange(0, duration);
              onClearAllCuts();
            }}
          >
            Reset All
          </Button>
          <ExportButton
            videoData={getVideoData()}
            variant="contained"
            size="small"
            color="primary"
          >
            Export
          </ExportButton>
        </Box>
      </Paper>

      {/* Trim Dialog */}
      <Dialog open={trimDialog} onClose={() => setTrimDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Set Trim Points</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={6}>
              <TextField
                label="Start Time (MM:SS)"
                value={formatTime(tempTrimStart)}
                onChange={(e) => {
                  const time = parseTimeInput(e.target.value);
                  setTempTrimStart(Math.max(0, Math.min(time, duration)));
                }}
                fullWidth
                size="small"
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                label="End Time (MM:SS)"
                value={formatTime(tempTrimEnd)}
                onChange={(e) => {
                  const time = parseTimeInput(e.target.value);
                  setTempTrimEnd(Math.max(0, Math.min(time, duration)));
                }}
                fullWidth
                size="small"
              />
            </Grid>
          </Grid>
          <Typography variant="body2" sx={{ mt: 2, color: '#333', fontWeight: 'medium' }}>
            Resulting duration: {formatTime(Math.max(0, tempTrimEnd - tempTrimStart))}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTrimDialog(false)}>Cancel</Button>
          <Button onClick={handleApplyTrim} variant="contained">Apply Trim</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default EditingControls;
