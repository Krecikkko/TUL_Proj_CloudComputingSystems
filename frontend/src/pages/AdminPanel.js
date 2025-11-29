import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Alert
} from '@mui/material';
import {
  People as UsersIcon,
  MenuBook as LogBookIcon,
  Assessment as StatsIcon,
  AdminPanelSettings as AdminIcon
} from '@mui/icons-material';
import Layout from '../components/Layout/Layout';
import LogBook from '../components/Admin/LogBook';
import UserManagement from '../components/Admin/UserManagement';
import { useAuth } from '../components/Auth/AuthContext';

const TabPanel = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const AdminPanel = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  if (user?.role !== 'admin') {
    return (
      <Layout>
        <Alert severity="error">
          Access Denied: Admin privileges required
        </Alert>
      </Layout>
    );
  }

  return (
    <Layout maxWidth="xl">
      <Box>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <AdminIcon sx={{ fontSize: 32 }} />
            <Typography variant="h4">
              Admin Panel
            </Typography>
          </Box>
          <Typography variant="body1" color="textSecondary">
            System administration and monitoring
          </Typography>
        </Box>

        {/* Admin Content */}
        <Paper elevation={2}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeTab} onChange={handleTabChange}>
              <Tab 
                label="User Management" 
                icon={<UsersIcon />} 
                iconPosition="start"
              />
              <Tab 
                label="System LogBook" 
                icon={<LogBookIcon />} 
                iconPosition="start"
              />
            </Tabs>
          </Box>

          <Box sx={{ p: 3 }}>
            <TabPanel value={activeTab} index={0}>
              <UserManagement />
            </TabPanel>
            
            <TabPanel value={activeTab} index={1}>
              <LogBook />
            </TabPanel>
          </Box>
        </Paper>

        {/* Admin Info */}
        <Box sx={{ mt: 4 }}>
          <Alert severity="warning">
            <Typography variant="subtitle2" gutterBottom>
              Admin Guidelines:
            </Typography>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              <li>All admin actions are logged in the system</li>
              <li>Be careful when deleting users - this will also delete their files</li>
              <li>LogBook entries cannot be deleted or modified</li>
              <li>Export LogBook regularly for audit purposes</li>
            </ul>
          </Alert>
        </Box>
      </Box>
    </Layout>
  );
};

export default AdminPanel;
