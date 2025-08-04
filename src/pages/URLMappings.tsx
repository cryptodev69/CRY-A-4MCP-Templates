/**
 * URL Mappings Management Component
 * 
 * This component provides a comprehensive interface for managing URL mappings in the crawler system.
 * It handles the technical configuration of URL-to-extractor associations, including advanced
 * settings like rate limiting, retry logic, validation rules, and crawler-specific parameters.
 * 
 * Key Features:
 * - Create and edit URL mappings with extractor associations
 * - Configure technical parameters (timeouts, retries, rate limits)
 * - Set validation rules and crawler settings
 * - Manage priority ordering and active status
 * - Display mapping statistics and last extraction times
 * 
 * Architecture Note:
 * This component focuses on the technical URL mappings (url_mappings table) as opposed to
 * the business-focused URL configurations (url_configurations table). It provides detailed
 * technical configuration options for developers and system administrators.
 * 
 * Mock Data Implementation:
 * Currently uses mock data for development and UI testing. Backend services should be
 * implemented to match this UI structure and data flow.
 * 
 * @component
 * @author Development Team
 * @version 1.0.0
 */

import React, { useState, useEffect } from 'react';
// import { useApp } from '../contexts/AppContext';
import { useTheme } from '../contexts/ThemeContext';
import { Plus, Edit, Trash2, Power, PowerOff, Settings, ArrowUp, ArrowDown, Link as LinkIcon, X } from 'lucide-react';
import { format } from 'date-fns';

/**
 * URL Configuration Interface
 * 
 * Represents a URL configuration for technical mapping purposes only.
 * Contains only technical fields required for URL mapping operations.
 * Business-related fields are managed separately in the URL Manager.
 * 
 * @interface URLConfig
 */
interface URLConfig {
  /** Unique identifier for the URL configuration */
  id: number;
  /** The URL pattern or specific URL to be mapped */
  url: string;
  /** Display name for the URL configuration */
  name: string;
  /** Whether this URL configuration is currently active */
  is_active: boolean;
  /** Timestamp when the configuration was created */
  created_at: string;
  /** Timestamp when the configuration was last updated */
  updated_at: string;
}

/**
 * Extractor Interface
 * 
 * Represents an extractor that can be associated with URL mappings.
 * Extractors define how data should be extracted from crawled URLs.
 * 
 * @interface Extractor
 */
interface Extractor {
  /** Unique identifier for the extractor */
  id: number;
  /** Display name of the extractor */
  name: string;
  /** Type/category of the extractor */
  type: string;
  /** Whether this extractor is currently active */
  is_active: boolean;
  /** Description of what this extractor does */
  description?: string;
}

/**
 * URL Mapping Form Data Interface
 * 
 * Represents the structure of data used in the URL mapping form.
 * This mirrors the url_mappings database table schema.
 * 
 * @interface URLMappingFormData
 */
interface URLMappingFormData {
  /** Display name for the URL mapping */
  name: string;
  /** Reference to the URL configuration ID */
  url_config_id: number | null;
  /** References to extractor IDs (supports multiple extractors) */
  extractor_ids: number[];
  /** Rate limit in requests per minute */
  rate_limit: number;
  /** Priority level (1-100, higher = more priority) */
  priority: number;
  /** Whether this mapping is currently active */
  is_active: boolean;
  /** JSON string containing metadata */
  metadata: string;
  /** JSON string containing validation rules */
  validation_rules: string;
  /** JSON string containing crawler-specific settings */
  crawler_settings: string;
  /** Array of tags for categorization */
  tags: string[];
  /** Additional notes or comments */
  notes: string;
  /** Category classification */
  category: string;
}

/**
 * URL Mapping Display Interface
 * 
 * Extended interface for displaying URL mappings with additional computed fields.
 * 
 * @interface URLMappingDisplay
 */
interface URLMappingDisplay extends URLMappingFormData {
  /** Unique identifier for the mapping */
  id: number;
  /** URL pattern from the associated URL configuration */
  url: string;
  /** Configuration object parsed from JSON */
  config?: any;
  /** Number of successful extractions */
  extractionCount: number;
  /** Success rate percentage */
  successRate: number;
  /** Timestamp of last extraction */
  lastExtracted: Date | null;
  /** Timestamp when the mapping was created */
  created_at: string;
  /** Timestamp when the mapping was last updated */
  updated_at: string;
}

/**
 * Mock Data: URL Configurations
 * 
 * Simulates the url_configurations table data.
 * These represent business-focused URL configurations that can be
 * associated with technical URL mappings.
 */
const MOCK_URL_CONFIGS: URLConfig[] = [
  {
    id: 1,
    url: 'https://example-news.com/*',
    name: 'Example News Site',
    is_active: true,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z'
  },
  {
    id: 2,
    url: 'https://api.crypto-data.com/v1/*',
    name: 'Crypto Data API',
    is_active: true,
    created_at: '2024-01-16T14:30:00Z',
    updated_at: '2024-01-16T14:30:00Z'
  },
  {
    id: 3,
    url: 'https://social-platform.com/posts/*',
    name: 'Social Media Posts',
    is_active: false,
    created_at: '2024-01-17T09:15:00Z',
    updated_at: '2024-01-17T09:15:00Z'
  },
  {
    id: 4,
    url: 'https://ecommerce-site.com/products/*',
    name: 'E-commerce Products',
    is_active: true,
    created_at: '2024-01-18T16:45:00Z',
    updated_at: '2024-01-18T16:45:00Z'
  },
  {
    id: 5,
    url: 'https://blog-platform.com/articles/*',
    name: 'Blog Articles',
    is_active: true,
    created_at: '2024-01-19T11:20:00Z',
    updated_at: '2024-01-19T11:20:00Z'
  }
];

/**
 * Mock Data: Extractors
 * 
 * Simulates available extractors that can be associated with URL mappings.
 * Each extractor defines how data should be extracted from crawled content.
 */
