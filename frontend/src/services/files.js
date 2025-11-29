import api from './api';
import fileDownload from 'js-file-download';

const fileService = {
  listFiles: async (search = '', sort = 'date_desc') => {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (sort) params.append('sort', sort);
      
      const response = await api.get(`/files?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getFileInfo: async (fileId) => {
    try {
      const response = await api.get(`/files/${fileId}/info`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  uploadFile: async (file, notes = '', onProgress) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (notes) formData.append('notes', notes);

      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(percentCompleted);
          }
        },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  downloadFile: async (fileId, filename) => {
    try {
      const response = await api.get(`/download/${fileId}`, {
        responseType: 'blob',
      });
      fileDownload(response.data, filename || `file_${fileId}`);
      return true;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  deleteFile: async (fileId) => {
    try {
      const response = await api.delete(`/delete/${fileId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  deleteMultipleFiles: async (fileIds) => {
    try {
      const response = await api.post('/delete-multiple', { file_ids: fileIds });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getFileVersions: async (fileId) => {
    try {
      const response = await api.get(`/files/${fileId}/versions`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  downloadZip: async (fileIds) => {
    try {
      const response = await api.post('/files/download-zip', 
        { file_ids: fileIds },
        { responseType: 'blob' }
      );
      fileDownload(response.data, `files_${Date.now()}.zip`);
      return true;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  rollbackVersion: async (fileId, versionNumber) => {
    try {
      const response = await api.post(`/files/${fileId}/rollback/${versionNumber}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  generateShareLink: async (fileId) => {
    try {
      const response = await api.post(`/files/${fileId}/share`);
      const baseUrl = window.location.origin;
      return {
        ...response.data,
        full_url: `${baseUrl}${response.data.share_url}`
      };
    } catch (error) {
      throw error.response?.data || error;
    }
  }
};

export const adminService = {
  getAllUsers: async () => {
    try {
      const response = await api.get('/admin/users');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  deleteUser: async (userId) => {
    try {
      const response = await api.delete(`/admin/users/${userId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  updateUserRole: async (userId, role) => {
    try {
      const response = await api.put(`/admin/users/${userId}/role`, { role });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getLogbook: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      if (filters.user_id) params.append('user_id', filters.user_id);
      if (filters.action) params.append('action', filters.action);
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      if (filters.sort_by) params.append('sort_by', filters.sort_by);
      
      const response = await api.get(`/logbook?${params.toString()}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  getLogbookStats: async () => {
    try {
      const response = await api.get('/logbook/stats');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  exportLogbook: async () => {
    try {
      const response = await api.get('/logbook/export', {
        responseType: 'blob',
      });
      fileDownload(response.data, `logbook_export_${Date.now()}.csv`);
      return true;
    } catch (error) {
      throw error.response?.data || error;
    }
  }
};

export default fileService;
