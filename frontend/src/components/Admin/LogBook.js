import React, { useState, useEffect } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
  CircularProgress,
  Alert,
  Chip,
  Card,
  CardContent,
  Grid,
  TablePagination,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Assessment as StatsIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon
} from '@mui/icons-material';
import { adminService } from '../../services/files';
import { formatDate, formatRelativeTime } from '../../utils/formatters';
import { LOGBOOK_ACTIONS } from '../../utils/constants';

const LogBook = () => {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  
  const [filters, setFilters] = useState({
    user_id: '',
    action: '',
    start_date: '',
    end_date: '',
    sort_by: 'timestamp_desc'
  });

  useEffect(() => {
    fetchLogs();
    fetchStats();
  }, []);

  const fetchLogs = async (currentFilters = filters) => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminService.getLogbook(currentFilters);
      setLogs(data);
    } catch (error) {
      setError('Failed to load logbook entries');
      console.error('Logbook error:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const statsData = await adminService.getLogbookStats();
      setStats(statsData);
    } catch (error) {
      console.error('Stats error:', error);
    }
  };

  const handleFilterChange = (field, value) => {
    const newFilters = { ...filters, [field]: value };
    setFilters(newFilters);
    fetchLogs(newFilters);
  };

  const handleClearFilters = () => {
    const clearedFilters = {
      user_id: '',
      action: '',
      start_date: '',
      end_date: '',
      sort_by: 'timestamp_desc'
    };
    setFilters(clearedFilters);
    fetchLogs(clearedFilters);
  };

  const handleExport = async () => {
    try {
      await adminService.exportLogbook();
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getActionColor = (action) => {
    const colorMap = {
      login: 'success',
      logout: 'default',
      upload: 'primary',
      download: 'info',
      delete: 'error',
      rollback: 'warning',
      download_share: 'info',
      share_create: 'secondary'
    };
    return colorMap[action] || 'default';
  };

  const getActionIcon = (action) => {
    const iconMap = {
      login: '🔑',
      logout: '🚪',
      upload: '📤',
      download: '📥',
      delete: '🗑️',
      rollback: '⏪',
      download_share: '🔗',
      share_create: '📎'
    };
    return iconMap[action] || '📝';
  };

  const paginatedLogs = logs.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  return (
    <Box>
      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Logins
                </Typography>
                <Typography variant="h5">
                  {stats.total_logins || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Uploads
                </Typography>
                <Typography variant="h5">
                  {stats.total_uploads || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Downloads
                </Typography>
                <Typography variant="h5">
                  {stats.total_downloads || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined">
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Unique Users
                </Typography>
                <Typography variant="h5">
                  {stats.total_unique_users || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
          <TextField
            size="small"
            label="User ID"
            type="number"
            value={filters.user_id}
            onChange={(e) => handleFilterChange('user_id', e.target.value)}
            sx={{ width: 120 }}
          />
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Action</InputLabel>
            <Select
              value={filters.action}
              label="Action"
              onChange={(e) => handleFilterChange('action', e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              {LOGBOOK_ACTIONS.map(action => (
                <MenuItem key={action.value} value={action.value}>
                  {action.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField
            size="small"
            label="Start Date"
            type="date"
            value={filters.start_date}
            onChange={(e) => handleFilterChange('start_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={{ width: 150 }}
          />
          
          <TextField
            size="small"
            label="End Date"
            type="date"
            value={filters.end_date}
            onChange={(e) => handleFilterChange('end_date', e.target.value)}
            InputLabelProps={{ shrink: true }}
            sx={{ width: 150 }}
          />
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Sort</InputLabel>
            <Select
              value={filters.sort_by}
              label="Sort"
              onChange={(e) => handleFilterChange('sort_by', e.target.value)}
            >
              <MenuItem value="timestamp_desc">Newest First</MenuItem>
              <MenuItem value="timestamp_asc">Oldest First</MenuItem>
            </Select>
          </FormControl>
          
          <Tooltip title="Clear Filters">
            <IconButton onClick={handleClearFilters} size="small">
              <ClearIcon />
            </IconButton>
          </Tooltip>
          
          <Box sx={{ flexGrow: 1 }} />
          
          <Button
            size="small"
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => fetchLogs()}
          >
            Refresh
          </Button>
          
          <Button
            size="small"
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={handleExport}
          >
            Export CSV
          </Button>
        </Box>
      </Paper>

      {/* Logs Table */}
      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : logs.length === 0 ? (
        <Alert severity="info">No log entries found</Alert>
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>User ID</TableCell>
                  <TableCell>File ID</TableCell>
                  <TableCell>IP Address</TableCell>
                  <TableCell>Details</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedLogs.map((log) => (
                  <TableRow key={log.id} hover>
                    <TableCell>{log.id}</TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {formatDate(log.timestamp)}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {formatRelativeTime(log.timestamp)}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${getActionIcon(log.action)} ${log.action}`}
                        size="small"
                        color={getActionColor(log.action)}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{log.user_id || '-'}</TableCell>
                    <TableCell>{log.file_id || '-'}</TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {log.ip_address || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {log.details && (
                        <Typography variant="caption">
                          {JSON.stringify(log.details)}
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            component="div"
            count={logs.length}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[10, 25, 50, 100]}
          />
        </>
      )}
    </Box>
  );
};

export default LogBook;
