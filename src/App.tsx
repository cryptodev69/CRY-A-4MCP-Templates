/**
 * @fileoverview Main Application Component for CRY-A-4MCP Platform
 * 
 * This is the root component of the CRY-A-4MCP (Crypto AI 4 Model Context Protocol) platform,
 * a comprehensive web crawling and data extraction system. The application provides a modern
 * React-based interface for managing web crawlers, URL configurations, extraction strategies,
 * and analytics.
 * 
 * Key Features:
 * - Multi-page routing with React Router
 * - Theme management with dark/light mode support
 * - Global application state management
 * - Responsive layout with navigation
 * - Comprehensive crawling and extraction tools
 * 
 * Architecture:
 * - Uses React 18+ with TypeScript for type safety
 * - Context API for state management (AppContext, ThemeContext)
 * - Component-based architecture with reusable UI elements
 * - Service layer for API communication
 * 
 * @author CRY-A-4MCP Development Team
 * @version 1.0.0
 * @since 2024
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Context Providers for global state management
import { AppProvider } from './contexts/AppContext';
import { ThemeProvider } from './contexts/ThemeContext';

// Layout and Navigation Components
import Layout from './components/Layout';

// Page Components - Main application views
import Dashboard from './pages/Dashboard';           // Main dashboard with overview and quick actions
import URLManager from './components/URLManager';    // URL configuration and management interface
import CrawlJobs from './pages/CrawlJobs';          // Job queue and execution monitoring
import Crawlers from './pages/Crawlers';            // Crawler configuration and management
import URLMappings from './pages/URLMappings';      // URL-to-extractor mapping configuration
import Analytics from './pages/Analytics';          // Performance metrics and data visualization
import Extractors from './pages/Extractors';        // Data extraction strategy management
import TestURL from './pages/TestURL';              // URL testing and validation tools
import Settings from './pages/Settings';            // Application configuration and preferences

// Global styles
import './App.css';

/**
 * Main Application Component
 * 
 * This component serves as the root of the application and orchestrates the overall
 * structure including routing, context providers, and layout. It implements a
 * hierarchical provider pattern to ensure proper state management and theming
 * throughout the application.
 * 
 * Component Hierarchy:
 * App
 * ├── ThemeProvider (Theme management and dark/light mode)
 * │   └── AppProvider (Global application state)
 * │       └── Router (React Router for navigation)
 * │           └── Layout (Common layout with navigation)
 * │               └── Routes (Page routing configuration)
 * 
 * Route Configuration:
 * - / : Dashboard - Main overview and quick actions
 * - /url-manager : URL Manager - Configure and manage URLs
 * - /crawl-jobs : Crawl Jobs - Monitor and manage crawling jobs
 * - /crawlers : Crawlers - Configure crawler instances
 * - /url-mappings : URL Mappings - Map URLs to extraction strategies
 * - /analytics : Analytics - View performance metrics and reports
 * - /extractors : Extractors - Manage data extraction strategies
 * - /test-url : Test URL - Test and validate URL configurations
 * - /settings : Settings - Application configuration
 * 
 * @returns {React.ReactElement} The complete application with routing and context providers
 */
function App(): React.ReactElement {
  return (
    <ThemeProvider>
      <AppProvider>
        <Router>
          <Layout>
            <Routes>
              {/* Main Dashboard - Overview and quick actions */}
              <Route path="/" element={<Dashboard />} />
              
              {/* URL Management - Configure and manage target URLs */}
              <Route path="/url-manager" element={<URLManager />} />
              
              {/* Crawl Jobs - Monitor and manage crawling operations */}
              <Route path="/crawl-jobs" element={<CrawlJobs />} />
              
              {/* Crawlers - Configure and manage crawler instances */}
              <Route path="/crawlers" element={<Crawlers />} />
              
              {/* URL Mappings - Map URLs to specific extraction strategies */}
              <Route path="/url-mappings" element={<URLMappings />} />
              
              {/* Analytics - Performance metrics and data visualization */}
              <Route path="/analytics" element={<Analytics />} />
              
              {/* Extractors - Manage data extraction strategies and configurations */}
              <Route path="/extractors" element={<Extractors />} />
              
              {/* Test URL - Test and validate URL configurations */}
              <Route path="/test-url" element={<TestURL />} />
              
              {/* Settings - Application configuration and user preferences */}
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
        </Router>
      </AppProvider>
    </ThemeProvider>
  );
}

export default App;
