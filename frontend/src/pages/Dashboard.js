import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Tabs,
  Tab,
  Alert,
  Skeleton
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  FolderOpen as FolderIcon,
  Storage as StorageIcon,
  Assessment as StatsIcon,
  History as RecentIcon
} from '@mui/icons-material';
import Layout from '../components/Layout/Layout';
import FileUpload from '../components/FileManagement/FileUpload';
import FileList from '../components/FileManagement/FileList';
import { useAuth } from '../components/Auth/AuthContext';
import authService from '../services/auth';
import { formatFileSize } from '../utils/formatters';

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

const Dashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    fetchUserStats();
  }, []);

  const fetchUserStats = async () => {
    try {
      const userStats = await authService.getUserStats();
      setStats(userStats);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoadingStats(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleUploadSuccess = () => {
    setRefreshKey(prev => prev + 1);
    fetchUserStats();
    setActiveTab(1);
  };

  return (
    <Layout>
      <Box>
        {/* Welcome Section */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Welcome back, {user?.username}!
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage your cloud storage and files
          </Typography>
        </Box>

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <FolderIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Files
                    </Typography>
                    <Typography variant="h5">
                      {loadingStats ? (
                        <Skeleton width={50} />
                      ) : (
                        stats?.files_uploaded || 0
                      )}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <StorageIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Storage Used
                    </Typography>
                    <Typography variant="h5">
                      {loadingStats ? (
                        <Skeleton width={80} />
                      ) : (
                        stats?.storage_used || '0 Bytes'
                      )}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <StatsIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Account Type
                    </Typography>
                    <Typography variant="h5">
                      {user?.role === 'admin' ? 'Admin' : 'User'}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <RecentIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Storage Limit
                    </Typography>
                    <Typography variant="h5">
                      100 MB/file
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Main Content Area */}
        <Paper elevation={2}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeTab} onChange={handleTabChange}>
              <Tab 
                label="Upload Files" 
                icon={<UploadIcon />} 
                iconPosition="start"
              />
              <Tab 
                label="My Files" 
                icon={<FolderIcon />} 
                iconPosition="start"
              />
            </Tabs>
          </Box>

          <Box sx={{ p: 3 }}>
            <TabPanel value={activeTab} index={0}>
              <FileUpload onUploadSuccess={handleUploadSuccess} />
            </TabPanel>
            
            <TabPanel value={activeTab} index={1}>
              <FileList key={refreshKey} />
            </TabPanel>
          </Box>
        </Paper>

        {/* Help Section */}
        <Box sx={{ mt: 4 }}>
          <Alert severity="info">
            <Typography variant="subtitle2" gutterBottom>
              Quick Tips:
            </Typography>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              <li>Drag and drop files or click to browse</li>
              <li>Maximum file size is 100MB per file</li>
              <li>Upload multiple files at once</li>
              <li>Files with the same name create new versions</li>
              <li>Download multiple files as ZIP archive</li>
              <li>Share files with public links</li>
            </ul>
          </Alert>
        </Box>
      </Box>
    </Layout>
  );
};

export default Dashboard;
