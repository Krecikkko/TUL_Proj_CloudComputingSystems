import React, { useState, useEffect, useCallback } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Checkbox,
  Tooltip,
  Box,
  Typography,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Chip,
  TablePagination,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Download as DownloadIcon,
  Delete as DeleteIcon,
  History as VersionIcon,
  Share as ShareIcon,
  Search as SearchIcon,
  Archive as ZipIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import fileService from '../../services/files';
import { formatFileSize, formatDate, getFileIcon } from '../../utils/formatters';
import { FILE_SORT_OPTIONS } from '../../utils/constants';
import VersionHistory from './VersionHistory';
import FileActions from './FileActions';

const FileList = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('date_desc');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  const [versionModalOpen, setVersionModalOpen] = useState(false);
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 500); 

    return () => clearTimeout(timer);
  }, [searchTerm]);
  
  useEffect(() => {
    fetchFiles();
  }, [debouncedSearchTerm, sortBy]);
  
  const fetchFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fileService.listFiles(debouncedSearchTerm, sortBy);
      setFiles(data);
    } catch (error) {
      setError('Failed to load files');
      console.error('Error fetching files:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAll = (event) => {
    if (event.target.checked) {
      setSelected(files.map(f => f.id));
    } else {
      setSelected([]);
    }
  };

  const handleSelect = (fileId) => {
    setSelected(prev => {
      if (prev.includes(fileId)) {
        return prev.filter(id => id !== fileId);
      } else {
        return [...prev, fileId];
      }
    });
  };

  const handleDownload = async (fileId, filename) => {
    try {
      await fileService.downloadFile(fileId, filename);
    } catch (error) {
      console.error('Download error:', error);
    }
  };

  const handleDelete = async (fileId) => {
    if (window.confirm('Are you sure you want to delete this file?')) {
      try {
        await fileService.deleteFile(fileId);
        await fetchFiles();
        setSelected(prev => prev.filter(id => id !== fileId));
      } catch (error) {
        console.error('Delete error:', error);
      }
    }
  };

  const handleBulkDelete = async () => {
    if (selected.length === 0) return;
    
    if (window.confirm(`Are you sure you want to delete ${selected.length} files?`)) {
      try {
        await fileService.deleteMultipleFiles(selected);
        setSelected([]);
        await fetchFiles();
      } catch (error) {
        console.error('Bulk delete error:', error);
      }
    }
  };

  const handleBulkDownload = async () => {
    if (selected.length === 0) return;
    
    try {
      await fileService.downloadZip(selected);
    } catch (error) {
      console.error('Bulk download error:', error);
    }
  };

  const handleShowVersions = (file) => {
    setSelectedFile(file);
    setVersionModalOpen(true);
  };

  const handleShare = (file) => {
    setSelectedFile(file);
    setShareModalOpen(true);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const paginatedFiles = files.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
        <Button size="small" onClick={fetchFiles} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    );
  }

  return (
    <Box>
      {/* Search and Sort Controls */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          size="small"
          placeholder="Search files..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ flexGrow: 1, minWidth: 200 }}
        />
        
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Sort By</InputLabel>
          <Select
            value={sortBy}
            label="Sort By"
            onChange={(e) => setSortBy(e.target.value)}
          >
            {FILE_SORT_OPTIONS.map(option => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchFiles}
        >
          Refresh
        </Button>
      </Box>

      {/* Bulk Actions */}
      {selected.length > 0 && (
        <Box sx={{ mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
          <Typography variant="body2">
            {selected.length} file(s) selected
          </Typography>
          <Button
            size="small"
            variant="contained"
            startIcon={<ZipIcon />}
            onClick={handleBulkDownload}
          >
            Download as ZIP
          </Button>
          <Button
            size="small"
            variant="contained"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleBulkDelete}
          >
            Delete Selected
          </Button>
          <Button
            size="small"
            variant="outlined"
            onClick={() => setSelected([])}
          >
            Clear Selection
          </Button>
        </Box>
      )}

      {/* Files Table */}
      {files.length === 0 ? (
        <Alert severity="info">
          No files found. Upload your first file to get started!
        </Alert>
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      indeterminate={selected.length > 0 && selected.length < files.length}
                      checked={files.length > 0 && selected.length === files.length}
                      onChange={handleSelectAll}
                    />
                  </TableCell>
                  <TableCell>File Name</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Upload Date</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedFiles.map((file) => (
                  <TableRow
                    key={file.id}
                    hover
                    selected={selected.includes(file.id)}
                  >
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selected.includes(file.id)}
                        onChange={() => handleSelect(file.id)}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2">
                          {getFileIcon(file.filename)}
                        </Typography>
                        <Typography variant="body2">
                          {file.filename}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{formatFileSize(file.size)}</TableCell>
                    <TableCell>{formatDate(file.uploaded_at)}</TableCell>
                    <TableCell align="center">
                      <Tooltip title="Download">
                        <IconButton
                          size="small"
                          onClick={() => handleDownload(file.id, file.filename)}
                        >
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Version History">
                        <IconButton
                          size="small"
                          onClick={() => handleShowVersions(file)}
                        >
                          <VersionIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Share">
                        <IconButton
                          size="small"
                          onClick={() => handleShare(file)}
                        >
                          <ShareIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDelete(file.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <TablePagination
            component="div"
            count={files.length}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        </>
      )}

      {/* Version History Modal */}
      {selectedFile && (
        <VersionHistory
          open={versionModalOpen}
          onClose={() => {
            setVersionModalOpen(false);
            setSelectedFile(null);
          }}
          file={selectedFile}
          onVersionChange={fetchFiles}
        />
      )}

      {/* File Actions Modal (Share) */}
      {selectedFile && (
        <FileActions
          open={shareModalOpen}
          onClose={() => {
            setShareModalOpen(false);
            setSelectedFile(null);
          }}
          file={selectedFile}
        />
      )}
    </Box>
  );
};

export default FileList;