const MOCK_EXTRACTORS: Extractor[] = [
  {
    id: 1,
    name: 'Article Content Extractor',
    type: 'content',
    is_active: true,
    description: 'Extracts article title, content, and metadata from news sites'
  },
  {
    id: 2,
    name: 'API JSON Parser',
    type: 'api',
    is_active: true,
    description: 'Parses JSON responses from REST APIs'
  },
  {
    id: 3,
    name: 'Social Media Post Extractor',
    type: 'social',
    is_active: true,
    description: 'Extracts posts, comments, and engagement metrics'
  },
  {
    id: 4,
    name: 'Product Information Extractor',
    type: 'ecommerce',
    is_active: true,
    description: 'Extracts product details, prices, and reviews'
  },
  {
    id: 5,
    name: 'Generic HTML Extractor',
    type: 'html',
    is_active: true,
    description: 'General-purpose HTML content extraction'
  },
  {
    id: 6,
    name: 'Image Metadata Extractor',
    type: 'media',
    is_active: false,
    description: 'Extracts metadata from images and media files'
  }
];

/**
 * Mock Data: URL Mappings
 * 
 * Simulates existing URL mappings with their technical configurations.
 * These represent the url_mappings table data.
 */
const MOCK_URL_MAPPINGS: URLMappingDisplay[] = [
  {
    id: 1,
    name: 'News Article Mapping',
    url: 'https://example-news.com/*',
    url_config_id: 1,
    extractor_ids: [1],
    rate_limit: 60,
    priority: 10,
    is_active: true,
    metadata: JSON.stringify({
      source: 'news',
      language: 'en',
      region: 'US'
    }),
    validation_rules: JSON.stringify({
      required: true,
      minLength: 100,
      maxLength: 10000
    }),
    crawler_settings: JSON.stringify({
      timeout: 30000,
      retryAttempts: 3,
      retryDelay: 1000,
      userAgent: 'NewsBot/1.0',
      delay: 2000,
      maxRedirects: 5
    }),
    tags: ['news', 'articles', 'content'],
    notes: 'Primary news content extraction mapping',
    category: 'news',
    config: {
      timeout: 30000,
      retryAttempts: 3,
      patternType: 'wildcard'
    },
    extractionCount: 1247,
    successRate: 94.2,
    lastExtracted: new Date('2024-01-20T15:30:00Z'),
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-20T15:30:00Z'
  },
  {
    id: 2,
    name: 'Crypto API Mapping',
    url: 'https://api.crypto-data.com/v1/*',
    url_config_id: 2,
    extractor_ids: [2],
    rate_limit: 120,
    priority: 8,
    is_active: true,
    metadata: JSON.stringify({
      dataType: 'financial',
      updateFrequency: 'realtime'
    }),
    validation_rules: JSON.stringify({
      required: true,
      format: 'json'
    }),
    crawler_settings: JSON.stringify({
      timeout: 15000,
      retryAttempts: 5,
      retryDelay: 500,
      customHeaders: {
        'Authorization': 'Bearer token',
        'Accept': 'application/json'
      }
    }),
    tags: ['crypto', 'api', 'financial'],
    notes: 'High-frequency crypto data extraction',
    category: 'api',
    config: {
      timeout: 15000,
      retryAttempts: 5,
      patternType: 'exact'
    },
    extractionCount: 5632,
    successRate: 98.7,
    lastExtracted: new Date('2024-01-20T16:45:00Z'),
    created_at: '2024-01-16T14:45:00Z',
    updated_at: '2024-01-20T16:45:00Z'
  },
  {
    id: 3,
    name: 'Product Catalog Mapping',
    url: 'https://ecommerce-site.com/products/*',
    url_config_id: 4,
    extractor_ids: [4, 5],
    rate_limit: 30,
    priority: 6,
    is_active: true,
    metadata: JSON.stringify({
      category: 'ecommerce',
      priceTracking: true
    }),
    validation_rules: JSON.stringify({
      required: false,
      minLength: 50
    }),
    crawler_settings: JSON.stringify({
      timeout: 45000,
      retryAttempts: 2,
      retryDelay: 2000,
      delay: 5000
    }),
    tags: ['ecommerce', 'products', 'prices'],
    notes: 'Product information and pricing data',
    category: 'ecommerce',
    config: {
      timeout: 45000,
      retryAttempts: 2,
      patternType: 'wildcard'
    },
    extractionCount: 892,
    successRate: 87.3,
    lastExtracted: new Date('2024-01-20T12:15:00Z'),
    created_at: '2024-01-18T17:00:00Z',
    updated_at: '2024-01-20T12:15:00Z'
  }
];

/**
 * Default Form Data
 * 
 * Initial state for the URL mapping form with sensible defaults.
 */
const DEFAULT_FORM_DATA: URLMappingFormData = {
  name: '',
  url_config_id: null,
  extractor_ids: [],
  rate_limit: 60,
  priority: 5,
  is_active: true,
  metadata: '{}',
  validation_rules: '{}',
  crawler_settings: JSON.stringify({
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
  }),
  tags: [],
  notes: '',
  category: ''
};

/**
 * URL Mappings Management Component
 * 
 * Main component for managing URL mappings and their technical configurations.
 * Provides a comprehensive interface for creating, editing, and managing URL mappings.
 */
