# API Integration Guide

## Overview
This document describes how the frontend integrates with the backend FastAPI server.

## API Configuration

### Base Setup (services/api.js)
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Authentication
JWT token is automatically attached to all requests:
```javascript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/api/register` | Register new user | `{username, email, password}` | `{message}` |
| POST | `/api/login` | User login | `{username, password}` | `{token, user}` |
| GET | `/api/me` | Get current user | - | `{id, username, email, role, created_at}` |
| POST | `/api/logout` | Logout | - | 204 No Content |

### File Management Endpoints
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/files` | List user files | `?search=&sort=` | `[{id, filename, size, uploaded_at}]` |
| POST | `/api/upload` | Upload file | FormData with file | `{file_id, filename, size, version}` |
| GET | `/api/download/{id}` | Download file | - | Binary file |
| DELETE | `/api/delete/{id}` | Delete file | - | `{message}` |
| POST | `/api/delete-multiple` | Delete multiple | `{file_ids: []}` | `{deleted_count}` |

### Version Control Endpoints
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/files/{id}/versions` | Get versions | - | `[{version, size, uploaded_at}]` |
| POST | `/api/files/download-zip` | Download ZIP | `{file_ids: []}` | Binary ZIP |

### Admin Endpoints
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/admin/users` | List all users | - | `[{id, username, email, role}]` |
| DELETE | `/api/admin/users/{id}` | Delete user | - | 204 No Content |
| PUT | `/api/admin/users/{id}/role` | Change role | `{role}` | `{user}` |

### LogBook Endpoints
| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/logbook` | Get logs | `?user_id=&action=&start_date=&end_date=` | `[{logs}]` |
| GET | `/api/logbook/stats` | Get statistics | - | `{stats}` |
| GET | `/api/logbook/export` | Export CSV | - | CSV file |

## Error Handling

### Global Error Handler
```javascript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired - redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Error Response Format
```json
{
  "detail": "Error message here"
}
```

## File Upload Implementation

### Single File Upload
```javascript
const formData = new FormData();
formData.append('file', file);
formData.append('notes', 'Optional notes');

const response = await api.post('/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
  onUploadProgress: (progressEvent) => {
    const percentCompleted = Math.round(
      (progressEvent.loaded * 100) / progressEvent.total
    );
    // Update progress
  }
});
```

### File Size Validation
- Frontend limit: 100MB
- Checked before upload
- Backend also validates

## Authentication Flow

1. **Registration**
   - User fills form
   - POST to `/api/register`
   - Show success message
   - Redirect to login

2. **Login**
   - User enters credentials
   - POST to `/api/login`
   - Store token in localStorage
   - Store user object
   - Redirect to dashboard

3. **Protected Routes**
   - Check token exists
   - Add to request headers
   - Handle 401 responses

4. **Logout**
   - POST to `/api/logout`
   - Clear localStorage
   - Redirect to login

## WebSocket Integration (Future)
Prepared for real-time updates:
```javascript
const ws = new WebSocket(`ws://localhost:8000/ws`);
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle real-time updates
};
```

## Rate Limiting
Currently no rate limiting implemented.
Future consideration for:
- Upload limits per user
- API call limits
- Download bandwidth limits

## CORS Configuration
Backend must allow frontend origin:
```python
allow_origins=["http://localhost:3000"]
```

## Security Considerations
- JWT tokens expire after 60 minutes
- Tokens stored in localStorage (consider httpOnly cookies for production)
- All API calls use HTTPS in production
- File uploads validated for type and size
- SQL injection prevented by ORM
- XSS prevented by React escaping

## Testing API Integration
```javascript
// Test authentication
const testAuth = async () => {
  try {
    const user = await authService.getCurrentUser();
    console.log('Authenticated:', user);
  } catch (error) {
    console.error('Not authenticated');
  }
};

// Test file operations
const testFiles = async () => {
  const files = await fileService.listFiles();
  console.log('Files:', files);
};
```