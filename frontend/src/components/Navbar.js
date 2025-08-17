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
  Avatar
} from '@mui/material';
import {
  VideoLibrary,
  AccountCircle,
  Settings,
  Help
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const menuItems = [
    { label: 'Home', path: '/' },
    { label: 'Upload', path: '/upload' },
    { label: 'Editor', path: '/editor' },
    { label: 'Analysis', path: '/analysis' },
    { label: 'Projects', path: '/projects' }
  ];

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
