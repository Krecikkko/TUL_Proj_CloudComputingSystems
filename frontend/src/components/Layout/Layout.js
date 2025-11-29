import React from 'react';
import { Box, Container } from '@mui/material';
import Navbar from './Navbar';

const Layout = ({ children, maxWidth = 'lg' }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Container 
        component="main" 
        maxWidth={maxWidth}
        sx={{ 
          flexGrow: 1, 
          py: 4,
          px: { xs: 2, sm: 3 }
        }}
      >
        {children}
      </Container>
      <Box
        component="footer"
        sx={{
          py: 2,
          px: 2,
          mt: 'auto',
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[200]
              : theme.palette.grey[800],
          textAlign: 'center'
        }}
      >
        <small>© 2025 Cloud Storage System - TUL Project</small>
      </Box>
    </Box>
  );
};

export default Layout;
