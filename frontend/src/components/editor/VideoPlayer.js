import React, { useRef, useEffect, useState, useCallback } from 'react';
import {
  Box,
  IconButton,
  Typography,
  Slider,
  Paper
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  VolumeUp,
  VolumeOff,
  Fullscreen
} from '@mui/icons-material';

const VideoPlayer = ({ 
  videoUrl, 
  currentTime, 
  onTimeUpdate, 
  playing, 
  onPlayPause,
  trimStart = 0,
  trimEnd = null,
  cuts = [],
  filters = []
}) => {
  const videoRef = useRef(null);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [muted, setMuted] = useState(false);

  // Format time for display
  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  // Handle video metadata loaded
  const handleLoadedMetadata = useCallback(() => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  }, []);

  // Handle time update
  const handleTimeUpdate = useCallback(() => {
    if (videoRef.current && onTimeUpdate) {
      const time = videoRef.current.currentTime;
      
      // Check if we've hit trim end
      if (trimEnd && time >= trimEnd) {
        videoRef.current.pause();
        onPlayPause(false);
        return;
      }
      
      // Check if we've hit a cut point - skip to next segment
      const cutPoint = cuts.find(cut => Math.abs(time - cut) < 0.1);
      if (cutPoint) {
        const nextSegmentStart = cuts.find(cut => cut > cutPoint + 0.5);
        if (nextSegmentStart) {
          videoRef.current.currentTime = nextSegmentStart;
        }
      }
      
      onTimeUpdate(time);
    }
  }, [onTimeUpdate, trimEnd, cuts, onPlayPause]);

  // Sync video playing state
  useEffect(() => {
    if (videoRef.current) {
      if (playing) {
        videoRef.current.play();
      } else {
        videoRef.current.pause();
      }
    }
  }, [playing]);

  // Sync current time
  useEffect(() => {
    if (videoRef.current && Math.abs(videoRef.current.currentTime - currentTime) > 0.5) {
      videoRef.current.currentTime = currentTime;
    }
  }, [currentTime]);

  // Apply CSS filters
  const getFilterStyle = () => {
    let filterString = '';
    
    filters.forEach(filter => {
      switch (filter.type) {
        case 'brightness':
          filterString += `brightness(${filter.value}%) `;
          break;
        case 'contrast':
          filterString += `contrast(${filter.value}%) `;
          break;
        case 'saturation':
          filterString += `saturate(${filter.value}%) `;
          break;
        case 'blur':
          filterString += `blur(${filter.value}px) `;
          break;
        case 'grayscale':
          filterString += `grayscale(${filter.value}%) `;
          break;
        case 'sepia':
          filterString += `sepia(${filter.value}%) `;
          break;
        case 'hue-rotate':
          filterString += `hue-rotate(${filter.value}deg) `;
          break;
        default:
          break;
      }
    });
    
    return filterString.trim() || 'none';
  };

  const handleVolumeChange = (event, newValue) => {
    const volumeValue = newValue / 100;
    setVolume(volumeValue);
    if (videoRef.current) {
      videoRef.current.volume = volumeValue;
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !muted;
      setMuted(!muted);
    }
  };

  const toggleFullscreen = () => {
    if (videoRef.current) {
      if (videoRef.current.requestFullscreen) {
        videoRef.current.requestFullscreen();
      }
    }
  };

  const handleSeek = (event, newValue) => {
    if (videoRef.current) {
      const time = (newValue / 100) * duration;
      
      // Ensure we don't seek before trim start or after trim end
      let adjustedTime = Math.max(time, trimStart);
      if (trimEnd) {
        adjustedTime = Math.min(adjustedTime, trimEnd);
      }
      
      videoRef.current.currentTime = adjustedTime;
      onTimeUpdate(adjustedTime);
    }
  };

  const getSeekPosition = () => {
    if (duration === 0) return 0;
    return (currentTime / duration) * 100;
  };

  return (
    <Paper elevation={3} sx={{ overflow: 'hidden' }}>
      <Box sx={{ position: 'relative', backgroundColor: '#000' }}>
        {/* Video Element */}
        <video
          ref={videoRef}
          src={videoUrl}
          style={{
            width: '100%',
            height: '400px',
            objectFit: 'contain',
            filter: getFilterStyle()
          }}
          onLoadedMetadata={handleLoadedMetadata}
          onTimeUpdate={handleTimeUpdate}
          onError={(e) => console.error('Video error:', e)}
        />

        {/* Trim Overlay Indicators */}
        {(trimStart > 0 || trimEnd < duration) && (
          <>
            {/* Left trim overlay */}
            {trimStart > 0 && (
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: `${(trimStart / duration) * 100}%`,
                  height: '100%',
                  backgroundColor: 'rgba(255, 0, 0, 0.3)',
                  pointerEvents: 'none',
                  zIndex: 1
                }}
              />
            )}
            
            {/* Right trim overlay */}
            {trimEnd && trimEnd < duration && (
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  right: 0,
                  width: `${((duration - trimEnd) / duration) * 100}%`,
                  height: '100%',
                  backgroundColor: 'rgba(255, 0, 0, 0.3)',
                  pointerEvents: 'none',
                  zIndex: 1
                }}
              />
            )}
          </>
        )}

        {/* Cut Point Indicators */}
        {cuts.map((cutTime, index) => (
          <Box
            key={index}
            sx={{
              position: 'absolute',
              top: 0,
              left: `${(cutTime / duration) * 100}%`,
              width: '2px',
              height: '100%',
              backgroundColor: '#ff9800',
              zIndex: 2,
              pointerEvents: 'none'
            }}
          />
        ))}
      </Box>

      {/* Controls */}
      <Box sx={{ p: 2, backgroundColor: '#ffffff', borderTop: '1px solid #e0e0e0' }}>
        {/* Seek Bar */}
        <Box sx={{ mb: 2 }}>
          <Slider
            value={getSeekPosition()}
            onChange={handleSeek}
            aria-labelledby="video-seek-slider"
            sx={{
              '& .MuiSlider-track': {
                backgroundColor: '#2196f3'
              },
              '& .MuiSlider-thumb': {
                backgroundColor: '#2196f3'
              }
            }}
          />
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="caption" sx={{ color: '#333', fontWeight: 'medium' }}>
              {formatTime(currentTime)}
            </Typography>
            <Typography variant="caption" sx={{ color: '#333', fontWeight: 'medium' }}>
              {formatTime(duration)}
            </Typography>
          </Box>
        </Box>

        {/* Control Buttons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Play/Pause */}
          <IconButton onClick={() => onPlayPause(!playing)} color="primary">
            {playing ? <Pause /> : <PlayArrow />}
          </IconButton>

          {/* Volume Controls */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 120 }}>
            <IconButton onClick={toggleMute} size="small">
              {muted ? <VolumeOff /> : <VolumeUp />}
            </IconButton>
            <Slider
              value={muted ? 0 : volume * 100}
              onChange={handleVolumeChange}
              aria-labelledby="volume-slider"
              size="small"
              sx={{ width: 80 }}
            />
          </Box>

          {/* Time Display */}
          <Typography variant="body2" sx={{ ml: 'auto', mr: 2, color: '#333', fontWeight: 'medium' }}>
            {formatTime(currentTime)} / {formatTime(duration)}
          </Typography>

          {/* Fullscreen */}
          <IconButton onClick={toggleFullscreen} size="small">
            <Fullscreen />
          </IconButton>
        </Box>
      </Box>
    </Paper>
  );
};

export default VideoPlayer;
