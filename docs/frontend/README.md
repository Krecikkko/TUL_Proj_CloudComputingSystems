# Frontend Documentation

## Overview
React-based frontend for the Cloud Storage System, providing a modern UI for file management with version control.

## Quick Links
- [Setup Guide](./SETUP.md)
- [Architecture](./ARCHITECTURE.md)  
- [API Integration](./API_INTEGRATION.md)
- [Component Reference](./COMPONENTS.md)

## Technology Stack
- **Framework:** React 18.2.0
- **UI Library:** Material-UI v5
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **State Management:** React Context API
- **File Upload:** React Dropzone

## Features Implemented

### User Authentication
- JWT-based authentication
- Login/Register pages
- Auto token refresh
- Protected routes

### File Management
- Drag-and-drop upload
- Search files by name
- Sort by date or name
- Select multiple files for bulk operations
- Download individual files or multiple as ZIP
- View version history for each file (current version only downloadable)
- Generate public share links

### Version Control
- Track and view file version history
- Download current file version

### Admin Panel
- User management
- System logbook viewer
- CSV export functionality

### File Sharing
- Public share link generation
- Access without authentication

## Project Structure
```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   ├── FileManagement/
│   │   ├── Admin/
│   │   └── Layout/
│   ├── pages/
│   ├── services/
│   ├── utils/
│   └── App.js
└── package.json
```

## Available Scripts
- `npm start` - Run development server
- `npm build` - Build for production
- `npm test` - Run tests

## Environment Variables
```
REACT_APP_API_URL=http://localhost:8000
```

## Browser Support
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Metrics
- Bundle size: ~350KB (gzipped)
- First contentful paint: <2s
- Time to interactive: <3s

## Author
**Daniyar Zhumatayev** - Frontend Developer & Project Coordinator

## License
This project is part of TUL Cloud Computing Systems course.