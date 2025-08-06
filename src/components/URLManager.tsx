/**
 * @fileoverview URL Manager Component for CRY-A-4MCP Platform
 * 
 * This component provides a comprehensive interface for managing URL configurations
 * within the CRY-A-4MCP platform. It allows users to view, create, edit, and delete
 * URL configurations with different profile types and categories.
 * 
 * Key Features:
 * - Profile-based URL filtering (Degen Gambler, Gem Hunter, Traditional Investor, DeFi Yield Farmer)
 * - Predefined URL configurations with detailed metadata
 * - Custom URL addition with full configuration options
 * - Real-time search and filtering capabilities
 * - Visual indicators for scraping difficulty and API availability
 * - Responsive design with dark/light theme support
 * 
 * Architecture:
 * - React functional component with hooks for state management
 * - Integration with backend API for CRUD operations
 * - Theme context integration for consistent styling
 * - Modular interface design with reusable components
 * 
 * API Dependencies:
 * - Backend API service must be running on configured endpoint
 * - Requires /api/url-configs/ endpoint for data operations
 * 
 * @author CRY-A-4MCP Development Team
 * @version 1.0.0
 * @since 2024
 */

import React, { useState, useEffect } from 'react';
import {
  Plus,
  X,
  Edit,
  ChevronDown,
  Shield,
  TrendingUp,
  Building,
  Sprout,
  Info,
  ExternalLink,
  AlertTriangle,
  Star,
  Search,
  Filter,
  Trash2
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

/**
 * IMPORTANT: Backend API Service Requirement
 * 
 * This component requires the backend API service to be running.
 * If the URL manager cannot pull data, ensure the API service is started:
 * 
 * Command: python simple_web_api.py
 * Location: ~/Documents/Programming/Crypto AI platform/CRY-A-4MCP-Templates/starter-mcp-server/src/cry_a_4mcp/
 * 
 * The API provides endpoints for:
 * - GET /api/url-configurations/ - Retrieve URL configurations
 * - POST /api/url-configurations/ - Create new URL configuration
 * - PUT /api/url-configurations/{id} - Update existing configuration
 * - DELETE /api/url-configurations/{id} - Delete configuration
 */  

/**
 * URL Configuration Interface
 * 
 * Represents a complete URL configuration with all metadata and settings
 * for web crawling and data extraction operations.
 * 
 * @interface URLConfig
 */
interface URLConfig {
  /** Unique identifier for the URL configuration */
  id: number;
  
  /** Human-readable name for the URL configuration */
  name: string;
  
  /** Target URL for crawling operations */
  url: string;
  
  /** Profile type categorizing the intended use case */
  profile_type: string;
  
  /** Optional detailed description of the URL and its purpose */
  description?: string;
  
  /** Category classification for organizational purposes */
  category?: string;
  
  /** Priority level for crawling operations (1-5, higher = more important) */
  priority?: number;
  
  /** Assessment of scraping difficulty (Low, Medium, High, Impossible) */
  scraping_difficulty?: string;
  
  /** Whether the target site provides an official API */
  has_official_api?: boolean;
  
  /** Pricing information for official API access */
  api_pricing?: string | { description?: string; [key: string]: any };
  
  /** Recommended approach for data extraction */
  recommendation?: string;
  
  /** Key data points available from this source */
  key_data_points?: string | string[] | { description?: string; [key: string]: any };
  
  /** Specific target data to extract */
  target_data?: string | { description?: string; [key: string]: any };
  
  /** Business rationale for including this URL */
  rationale?: string;
  
  /** Cost-benefit analysis for data extraction */
  cost_analysis?: string | { description?: string; [key: string]: any };
  
  /** Timestamp of configuration creation */
  created_at?: string;
  
  /** Timestamp of last configuration update */
  updated_at?: string;
}

/**
 * URL Configuration Creation Interface
 * 
 * Represents the data structure for creating new URL configurations,
 * excluding auto-generated fields like ID and timestamps.
 * 
 * @interface URLConfigCreate
 */
interface URLConfigCreate {
  /** Human-readable name for the URL configuration */
  name: string;
  
  /** Target URL for crawling operations */
  url: string;
  
  /** Profile type categorizing the intended use case */
  profile_type: string;
  
  /** Optional detailed description of the URL and its purpose */
  description?: string;
  
  /** Category classification for organizational purposes */
  category?: string;
  
  /** Priority level for crawling operations (1-5, higher = more important) */
  priority?: number;
  
  /** Assessment of scraping difficulty (Low, Medium, High, Impossible) */
  scraping_difficulty?: string;
  
  /** Whether the target site provides an official API */
  has_official_api?: boolean;
  
  /** Pricing information for official API access */
  api_pricing?: string | { description?: string; [key: string]: any };
  
  /** Recommended approach for data extraction */
  recommendation?: string;
  
  /** Key data points available from this source */
  key_data_points?: string | string[] | { description?: string; [key: string]: any };
  
  /** Specific target data to extract */
  target_data?: string | { description?: string; [key: string]: any };
  
  /** Business rationale for including this URL */
  rationale?: string;
  
  /** Cost-benefit analysis for data extraction */
  cost_analysis?: string | { description?: string; [key: string]: any };
}

/**
 * URL Manager Component Props
 * 
 * Defines the props interface for the URLManager component,
 * enabling integration with parent components and callback handling.
 * 
 * @interface URLManagerProps
 */
interface URLManagerProps {
  /** Array of currently selected URL strings */
  selectedUrls?: string[];
  
  /** Callback function triggered when URL selection changes */
  onUrlsChange?: (urls: string[]) => void;
  
  /** Callback function triggered when a URL configuration is selected */
  onConfigSelect?: (config: URLConfig) => void;
}

/**
 * Profile Type Icon Mapping
 * 
 * Maps profile types to their corresponding React icon components for visual representation
 * in the URL configuration interface. Provides intuitive visual categorization
 * of different crypto trading profiles and investment strategies.
 * 
 * @constant {Object.<string, JSX.Element>} profileIcons
 */
const profileIcons = {
  'Degen Gambler': <TrendingUp size={16} />,      // High-risk, high-reward trading
  'Gem Hunter': <Shield size={16} />,             // Early-stage project discovery
  'Traditional Investor': <Building size={16} />, // Conservative institutional approach
  'DeFi Yield Farmer': <Sprout size={16} />       // Yield optimization strategies
};

/**
 * Priority Level Color Mapping
 * 
 * Maps priority levels (1-5) to their corresponding hex color codes
 * for visual indication of URL configuration importance. Higher numbers
 * indicate higher priority with more intense colors.
 * 
 * @constant {Object.<number, string>} difficultyColors
 */
const difficultyColors = {
  1: '#10b981', // green - lowest priority
  2: '#3b82f6', // blue - low priority
  3: '#f59e0b', // yellow - medium priority
  4: '#ef4444', // red - high priority
  5: '#dc2626'  // dark red - highest priority
} as const;

const URLManager: React.FC<URLManagerProps> = ({ selectedUrls = [], onUrlsChange, onConfigSelect }) => {
  const { isDarkMode } = useTheme();
  const [predefinedConfigs, setPredefinedConfigs] = useState<URLConfig[]>([]);
  const [filteredConfigs, setFilteredConfigs] = useState<URLConfig[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<string>('all');
  const [customUrl, setCustomUrl] = useState<string>('');
  const [showAddDialog, setShowAddDialog] = useState<boolean>(false);
  const [newConfig, setNewConfig] = useState<Partial<URLConfig>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  // Helper function to safely get cost analysis text
  const getCostAnalysisText = (costAnalysis?: string | { description?: string; [key: string]: any }): string => {
    if (!costAnalysis) return '';
    if (typeof costAnalysis === 'string') return costAnalysis;
    return costAnalysis.description || JSON.stringify(costAnalysis);
  };

  // Helper function to safely get cost analysis for form input
  const getCostAnalysisValue = (costAnalysis?: string | { description?: string; [key: string]: any }): string => {
    if (!costAnalysis) return '';
    if (typeof costAnalysis === 'string') return costAnalysis;
    return costAnalysis.description || '';
  };

  // Helper function to safely get API pricing text
  const getApiPricingText = (apiPricing?: string | { description?: string; [key: string]: any }): string => {
    if (!apiPricing) return '';
    if (typeof apiPricing === 'string') return apiPricing;
    return apiPricing.description || JSON.stringify(apiPricing);
  };

  // Helper function to safely get API pricing for form input
  const getApiPricingValue = (apiPricing?: string | { description?: string; [key: string]: any }): string => {
    if (!apiPricing) return '';
    if (typeof apiPricing === 'string') return apiPricing;
    return apiPricing.description || '';
  };

  // Helper function to safely get key data points text
  const getKeyDataPointsText = (keyDataPoints?: string | string[] | { description?: string; [key: string]: any }): string => {
    if (!keyDataPoints) return '';
    if (typeof keyDataPoints === 'string') return keyDataPoints;
    if (Array.isArray(keyDataPoints)) return keyDataPoints.join(', ');
    return keyDataPoints.description || JSON.stringify(keyDataPoints);
  };

  // Helper function to safely get key data points for form input
  const getKeyDataPointsValue = (keyDataPoints?: string | string[] | { description?: string; [key: string]: any }): string => {
    if (!keyDataPoints) return '';
    if (typeof keyDataPoints === 'string') return keyDataPoints;
    if (Array.isArray(keyDataPoints)) return keyDataPoints.join(', ');
    return keyDataPoints.description || '';
  };

  // Helper function to safely get target data text
  const getTargetDataText = (targetData?: string | { description?: string; [key: string]: any }): string => {
    if (!targetData) return '';
    if (typeof targetData === 'string') return targetData;
    return targetData.description || JSON.stringify(targetData);
  };

  // Helper function to safely get target data for form input
  const getTargetDataValue = (targetData?: string | { description?: string; [key: string]: any }): string => {
    if (!targetData) return '';
    if (typeof targetData === 'string') return targetData;
    return targetData.description || '';
  };

  // Remove hardcoded data - all configurations now come from the database

  // Fetch URL configurations from backend API
  const fetchURLConfigs = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/url-configurations/');
      if (!response.ok) {
        throw new Error('Failed to fetch URL configurations');
      }
      const data = await response.json();
      setPredefinedConfigs(data);
      setFilteredConfigs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchURLConfigs();
  }, []);



  useEffect(() => {
    if (selectedProfile === 'all') {
      setFilteredConfigs(predefinedConfigs);
    } else {
      setFilteredConfigs(predefinedConfigs.filter(config => config.profile_type === selectedProfile));
    }
  }, [selectedProfile, predefinedConfigs]);

  const handleUrlToggle = (url: string) => {
    if (!onUrlsChange) return;
    const newUrls = selectedUrls.includes(url)
      ? selectedUrls.filter(u => u !== url)
      : [...selectedUrls, url];
    onUrlsChange(newUrls);
  };

  const handleCustomUrlAdd = () => {
    if (customUrl && !selectedUrls.includes(customUrl) && onUrlsChange) {
      onUrlsChange([...selectedUrls, customUrl]);
      setCustomUrl('');
    }
  };

  const handleConfigSelect = (config: URLConfig) => {
    handleUrlToggle(config.url);
    if (onConfigSelect) {
      onConfigSelect(config);
    }
  };

  const handleAddConfig = async () => {
    try {
      // Transform form data to match backend expectations
      const transformedConfig = {
        ...newConfig,
        // Map priority to business_priority for backend compatibility
        business_priority: newConfig.priority || 1,
        // Convert key_data_points from string to array
        key_data_points: newConfig.key_data_points 
          ? (typeof newConfig.key_data_points === 'string' 
              ? newConfig.key_data_points.split(',').map(item => item.trim()).filter(item => item.length > 0)
              : newConfig.key_data_points)
          : [],
        // Convert target_data from string to dictionary
        target_data: newConfig.target_data 
          ? (typeof newConfig.target_data === 'string' 
              ? { description: newConfig.target_data }
              : newConfig.target_data)
          : {},
        // Convert cost_analysis from string to dictionary
        cost_analysis: newConfig.cost_analysis 
          ? (typeof newConfig.cost_analysis === 'string' 
              ? { description: newConfig.cost_analysis }
              : newConfig.cost_analysis)
          : {}
      };
      
      // Remove the frontend priority field to avoid confusion
      delete transformedConfig.priority;
      
      console.log('Original form data:', newConfig);
      console.log('Transformed payload:', transformedConfig);
      console.log('Stringified payload:', JSON.stringify(transformedConfig, null, 2));
      
      const response = await fetch('/api/url-configurations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transformedConfig),
      });
      
      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response body:', errorText);
        
        let errorMessage = 'Failed to create URL configuration';
        try {
          const errorData = JSON.parse(errorText);
          console.error('Parsed error data:', errorData);
          if (errorData.detail) {
            errorMessage = Array.isArray(errorData.detail) 
               ? errorData.detail.map((err: any) => `${err.loc?.join('.')} - ${err.msg}`).join(', ')
               : errorData.detail;
          }
        } catch (parseError) {
          console.error('Could not parse error response as JSON:', parseError);
          errorMessage = `HTTP ${response.status}: ${errorText}`;
        }
        
        throw new Error(errorMessage);
      }
      
      const createdConfig = await response.json();
      console.log('Successfully created config:', createdConfig);
      setPredefinedConfigs([...predefinedConfigs, createdConfig]);
      setShowAddDialog(false);
      setNewConfig({});
    } catch (err) {
      console.error('Full error object:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };



  const handleDeleteConfig = async (configId: number) => {
    try {
      const response = await fetch(`/api/url-configurations/${configId}/`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete URL configuration');
      }
      
      setPredefinedConfigs(predefinedConfigs.filter(config => config.id !== configId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const profileTypes = ['all', ...Array.from(new Set(predefinedConfigs.map(config => config.profile_type)))];

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[200px]">
        <div className={`${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Loading URL configurations...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className={`mb-6 text-2xl font-semibold ${
        isDarkMode ? 'text-gray-100' : 'text-gray-800'
      }`}>
        URL Management
      </h2>
      
      {error && (
        <div className={`rounded-lg p-3 mb-4 ${
          isDarkMode 
            ? 'bg-red-900/20 border border-red-800 text-red-400' 
            : 'bg-red-50 border border-red-200 text-red-600'
        }`}>
          {error}
        </div>
      )}

      {/* Profile Filter */}
      <div className="mb-6">
        <label className={`block mb-2 font-medium ${
          isDarkMode ? 'text-gray-300' : 'text-gray-700'
        }`}>
          Filter by Profile Type
        </label>
        <select
          value={selectedProfile}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelectedProfile(e.target.value)}
          className={`w-full px-3 py-2 text-sm rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            isDarkMode 
              ? 'bg-gray-800 border-gray-600 text-gray-200' 
              : 'bg-white border-gray-300 text-gray-900'
          }`}
        >
          <option value="all">All Profiles</option>
          {profileTypes.slice(1).map(profile => (
            <option key={profile} value={profile}>
              {profile}
            </option>
          ))}
        </select>
      </div>

      {/* Custom URL Input */}
      <div className={`rounded-lg p-4 mb-6 border shadow-sm ${
        isDarkMode 
          ? 'bg-gray-800 border-gray-700' 
          : 'bg-white border-gray-200'
      }`}>
        <div className="flex justify-between items-center mb-4">
          <h3 className={`text-lg font-semibold ${
            isDarkMode ? 'text-gray-100' : 'text-gray-800'
          }`}>
            Add Custom URL
          </h3>
          <button
            onClick={() => setShowAddDialog(true)}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-md text-sm font-medium transition-colors"
          >
            <Plus size={16} />
            Add Configuration
          </button>
        </div>
        <div className="flex gap-3">
          <input
            type="text"
            value={customUrl}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCustomUrl(e.target.value)}
            placeholder="https://example.com"
            className={`flex-1 px-3 py-2 text-sm rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-gray-200 placeholder-gray-400' 
                : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
            }`}
          />
          <button
            onClick={handleCustomUrlAdd}
            disabled={!customUrl}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              customUrl 
                ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer' 
                : 'bg-gray-400 text-white cursor-not-allowed'
            }`}
          >
            <Plus size={16} />
            Add
          </button>
        </div>
      </div>

      {/* Selected URLs Summary */}
      {selectedUrls.length > 0 && (
        <div className={`rounded-lg p-4 mb-6 border shadow-sm ${
          isDarkMode 
            ? 'bg-gray-800 border-gray-700' 
            : 'bg-white border-gray-200'
        }`}>
          <h3 className={`mb-4 text-lg font-semibold ${
            isDarkMode ? 'text-gray-100' : 'text-gray-800'
          }`}>
            Selected URLs ({selectedUrls.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {selectedUrls.map((url, index) => (
              <div
                key={index}
                className={`flex items-center gap-2 px-2 py-1 rounded-full text-xs border ${
                  isDarkMode 
                    ? 'bg-blue-900/30 border-blue-700 text-blue-300' 
                    : 'bg-blue-50 border-blue-500 text-blue-700'
                }`}
              >
                <span>{url}</span>
                <button
                  onClick={() => handleUrlToggle(url)}
                  className={`p-0 bg-transparent border-none cursor-pointer flex items-center ${
                    isDarkMode ? 'text-blue-300 hover:text-blue-200' : 'text-blue-700 hover:text-blue-800'
                  }`}
                >
                  <X size={12} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Predefined URL Configurations */}
      <h3 className={`mb-4 text-lg font-semibold ${
        isDarkMode ? 'text-gray-100' : 'text-gray-800'
      }`}>
        Predefined URL Configurations
      </h3>
      
      <div className="grid grid-cols-[repeat(auto-fill,minmax(350px,1fr))] gap-4">
        {filteredConfigs.map((config) => (
          <div
            key={config.id}
            onClick={() => handleConfigSelect(config)}
            className={`rounded-lg p-4 cursor-pointer transition-all duration-150 hover:shadow-md ${
              isDarkMode 
                ? 'bg-gray-800 hover:bg-gray-750' 
                : 'bg-white hover:bg-gray-50'
            } ${
              selectedUrls.includes(config.url) 
                ? (isDarkMode ? 'border-2 border-blue-500' : 'border-2 border-blue-500')
                : (isDarkMode ? 'border border-gray-700' : 'border border-gray-200')
            } shadow-sm`}
          >
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <h4 className={`mb-2 text-base font-semibold ${
                  isDarkMode ? 'text-gray-100' : 'text-gray-800'
                }`}>
                  {config.name}
                </h4>
                <div className="flex items-center gap-2">
                  <span className={isDarkMode ? 'text-gray-400' : 'text-gray-500'}>
                    {profileIcons[config.profile_type as keyof typeof profileIcons]}
                  </span>
                  <span className={`text-sm ${
                    isDarkMode ? 'text-gray-400' : 'text-gray-500'
                  }`}>
                    {config.profile_type}
                  </span>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={(e: React.MouseEvent) => {
                    e.stopPropagation();
                    window.open(config.url, '_blank');
                  }}
                  className={`p-1 rounded bg-transparent border-none cursor-pointer flex items-center transition-colors ${
                    isDarkMode 
                      ? 'text-gray-400 hover:text-gray-300' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <ExternalLink size={16} />
                </button>
                <button
                  onClick={(e: React.MouseEvent) => {
                    e.stopPropagation();
                    handleDeleteConfig(config.id);
                  }}
                  className="p-1 rounded bg-transparent border-none cursor-pointer flex items-center text-red-500 hover:text-red-600 transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>

            {config.description && (
              <p className={`mb-3 text-sm leading-relaxed ${
                isDarkMode ? 'text-gray-300' : 'text-gray-600'
              }`}>
                {config.description}
              </p>
            )}

            <div className="flex gap-2 mb-3 flex-wrap">
              {config.category && (
                <span className={`px-2 py-1 rounded-full text-xs border ${
                  isDarkMode 
                    ? 'bg-blue-900/30 border-blue-700 text-blue-300' 
                    : 'bg-blue-50 border-blue-500 text-blue-700'
                }`}>
                  {config.category}
                </span>
              )}
              {config.priority && (
                <span className={`px-2 py-1 rounded-full text-xs border ${
                  config.priority >= 4
                    ? (isDarkMode ? 'bg-red-900/30 border-red-700 text-red-300' : 'bg-red-50 border-red-500 text-red-700')
                    : config.priority >= 3
                    ? (isDarkMode ? 'bg-orange-900/30 border-orange-700 text-orange-300' : 'bg-orange-50 border-orange-500 text-orange-700')
                    : (isDarkMode ? 'bg-gray-900/30 border-gray-700 text-gray-300' : 'bg-gray-50 border-gray-500 text-gray-700')
                }`}>
                  Priority: {config.priority}/5
                </span>
              )}
              {config.scraping_difficulty && (
                <span className={`px-2 py-1 rounded-full text-xs border ${
                  config.scraping_difficulty === 'High' || config.scraping_difficulty === 'Impossible'
                    ? (isDarkMode ? 'bg-red-900/30 border-red-700 text-red-300' : 'bg-red-50 border-red-500 text-red-700')
                    : config.scraping_difficulty === 'Medium'
                    ? (isDarkMode ? 'bg-yellow-900/30 border-yellow-700 text-yellow-300' : 'bg-yellow-50 border-yellow-500 text-yellow-700')
                    : (isDarkMode ? 'bg-green-900/30 border-green-700 text-green-300' : 'bg-green-50 border-green-500 text-green-700')
                }`}>
                  {config.scraping_difficulty}
                </span>
              )}
              {config.has_official_api && (
                <span className={`px-2 py-1 rounded-full text-xs border ${
                  isDarkMode 
                    ? 'bg-emerald-900/30 border-emerald-700 text-emerald-300' 
                    : 'bg-emerald-50 border-emerald-500 text-emerald-700'
                }`}>
                  API Available
                </span>
              )}
              {config.api_pricing && (
                <span className={`px-2 py-1 rounded-full text-xs border ${
                  getApiPricingText(config.api_pricing).toLowerCase().includes('free')
                    ? (isDarkMode ? 'bg-green-900/30 border-green-700 text-green-300' : 'bg-green-50 border-green-500 text-green-700')
                    : getApiPricingText(config.api_pricing).toLowerCase().includes('paid') || getApiPricingText(config.api_pricing).toLowerCase().includes('$')
                    ? (isDarkMode ? 'bg-purple-900/30 border-purple-700 text-purple-300' : 'bg-purple-50 border-purple-500 text-purple-700')
                    : (isDarkMode ? 'bg-gray-900/30 border-gray-700 text-gray-300' : 'bg-gray-50 border-gray-500 text-gray-700')
                }`}>
                  {getApiPricingText(config.api_pricing).length > 20 ? getApiPricingText(config.api_pricing).substring(0, 20) + '...' : getApiPricingText(config.api_pricing)}
                </span>
              )}
              {config.cost_analysis && (
                <span className={`px-2 py-1 rounded-full text-xs border ${
                  getCostAnalysisText(config.cost_analysis).toLowerCase().includes('low cost') || getCostAnalysisText(config.cost_analysis).toLowerCase().includes('cheap')
                    ? (isDarkMode ? 'bg-green-900/30 border-green-700 text-green-300' : 'bg-green-50 border-green-500 text-green-700')
                    : getCostAnalysisText(config.cost_analysis).toLowerCase().includes('high cost') || getCostAnalysisText(config.cost_analysis).toLowerCase().includes('expensive')
                    ? (isDarkMode ? 'bg-red-900/30 border-red-700 text-red-300' : 'bg-red-50 border-red-500 text-red-700')
                    : (isDarkMode ? 'bg-blue-900/30 border-blue-700 text-blue-300' : 'bg-blue-50 border-blue-500 text-blue-700')
                }`}>
                  Cost Analysis
                </span>
              )}
              {config.recommendation && (
                <span className={`px-2 py-1 rounded-full text-xs border ${
                  config.recommendation.toLowerCase().includes('recommended') || config.recommendation.toLowerCase().includes('good')
                    ? (isDarkMode ? 'bg-green-900/30 border-green-700 text-green-300' : 'bg-green-50 border-green-500 text-green-700')
                    : config.recommendation.toLowerCase().includes('not recommended') || config.recommendation.toLowerCase().includes('avoid')
                    ? (isDarkMode ? 'bg-red-900/30 border-red-700 text-red-300' : 'bg-red-50 border-red-500 text-red-700')
                    : (isDarkMode ? 'bg-indigo-900/30 border-indigo-700 text-indigo-300' : 'bg-indigo-50 border-indigo-500 text-indigo-700')
                }`}>
                  Recommended
                </span>
              )}
            </div>

            <div className="mt-3">
              <details className="cursor-pointer">
                <summary className={`text-sm font-medium mb-2 flex items-center ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>
                  <ChevronDown size={16} className="inline mr-1" />
                  Details
                </summary>
                <div className={`pl-5 text-sm ${
                  isDarkMode ? 'text-gray-400' : 'text-gray-600'
                }`}>
                  {config.recommendation && (
                    <div className="mb-3">
                      <strong className={isDarkMode ? 'text-gray-300' : 'text-gray-700'}>Recommendation:</strong>
                      <p className="mt-1 leading-relaxed">{config.recommendation}</p>
                    </div>
                  )}

                  {config.key_data_points && (
                    <div className="mb-3">
                      <strong className={isDarkMode ? 'text-gray-300' : 'text-gray-700'}>Key Data Points:</strong>
                      <p className="mt-1 leading-relaxed">{getKeyDataPointsText(config.key_data_points)}</p>
                    </div>
                  )}

                  {config.target_data && (
                    <div className="mb-3">
                      <strong className={isDarkMode ? 'text-gray-300' : 'text-gray-700'}>Target Data:</strong>
                      <p className="mt-1 leading-relaxed">{getTargetDataText(config.target_data)}</p>
                    </div>
                  )}

                  {config.api_pricing && (
                    <div className="mb-3">
                      <strong className={isDarkMode ? 'text-gray-300' : 'text-gray-700'}>API Pricing:</strong>
                      <p className="mt-1 leading-relaxed">{getApiPricingText(config.api_pricing)}</p>
                    </div>
                  )}

                  {config.rationale && (
                    <div className="mb-3">
                      <strong className={isDarkMode ? 'text-gray-300' : 'text-gray-700'}>Rationale:</strong>
                      <p className="mt-1 leading-relaxed">{config.rationale}</p>
                    </div>
                  )}

                  {config.cost_analysis && (
                    <div>
                      <strong className={isDarkMode ? 'text-gray-300' : 'text-gray-700'}>Cost Analysis:</strong>
                      <p className="mt-1 leading-relaxed">{getCostAnalysisText(config.cost_analysis)}</p>
                    </div>
                  )}
                </div>
              </details>
            </div>

            {config.priority && (
              <div className="flex justify-end items-center mt-3">
                <div className="flex gap-0.5">
                  {Array.from({ length: 5 }, (_, i) => (
                    <Star
                      key={i}
                      size={14}
                      fill={i < (config.priority || 0) ? '#fbbf24' : 'none'}
                      color={i < (config.priority || 0) ? '#fbbf24' : (isDarkMode ? '#4b5563' : '#d1d5db')}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredConfigs.length === 0 && (
        <div className={`text-center py-8 ${
          isDarkMode ? 'text-gray-400' : 'text-gray-500'
        }`}>
          No URL configurations found for the selected profile.
        </div>
      )}

      {/* Add Configuration Dialog */}
      {showAddDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className={`p-6 rounded-lg w-full max-w-md max-h-[80vh] overflow-auto ${
            isDarkMode ? 'bg-gray-800' : 'bg-white'
          }`}>
            <div className="flex justify-between items-center mb-5">
              <h3 className={`text-xl font-semibold ${
                isDarkMode ? 'text-white' : 'text-gray-900'
              }`}>Add URL Configuration</h3>
              <button
                onClick={() => setShowAddDialog(false)}
                className={`p-1 rounded hover:bg-opacity-10 hover:bg-gray-500 transition-colors ${
                  isDarkMode ? 'text-gray-400 hover:text-gray-300' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="grid gap-4">
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Name *</label>
                <input
                  type="text"
                  value={newConfig.name || ''}
                  onChange={(e) => setNewConfig({ ...newConfig, name: e.target.value })}
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                />
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>URL *</label>
                <input
                  type="url"
                  value={newConfig.url || ''}
                  onChange={(e) => setNewConfig({ ...newConfig, url: e.target.value })}
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                />
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Profile Type *</label>
                <select
                  value={newConfig.profile_type || ''}
                  onChange={(e) => setNewConfig({ ...newConfig, profile_type: e.target.value })}
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  }`}
                >
                  <option value="">Select Profile Type</option>
                  <option value="Degen Gambler">Degen Gambler</option>
                  <option value="Gem Hunter">Gem Hunter</option>
                  <option value="Traditional Investor">Traditional Investor</option>
                  <option value="DeFi Yield Farmer">DeFi Yield Farmer</option>
                </select>
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Description</label>
                <textarea
                  value={newConfig.description || ''}
                  onChange={(e) => setNewConfig({ ...newConfig, description: e.target.value })}
                  rows={3}
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                />
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Category</label>
                <select
                  value={newConfig.category || ''}
                  onChange={(e) => setNewConfig({ ...newConfig, category: e.target.value })}
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  }`}
                >
                  <option value="">Select Category</option>
                  <option value="DeFi Analytics">DeFi Analytics</option>
                  <option value="NFT Marketplace">NFT Marketplace</option>
                  <option value="Crypto News">Crypto News</option>
                  <option value="Trading Platform">Trading Platform</option>
                  <option value="Blockchain Explorer">Blockchain Explorer</option>
                  <option value="Social Media">Social Media</option>
                  <option value="Research Platform">Research Platform</option>
                  <option value="Portfolio Tracker">Portfolio Tracker</option>
                </select>
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Priority (1-5)</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={newConfig.priority || 1}
                  onChange={(e) => setNewConfig({ ...newConfig, priority: parseInt(e.target.value) || 1 })}
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                />
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Scraping Difficulty</label>
                <select
                  value={newConfig.scraping_difficulty || ''}
                  onChange={(e) => setNewConfig({ ...newConfig, scraping_difficulty: e.target.value })}
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  }`}
                >
                  <option value="">Select Difficulty</option>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Impossible">Impossible</option>
                </select>
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Has Official API</label>
                <select
                  value={newConfig.has_official_api === undefined ? '' : newConfig.has_official_api.toString()}
                  onChange={(e) => setNewConfig({ ...newConfig, has_official_api: e.target.value === 'true' })}
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white' 
                      : 'bg-white border-gray-300 text-gray-900'
                  }`}
                >
                  <option value="">Select API Availability</option>
                  <option value="true">Yes</option>
                  <option value="false">No</option>
                </select>
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>API Pricing</label>
                <input
                  type="text"
                  value={getApiPricingValue(newConfig.api_pricing)}
                  onChange={(e) => setNewConfig({ ...newConfig, api_pricing: e.target.value })}
                  placeholder="e.g., Free, $10/month, Pay-per-use"
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                />
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Recommendation</label>
                <textarea
                  value={newConfig.recommendation || ''}
                  onChange={(e) => setNewConfig({ ...newConfig, recommendation: e.target.value })}
                  rows={2}
                  placeholder="Recommended approach for data extraction"
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                />
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Key Data Points</label>
                <textarea
                  value={getKeyDataPointsValue(newConfig.key_data_points)}
                  onChange={(e) => setNewConfig({ ...newConfig, key_data_points: e.target.value })}
                  rows={2}
                  placeholder="Key data points available from this source"
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                />
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Target Data</label>
                <textarea
                  value={getTargetDataValue(newConfig.target_data)}
                  onChange={(e) => setNewConfig({ ...newConfig, target_data: e.target.value })}
                  rows={2}
                  placeholder="Specific target data to extract"
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                />
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Rationale</label>
                <textarea
                  value={newConfig.rationale || ''}
                  onChange={(e) => setNewConfig({ ...newConfig, rationale: e.target.value })}
                  rows={2}
                  placeholder="Business rationale for including this URL"
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                />
              </div>
              
              <div>
                <label className={`block mb-1 font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>Cost Analysis</label>
                <textarea
                  value={getCostAnalysisValue(newConfig.cost_analysis)}
                  onChange={(e) => setNewConfig({ ...newConfig, cost_analysis: e.target.value })}
                  rows={2}
                  placeholder="Cost-benefit analysis for data extraction"
                  className={`w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                />
              </div>
              
              <div className="flex justify-end gap-3 mt-5">
                <button
                  onClick={() => setShowAddDialog(false)}
                  className={`px-4 py-2 rounded-md border transition-colors ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600' 
                      : 'bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddConfig}
                  disabled={!newConfig.name || !newConfig.url || !newConfig.profile_type || !newConfig.category}
                  className={`px-4 py-2 rounded-md text-white transition-colors ${
                    newConfig.name && newConfig.url && newConfig.profile_type && newConfig.category
                      ? 'bg-emerald-600 hover:bg-emerald-700 cursor-pointer' 
                      : 'bg-gray-400 cursor-not-allowed'
                  }`}
                >
                  Add Configuration
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default URLManager;