function URLMappings() {
  // Context hooks for app state and theming
  // const { actions } = useApp(); // Commented out for mock implementation
  const { isDarkMode } = useTheme();

  // Component state management
  const [mappings, setMappings] = useState<URLMappingDisplay[]>(MOCK_URL_MAPPINGS);
  const [urlConfigs, setUrlConfigs] = useState<URLConfig[]>(MOCK_URL_CONFIGS);
  const [extractors, setExtractors] = useState<Extractor[]>(MOCK_EXTRACTORS);
  const [formData, setFormData] = useState<URLMappingFormData>(DEFAULT_FORM_DATA);
  const [editingMapping, setEditingMapping] = useState<URLMappingDisplay | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [showAdvancedConfig, setShowAdvancedConfig] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Initialize component data
   * 
   * Loads initial data when component mounts.
   * In a real implementation, this would fetch data from APIs.
   */
  useEffect(() => {
    initializeData();
  }, []);

  /**
   * Initialize Data Function
   * 
   * Simulates loading data from backend services.
   * Sets up mock data for development and testing.
   */
  const initializeData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // In a real implementation, these would be API calls:
      // const urlConfigsResponse = await fetch('/api/url-configurations/');
      // const extractorsResponse = await fetch('/api/extractors/');
      // const mappingsResponse = await fetch('/api/url-mappings/');
      
      // For now, we use mock data
      setUrlConfigs(MOCK_URL_CONFIGS);
      setExtractors(MOCK_EXTRACTORS.filter(e => e.is_active));
      setMappings(MOCK_URL_MAPPINGS);
      
    } catch (err) {
      setError('Failed to load data. Please try again.');
      console.error('Error initializing data:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle Form Submission
   * 
   * Processes form submission for creating or updating URL mappings.
   * Validates input data and updates the mappings list.
   * 
   * @param e - Form submission event
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      
      // Validate required fields
      if (!formData.name.trim()) {
        throw new Error('Mapping name is required');
      }
      
      if (!formData.url_config_id) {
        throw new Error('URL configuration is required');
      }
      
      if (!formData.extractor_ids || formData.extractor_ids.length === 0) {
        throw new Error('At least one extractor must be selected');
      }
      
      // Validate JSON fields
      try {
        JSON.parse(formData.metadata || '{}');
        JSON.parse(formData.validation_rules || '{}');
        JSON.parse(formData.crawler_settings || '{}');
      } catch {
        throw new Error('Invalid JSON in configuration fields');
      }
      
      // Find the associated URL configuration
      const urlConfig = urlConfigs.find(config => config.id === formData.url_config_id);
      if (!urlConfig) {
        throw new Error('Selected URL configuration not found');
      }
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 300));
      
      if (editingMapping) {
        // Update existing mapping
        const updatedMapping: URLMappingDisplay = {
          ...editingMapping,
          ...formData,
          url: urlConfig.url,
          config: JSON.parse(formData.crawler_settings || '{}'),
          updated_at: new Date().toISOString()
        };
        
        setMappings(prev => prev.map(mapping => 
          mapping.id === editingMapping.id ? updatedMapping : mapping
        ));
        
        // In a real implementation:
        // await actions.updateMapping(editingMapping.id, formData);
        
      } else {
        // Create new mapping
        const newMapping: URLMappingDisplay = {
          id: Math.max(...mappings.map(m => m.id), 0) + 1,
          ...formData,
          url: urlConfig.url,
          config: JSON.parse(formData.crawler_settings || '{}'),
          extractionCount: 0,
          successRate: 0,
          lastExtracted: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        setMappings(prev => [...prev, newMapping]);
        
        // In a real implementation:
        // await actions.createMapping(formData);
      }
      
      // Reset form and close
      resetForm();
      setShowForm(false);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle Edit Mapping
   * 
   * Prepares the form for editing an existing URL mapping.
   * Populates form fields with current mapping data.
   * 
   * @param mapping - The mapping to edit
   */
  const handleEdit = (mapping: URLMappingDisplay) => {
    try {
      // Populate form with mapping data
      setFormData({
        name: mapping.name,
        url_config_id: mapping.url_config_id,
        extractor_ids: mapping.extractor_ids || [],
        rate_limit: mapping.rate_limit,
        priority: mapping.priority,
        is_active: mapping.is_active,
        metadata: mapping.metadata || '{}',
        validation_rules: mapping.validation_rules || '{}',
        crawler_settings: mapping.crawler_settings || JSON.stringify({
          timeout: 30000,
          retryAttempts: 3,
          retryDelay: 1000
        }),
        tags: mapping.tags || [],
        notes: mapping.notes || '',
        category: mapping.category || ''
      });
      
      setEditingMapping(mapping);
      setShowForm(true);
      setShowAdvancedConfig(true); // Show advanced config when editing
      
    } catch (err) {
      setError('Failed to load mapping data for editing');
      console.error('Error preparing edit form:', err);
    }
  };

  /**
   * Handle Delete Mapping
   * 
   * Removes a URL mapping from the list.
   * In a real implementation, this would call the backend API.
   * 
   * @param mappingId - ID of the mapping to delete
   */
  const handleDelete = async (mappingId: number) => {
    if (!window.confirm('Are you sure you want to delete this URL mapping?')) {
      return;
    }
    
    try {
      setLoading(true);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 200));
      
      setMappings(prev => prev.filter(mapping => mapping.id !== mappingId));
      
      // In a real implementation:
      // await actions.deleteMapping(mappingId);
      
    } catch (err) {
      setError('Failed to delete mapping');
      console.error('Error deleting mapping:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Toggle Mapping Active Status
   * 
   * Toggles the active status of a URL mapping.
   * 
   * @param mappingId - ID of the mapping to toggle
   */
  const toggleActive = async (mappingId: number) => {
    try {
      const mapping = mappings.find(m => m.id === mappingId);
      if (!mapping) return;
      
      const updatedMapping = {
        ...mapping,
        is_active: !mapping.is_active,
        updated_at: new Date().toISOString()
      };
      
      setMappings(prev => prev.map(m => 
        m.id === mappingId ? updatedMapping : m
      ));
      
      // In a real implementation:
      // await actions.updateMapping(mappingId, { is_active: !mapping.is_active });
      
    } catch (err) {
      setError('Failed to update mapping status');
      console.error('Error toggling mapping status:', err);
    }
  };

  /**
   * Handle Priority Change
   * 
   * Adjusts the priority of a URL mapping up or down.
   * 
   * @param mappingId - ID of the mapping to adjust
   * @param direction - Direction to adjust priority ('up' or 'down')
   */
  const handlePriorityChange = async (mappingId: number, direction: 'up' | 'down') => {
    try {
      const mapping = mappings.find(m => m.id === mappingId);
      if (!mapping) return;
      
      const newPriority = direction === 'up' 
        ? Math.min(mapping.priority + 1, 100)
        : Math.max(mapping.priority - 1, 1);
      
      const updatedMapping = {
        ...mapping,
        priority: newPriority,
        updated_at: new Date().toISOString()
      };
      
      setMappings(prev => prev.map(m => 
        m.id === mappingId ? updatedMapping : m
      ));
      
      // In a real implementation:
      // await actions.updateMapping(mappingId, { priority: newPriority });
      
    } catch (err) {
      setError('Failed to update mapping priority');
      console.error('Error updating priority:', err);
    }
  };

  /**
   * Reset Form
   * 
   * Resets the form to its default state and clears editing mode.
   */
  const resetForm = () => {
    setFormData(DEFAULT_FORM_DATA);
    setEditingMapping(null);
    setShowAdvancedConfig(false);
    setError(null);
  };

  /**
   * Handle New Mapping
   * 
   * Prepares the form for creating a new URL mapping.
   */
  const handleNewMapping = () => {
    resetForm();
    setShowForm(true);
  };

  // Loading state
  if (loading && mappings.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className={isDarkMode ? 'text-gray-300' : 'text-gray-600'}>
            Loading URL mappings...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen transition-colors duration-200 ${
      isDarkMode ? 'bg-gray-900' : 'bg-gray-50'
    }`}>
      <div className="container mx-auto px-4 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className={`text-3xl font-bold ${
                isDarkMode ? 'text-white' : 'text-gray-900'
              }`}>
                URL Mappings
              </h1>
              <p className={`mt-2 text-sm ${
                isDarkMode ? 'text-gray-400' : 'text-gray-600'
              }`}>
                Configure technical URL-to-extractor mappings with advanced settings
              </p>
            </div>
            <button
              onClick={handleNewMapping}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl flex items-center gap-2"
            >
              <Plus size={16} />
              New Mapping
            </button>
          </div>
          
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className={`rounded-lg p-4 ${
              isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
            }`}>
              <div className={`text-2xl font-bold ${
                isDarkMode ? 'text-white' : 'text-gray-900'
              }`}>
                {mappings.length}
              </div>
              <div className={`text-sm ${
                isDarkMode ? 'text-gray-400' : 'text-gray-600'
              }`}>
                Total Mappings
              </div>
            </div>
            <div className={`rounded-lg p-4 ${
              isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
            }`}>
              <div className={`text-2xl font-bold text-green-600`}>
                {mappings.filter(m => m.is_active).length}
              </div>
              <div className={`text-sm ${
                isDarkMode ? 'text-gray-400' : 'text-gray-600'
              }`}>
                Active Mappings
              </div>
            </div>
            <div className={`rounded-lg p-4 ${
              isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
            }`}>
              <div className={`text-2xl font-bold text-blue-600`}>
                {mappings.reduce((sum, m) => sum + m.extractionCount, 0).toLocaleString()}
              </div>
              <div className={`text-sm ${
                isDarkMode ? 'text-gray-400' : 'text-gray-600'
              }`}>
                Total Extractions
              </div>
            </div>
            <div className={`rounded-lg p-4 ${
              isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
            }`}>
              <div className={`text-2xl font-bold text-purple-600`}>
                {mappings.length > 0 ? (
                  (mappings.reduce((sum, m) => sum + m.successRate, 0) / mappings.length).toFixed(1)
                ) : '0'}%
              </div>
              <div className={`text-sm ${
                isDarkMode ? 'text-gray-400' : 'text-gray-600'
              }`}>
                Avg Success Rate
              </div>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            <div className="flex items-center justify-between">
              <span>{error}</span>
              <button
                onClick={() => setError(null)}
                className="text-red-500 hover:text-red-700"
              >
                <X size={16} />
              </button>
            </div>
          </div>
        )}

        {/* Form Section */}
        {showForm && (
          <div className={`rounded-xl shadow-xl mb-8 overflow-hidden ${
            isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
          }`}>
            <div className={`px-6 py-4 border-b ${
              isDarkMode ? 'border-gray-700 bg-gray-750' : 'border-gray-200 bg-gray-50'
            }`}>
              <h2 className={`text-xl font-semibold ${
                isDarkMode ? 'text-white' : 'text-gray-900'
              }`}>
                {editingMapping ? 'Edit URL Mapping' : 'Create New URL Mapping'}
              </h2>
              <p className={`mt-1 text-sm ${
                isDarkMode ? 'text-gray-400' : 'text-gray-600'
              }`}>
                Configure technical parameters for URL-to-extractor association
              </p>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {/* Basic Configuration */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Mapping Name */}
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? 'text-gray-300' : 'text-gray-700'
                  }`}>
                    Mapping Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Enter a descriptive name for this mapping"
                    className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      isDarkMode 
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                        : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                    }`}
                  />
                </div>

                {/* URL Configuration */}
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? 'text-gray-300' : 'text-gray-700'
                  }`}>
                    URL Configuration *
                  </label>
                  <select
                    required
                    value={formData.url_config_id || ''}
                    onChange={(e) => setFormData({ ...formData, url_config_id: parseInt(e.target.value) || null })}
                    className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      isDarkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    }`}
                  >
                    <option value="">Select a URL configuration</option>
                    {urlConfigs.filter(config => config.is_active).map(config => (
                      <option key={config.id} value={config.id}>
                        {config.name} - {config.url}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Extractor Selection */}
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? 'text-gray-300' : 'text-gray-700'
                  }`}>
                    Extractors *
                  </label>
                  <div className={`border rounded-lg p-3 max-h-48 overflow-y-auto ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600' 
                      : 'bg-white border-gray-300'
                  }`}>
                    {extractors.length === 0 ? (
                      <p className={`text-sm ${
                        isDarkMode ? 'text-gray-400' : 'text-gray-500'
                      }`}>
                        No extractors available
                      </p>
                    ) : (
                      extractors.map(extractor => (
                        <label key={extractor.id} className={`flex items-center space-x-3 p-2 rounded hover:bg-opacity-50 cursor-pointer ${
                          isDarkMode ? 'hover:bg-gray-600' : 'hover:bg-gray-100'
                        }`}>
                          <input
                            type="checkbox"
                            checked={formData.extractor_ids.includes(extractor.id)}
                            onChange={(e) => {
                              const updatedIds = e.target.checked
                                ? [...formData.extractor_ids, extractor.id]
                                : formData.extractor_ids.filter(id => id !== extractor.id);
                              setFormData({ ...formData, extractor_ids: updatedIds });
                            }}
                            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                          />
                          <div className="flex-1">
                            <div className={`text-sm font-medium ${
                              isDarkMode ? 'text-white' : 'text-gray-900'
                            }`}>
                              {extractor.name}
                            </div>
                            <div className={`text-xs ${
                              isDarkMode ? 'text-gray-400' : 'text-gray-500'
                            }`}>
                              {extractor.type} • {extractor.is_active ? 'Active' : 'Inactive'}
                            </div>
                            {extractor.description && (
                              <div className={`text-xs mt-1 ${
                                isDarkMode ? 'text-gray-400' : 'text-gray-500'
                              }`}>
                                {extractor.description}
                              </div>
                            )}
                          </div>
                        </label>
                      ))
                    )}
                  </div>
                  {formData.extractor_ids.length > 0 && (
                    <div className="mt-2">
                      <p className={`text-xs ${
                        isDarkMode ? 'text-gray-400' : 'text-gray-500'
                      }`}>
                        {formData.extractor_ids.length} extractor{formData.extractor_ids.length !== 1 ? 's' : ''} selected
                      </p>
                    </div>
                  )}
                </div>

                {/* Priority */}
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? 'text-gray-300' : 'text-gray-700'
                  }`}>
                    Priority (1-100)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 5 })}
                    className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      isDarkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    }`}
                  />
                </div>

                {/* Rate Limit */}
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? 'text-gray-300' : 'text-gray-700'
                  }`}>
                    Rate Limit (requests per minute)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="1000"
                    value={formData.rate_limit}
                    onChange={(e) => setFormData({ ...formData, rate_limit: parseInt(e.target.value) || 60 })}
                    className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      isDarkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    }`}
                  />
                </div>

                {/* Category */}
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? 'text-gray-300' : 'text-gray-700'
                  }`}>
                    Category
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      isDarkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    }`}
                  >
                    <option value="">Select a category</option>
                    <option value="news">News</option>
                    <option value="ecommerce">E-commerce</option>
                    <option value="social">Social Media</option>
                    <option value="blog">Blog</option>
                    <option value="api">API</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              {/* Tags */}
              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>
                  Tags
                </label>
                <input
                  type="text"
                  value={formData.tags.join(', ')}
                  onChange={(e) => {
                    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
                    setFormData({ ...formData, tags });
                  }}
                  placeholder="Enter tags separated by commas"
                  className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                />
              </div>

              {/* Notes */}
              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>
                  Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Add any notes or comments"
                  rows={3}
                  className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                />
              </div>

              {/* Active Status */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="isActive"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="w-4 h-4 accent-blue-500 rounded"
                />
                <label htmlFor="isActive" className={`ml-2 text-sm ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>
                  Active
                </label>
              </div>

              {/* Advanced Configuration Toggle */}
              <div className={`border-t pt-4 ${
                isDarkMode ? 'border-gray-600' : 'border-gray-200'
              }`}>
                <button
                  type="button"
                  onClick={() => setShowAdvancedConfig(!showAdvancedConfig)}
                  className="flex items-center gap-2 bg-transparent border-none cursor-pointer text-sm font-medium text-blue-500 hover:text-blue-600 transition-colors duration-200 p-0"
                >
                  <Settings size={16} />
                  <span>Advanced Configuration</span>
                  {showAdvancedConfig ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
                </button>
              </div>

              {/* Advanced Configuration Section */}
              {showAdvancedConfig && (
                <div className={`p-4 rounded-lg border space-y-4 transition-all duration-200 ${
                  isDarkMode 
                    ? 'bg-gray-700 border-gray-600' 
                    : 'bg-gray-50 border-gray-200'
                }`}>
                  {/* Crawler Settings */}
                  <div className="space-y-4">
                    <h4 className={`text-md font-medium ${
                      isDarkMode ? 'text-gray-200' : 'text-gray-800'
                    }`}>
                      Crawler Settings
                    </h4>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Timeout */}
                      <div>
                        <label className={`block text-sm font-medium mb-1 ${
                          isDarkMode ? 'text-gray-300' : 'text-gray-700'
                        }`}>
                          Timeout (ms)
                        </label>
                        <input
                          type="number"
                          min="1000"
                          max="300000"
                          value={(() => {
                            try {
                              const settings = JSON.parse(formData.crawler_settings || '{}');
                              return settings.timeout || 30000;
                            } catch {
                              return 30000;
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const settings = JSON.parse(formData.crawler_settings || '{}');
                              settings.timeout = parseInt(e.target.value) || 30000;
                              setFormData({ ...formData, crawler_settings: JSON.stringify(settings) });
                            } catch {
                              setFormData({ ...formData, crawler_settings: JSON.stringify({ timeout: parseInt(e.target.value) || 30000 }) });
                            }
                          }}
                          className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                            isDarkMode 
                              ? 'bg-gray-600 border-gray-500 text-white' 
                              : 'bg-white border-gray-300 text-gray-900'
                          }`}
                        />
                      </div>
                      
                      {/* Retry Attempts */}
                      <div>
                        <label className={`block text-sm font-medium mb-1 ${
                          isDarkMode ? 'text-gray-300' : 'text-gray-700'
                        }`}>
                          Retry Attempts
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="10"
                          value={(() => {
                            try {
                              const settings = JSON.parse(formData.crawler_settings || '{}');
                              return settings.retryAttempts || 3;
                            } catch {
                              return 3;
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const settings = JSON.parse(formData.crawler_settings || '{}');
                              settings.retryAttempts = parseInt(e.target.value) || 3;
                              setFormData({ ...formData, crawler_settings: JSON.stringify(settings) });
                            } catch {
                              setFormData({ ...formData, crawler_settings: JSON.stringify({ retryAttempts: parseInt(e.target.value) || 3 }) });
                            }
                          }}
                          className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                            isDarkMode 
                              ? 'bg-gray-600 border-gray-500 text-white' 
                              : 'bg-white border-gray-300 text-gray-900'
                          }`}
                        />
                      </div>
                      
                      {/* Retry Delay */}
                      <div>
                        <label className={`block text-sm font-medium mb-1 ${
                          isDarkMode ? 'text-gray-300' : 'text-gray-700'
                        }`}>
                          Retry Delay (ms)
                        </label>
                        <input
                          type="number"
                          min="100"
                          max="60000"
                          value={(() => {
                            try {
                              const settings = JSON.parse(formData.crawler_settings || '{}');
                              return settings.retryDelay || 1000;
                            } catch {
                              return 1000;
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const settings = JSON.parse(formData.crawler_settings || '{}');
                              settings.retryDelay = parseInt(e.target.value) || 1000;
                              setFormData({ ...formData, crawler_settings: JSON.stringify(settings) });
                            } catch {
                              setFormData({ ...formData, crawler_settings: JSON.stringify({ retryDelay: parseInt(e.target.value) || 1000 }) });
                            }
                          }}
                          className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                            isDarkMode 
                              ? 'bg-gray-600 border-gray-500 text-white' 
                              : 'bg-white border-gray-300 text-gray-900'
                          }`}
                        />
                      </div>
                    </div>
                    
                    {/* User Agent and Delay */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className={`block text-sm font-medium mb-1 ${
                          isDarkMode ? 'text-gray-300' : 'text-gray-700'
                        }`}>
                          User Agent
                        </label>
                        <input
                          type="text"
                          value={(() => {
                            try {
                              const settings = JSON.parse(formData.crawler_settings || '{}');
                              return settings.userAgent || '';
                            } catch {
                              return '';
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const settings = JSON.parse(formData.crawler_settings || '{}');
                              if (e.target.value) {
                                settings.userAgent = e.target.value;
                              } else {
                                delete settings.userAgent;
                              }
                              setFormData({ ...formData, crawler_settings: JSON.stringify(settings) });
                            } catch {
                              const newSettings = e.target.value ? { userAgent: e.target.value } : {};
                              setFormData({ ...formData, crawler_settings: JSON.stringify(newSettings) });
                            }
                          }}
                          placeholder="Custom Bot/1.0"
                          className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                            isDarkMode 
                              ? 'bg-gray-600 border-gray-500 text-white placeholder-gray-400' 
                              : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                          }`}
                        />
                      </div>
                      
                      <div>
                        <label className={`block text-sm font-medium mb-1 ${
                          isDarkMode ? 'text-gray-300' : 'text-gray-700'
                        }`}>
                          Delay (ms)
                        </label>
                        <input
                          type="number"
                          min="0"
                          max="60000"
                          value={(() => {
                            try {
                              const settings = JSON.parse(formData.crawler_settings || '{}');
                              return settings.delay || '';
                            } catch {
                              return '';
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const settings = JSON.parse(formData.crawler_settings || '{}');
                              if (e.target.value) {
                                settings.delay = parseInt(e.target.value);
                              } else {
                                delete settings.delay;
                              }
                              setFormData({ ...formData, crawler_settings: JSON.stringify(settings) });
                            } catch {
                              const newSettings = e.target.value ? { delay: parseInt(e.target.value) } : {};
                              setFormData({ ...formData, crawler_settings: JSON.stringify(newSettings) });
                            }
                          }}
                          placeholder="1000"
                          className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                            isDarkMode 
                              ? 'bg-gray-600 border-gray-500 text-white placeholder-gray-400' 
                              : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                          }`}
                        />
                      </div>
                    </div>
                  </div>
                  
                  {/* Validation Rules */}
                  <div className="space-y-4">
                    <h4 className={`text-md font-medium ${
                      isDarkMode ? 'text-gray-200' : 'text-gray-800'
                    }`}>
                      Validation Rules
                    </h4>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Required Field */}
                      <div className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          id="validation-required"
                          checked={(() => {
                            try {
                              const rules = JSON.parse(formData.validation_rules || '{}');
                              return rules.required || false;
                            } catch {
                              return false;
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const rules = JSON.parse(formData.validation_rules || '{}');
                              rules.required = e.target.checked;
                              setFormData({ ...formData, validation_rules: JSON.stringify(rules) });
                            } catch {
                              setFormData({ ...formData, validation_rules: JSON.stringify({ required: e.target.checked }) });
                            }
                          }}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <label htmlFor="validation-required" className={`text-sm ${
                          isDarkMode ? 'text-gray-300' : 'text-gray-700'
                        }`}>
                          Required field
                        </label>
                      </div>
                      
                      {/* Min Length */}
                      <div>
                        <label className={`block text-sm font-medium mb-1 ${
                          isDarkMode ? 'text-gray-300' : 'text-gray-700'
                        }`}>
                          Min Length
                        </label>
                        <input
                          type="number"
                          min="0"
                          value={(() => {
                            try {
                              const rules = JSON.parse(formData.validation_rules || '{}');
                              return rules.minLength || '';
                            } catch {
                              return '';
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const rules = JSON.parse(formData.validation_rules || '{}');
                              if (e.target.value) {
                                rules.minLength = parseInt(e.target.value);
                              } else {
                                delete rules.minLength;
                              }
                              setFormData({ ...formData, validation_rules: JSON.stringify(rules) });
                            } catch {
                              const newRules = e.target.value ? { minLength: parseInt(e.target.value) } : {};
                              setFormData({ ...formData, validation_rules: JSON.stringify(newRules) });
                            }
                          }}
                          placeholder="Optional"
                          className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                            isDarkMode 
                              ? 'bg-gray-600 border-gray-500 text-white placeholder-gray-400' 
                              : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                          }`}
                        />
                      </div>
                      
                      {/* Max Length */}
                      <div>
                        <label className={`block text-sm font-medium mb-1 ${
                          isDarkMode ? 'text-gray-300' : 'text-gray-700'
                        }`}>
                          Max Length
                        </label>
                        <input
                          type="number"
                          min="0"
                          value={(() => {
                            try {
                              const rules = JSON.parse(formData.validation_rules || '{}');
                              return rules.maxLength || '';
                            } catch {
                              return '';
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const rules = JSON.parse(formData.validation_rules || '{}');
                              if (e.target.value) {
                                rules.maxLength = parseInt(e.target.value);
                              } else {
                                delete rules.maxLength;
                              }
                              setFormData({ ...formData, validation_rules: JSON.stringify(rules) });
                            } catch {
                              const newRules = e.target.value ? { maxLength: parseInt(e.target.value) } : {};
                              setFormData({ ...formData, validation_rules: JSON.stringify(newRules) });
                            }
                          }}
                          placeholder="Optional"
                          className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                            isDarkMode 
                              ? 'bg-gray-600 border-gray-500 text-white placeholder-gray-400' 
                              : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                          }`}
                        />
                      </div>
                    </div>
                  </div>
                  
                  {/* Metadata */}
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${
                      isDarkMode ? 'text-gray-300' : 'text-gray-700'
                    }`}>
                      Metadata (JSON format)
                    </label>
                    <textarea
                      value={formData.metadata}
                      onChange={(e) => setFormData({ ...formData, metadata: e.target.value })}
                      placeholder='{"source": "example", "category": "news"}'
                      rows={3}
                      className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                        isDarkMode 
                          ? 'bg-gray-600 border-gray-500 text-white placeholder-gray-400' 
                          : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                      }`}
                    />
                  </div>
                </div>
              )}

              {/* Form Actions */}
               <div className="flex gap-3 pt-4">
                 <button
                   type="submit"
                   disabled={loading}
                   className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl flex items-center gap-2"
                 >
                   {loading && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
                   {editingMapping ? 'Update Mapping' : 'Create Mapping'}
                 </button>
                 <button
                   type="button"
                   onClick={() => {
                     resetForm();
                     setShowForm(false);
                   }}
                   disabled={loading}
                   className={`px-6 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105 ${
                     isDarkMode 
                       ? 'bg-gray-600 hover:bg-gray-500 text-gray-300 disabled:bg-gray-700' 
                       : 'bg-gray-200 hover:bg-gray-300 text-gray-700 disabled:bg-gray-300'
                   }`}
                 >
                   Cancel
                 </button>
               </div>
             </form>
           </div>
         )}

         {/* Mappings List */}
         <div className={`rounded-xl shadow-xl overflow-hidden ${
           isDarkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
         }`}>
           <div className={`px-6 py-4 border-b ${
             isDarkMode ? 'border-gray-700 bg-gray-750' : 'border-gray-200 bg-gray-50'
           }`}>
             <h2 className={`text-xl font-semibold ${
               isDarkMode ? 'text-white' : 'text-gray-900'
             }`}>
               URL Mappings List
             </h2>
             <p className={`mt-1 text-sm ${
               isDarkMode ? 'text-gray-400' : 'text-gray-600'
             }`}>
               Manage and monitor your URL mapping configurations
             </p>
           </div>

           <div className="overflow-x-auto">
             <table className="w-full border-collapse">
               <thead className={`${
                 isDarkMode ? 'bg-gray-700' : 'bg-gray-50'
               }`}>
                 <tr>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Priority
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Mapping Details
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Extractors
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Status
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Performance
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Last Activity
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Actions
                   </th>
                 </tr>
               </thead>
               <tbody className={`divide-y ${
                 isDarkMode 
                   ? 'bg-gray-800 divide-gray-700' 
                   : 'bg-white divide-gray-200'
               }`}>
                 {mappings.map((mapping) => {
                   const mappingExtractors = extractors.filter(e => mapping.extractor_ids.includes(e.id));
                   return (
                     <tr key={mapping.id} className={`hover:${
                       isDarkMode ? 'bg-gray-700' : 'bg-gray-50'
                     } transition-colors duration-200`}>
                       {/* Priority Column */}
                       <td className="px-6 py-4 whitespace-nowrap">
                         <div className="flex items-center gap-2">
                           <span className={`inline-flex items-center justify-center w-8 h-8 text-sm font-semibold rounded-full ${
                             mapping.priority >= 8 ? 'bg-red-600 text-white' :
                             mapping.priority >= 5 ? 'bg-yellow-600 text-white' :
                             'bg-green-600 text-white'
                           }`}>
                             {mapping.priority}
                           </span>
                           <div className="flex flex-col gap-1">
                             <button
                               onClick={() => handlePriorityChange(mapping.id, 'up')}
                               className={`p-1 text-xs rounded transition-all duration-200 hover:scale-110 ${
                                 isDarkMode 
                                   ? 'border border-gray-600 bg-gray-700 text-gray-300 hover:bg-gray-600' 
                                   : 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                               }`}
                               title="Increase Priority"
                             >
                               <ArrowUp size={12} />
                             </button>
                             <button
                               onClick={() => handlePriorityChange(mapping.id, 'down')}
                               className={`p-1 text-xs rounded transition-all duration-200 hover:scale-110 ${
                                 isDarkMode 
                                   ? 'border border-gray-600 bg-gray-700 text-gray-300 hover:bg-gray-600' 
                                   : 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                               }`}
                               title="Decrease Priority"
                             >
                               <ArrowDown size={12} />
                             </button>
                           </div>
                         </div>
                       </td>

                       {/* Mapping Details Column */}
                       <td className="px-6 py-4">
                         <div className="flex items-start gap-3">
                           <LinkIcon className={`mt-1 h-5 w-5 ${
                             isDarkMode ? 'text-gray-400' : 'text-gray-500'
                           }`} />
                           <div>
                             <div className={`text-sm font-medium ${
                               isDarkMode ? 'text-white' : 'text-gray-900'
                             }`}>
                               {mapping.name}
                             </div>
                             <div className={`text-xs mt-1 ${
                               isDarkMode ? 'text-gray-400' : 'text-gray-500'
                             }`}>
                               {mapping.url}
                             </div>
                             {mapping.tags && mapping.tags.length > 0 && (
                               <div className="flex flex-wrap gap-1 mt-2">
                                 {mapping.tags.slice(0, 3).map((tag, index) => (
                                   <span key={index} className={`text-xs px-2 py-1 rounded ${
                                     isDarkMode 
                                       ? 'bg-gray-600 text-gray-300' 
                                       : 'bg-gray-100 text-gray-700'
                                   }`}>
                                     {tag}
                                   </span>
                                 ))}
                                 {mapping.tags.length > 3 && (
                                   <span className={`text-xs px-2 py-1 rounded ${
                                     isDarkMode 
                                       ? 'bg-gray-600 text-gray-300' 
                                       : 'bg-gray-100 text-gray-700'
                                   }`}>
                                     +{mapping.tags.length - 3}
                                   </span>
                                 )}
                               </div>
                             )}
                           </div>
                         </div>
                       </td>

                       {/* Extractor Column */}
                       <td className="px-6 py-4">
                         {mappingExtractors.length > 0 ? (
                           <div className="space-y-1">
                             {mappingExtractors.slice(0, 2).map((extractor, index) => (
                               <div key={extractor.id}>
                                 <div className={`text-sm font-medium ${
                                   isDarkMode ? 'text-white' : 'text-gray-900'
                                 }`}>
                                   {extractor.name}
                                 </div>
                                 <div className={`text-xs ${
                                   isDarkMode ? 'text-gray-400' : 'text-gray-500'
                                 }`}>
                                   {extractor.type} • {extractor.is_active ? 'Active' : 'Inactive'}
                                 </div>
                               </div>
                             ))}
                             {mappingExtractors.length > 2 && (
                               <div className={`text-xs ${
                                 isDarkMode ? 'text-gray-400' : 'text-gray-500'
                               }`}>
                                 +{mappingExtractors.length - 2} more
                               </div>
                             )}
                           </div>
                         ) : (
                           <span className="text-xs text-red-500">
                             No extractors assigned
                           </span>
                         )}
                       </td>

                       {/* Status Column */}
                       <td className="px-6 py-4 whitespace-nowrap">
                         <div className="flex items-center gap-2">
                           <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                             mapping.is_active 
                               ? 'bg-green-100 text-green-800' 
                               : 'bg-red-100 text-red-800'
                           }`}>
                             {mapping.is_active ? 'Active' : 'Inactive'}
                           </span>
                           <button
                             onClick={() => toggleActive(mapping.id)}
                             className={`p-1 rounded transition-all duration-200 hover:scale-110 ${
                               mapping.is_active 
                                 ? 'text-green-600 hover:bg-green-100' 
                                 : 'text-gray-400 hover:bg-gray-100'
                             }`}
                             title={mapping.is_active ? 'Disable mapping' : 'Enable mapping'}
                           >
                             {mapping.is_active ? <Power size={16} /> : <PowerOff size={16} />}
                           </button>
                         </div>
                         <div className={`text-xs mt-1 ${
                           isDarkMode ? 'text-gray-400' : 'text-gray-500'
                         }`}>
                           Rate: {mapping.rate_limit}/min
                         </div>
                       </td>

                       {/* Performance Column */}
                       <td className="px-6 py-4 whitespace-nowrap">
                         <div className={`text-sm ${
                           isDarkMode ? 'text-gray-300' : 'text-gray-700'
                         }`}>
                           <div className="flex items-center gap-2">
                             <span className="text-xs font-medium">
                               {mapping.extractionCount.toLocaleString()}
                             </span>
                             <span className={`text-xs ${
                               isDarkMode ? 'text-gray-400' : 'text-gray-500'
                             }`}>
                               extractions
                             </span>
                           </div>
                           <div className="flex items-center gap-2 mt-1">
                             <div className={`w-16 h-2 rounded-full ${
                               isDarkMode ? 'bg-gray-600' : 'bg-gray-200'
                             }`}>
                               <div 
                                 className={`h-2 rounded-full ${
                                   mapping.successRate >= 90 ? 'bg-green-500' :
                                   mapping.successRate >= 70 ? 'bg-yellow-500' :
                                   'bg-red-500'
                                 }`}
                                 style={{ width: `${mapping.successRate}%` }}
                               ></div>
                             </div>
                             <span className={`text-xs ${
                               isDarkMode ? 'text-gray-400' : 'text-gray-500'
                             }`}>
                               {mapping.successRate.toFixed(1)}%
                             </span>
                           </div>
                         </div>
                       </td>

                       {/* Last Activity Column */}
                       <td className="px-6 py-4 whitespace-nowrap">
                         <div className={`text-sm ${
                           isDarkMode ? 'text-gray-400' : 'text-gray-500'
                         }`}>
                           {mapping.lastExtracted ? (
                             <div>
                               <div>{format(mapping.lastExtracted, 'MMM dd, yyyy')}</div>
                               <div className="text-xs">{format(mapping.lastExtracted, 'HH:mm')}</div>
                             </div>
                           ) : (
                             <span className="text-xs">Never extracted</span>
                           )}
                         </div>
                       </td>

                       {/* Actions Column */}
                       <td className="px-6 py-4 whitespace-nowrap">
                         <div className="flex gap-2">
                           <button
                             onClick={() => handleEdit(mapping)}
                             className={`p-2 text-xs font-medium rounded-lg transition-all duration-200 hover:scale-105 ${
                               isDarkMode 
                                 ? 'border border-gray-600 bg-gray-700 text-gray-300 hover:bg-gray-600' 
                                 : 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                             }`}
                             title="Edit mapping"
                           >
                             <Edit size={14} />
                           </button>
                           <button
                             onClick={() => handleDelete(mapping.id)}
                             className="p-2 text-xs font-medium rounded-lg bg-red-600 hover:bg-red-700 text-white transition-all duration-200 hover:scale-105"
                             title="Delete mapping"
                           >
                             <Trash2 size={14} />
                           </button>
                         </div>
                       </td>
                     </tr>
                   );
                 })}
               </tbody>
             </table>
           </div>

           {/* Empty State */}
           {mappings.length === 0 && (
             <div className="text-center py-12">
               <LinkIcon className={`mx-auto h-12 w-12 mb-4 ${
                 isDarkMode ? 'text-gray-600' : 'text-gray-400'
               }`} />
               <h3 className={`text-lg font-medium mb-2 ${
                 isDarkMode ? 'text-gray-300' : 'text-gray-700'
               }`}>
                 No URL mappings found
               </h3>
               <p className={`mb-4 ${
                 isDarkMode ? 'text-gray-400' : 'text-gray-500'
               }`}>
                 Create your first URL mapping to start configuring your crawler.
               </p>
               <button
                 onClick={handleNewMapping}
                 className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl flex items-center gap-2 mx-auto"
               >
                 <Plus size={16} />
                 Create First Mapping
               </button>
             </div>
           )}
         </div>
       </div>
     </div>
   );
 }

 export default URLMappings;