import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Chip,
  CircularProgress,
  Alert,
  Box,
  Divider,
  Tooltip
} from '@mui/material';
import {
  Download as DownloadIcon,
  Restore as RestoreIcon,
  Close as CloseIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import fileService from '../../services/files';
import { formatFileSize, formatDate, formatRelativeTime } from '../../utils/formatters';

const VersionHistory = ({ open, onClose, file, onVersionChange }) => {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fileInfo, setFileInfo] = useState(null);

  useEffect(() => {
    if (open && file) {
      fetchVersions();
      fetchFileInfo();
    }
  }, [open, file]);

  const fetchVersions = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fileService.getFileVersions(file.id);
      setVersions(data);
    } catch (error) {
      setError('Failed to load version history');
      console.error('Error fetching versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFileInfo = async () => {
    try {
      const info = await fileService.getFileInfo(file.id);
      setFileInfo(info);
    } catch (error) {
      console.error('Error fetching file info:', error);
    }
  };

  const handleRollback = async (versionNumber) => {
    if (window.confirm(`Roll back to version ${versionNumber}? This will make version ${versionNumber} the current version.`)) {
      try {
        await fileService.rollbackVersion(file.id, versionNumber);
        await fetchVersions();
        if (onVersionChange) {
          onVersionChange();
        }
      } catch (error) {
        console.error('Rollback error:', error);
        setError('Failed to rollback version');
      }
    }
  };

  const handleDownloadCurrent = async () => {
    try {
      await fileService.downloadFile(file.id, file.filename);
    } catch (error) {
      console.error('Download error:', error);
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">
            Version History - {file?.filename}
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {fileInfo && (
          <Box sx={{ mb: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              File Information
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Chip 
                label={`Owner: ${fileInfo.owner}`} 
                size="small" 
                variant="outlined" 
              />
              <Chip 
                label={`Total Versions: ${fileInfo.versions}`} 
                size="small" 
                variant="outlined" 
                color="primary"
              />
              <Chip 
                label={`Total Size: ${formatFileSize(fileInfo.size)}`} 
                size="small" 
                variant="outlined" 
              />
            </Box>
          </Box>
        )}

        <Divider sx={{ mb: 2 }} />

        {loading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : versions.length === 0 ? (
          <Alert severity="info">No version history available</Alert>
        ) : (
          <>
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                Only the current version can be downloaded. To access an older version, rollback to it first.
              </Typography>
            </Alert>
            <List>
              {versions.map((version, index) => (
                <ListItem
                  key={version.version}
                  sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    bgcolor: index === 0 ? 'action.selected' : 'background.paper'
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1">
                          Version {version.version}
                        </Typography>
                        {index === 0 && (
                          <Chip 
                            label="Current" 
                            size="small" 
                            color="primary" 
                          />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          Size: {formatFileSize(version.size)}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Uploaded: {formatDate(version.uploaded_at)}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          ({formatRelativeTime(version.uploaded_at)})
                        </Typography>
                        {version.notes && (
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              <InfoIcon fontSize="small" />
                              {version.notes}
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    {/* Only show download button for current version */}
                    {index === 0 ? (
                      <Tooltip title="Download current version">
                        <IconButton
                          edge="end"
                          onClick={handleDownloadCurrent}
                        >
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                    ) : (
                      <Tooltip title="Rollback to this version">
                        <IconButton
                          edge="end"
                          onClick={() => handleRollback(version.version_number)}
                          color="primary"
                        >
                          <RestoreIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default VersionHistory;