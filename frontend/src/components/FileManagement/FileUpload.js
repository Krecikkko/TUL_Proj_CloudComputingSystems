import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  TextField
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import fileService from '../../services/files';
import { formatFileSize, validateFileSize } from '../../utils/formatters';
import { MAX_FILE_SIZE_MB } from '../../utils/constants';

const FileUpload = ({ onUploadSuccess }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [notes, setNotes] = useState('');

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
  const validFiles = acceptedFiles.map(file => {
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      return {
        file,
        name: file.name,
        size: file.size,
        status: 'error',
        progress: 0,
        error: `File size exceeds ${MAX_FILE_SIZE_MB}MB limit`
      };
    }
    return {
      file,
      name: file.name,
      size: file.size,
      status: 'pending',
      progress: 0,
      error: null
    };
  });

  const invalidFiles = rejectedFiles.map(({ file, errors }) => ({
    file,
    name: file.name,
    size: file.size,
    status: 'error',
    progress: 0,
    error: file.size > MAX_FILE_SIZE_MB * 1024 * 1024 
      ? `File size exceeds ${MAX_FILE_SIZE_MB}MB limit (file is ${(file.size / (1024 * 1024)).toFixed(2)}MB)`
      : errors[0]?.message || 'Invalid file'
  }));

  setFiles(prev => [...prev, ...validFiles, ...invalidFiles]);
}, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxSize: MAX_FILE_SIZE_MB * 1024 * 1024,
    multiple: true
  });

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    setUploading(true);
    const pendingFiles = files.filter(f => f.status === 'pending');

    for (let i = 0; i < pendingFiles.length; i++) {
      const fileItem = pendingFiles[i];
      const fileIndex = files.findIndex(f => f === fileItem);

      try {
        setFiles(prev => prev.map((f, idx) => 
          idx === fileIndex ? { ...f, status: 'uploading' } : f
        ));

        await fileService.uploadFile(
          fileItem.file,
          notes,
          (progress) => {
            setFiles(prev => prev.map((f, idx) => 
              idx === fileIndex ? { ...f, progress } : f
            ));
          }
        );

        setFiles(prev => prev.map((f, idx) => 
          idx === fileIndex ? { ...f, status: 'success', progress: 100 } : f
        ));
      } catch (error) {
        setFiles(prev => prev.map((f, idx) => 
          idx === fileIndex ? { 
            ...f, 
            status: 'error', 
            error: error.detail || 'Upload failed' 
          } : f
        ));
      }
    }

    setUploading(false);
    setNotes('');
    
    if (onUploadSuccess) {
      onUploadSuccess();
    }

    setTimeout(() => {
      setFiles(prev => prev.filter(f => f.status !== 'success'));
    }, 3000);
  };

  const clearAll = () => {
    setFiles([]);
    setNotes('');
  };

  const hasValidFiles = files.some(f => f.status === 'pending');

  return (
    <Box>
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          backgroundColor: isDragActive ? 'action.hover' : 'background.default',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover'
          }
        }}
      >
        <input {...getInputProps()} />
        <Box sx={{ textAlign: 'center' }}>
          <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            or click to browse files
          </Typography>
          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
            Maximum file size: {MAX_FILE_SIZE_MB}MB
          </Typography>
        </Box>
      </Paper>

      {files.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Files to upload ({files.length})
          </Typography>

          <List>
            {files.map((file, index) => (
              <ListItem
                key={index}
                sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                  mb: 1
                }}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body1">{file.name}</Typography>
                      {file.status === 'success' && (
                        <SuccessIcon color="success" fontSize="small" />
                      )}
                      {file.status === 'error' && (
                        <ErrorIcon color="error" fontSize="small" />
                      )}
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        {formatFileSize(file.size)}
                      </Typography>
                      {file.status === 'uploading' && (
                        <LinearProgress
                          variant="determinate"
                          value={file.progress}
                          sx={{ mt: 1 }}
                        />
                      )}
                      {file.error && (
                        <Alert severity="error" sx={{ mt: 1 }}>
                          {file.error}
                        </Alert>
                      )}
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <Chip
                    label={file.status}
                    size="small"
                    color={
                      file.status === 'success' ? 'success' :
                      file.status === 'error' ? 'error' :
                      file.status === 'uploading' ? 'primary' :
                      'default'
                    }
                    sx={{ mr: 1 }}
                  />
                  {file.status !== 'uploading' && (
                    <IconButton
                      edge="end"
                      onClick={() => removeFile(index)}
                      disabled={uploading}
                    >
                      <DeleteIcon />
                    </IconButton>
                  )}
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>

          <TextField
            fullWidth
            label="Version Notes (optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            multiline
            rows={2}
            sx={{ mb: 2 }}
            disabled={uploading}
          />

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<UploadIcon />}
              onClick={uploadFiles}
              disabled={!hasValidFiles || uploading}
              fullWidth
            >
              {uploading ? 'Uploading...' : 'Upload Files'}
            </Button>
            <Button
              variant="outlined"
              onClick={clearAll}
              disabled={uploading}
            >
              Clear All
            </Button>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default FileUpload;
