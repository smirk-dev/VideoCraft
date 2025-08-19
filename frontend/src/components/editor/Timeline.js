import React, { useState, useRef, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  Slider
} from '@mui/material';
import {
  ContentCut,
  Delete,
  ZoomIn,
  ZoomOut
} from '@mui/icons-material';

const Timeline = ({ 
  duration, 
  currentTime, 
  onSeek, 
  trimStart, 
  trimEnd, 
  onTrimChange,
  cuts,
  onAddCut,
  onRemoveCut
}) => {
  const [zoom, setZoom] = useState(1);
  const [isDragging, setIsDragging] = useState(false);
  const [dragType, setDragType] = useState(null); // 'playhead', 'trimStart', 'trimEnd'
  const timelineRef = useRef(null);

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const getPixelPosition = (time) => {
    if (!timelineRef.current || duration === 0) return 0;
    const timelineWidth = timelineRef.current.offsetWidth - 40; // Account for padding
    return (time / duration) * timelineWidth * zoom;
  };

  const getTimeFromPixel = (pixel) => {
    if (!timelineRef.current || duration === 0) return 0;
    const timelineWidth = timelineRef.current.offsetWidth - 40;
    return Math.max(0, Math.min(duration, (pixel / (timelineWidth * zoom)) * duration));
  };

  const handleMouseDown = useCallback((e, type) => {
    setIsDragging(true);
    setDragType(type);
    e.preventDefault();
  }, []);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging || !timelineRef.current) return;

    const rect = timelineRef.current.getBoundingClientRect();
    const pixel = e.clientX - rect.left - 20; // Account for padding
    const time = getTimeFromPixel(pixel);

    if (dragType === 'playhead') {
      onSeek(time);
    } else if (dragType === 'trimStart') {
      const newTrimStart = Math.max(0, Math.min(time, trimEnd - 0.1));
      onTrimChange(newTrimStart, trimEnd);
    } else if (dragType === 'trimEnd') {
      const newTrimEnd = Math.min(duration, Math.max(time, trimStart + 0.1));
      onTrimChange(trimStart, newTrimEnd);
    }
  }, [isDragging, dragType, trimStart, trimEnd, duration, onSeek, onTrimChange]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    setDragType(null);
  }, []);

  const handleTimelineClick = useCallback((e) => {
    if (isDragging) return;

    const rect = timelineRef.current.getBoundingClientRect();
    const pixel = e.clientX - rect.left - 20;
    const time = getTimeFromPixel(pixel);

    // Check if clicking near a cut point (within 5 pixels)
    const cutPoint = cuts.find(cut => Math.abs(getPixelPosition(cut) - pixel) < 5);
    
    if (e.detail === 2) { // Double click
      if (cutPoint) {
        onRemoveCut(cutPoint);
      } else {
        onAddCut(time);
      }
    } else {
      onSeek(time);
    }
  }, [isDragging, cuts, onSeek, onAddCut, onRemoveCut]);

  // Add event listeners
  React.useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const handleZoomIn = () => setZoom(prev => Math.min(prev * 1.5, 5));
  const handleZoomOut = () => setZoom(prev => Math.max(prev / 1.5, 0.5));

  return (
    <Paper elevation={2} sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Timeline</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Add cut point (double-click timeline)">
            <IconButton size="small">
              <ContentCut />
            </IconButton>
          </Tooltip>
          <Tooltip title="Zoom out">
            <IconButton size="small" onClick={handleZoomOut}>
              <ZoomOut />
            </IconButton>
          </Tooltip>
          <Typography variant="caption" sx={{ mx: 1 }}>
            {Math.round(zoom * 100)}%
          </Typography>
          <Tooltip title="Zoom in">
            <IconButton size="small" onClick={handleZoomIn}>
              <ZoomIn />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Timeline Container */}
      <Box
        ref={timelineRef}
        sx={{
          position: 'relative',
          height: 80,
          backgroundColor: '#f0f0f0',
          borderRadius: 1,
          cursor: 'crosshair',
          overflow: 'hidden',
          p: '20px',
          userSelect: 'none'
        }}
        onClick={handleTimelineClick}
      >
        {/* Video Track */}
        <Box
          sx={{
            position: 'absolute',
            top: 30,
            left: 20,
            right: 20,
            height: 20,
            backgroundColor: '#2196f3',
            borderRadius: 1,
            opacity: 0.7
          }}
        />

        {/* Trim Start Handle */}
        <Box
          sx={{
            position: 'absolute',
            top: 25,
            left: getPixelPosition(trimStart) + 15,
            width: 10,
            height: 30,
            backgroundColor: '#ff5722',
            cursor: 'ew-resize',
            borderRadius: '2px 0 0 2px',
            zIndex: 3
          }}
          onMouseDown={(e) => handleMouseDown(e, 'trimStart')}
        >
          <Box
            sx={{
              position: 'absolute',
              top: -5,
              left: -5,
              width: 20,
              height: 40,
              cursor: 'ew-resize'
            }}
          />
        </Box>

        {/* Trim End Handle */}
        <Box
          sx={{
            position: 'absolute',
            top: 25,
            left: getPixelPosition(trimEnd || duration) + 15,
            width: 10,
            height: 30,
            backgroundColor: '#ff5722',
            cursor: 'ew-resize',
            borderRadius: '0 2px 2px 0',
            zIndex: 3
          }}
          onMouseDown={(e) => handleMouseDown(e, 'trimEnd')}
        >
          <Box
            sx={{
              position: 'absolute',
              top: -5,
              left: -5,
              width: 20,
              height: 40,
              cursor: 'ew-resize'
            }}
          />
        </Box>

        {/* Cut Points */}
        {cuts.map((cutTime, index) => (
          <Tooltip key={index} title={`Cut at ${formatTime(cutTime)} (double-click to remove)`}>
            <Box
              sx={{
                position: 'absolute',
                top: 20,
                left: getPixelPosition(cutTime) + 18,
                width: 4,
                height: 40,
                backgroundColor: '#ff9800',
                cursor: 'pointer',
                zIndex: 2,
                '&:hover': {
                  backgroundColor: '#f57c00',
                  width: 6,
                  left: getPixelPosition(cutTime) + 17
                }
              }}
            />
          </Tooltip>
        ))}

        {/* Playhead */}
        <Box
          sx={{
            position: 'absolute',
            top: 15,
            left: getPixelPosition(currentTime) + 18,
            width: 2,
            height: 50,
            backgroundColor: '#e91e63',
            cursor: 'ew-resize',
            zIndex: 4,
            '&::before': {
              content: '""',
              position: 'absolute',
              top: -8,
              left: -6,
              width: 14,
              height: 14,
              backgroundColor: '#e91e63',
              borderRadius: '50%'
            }
          }}
          onMouseDown={(e) => handleMouseDown(e, 'playhead')}
        />

        {/* Time Markers */}
        {Array.from({ length: Math.floor(duration / 10) + 1 }, (_, i) => i * 10).map((time) => (
          <Box key={time}>
            <Box
              sx={{
                position: 'absolute',
                top: 55,
                left: getPixelPosition(time) + 20,
                width: 1,
                height: 10,
                backgroundColor: '#333'
              }}
            />
            <Typography
              variant="caption"
              sx={{
                position: 'absolute',
                top: 67,
                left: getPixelPosition(time) + 12,
                fontSize: '10px',
                color: '#333',
                fontWeight: 'bold'
              }}
            >
              {formatTime(time)}
            </Typography>
          </Box>
        ))}
      </Box>

      {/* Timeline Info */}
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="body2" sx={{ color: '#333', fontWeight: 'medium' }}>
          Trim: {formatTime(trimStart)} - {formatTime(trimEnd || duration)} 
          ({formatTime((trimEnd || duration) - trimStart)} duration)
        </Typography>
        <Typography variant="body2" sx={{ color: '#333', fontWeight: 'medium' }}>
          {cuts.length} cut{cuts.length !== 1 ? 's' : ''}
        </Typography>
      </Box>

      {/* Instructions */}
      <Typography variant="caption" sx={{ mt: 1, display: 'block', color: '#555', fontWeight: 'medium' }}>
        💡 Click to seek • Double-click to add/remove cuts • Drag handles to trim • Drag playhead to scrub
      </Typography>
    </Paper>
  );
};

export default Timeline;
