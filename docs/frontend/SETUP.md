# Frontend Setup Guide

## Prerequisites
- Node.js 18+ 
- npm 9+
- Git

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/Krecikkko/TUL_Proj_CloudComputingSystems.git
cd TUL_Proj_CloudComputingSystems/frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment
Create `.env` file in frontend folder:
```
REACT_APP_API_URL=http://localhost:8000
```

For production:
```
REACT_APP_API_URL=https://your-api-domain.com
```

### 4. Start Development Server
```bash
npm start
```
Application will open at http://localhost:3000

## Backend Setup Required
The frontend requires the backend to be running:

```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Build for Production

### 1. Create Production Build
```bash
npm run build
```

### 2. Serve with Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/cloud-storage/build;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Docker Setup (Optional)
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Common Issues

### CORS Errors
Ensure backend has CORS middleware configured:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Build Errors
Clear cache and rebuild:
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Port Already in Use
```bash
# Windows
npx kill-port 3000
# Or use different port
PORT=3001 npm start
```

## Testing

### Run Tests
```bash
npm test
```

### Test Coverage
```bash
npm test -- --coverage
```

## Development Tools

### VS Code Extensions
- ES7 React snippets
- Prettier
- ESLint
- Material Icon Theme

### Chrome Extensions
- React Developer Tools
- Redux DevTools (for debugging context)

## Folder Structure
```
frontend/
├── public/           # Static files
├── src/
│   ├── components/   # Reusable components
│   ├── pages/        # Page components
│   ├── services/     # API services
│   ├── utils/        # Utility functions
│   ├── App.js        # Main app component
│   └── index.js      # Entry point
├── .env              # Environment variables
├── .gitignore        # Git ignore rules
└── package.json      # Dependencies
```

## Next Steps
1. Configure environment variables
2. Run backend server
3. Start frontend development server
4. Login with test credentials
5. Begin development