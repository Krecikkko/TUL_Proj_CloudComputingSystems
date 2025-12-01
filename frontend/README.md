# Cloud Storage System - Frontend

## 📁 Project Overview
This is the React frontend for the Cloud Storage System, a university project for Cloud Computing Systems course at TUL. The application provides a web interface for secure file storage, version control, and sharing capabilities.

## 🚀 Features
- **User Authentication**: Registration, login, and JWT-based authentication
- **File Management**: Upload, download, delete files with drag-and-drop support
- **Version Control**: Track file versions and rollback to previous versions
- **File Sharing**: Generate public share links for files
- **Bulk Operations**: Download multiple files as ZIP
- **Admin Panel**: User management and system activity logs (admin only)
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 📋 Prerequisites
- Node.js (v18.0.0 or higher)
- npm (v9.0.0 or higher)
- Backend API running (see backend README)

## 🛠️ Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/Krecikkko/TUL_Proj_CloudComputingSystems.git
cd TUL_Proj_CloudComputingSystems/frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Configure Environment
Create a `.env` file in the frontend directory:
```env
REACT_APP_API_URL=http://localhost:8000
```

For production, update this to your server's URL:
```env
REACT_APP_API_URL=https://your-server-domain.com
```

### Step 4: Run Development Server
```bash
npm start
```

The application will open at `http://localhost:3000`

## 📦 Project Structure
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/           # Reusable components
│   │   ├── Auth/             # Authentication components
│   │   ├── FileManagement/   # File-related components
│   │   ├── Admin/            # Admin panel components
│   │   └── Layout/           # Layout components
│   ├── pages/                # Page components
│   │   ├── Login.js
│   │   ├── Register.js
│   │   ├── Dashboard.js
│   │   ├── Profile.js
│   │   └── AdminPanel.js
│   ├── services/             # API services
│   │   ├── api.js           # Axios configuration
│   │   ├── auth.js          # Authentication service
│   │   └── files.js         # File operations service
│   ├── utils/                # Utility functions
│   │   ├── constants.js     # App constants
│   │   └── formatters.js    # Data formatters
│   ├── App.js               # Main app component
│   ├── index.js             # Entry point
│   └── index.css            # Global styles
├── package.json
├── .env                     # Environment variables
└── README.md
```

## 🔧 Available Scripts

### `npm start`
Runs the app in development mode on port 3000

### `npm build`
Builds the app for production to the `build` folder

### `npm test`
Runs the test suite (if tests are implemented)

### `npm eject`
**Note: This is a one-way operation!**

## 🚀 Deployment

### Building for Production
```bash
npm run build
```

This creates an optimized production build in the `build` folder.

### Deploying to Server

#### Option 1: Serve with Nginx
1. Build the application:
```bash
npm run build
```

2. Copy build files to server:
```bash
scp -r build/* user@your-server:/var/www/html/
```

3. Configure Nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Option 2: Deploy to Hosting Service
You can deploy to services like:
- **Netlify**: Drag and drop the `build` folder
- **Vercel**: Connect GitHub repo and deploy
- **GitHub Pages**: Use gh-pages package

## 🔐 Authentication Flow
1. User registers with username, email, and password
2. User logs in and receives JWT token
3. Token is stored in localStorage
4. Token is sent with each API request in Authorization header
5. Token expires after 60 minutes (configurable in backend)

## 📱 Features Guide

### File Upload
- Drag and drop files or click to browse
- Multiple files can be uploaded at once
- Maximum file size: 100MB per file
- Upload progress shown for each file
- Files with same name create new versions

### File Management
- Search files by name
- Sort by date or name
- Select multiple files for bulk operations
- Download individual files or multiple as ZIP
- View version history for each file
- Generate public share links

### Admin Panel (Admin Only)
- View all system users
- Change user roles
- Delete user accounts
- View system activity logs
- Export logs as CSV
- Filter logs by user, action, or date

### User Profile
- Update username and email
- Change password
- View storage statistics
- See account creation date

## 🐛 Troubleshooting

### Common Issues

#### 1. Cannot Connect to Backend
- Ensure backend is running on port 8000
- Check `.env` file has correct API URL
- Verify CORS is configured in backend

#### 2. Authentication Issues
- Clear browser localStorage
- Check token expiration
- Verify backend JWT configuration

#### 3. File Upload Fails
- Check file size (max 100MB)
- Verify backend storage permissions
- Check network connection

#### 4. Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 🧪 Testing

### Manual Testing Checklist
- [ ] User registration
- [ ] User login/logout
- [ ] File upload (single and multiple)
- [ ] File download
- [ ] Version history
- [ ] File deletion
- [ ] Bulk operations
- [ ] Share link generation
- [ ] Admin user management
- [ ] Admin logbook viewing
- [ ] Profile updates
- [ ] Password changes

## 📝 API Endpoints Used

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/me` - Get current user
- `POST /api/logout` - User logout

### Files
- `GET /api/files` - List user files
- `POST /api/upload` - Upload file
- `GET /api/download/{id}` - Download file
- `DELETE /api/delete/{id}` - Delete file
- `POST /api/delete-multiple` - Delete multiple files
- `GET /api/files/{id}/versions` - Get file versions
- `POST /api/files/{id}/rollback/{version}` - Rollback to version
- `POST /api/files/{id}/share` - Generate share link
- `POST /api/files/download-zip` - Download as ZIP

### Admin
- `GET /api/admin/users` - List all users
- `DELETE /api/admin/users/{id}` - Delete user
- `PUT /api/admin/users/{id}/role` - Change user role
- `GET /api/logbook` - Get system logs
- `GET /api/logbook/export` - Export logs as CSV

### User
- `PUT /api/users/updateme` - Update profile
- `GET /api/users/stats` - Get user statistics

## 🤝 Contributing

### Git Workflow
1. Create feature branch from `develop`
```bash
git checkout -b feature/your-feature-name
```

2. Make changes and commit
```bash
git add .
git commit -m "[Frontend] Your commit message"
```

3. Push and create pull request
```bash
git push origin feature/your-feature-name
```

## 📄 License
This project is part of university coursework at TUL.

## 👥 Team Members
- **Daniyar Zhumatayev** - Frontend Developer & Project Coordinator
- Laura Gabryjańczyk - Authentication & User Management
- Jakub Suliga - File Operations & Storage API
- Maksym Tsyhypalo - Version Control & LogBook System
- Kuzma Martysiuk - DevOps & Infrastructure

## 📞 Support
For issues or questions, contact the team via:
- GitHub Issues
- University Email

## 🎯 Project Status
- [x] Project Setup
- [x] Authentication UI
- [x] File Management UI
- [x] Version Control UI
- [x] Admin Panel
- [x] User Profile
- [x] Responsive Design
- [x] API Integration
- [ ] Unit Tests
- [ ] E2E Tests
- [ ] Performance Optimization

---
**Last Updated**: 30.11.2025
**Version**: 1.2.0
