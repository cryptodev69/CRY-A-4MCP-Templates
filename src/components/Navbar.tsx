import React from 'react';
import { Link } from 'react-router-dom';
import { BarChart3, Globe, Settings, TestTube, Layers, Home, PlayCircle, Moon, Sun } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const Navbar: React.FC = () => {
  const { isDarkMode, toggleTheme } = useTheme();
  
  return (
    <nav className={`sticky top-0 z-50 transition-all duration-300 ${
      isDarkMode 
        ? 'bg-gray-900 border-gray-700 shadow-lg' 
        : 'bg-white border-gray-200 shadow-sm'
    } border-b`} style={{
      padding: '0 24px',
      height: '64px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <div style={{
          fontSize: '1.5rem'
        }}>🤖</div>
        <h1 className={`m-0 text-xl font-bold tracking-tight ${
          isDarkMode ? 'text-white' : 'text-gray-900'
        }`}>CRY-A-4MCP</h1>
      </div>
      
      <div style={{
        display: 'flex',
        gap: '8px',
        alignItems: 'center'
      }}>
        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className={`p-2 rounded-lg transition-all duration-200 ${
            isDarkMode 
              ? 'bg-gray-800 hover:bg-gray-700 text-yellow-400' 
              : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
          }`}
          title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        {[
          { to: '/', label: 'Dashboard' },
          { to: '/analytics', label: 'Analytics' },
          { to: '/crawlers', label: 'Crawlers' },
          { to: '/url-manager', label: 'URL Manager' },
          { to: '/extractors', label: 'Extractors' },
          { to: '/crawl-jobs', label: 'Crawl Jobs' },
          { to: '/test-url', label: 'Test URL' },
          { to: '/settings', label: 'Settings' }
        ].map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className={`text-sm font-medium px-4 py-2 rounded-lg transition-all duration-200 no-underline ${
              isDarkMode 
                ? 'text-gray-300 hover:text-white hover:bg-gray-800' 
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            {item.label}
          </Link>
        ))}
      </div>
    </nav>
  );
};

export default Navbar;