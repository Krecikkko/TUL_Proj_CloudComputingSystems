export const APP_NAME = 'Cloud Storage System';

export const MAX_FILE_SIZE_MB = 100;
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

export const USER_ROLES = {
  ADMIN: 'admin',
  USER: 'user'
};

export const FILE_SORT_OPTIONS = [
  { value: 'date_desc', label: 'Newest First' },
  { value: 'date_asc', label: 'Oldest First' },
  { value: 'name_asc', label: 'Name (A-Z)' },
  { value: 'name_desc', label: 'Name (Z-A)' }
];

export const LOGBOOK_ACTIONS = [
  { value: 'login', label: 'Login' },
  { value: 'logout', label: 'Logout' },
  { value: 'upload', label: 'Upload' },
  { value: 'download', label: 'Download' },
  { value: 'delete', label: 'Delete' },
  { value: 'rollback', label: 'Rollback' },
  { value: 'download_share', label: 'Download (Shared)' },
  { value: 'share_create', label: 'Create Share Link' }
];

export const ACCEPTED_FILE_TYPES = {
  'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp'],
  'application/pdf': ['.pdf'],
  'application/msword': ['.doc'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/vnd.ms-excel': ['.xls'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-powerpoint': ['.ppt'],
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
  'text/*': ['.txt', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py'],
  'application/zip': ['.zip'],
  'application/x-rar-compressed': ['.rar'],
  'application/x-7z-compressed': ['.7z']
};

export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  ADMIN: '/admin',
  PROFILE: '/profile',
  SHARE: '/share/:shareId'
};

export const API_MESSAGES = {
  SUCCESS: {
    LOGIN: 'Login successful!',
    REGISTER: 'Registration successful! Please login.',
    UPLOAD: 'File uploaded successfully!',
    DELETE: 'File deleted successfully!',
    UPDATE_PROFILE: 'Profile updated successfully!',
    SHARE_LINK: 'Share link generated!',
    ROLLBACK: 'File rolled back to previous version!'
  },
  ERROR: {
    NETWORK: 'Network error. Please check your connection.',
    UNAUTHORIZED: 'Please login to continue.',
    FORBIDDEN: 'You do not have permission to perform this action.',
    NOT_FOUND: 'Resource not found.',
    SERVER: 'Server error. Please try again later.',
    FILE_TOO_LARGE: `File size exceeds ${MAX_FILE_SIZE_MB}MB limit.`,
    INVALID_FILE_TYPE: 'Invalid file type.',
    UPLOAD_FAILED: 'File upload failed. Please try again.',
    LOGIN_FAILED: 'Invalid username or password.',
    REGISTER_FAILED: 'Registration failed. Please try again.'
  }
};

export const TABLE_PAGINATION_OPTIONS = [10, 25, 50, 100];

export const THEME_COLORS = {
  primary: '#1976d2',
  secondary: '#dc004e',
  success: '#2e7d32',
  error: '#d32f2f',
  warning: '#ed6c02',
  info: '#0288d1'
};
