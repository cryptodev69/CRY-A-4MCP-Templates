# CRY-A-4MCP Frontend - Cryptocurrency Analysis Platform

A modern React-based frontend for the CRY-A-4MCP (Cryptocurrency Analysis for Model Context Protocol) platform, providing an intuitive interface for managing cryptocurrency data sources, crawlers, and analytics.

## 🚀 Quick Start

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Python 3.9+ (for backend API service)

### ⚠️ Important: Backend Dependency

**The frontend requires the backend API service to be running for full functionality.** The URL Manager and other components will fail to load data without the backend service.

### Complete Launch Procedure

**Step 1: Start Backend API Service (Required)**
```bash
# Navigate to backend directory
cd /Users/soulmynd/Documents/Programming/Crypto\ AI\ platform/CRY-A-4MCP-Templates/starter-mcp-server/src/cry_a_4mcp

# Start the FastAPI service
python simple_web_api.py
```

**Step 2: Start Frontend Development Server**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm start
```

### 🌐 Access Points

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (Swagger UI)

## 📋 Available Scripts

### `npm start`
Runs the app in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### `npm test`
Launches the test runner in interactive watch mode.

### `npm run build`
Builds the app for production to the `build` folder.

### `npm run eject`
**Note: This is a one-way operation. Once you `eject`, you can't go back!**

## 🏗️ Architecture Overview

### Frontend Components

- **URLManager**: Manages cryptocurrency data source configurations
- **Dashboard**: Main analytics and monitoring interface
- **CrawlJobs**: Job management and monitoring
- **Crawlers**: Crawler configuration and status
- **Analytics**: Data visualization and insights
- **Extractors**: Data extraction pipeline management

### Backend Integration

The frontend communicates with the FastAPI backend service (`simple_web_api.py`) which provides:

- **URL Configuration Management**: CRUD operations for data sources
- **Profile Type Management**: User profile-based configurations
- **Category Filtering**: Organized data source categorization
- **Health Monitoring**: Service status and health checks

### Key Features

- 🔗 **URL Configuration Management**: Add, edit, and manage cryptocurrency data sources
- 📊 **Real-time Analytics**: Monitor crawling performance and data quality
- 🎯 **Profile-based Filtering**: Tailored configurations for different user types:
  - Degen Gambler
  - Gem Hunter
  - Traditional Investor
  - DeFi Yield Farmer
- 🔍 **Advanced Search**: Filter by category, difficulty, and data type
- 📈 **Performance Monitoring**: Track crawling metrics and success rates

## 🛠️ Technology Stack

- **Frontend Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Routing**: React Router DOM
- **HTTP Client**: Fetch API
- **Backend**: FastAPI with SQLite
- **CORS**: Configured for localhost development

## 🔧 Development

### Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # React components
│   │   ├── URLManager.tsx  # URL configuration management
│   │   └── ...
│   ├── pages/             # Page components
│   ├── services/          # API service layer
│   ├── types/             # TypeScript type definitions
│   ├── contexts/          # React contexts
│   └── App.tsx            # Main application component
├── package.json
└── README.md
```

### Environment Configuration

The application is configured to work with:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- CORS enabled for cross-origin requests

### Adding New Data Sources

1. Use the URL Manager interface to add new cryptocurrency data sources
2. Configure profile types, categories, and scraping difficulty
3. Set API availability and pricing information
4. Define target data points and extraction rationale

## 🚨 Troubleshooting

### Common Issues

**1. URL Manager shows "No data available"**
- **Cause**: Backend API service not running
- **Solution**: Start the backend service first:
  ```bash
  cd starter-mcp-server/src/cry_a_4mcp
  python simple_web_api.py
  ```

**2. CORS errors in browser console**
- **Cause**: Backend not configured for frontend origin
- **Solution**: Ensure backend CORS settings include `http://localhost:3000`

**3. Port conflicts**
- **Frontend**: Change port with `PORT=3001 npm start`
- **Backend**: Modify port in `simple_web_api.py`

### Development Tips

- Always start the backend service before the frontend
- Check browser console for API connection errors
- Use the Swagger UI at `http://localhost:8000/docs` to test API endpoints
- Monitor the backend terminal for API request logs

## 📚 Related Documentation

- [Backend API Documentation](../starter-mcp-server/README.md)
- [Implementation Plan](../IMPLEMENTATION_PLAN.md)
- [Package Summary](../ENHANCED_PACKAGE_SUMMARY.md)

## 🤝 Contributing

When contributing to the frontend:

1. Ensure both frontend and backend services are running
2. Test URL Manager functionality with backend integration
3. Follow TypeScript best practices
4. Add appropriate error handling for API calls
5. Update this README for any new dependencies or procedures

---

**Note**: This frontend is part of the larger CRY-A-4MCP cryptocurrency analysis platform. For complete system setup, refer to the main project documentation.
