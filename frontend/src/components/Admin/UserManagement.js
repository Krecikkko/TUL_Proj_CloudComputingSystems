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
  IconButton,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  CircularProgress,
  Alert,
  Tooltip,
  TextField,
  InputAdornment
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  AdminPanelSettings as AdminIcon,
  Person as UserIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { adminService } from '../../services/files';
import { formatDate } from '../../utils/formatters';
import { useAuth } from '../Auth/AuthContext';

const UserManagement = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  const [roleDialog, setRoleDialog] = useState({ open: false, user: null });
  const [newRole, setNewRole] = useState('');
  const [deleteDialog, setDeleteDialog] = useState({ open: false, user: null });

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    const filtered = users.filter(user =>
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredUsers(filtered);
  }, [users, searchTerm]);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminService.getAllUsers();
      setUsers(data);
      setFilteredUsers(data);
    } catch (error) {
      setError('Failed to load users');
      console.error('Users error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async () => {
    if (!roleDialog.user || !newRole) return;
    
    try {
      await adminService.updateUserRole(roleDialog.user.id, newRole);
      await fetchUsers();
      setRoleDialog({ open: false, user: null });
      setNewRole('');
    } catch (error) {
      console.error('Role update error:', error);
      setError('Failed to update user role');
    }
  };

  const handleDeleteUser = async () => {
    if (!deleteDialog.user) return;
    
    try {
      await adminService.deleteUser(deleteDialog.user.id);
      await fetchUsers();
      setDeleteDialog({ open: false, user: null });
    } catch (error) {
      console.error('Delete user error:', error);
      setError('Failed to delete user');
    }
  };

  const openRoleDialog = (user) => {
    setRoleDialog({ open: true, user });
    setNewRole(user.role);
  };

  const openDeleteDialog = (user) => {
    setDeleteDialog({ open: true, user });
  };

  const getRoleChip = (role) => {
    if (role === 'admin') {
      return (
        <Chip
          icon={<AdminIcon />}
          label="Admin"
          color="warning"
          size="small"
        />
      );
    }
    return (
      <Chip
        icon={<UserIcon />}
        label="User"
        color="default"
        size="small"
      />
    );
  };

  return (
    <Box>
      {/* Controls */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
        <TextField
          size="small"
          placeholder="Search users..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ flexGrow: 1, maxWidth: 300 }}
        />
        
        <Box sx={{ flexGrow: 1 }} />
        
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchUsers}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Statistics */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="textSecondary">
          Total Users: {users.length} | 
          Admins: {users.filter(u => u.role === 'admin').length} | 
          Regular Users: {users.filter(u => u.role === 'user').length}
        </Typography>
      </Box>

      {/* Users Table */}
      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">
          {error}
          <Button size="small" onClick={fetchUsers} sx={{ ml: 2 }}>
            Retry
          </Button>
        </Alert>
      ) : filteredUsers.length === 0 ? (
        <Alert severity="info">
          {searchTerm ? 'No users found matching your search' : 'No users found'}
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Username</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Created At</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredUsers.map((user) => (
                <TableRow 
                  key={user.id} 
                  hover
                  sx={{
                    backgroundColor: user.id === currentUser?.id ? 'action.selected' : 'inherit'
                  }}
                >
                  <TableCell>{user.id}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {user.username}
                      {user.id === currentUser?.id && (
                        <Chip label="You" size="small" color="primary" variant="outlined" />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{getRoleChip(user.role)}</TableCell>
                  <TableCell>{formatDate(user.created_at)}</TableCell>
                  <TableCell align="center">
                    <Tooltip title="Change Role">
                      <span>
                        <IconButton
                          size="small"
                          onClick={() => openRoleDialog(user)}
                          disabled={user.id === currentUser?.id}
                        >
                          <EditIcon />
                        </IconButton>
                      </span>
                    </Tooltip>
                    
                    <Tooltip title={user.id === currentUser?.id ? "Can't delete yourself" : "Delete User"}>
                      <span>
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => openDeleteDialog(user)}
                          disabled={user.id === currentUser?.id}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </span>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Role Change Dialog */}
      <Dialog
        open={roleDialog.open}
        onClose={() => setRoleDialog({ open: false, user: null })}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>
          Change User Role
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="body2" gutterBottom>
              User: <strong>{roleDialog.user?.username}</strong>
            </Typography>
            
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>New Role</InputLabel>
              <Select
                value={newRole}
                label="New Role"
                onChange={(e) => setNewRole(e.target.value)}
              >
                <MenuItem value="user">User</MenuItem>
                <MenuItem value="admin">Admin</MenuItem>
              </Select>
            </FormControl>
            
            {newRole === 'admin' && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                Warning: This will give the user full admin privileges, including access to all files and system logs.
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRoleDialog({ open: false, user: null })}>
            Cancel
          </Button>
          <Button
            onClick={handleRoleChange}
            variant="contained"
            disabled={!newRole || newRole === roleDialog.user?.role}
          >
            Change Role
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, user: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Delete User Account
        </DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Warning: This action cannot be undone!
            </Typography>
          </Alert>
          
          <Typography variant="body1" gutterBottom>
            Are you sure you want to delete the user account:
          </Typography>
          
          <Box sx={{ pl: 2, mt: 1 }}>
            <Typography variant="body2">
              Username: <strong>{deleteDialog.user?.username}</strong>
            </Typography>
            <Typography variant="body2">
              Email: <strong>{deleteDialog.user?.email}</strong>
            </Typography>
          </Box>
          
          <Alert severity="warning" sx={{ mt: 2 }}>
            All files and data associated with this user will be permanently deleted.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, user: null })}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteUser}
            variant="contained"
            color="error"
          >
            Delete User
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserManagement;
