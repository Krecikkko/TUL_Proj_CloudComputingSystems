import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  IconButton,
  Alert,
  InputAdornment,
  Snackbar
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  Close as CloseIcon,
  Share as ShareIcon
} from '@mui/icons-material';
import fileService from '../../services/files';

const FileActions = ({ open, onClose, file }) => {
  const [shareLink, setShareLink] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);

  const handleGenerateShareLink = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fileService.generateShareLink(file.id);
      setShareLink(response.full_url);
    } catch (error) {
      setError('Failed to generate share link');
      console.error('Share link error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(shareLink)
      .then(() => {
        setCopySuccess(true);
      })
      .catch(err => {
        console.error('Failed to copy:', err);
      });
  };

  const handleClose = () => {
    setShareLink('');
    setError(null);
    onClose();
  };

  return (
    <>
      <Dialog 
        open={open} 
        onClose={handleClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6">
              Share File - {file?.filename}
            </Typography>
            <IconButton onClick={handleClose} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            {!shareLink ? (
              <>
                <Typography variant="body1" gutterBottom>
                  Generate a public link to share this file with others.
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                  Anyone with the link will be able to download the file without logging in.
                </Typography>
                
                <Button
                  variant="contained"
                  startIcon={<ShareIcon />}
                  onClick={handleGenerateShareLink}
                  disabled={loading}
                  fullWidth
                >
                  {loading ? 'Generating...' : 'Generate Share Link'}
                </Button>
              </>
            ) : (
              <>
                <Typography variant="body1" gutterBottom>
                  Share this link with others:
                </Typography>
                
                <TextField
                  fullWidth
                  value={shareLink}
                  variant="outlined"
                  InputProps={{
                    readOnly: true,
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={handleCopyLink}>
                          <CopyIcon />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{ mt: 2 }}
                />
                
                <Alert severity="info" sx={{ mt: 2 }}>
                  This link provides public access to download this file.
                  The link will remain active until you delete the file.
                </Alert>
              </>
            )}
            
            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
          {shareLink && (
            <Button
              variant="contained"
              onClick={handleCopyLink}
              startIcon={<CopyIcon />}
            >
              Copy Link
            </Button>
          )}
        </DialogActions>
      </Dialog>

      <Snackbar
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        open={copySuccess}
        autoHideDuration={3000}
        onClose={() => setCopySuccess(false)}
        message="Link copied to clipboard!"
      />
    </>
  );
};

export default FileActions;
