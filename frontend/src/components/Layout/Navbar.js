import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Box,
  Avatar,
  Divider,
  Chip
} from '@mui/material';
import {
  CloudUpload as CloudIcon,
  AccountCircle as AccountIcon,
  Dashboard as DashboardIcon,
  AdminPanelSettings as AdminIcon,
  Logout as LogoutIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { useAuth } from '../Auth/AuthContext';
import { APP_NAME } from '../../utils/constants';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, isAdmin } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleClose();
    await logout();
  };

  const handleNavigation = (path) => {
    handleClose();
    navigate(path);
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    const parts = name.split(' ');
    return parts.map(part => part[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <AppBar position="sticky">
      <Toolbar>
        <CloudIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 0, mr: 4 }}>
          {APP_NAME}
        </Typography>

        {user && (
          <Box sx={{ flexGrow: 1, display: 'flex', gap: 2 }}>
            <Button
              color="inherit"
              startIcon={<DashboardIcon />}
              onClick={() => navigate('/dashboard')}
              sx={{
                backgroundColor: location.pathname === '/dashboard' ? 'rgba(255,255,255,0.1)' : 'transparent'
              }}
            >
              Dashboard
            </Button>
            
            {isAdmin() && (
              <Button
                color="inherit"
                startIcon={<AdminIcon />}
                onClick={() => navigate('/admin')}
                sx={{
                  backgroundColor: location.pathname === '/admin' ? 'rgba(255,255,255,0.1)' : 'transparent'
                }}
              >
                Admin Panel
              </Button>
            )}
          </Box>
        )}

        <Box sx={{ flexGrow: 1 }} />

        {user ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
              {user.username}
            </Typography>
            
            {isAdmin() && (
              <Chip
                label="ADMIN"
                size="small"
                color="warning"
                sx={{ display: { xs: 'none', sm: 'flex' } }}
              />
            )}

            <IconButton
              size="large"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                {getInitials(user.username)}
              </Avatar>
            </IconButton>
            
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
            >
              <MenuItem disabled>
                <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                  <Typography variant="subtitle2">{user.username}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {user.email}
                  </Typography>
                </Box>
              </MenuItem>
              
              <Divider />
              
              <MenuItem onClick={() => handleNavigation('/profile')}>
                <PersonIcon sx={{ mr: 2 }} />
                Profile
              </MenuItem>
              
              <MenuItem onClick={() => handleNavigation('/dashboard')}>
                <DashboardIcon sx={{ mr: 2 }} />
                Dashboard
              </MenuItem>
              
              {isAdmin() && (
                <MenuItem onClick={() => handleNavigation('/admin')}>
                  <AdminIcon sx={{ mr: 2 }} />
                  Admin Panel
                </MenuItem>
              )}
              
              <Divider />
              
              <MenuItem onClick={handleLogout}>
                <LogoutIcon sx={{ mr: 2 }} />
                Logout
              </MenuItem>
            </Menu>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              color="inherit"
              onClick={() => navigate('/login')}
              sx={{
                backgroundColor: location.pathname === '/login' ? 'rgba(255,255,255,0.1)' : 'transparent'
              }}
            >
              Login
            </Button>
            <Button
              variant="outlined"
              sx={{ 
                color: 'white',
                borderColor: 'white',
                '&:hover': {
                  borderColor: 'white',
                  backgroundColor: 'rgba(255,255,255,0.1)'
                }
              }}
              onClick={() => navigate('/register')}
            >
              Register
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
