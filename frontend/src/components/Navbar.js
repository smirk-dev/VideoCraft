import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Chip,
  Tooltip
} from '@mui/material';
import {
  VideoLibrary,
  AccountCircle,
  Settings,
  Help,
  PlayCircleOutline,
  Edit
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useVideo } from '../context/VideoContext';
import ExportButton from './common/ExportButton';

const Navbar = () => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const { hasVideo, currentVideo, videoMetadata, videoUrl, editingData } = useVideo();

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleVideoClick = () => {
    if (hasVideo()) {
      navigate('/editor');
    }
  };

  const menuItems = [
    { label: 'Home', path: '/' },
    { label: 'Upload', path: '/upload' },
    { label: 'Editor', path: '/editor' },
    { label: 'Analysis', path: '/analysis' },
    { label: 'Recommendations', path: '/recommendations' },
    { label: 'Projects', path: '/projects' }
  ];

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Prepare video data for export in navbar
  const getVideoData = () => {
    if (!hasVideo() || !currentVideo) {
      return null;
    }
    
    return {
      filename: currentVideo,
      url: videoUrl,
      metadata: videoMetadata || {},
      editingData: editingData || {
        trimStart: 0,
        trimEnd: videoMetadata?.duration || 0,
        cuts: [],
        filters: []
      },
      timeline: {
        duration: videoMetadata?.duration || 0,
        currentTime: 0,
        trimStart: editingData?.trimStart || 0,
        trimEnd: editingData?.trimEnd || videoMetadata?.duration || 0,
        cuts: editingData?.cuts || []
      }
    };
  };

  return (
    <AppBar position="static" sx={{ backgroundColor: '#1a1a1a' }}>
      <Toolbar>
        <VideoLibrary sx={{ mr: 2 }} />
        <Typography
          variant="h6"
          component="div"
          sx={{ flexGrow: 1, cursor: 'pointer' }}
          onClick={() => navigate('/')}
        >
          VideoCraft AI
        </Typography>
        
        {/* Video Indicator & Export */}
        {hasVideo() && (
          <Box sx={{ mr: 2, display: 'flex', gap: 1, alignItems: 'center' }}>
            <Tooltip title={`Click to edit: ${currentVideo} (${formatDuration(videoMetadata?.duration || 0)})`}>
              <Chip
                icon={<PlayCircleOutline />}
                label={currentVideo}
                onClick={handleVideoClick}
                sx={{
                  backgroundColor: '#2196f3',
                  color: 'white',
                  cursor: 'pointer',
                  '&:hover': {
                    backgroundColor: '#1976d2'
                  }
                }}
                deleteIcon={<Edit />}
                onDelete={handleVideoClick}
              />
            </Tooltip>
            <ExportButton
              videoData={getVideoData()}
              variant="contained"
              size="small"
            >
              Export
            </ExportButton>
          </Box>
        )}
        
        <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
          {menuItems.map((item) => (
            <Button
              key={item.path}
              color="inherit"
              onClick={() => navigate(item.path)}
              sx={{ mx: 1 }}
            >
              {item.label}
            </Button>
          ))}
        </Box>

        <Box sx={{ ml: 2 }}>
          <IconButton
            size="large"
            edge="end"
            aria-label="account of current user"
            aria-controls="primary-search-account-menu"
            aria-haspopup="true"
            onClick={handleProfileMenuOpen}
            color="inherit"
          >
            <AccountCircle />
          </IconButton>
        </Box>

        <Menu
          anchorEl={anchorEl}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          keepMounted
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={handleMenuClose}>
            <Settings sx={{ mr: 1 }} />
            Settings
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>
            <Help sx={{ mr: 1 }} />
            Help
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
