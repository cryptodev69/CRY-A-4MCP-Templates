import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

/**
 * RoutingDebug component for diagnosing routing issues
 * Displays current route information and provides navigation buttons
 */
function RoutingDebug() {
  const location = useLocation();
  const navigate = useNavigate();

  const routes = [
    { path: '/', label: 'Dashboard' },
    { path: '/url-mappings', label: 'URL Mappings' },
    { path: '/url-manager', label: 'URL Manager' },
    { path: '/crawl-jobs', label: 'Crawl Jobs' },
    { path: '/crawlers', label: 'Crawlers' },
    { path: '/extractors', label: 'Extractors' },
    { path: '/analytics', label: 'Analytics' },
    { path: '/test-url', label: 'Test URL' }
  ];

  return (
    <div className="fixed bottom-4 right-4 bg-yellow-100 dark:bg-yellow-900 border border-yellow-300 dark:border-yellow-700 rounded-lg p-4 shadow-lg z-50">
      <h3 className="text-sm font-bold text-yellow-800 dark:text-yellow-200 mb-2">
        Routing Debug
      </h3>
      <div className="text-xs text-yellow-700 dark:text-yellow-300 mb-3">
        <div><strong>Current Path:</strong> {location.pathname}</div>
        <div><strong>Search:</strong> {location.search || 'None'}</div>
        <div><strong>Hash:</strong> {location.hash || 'None'}</div>
      </div>
      <div className="space-y-1">
        {routes.map(({ path, label }) => (
          <button
            key={path}
            onClick={() => navigate(path)}
            className={`block w-full text-left px-2 py-1 text-xs rounded transition-colors ${
              location.pathname === path
                ? 'bg-yellow-200 dark:bg-yellow-800 text-yellow-900 dark:text-yellow-100'
                : 'bg-yellow-50 dark:bg-yellow-950 text-yellow-700 dark:text-yellow-300 hover:bg-yellow-200 dark:hover:bg-yellow-800'
            }`}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default RoutingDebug;