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
import { Plus, Edit, Trash2, Power, PowerOff, Settings, ArrowUp, ArrowDown, Link as LinkIcon, X, AlertCircle, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import { urlMappingsService } from '../services/urlMappingsService';
import { ApiClientError } from '../services/apiClient';
import { URLConfig, URLMappingDisplay, URLMappingFormData, Extractor } from '../types/urlMappings';

// URLConfig interface is now imported from '../types/urlMappings'

// Extractor interface is now imported from '../types/urlMappings'

// URLMappingFormData interface is now imported from '../types/urlMappings'

// URLMappingDisplay interface is now imported from '../types/urlMappings'

/**
 * Mock Data: URL Configurations
 * 
 * Simulates the url_configurations table data.
 * These represent business-focused URL configurations that can be
 * associated with technical URL mappings.
 */
const MOCK_URL_CONFIGS: URLConfig[] = [
  {
    id: '1',
    url: 'https://example-news.com/*',
    name: 'Example News Site',
    isActive: true,
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
    baseUrl: 'https://example-news.com',
    profileType: 'news',
    category: 'news',
    description: 'Example news site configuration',
    priority: 5,
    scrapingDifficulty: 5,
    hasOfficialAPI: false,
    hasOfficialApi: false
  },
  {
    id: '2',
    url: 'https://api.crypto-data.com/v1/*',
    name: 'Crypto Data API',
    isActive: true,
    createdAt: '2024-01-16T14:30:00Z',
    updatedAt: '2024-01-16T14:30:00Z',
    baseUrl: 'https://api.crypto-data.com',
    profileType: 'api',
    category: 'crypto',
    description: 'Crypto data API configuration',
    priority: 8,
    scrapingDifficulty: 3,
    hasOfficialAPI: true,
    hasOfficialApi: true
  },
  {
    id: '3',
    url: 'https://social-platform.com/posts/*',
    name: 'Social Media Posts',
    isActive: false,
    createdAt: '2024-01-17T09:15:00Z',
    updatedAt: '2024-01-17T09:15:00Z',
    baseUrl: 'https://social-platform.com',
    profileType: 'social',
    category: 'social',
    description: 'Social media posts configuration',
    priority: 3,
    scrapingDifficulty: 8,
    hasOfficialAPI: false,
    hasOfficialApi: false
  },
  {
    id: '4',
    url: 'https://ecommerce-site.com/products/*',
    name: 'E-commerce Products',
    isActive: true,
    createdAt: '2024-01-18T16:45:00Z',
    updatedAt: '2024-01-18T16:45:00Z',
    baseUrl: 'https://ecommerce-site.com',
    profileType: 'ecommerce',
    category: 'ecommerce',
    description: 'E-commerce products configuration',
    priority: 6,
    scrapingDifficulty: 5,
    hasOfficialAPI: false,
    hasOfficialApi: false
  },
  {
    id: '5',
    url: 'https://blog-platform.com/articles/*',
    name: 'Blog Articles',
    isActive: true,
    createdAt: '2024-01-19T11:20:00Z',
    updatedAt: '2024-01-19T11:20:00Z',
    baseUrl: 'https://blog-platform.com',
    profileType: 'blog',
    category: 'content',
    description: 'Blog articles configuration',
    priority: 4,
    scrapingDifficulty: 3,
    hasOfficialAPI: false,
    hasOfficialApi: false
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
    id: '1',
    name: 'Article Content Extractor',
    type: 'content',
    isActive: true,
    description: 'Extracts article title, content, and metadata from news sites'
  },
  {
    id: '2',
    name: 'API JSON Parser',
    type: 'api',
    isActive: true,
    description: 'Parses JSON responses from REST APIs'
  },
  {
    id: '3',
    name: 'Social Media Post Extractor',
    type: 'social',
    isActive: true,
    description: 'Extracts posts, comments, and engagement metrics'
  },
  {
    id: '4',
    name: 'Product Information Extractor',
    type: 'ecommerce',
    isActive: true,
    description: 'Extracts product details, prices, and reviews'
  },
  {
    id: '5',
    name: 'Generic HTML Extractor',
    type: 'html',
    isActive: true,
    description: 'General-purpose HTML content extraction'
  },
  {
    id: '6',
    name: 'Image Metadata Extractor',
    type: 'media',
    isActive: false,
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
    id: '1',
    name: 'News Article Mapping',
    url: 'https://example-news.com/*',
    configurationId: '1',
    extractorId: '1',
    extractorIds: ['1'],
    rateLimit: 60,
    priority: 10,
    isActive: true,
    metadata: {
      source: 'news',
      language: 'en',
      region: 'US'
    },
    validationRules: {
      required: true,
      minLength: 100,
      maxLength: 10000
    },
    crawlerSettings: {
      timeout: 30000,
      retryAttempts: 3,
      retryDelay: 1000,
      userAgent: 'NewsBot/1.0',
      delay: 2000,
      maxRedirects: 5
    },
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
    lastExtracted: '2024-01-20T15:30:00Z',
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-20T15:30:00Z'
  },
  {
    id: '2',
    name: 'Crypto API Mapping',
    url: 'https://api.crypto-data.com/v1/*',
    configurationId: '2',
    extractorId: '2',
    extractorIds: ['2'],
    rateLimit: 120,
    priority: 8,
    isActive: true,
    metadata: {
      dataType: 'financial',
      updateFrequency: 'realtime'
    },
    validationRules: {
      required: true,
      format: 'json'
    },
    crawlerSettings: {
      timeout: 15000,
      retryAttempts: 5,
      retryDelay: 500,
      customHeaders: {
        'Authorization': 'Bearer token',
        'Accept': 'application/json'
      }
    },
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
    lastExtracted: '2024-01-20T16:45:00Z',
    created_at: '2024-01-16T14:45:00Z',
    updated_at: '2024-01-20T16:45:00Z'
  },
  {
    id: '3',
    name: 'Product Catalog Mapping',
    url: 'https://ecommerce-site.com/products/*',
    configurationId: '4',
    extractorId: '4',
    extractorIds: ['4'],
    rateLimit: 30,
    priority: 6,
    isActive: true,
    metadata: {
      category: 'ecommerce',
      priceTracking: true
    },
    validationRules: {
      required: false,
      minLength: 50
    },
    crawlerSettings: {
      timeout: 45000,
      retryAttempts: 2,
      retryDelay: 2000,
      delay: 5000
    },
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
    lastExtracted: '2024-01-20T12:15:00Z',
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
  configurationId: null,
  extractorId: null, // Legacy single extractor support
  extractorIds: [], // New multiple extractors support
  rateLimit: 60,
  priority: 5,
  isActive: true,
  metadata: '{}',
  validationRules: '{}',
  crawlerSettings: JSON.stringify({
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

  // Component State
  const [mappings, setMappings] = useState<URLMappingDisplay[]>([]);
  const [urlConfigs, setUrlConfigs] = useState<URLConfig[]>([]);
  const [extractors, setExtractors] = useState<Extractor[]>([]);
  const [formData, setFormData] = useState<URLMappingFormData>(DEFAULT_FORM_DATA);
  const [editingMapping, setEditingMapping] = useState<URLMappingDisplay | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [showAdvancedConfig, setShowAdvancedConfig] = useState(false);
  const [loading, setLoading] = useState(true);
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
   * Debug: Log state changes
   */
  useEffect(() => {
    console.log('=== State Updated ===');
    console.log('urlConfigs state:', urlConfigs.length, 'items:', urlConfigs);
    console.log('extractors state:', extractors.length, 'items:', extractors);
    console.log('extractors details:', extractors.map(e => ({ id: e.id, name: e.name, isActive: e.isActive })));
    console.log('Active URL configs for dropdown:', urlConfigs.filter(config => config.isActive).length);
    console.log('formData.extractorIds:', formData.extractorIds);
  }, [urlConfigs, extractors, formData.extractorIds]);

  /**
   * Initialize Data Function
   * 
   * Loads data from backend services using the API client.
   * Fetches URL configurations, extractors, and URL mappings.
   */
  const initializeData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('=== URLMappings Component Debug ===');
      console.log('Attempting to fetch data from backend APIs...');
      
      // Fetch all data from backend APIs
      const data = await urlMappingsService.getAllDataForUI();
      
      console.log('API Response:', data);
      console.log('URL Configurations count:', data.urlConfigurations?.length || 0);
      console.log('URL Configurations sample:', data.urlConfigurations?.slice(0, 2));
      console.log('Extractors count:', data.extractors?.length || 0);
      console.log('Extractors sample:', data.extractors?.slice(0, 2));
      console.log('URL Mappings count:', data.urlMappings?.length || 0);
      
      // Check if we got empty data and fall back to mock data
      if (data.urlConfigurations.length === 0 && data.extractors.length === 0) {
        console.warn('API returned empty data, falling back to mock data for development');
        console.log('Setting mock URL configs:', MOCK_URL_CONFIGS.length, 'items');
        console.log('Setting mock extractors:', MOCK_EXTRACTORS.filter(e => e.isActive).length, 'active items');
        console.log('Mock extractors details:', MOCK_EXTRACTORS.map(e => ({ id: e.id, name: e.name, isActive: e.isActive })));
        setUrlConfigs(MOCK_URL_CONFIGS);
        setExtractors(MOCK_EXTRACTORS.filter(e => e.isActive));
        setMappings(MOCK_URL_MAPPINGS);
        setError('Using mock data - backend API returned empty results');
      } else {
        console.log('Using API data - URL configs:', data.urlConfigurations.length, 'extractors:', data.extractors.length);
        console.log('Active extractors before filtering:', data.extractors.filter(e => e.isActive).length);
        console.log('All extractors isActive status:', data.extractors.map(e => ({ id: e.id, name: e.name, isActive: e.isActive })));
        
        // Data loaded successfully from API
        
        setUrlConfigs(data.urlConfigurations);
        setExtractors(data.extractors.filter(e => e.isActive));
        setMappings(data.urlMappings);
      }
      
    } catch (err) {
      console.error('Error initializing data:', err);
      console.warn('API failed, falling back to mock data for development');
      
      // Fall back to mock data when API fails
      console.log('Setting fallback mock data - URL configs:', MOCK_URL_CONFIGS.length, 'extractors:', MOCK_EXTRACTORS.filter(e => e.isActive).length);
      console.log('Fallback mock extractors details:', MOCK_EXTRACTORS.map(e => ({ id: e.id, name: e.name, isActive: e.isActive })));
      setUrlConfigs(MOCK_URL_CONFIGS);
      setExtractors(MOCK_EXTRACTORS.filter(e => e.isActive));
      setMappings(MOCK_URL_MAPPINGS);
      
      if (err instanceof ApiClientError) {
        setError(`API Error (using mock data): ${err.message}`);
      } else {
        setError('API connection failed (using mock data). Please check backend service.');
      }
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
      
      console.log('🔍 Form submission started:');
      console.log('  - Current formData:', formData);
      console.log('  - configurationId:', formData.configurationId);
      console.log('  - editingMapping:', editingMapping);
      
      // Validate required fields
      if (!formData.configurationId) {
        console.error('❌ No configurationId in form data');
        throw new Error('URL configuration is required');
      }
      
      if (formData.extractorIds.length === 0) {
        console.error('❌ No extractors selected');
        console.error('Available extractors:', extractors.length);
        console.error('Extractors list:', extractors.map(e => ({ id: e.id, name: e.name })));
        throw new Error('At least one extractor must be selected. Please check the extractors section and select at least one.');
      }
      
      // Validate JSON fields
      try {
        if (formData.validationRules && typeof formData.validationRules === 'string') {
          JSON.parse(formData.validationRules);
        }
        if (formData.crawlerSettings && typeof formData.crawlerSettings === 'string') {
          JSON.parse(formData.crawlerSettings);
        }
      } catch {
        throw new Error('Invalid JSON in configuration fields');
      }
      
      if (editingMapping) {
        // Update existing mapping
        const updateData = urlMappingsService.transformURLMappingToBackend(formData);
        
        console.log('🔍 Backend transformation for UPDATE:');
        console.log('  - Original formData:', formData);
        console.log('  - Transformed updateData:', updateData);
        console.log('  - url_config_id in update data:', updateData.url_config_id);
        
        // LOG THE ACTUAL HTTP REQUEST DETAILS
        console.log('🚀 ACTUAL HTTP REQUEST BEING SENT:');
        console.log('  - Method: PUT');
        console.log('  - Endpoint: /api/url-mappings/' + editingMapping.id);
        console.log('  - Mapping ID being updated:', editingMapping.id);
        console.log('  - Complete updateData object:', JSON.stringify(updateData, null, 2));
        console.log('  - All fields in updateData:');
        Object.keys(updateData).forEach(key => {
          const value = (updateData as any)[key];
          console.log(`    - ${key}: ${JSON.stringify(value)} (${typeof value})`);
        });
        
        const updatedMapping = await urlMappingsService.updateURLMapping(editingMapping.id, updateData);
        
        console.log('🔍 Backend response for UPDATE:', updatedMapping);
        
        // Transform the backend response to frontend format
        const transformedMapping = await urlMappingsService.transformURLMappingToFrontend(updatedMapping);
        
        // Update the local state with the updated mapping
        setMappings(prev => prev.map(m => 
          m.id === editingMapping.id ? transformedMapping : m
        ));
        
        // Close the form after successful update
        resetForm();
        setShowForm(false);
        setEditingMapping(null);
        console.log('🔍 Form closed after successful update');
        
      } else {
        // Create new mapping
        const createData = urlMappingsService.transformURLMappingToBackend(formData);
        
        console.log('🔍 Backend transformation for CREATE:');
        console.log('  - Original formData:', formData);
        console.log('  - Transformed createData:', createData);
        console.log('  - url_config_id in create data:', createData.url_config_id);
        
        const newMapping = await urlMappingsService.createURLMapping(createData);
        
        console.log('🔍 Backend response for CREATE:', newMapping);
        
        const transformedMapping = await urlMappingsService.transformURLMappingToFrontend(newMapping);
        
        setMappings(prev => [...prev, transformedMapping]);
        
        // Reset form and close only for new mappings
        resetForm();
        setShowForm(false);
      }
      
    } catch (err) {
      console.error('Error submitting form:', err);
      if (err instanceof ApiClientError) {
        setError(`Failed to save mapping: ${err.message}`);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An error occurred while saving the mapping');
      }
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
        configurationId: mapping.configurationId,
        extractorId: mapping.extractorId, // Legacy single extractor
        extractorIds: mapping.extractorIds || (mapping.extractorId ? [mapping.extractorId] : []), // Multiple extractors with backward compatibility
        rateLimit: mapping.rateLimit,
        priority: mapping.priority,
        isActive: mapping.isActive,
        metadata: JSON.stringify(mapping.metadata || {}),
        validationRules: JSON.stringify(mapping.validationRules || {}),
        crawlerSettings: JSON.stringify(mapping.crawlerSettings || {
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
  const handleDelete = async (mappingId: string) => {
    if (!window.confirm('Are you sure you want to delete this URL mapping?')) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Delete mapping via API
      await urlMappingsService.deleteURLMapping(mappingId);
      
      // Remove from local state
      setMappings(prev => prev.filter(mapping => mapping.id !== mappingId));
      
    } catch (err) {
      console.error('Error deleting mapping:', err);
      if (err instanceof ApiClientError) {
        setError(`Failed to delete mapping: ${err.message}`);
      } else {
        setError('Failed to delete mapping. Please try again.');
      }
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
  const toggleActive = async (mappingId: string) => {
    try {
      const mapping = mappings.find(m => m.id === mappingId);
      if (!mapping) return;
      
      // Update mapping via API
      const updatedMapping = await urlMappingsService.updateURLMapping(mappingId, {
        is_active: !mapping.isActive
      });
      
      const transformedMapping = await urlMappingsService.transformURLMappingToFrontend(updatedMapping);
      
      setMappings(prev => prev.map(m => 
        m.id === mappingId ? transformedMapping : m
      ));
      
    } catch (err) {
      console.error('Error toggling mapping status:', err);
      if (err instanceof ApiClientError) {
        setError(`Failed to update mapping status: ${err.message}`);
      } else {
        setError('Failed to update mapping status. Please try again.');
      }
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
  const handlePriorityChange = async (mappingId: string, direction: 'up' | 'down') => {
    try {
      const mapping = mappings.find(m => m.id === mappingId);
      if (!mapping) {
        console.error('❌ Mapping not found for ID:', mappingId);
        return;
      }
      
      console.log('🔍 Priority Change Debug - Input:');
      console.log('  - Mapping ID:', mappingId);
      console.log('  - Current mapping:', mapping);
      console.log('  - Current priority:', mapping.priority);
      console.log('  - Direction:', direction);
      
      const newPriority = direction === 'up' 
        ? Math.min(mapping.priority + 1, 10)
        : Math.max(mapping.priority - 1, 1);
      
      console.log('  - New priority:', newPriority);
      
      // Prepare update data
      const updateData = { priority: newPriority };
      console.log('🔍 Sending update data to backend:', updateData);
      
      // Update the mapping priority via API
      const updatedMappingResponse = await urlMappingsService.updateURLMapping(mappingId, updateData);
      
      console.log('🔍 Backend response:', updatedMappingResponse);
      console.log('  - Response priority:', updatedMappingResponse.priority);
      
      // Transform backend response to frontend format
      const updatedMapping = await urlMappingsService.transformURLMappingToFrontend(updatedMappingResponse);
      
      console.log('🔍 Transformed mapping:', updatedMapping);
      console.log('  - Transformed priority:', updatedMapping.priority);
      console.log('  - Transformed URL:', updatedMapping.url);
      
      // Preserve existing fields that might be missing from backend response
      const preservedMapping = {
        ...updatedMapping,
        // Preserve URL and other important fields from current mapping if missing in response
        url: updatedMapping.url || mapping.url,
        name: updatedMapping.name || mapping.name,
        configuration: updatedMapping.configuration || mapping.configuration
      };
      
      console.log('🔍 Preserved mapping with URL:', preservedMapping);
      console.log('  - Preserved URL:', preservedMapping.url);
      
      // Update local state with the preserved mapping
      setMappings(prev => {
        const newMappings = prev.map(m => 
          m.id === mappingId ? preservedMapping : m
        );
        console.log('🔍 Updated mappings state:', newMappings.find(m => m.id === mappingId));
        return newMappings;
      });
      
      console.log('✅ Priority update completed successfully');
      
    } catch (err) {
      console.error('❌ Error updating priority:', err);
      console.error('❌ Error details:', {
        message: err instanceof Error ? err.message : 'Unknown error',
        stack: err instanceof Error ? err.stack : undefined,
        response: (err as any)?.response
      });
      if (err instanceof ApiClientError) {
        setError(`Failed to update mapping priority: ${err.message}`);
      } else {
        setError('Failed to update mapping priority. Please try again.');
      }
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
                {mappings.filter(m => m.isActive).length}
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
                    value={formData.configurationId || ''}
                    onChange={(e) => {
                      const newConfigId = e.target.value || null;
                      console.log('🔍 URL Configuration dropdown changed:');
                      console.log('  - Previous configurationId:', formData.configurationId);
                      console.log('  - New configurationId:', newConfigId);
                      console.log('  - Selected option value:', e.target.value);
                      
                      setFormData(prevFormData => {
                        const updatedFormData = { ...prevFormData, configurationId: newConfigId };
                        console.log('  - Form data after update:', updatedFormData);
                        return updatedFormData;
                      });
                    }}
                    required
                    className={`w-full px-3 py-2 rounded-lg text-sm transition-all duration-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      isDarkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    }`}
                  >
                    <option value="">Select a URL configuration</option>
                    {urlConfigs.filter(config => config.isActive).map(config => (
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
                    Extractors * {formData.extractorIds.length > 0 && (
                      <span className="text-green-600 text-xs ml-2">({formData.extractorIds.length} selected)</span>
                    )}
                  </label>
                  <div className={`border rounded-lg p-3 max-h-48 overflow-y-auto ${
                    isDarkMode 
                      ? 'bg-gray-700 border-gray-600' 
                      : 'bg-white border-gray-300'
                  } ${
                    formData.extractorIds.length === 0 ? 'border-red-300' : ''
                  }`}>
                    {extractors.length === 0 ? (
                      <div className={`text-sm p-2 rounded ${
                        isDarkMode ? 'text-red-400 bg-red-900/20' : 'text-red-600 bg-red-50'
                      }`}>
                        ⚠️ No extractors available. Please check the backend connection or contact support.
                      </div>
                    ) : (
                      <>
                        {formData.extractorIds.length === 0 && (
                          <div className={`text-xs mb-2 p-2 rounded ${
                            isDarkMode ? 'text-yellow-400 bg-yellow-900/20' : 'text-yellow-700 bg-yellow-50'
                          }`}>
                            ⚠️ Please select at least one extractor to continue
                          </div>
                        )}
                        {extractors.map(extractor => (
                      <label key={extractor.id} className={`flex items-center space-x-3 p-2 rounded hover:bg-opacity-50 cursor-pointer ${
                        isDarkMode ? 'hover:bg-gray-600' : 'hover:bg-gray-100'
                      }`}>
                        <input
                          type="checkbox"
                          checked={formData.extractorIds.includes(extractor.id)}
                          onChange={(e) => {
                            const isChecked = e.target.checked;
                            console.log('🔍 Extractor checkbox changed:');
                            console.log('  - Extractor ID:', extractor.id);
                            console.log('  - Extractor Name:', extractor.name);
                            console.log('  - Is Checked:', isChecked);
                            console.log('  - Previous extractorIds:', formData.extractorIds);
                            
                            setFormData(prevFormData => {
                              let newExtractorIds: string[];
                              
                              if (isChecked) {
                                // Add extractor to selection
                                newExtractorIds = [...prevFormData.extractorIds, extractor.id];
                              } else {
                                // Remove extractor from selection
                                newExtractorIds = prevFormData.extractorIds.filter(id => id !== extractor.id);
                              }
                              
                              const updatedFormData = {
                                ...prevFormData, 
                                extractorIds: newExtractorIds,
                                extractorId: newExtractorIds.length > 0 ? newExtractorIds[0] : null // Use first selected for legacy
                              };
                              
                              console.log('  - New extractorIds:', newExtractorIds);
                              console.log('  - Updated form data:', updatedFormData);
                              
                              return updatedFormData;
                            });
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
                            {extractor.type} • {extractor.isActive ? 'Active' : 'Inactive'}
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
                        ))}
                       </>
                     )}
                  </div>
                  {formData.extractorIds.length > 0 && (
                    <div className="mt-2">
                      <p className={`text-xs ${
                        isDarkMode ? 'text-gray-400' : 'text-gray-500'
                      }`}>
                        {formData.extractorIds.length} extractor{formData.extractorIds.length !== 1 ? 's' : ''} selected
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
                    value={formData.rateLimit}
                    onChange={(e) => setFormData({ ...formData, rateLimit: parseInt(e.target.value) || 60 })}
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
                  checked={formData.isActive}
                  onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
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
                              const settings = JSON.parse(formData.crawlerSettings || '{}');
                              return settings.timeout || 30000;
                            } catch {
                              return 30000;
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const settings = JSON.parse(formData.crawlerSettings || '{}');
                              settings.timeout = parseInt(e.target.value) || 30000;
                              setFormData({ ...formData, crawlerSettings: JSON.stringify(settings) });
                            } catch {
                              setFormData({ ...formData, crawlerSettings: JSON.stringify({ timeout: parseInt(e.target.value) || 30000 }) });
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
                              const settings = JSON.parse(formData.crawlerSettings || '{}');
                              return settings.retryAttempts || 3;
                            } catch {
                              return 3;
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const settings = JSON.parse(formData.crawlerSettings || '{}');
                              settings.retryAttempts = parseInt(e.target.value) || 3;
                              setFormData({ ...formData, crawlerSettings: JSON.stringify(settings) });
                            } catch {
                              setFormData({ ...formData, crawlerSettings: JSON.stringify({ retryAttempts: parseInt(e.target.value) || 3 }) });
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
                              const settings = JSON.parse(formData.crawlerSettings || '{}');
                              return settings.retryDelay || 1000;
                            } catch {
                              return 1000;
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const settings = JSON.parse(formData.crawlerSettings || '{}');
                              settings.retryDelay = parseInt(e.target.value) || 1000;
                              setFormData({ ...formData, crawlerSettings: JSON.stringify(settings) });
                            } catch {
                              setFormData({ ...formData, crawlerSettings: JSON.stringify({ retryDelay: parseInt(e.target.value) || 1000 }) });
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
                              const settings = JSON.parse(formData.crawlerSettings || '{}');
                              return settings.userAgent || '';
                            } catch {
                              return '';
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const settings = JSON.parse(formData.crawlerSettings || '{}');
                              if (e.target.value) {
                                settings.userAgent = e.target.value;
                              } else {
                                delete settings.userAgent;
                              }
                              setFormData({ ...formData, crawlerSettings: JSON.stringify(settings) });
                            } catch {
                              const newSettings = e.target.value ? { userAgent: e.target.value } : {};
                              setFormData({ ...formData, crawlerSettings: JSON.stringify(newSettings) });
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
                              const settings = JSON.parse(formData.crawlerSettings || '{}');
                              return settings.delay || '';
                            } catch {
                              return '';
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const settings = JSON.parse(formData.crawlerSettings || '{}');
                              if (e.target.value) {
                                settings.delay = parseInt(e.target.value);
                              } else {
                                delete settings.delay;
                              }
                              setFormData({ ...formData, crawlerSettings: JSON.stringify(settings) });
                            } catch {
                              const newSettings = e.target.value ? { delay: parseInt(e.target.value) } : {};
                              setFormData({ ...formData, crawlerSettings: JSON.stringify(newSettings) });
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
                              const rules = JSON.parse(formData.validationRules || '{}');
                              return rules.required || false;
                            } catch {
                              return false;
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const rules = JSON.parse(formData.validationRules || '{}');
                              rules.required = e.target.checked;
                              setFormData({ ...formData, validationRules: JSON.stringify(rules) });
                            } catch {
                              setFormData({ ...formData, validationRules: JSON.stringify({ required: e.target.checked }) });
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
                              const rules = JSON.parse(formData.validationRules || '{}');
                              return rules.minLength || '';
                            } catch {
                              return '';
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const rules = JSON.parse(formData.validationRules || '{}');
                              if (e.target.value) {
                                rules.minLength = parseInt(e.target.value);
                              } else {
                                delete rules.minLength;
                              }
                              setFormData({ ...formData, validationRules: JSON.stringify(rules) });
                            } catch {
                              const newRules = e.target.value ? { minLength: parseInt(e.target.value) } : {};
                              setFormData({ ...formData, validationRules: JSON.stringify(newRules) });
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
                              const rules = JSON.parse(formData.validationRules || '{}');
                              return rules.maxLength || '';
                            } catch {
                              return '';
                            }
                          })()}
                          onChange={(e) => {
                            try {
                              const rules = JSON.parse(formData.validationRules || '{}');
                              if (e.target.value) {
                                rules.maxLength = parseInt(e.target.value);
                              } else {
                                delete rules.maxLength;
                              }
                              setFormData({ ...formData, validationRules: JSON.stringify(rules) });
                            } catch {
                              const newRules = e.target.value ? { maxLength: parseInt(e.target.value) } : {};
                              setFormData({ ...formData, validationRules: JSON.stringify(newRules) });
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
             <table className="min-w-full border-collapse table-auto">
               <thead className={`${
                 isDarkMode ? 'bg-gray-700' : 'bg-gray-50'
               }`}>
                 <tr>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider w-24 ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Priority
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider min-w-48 ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     URL
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider min-w-40 ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Mapping Details
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider min-w-48 ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Extractors
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider w-32 ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Status
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider w-36 ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Performance
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider w-40 ${
                     isDarkMode ? 'text-gray-300' : 'text-gray-500'
                   }`}>
                     Last Activity
                   </th>
                   <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider w-32 ${
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
                   // Handle both single extractorId (legacy) and multiple extractorIds
                   const extractorIdsList = mapping.extractorIds && mapping.extractorIds.length > 0 
                     ? mapping.extractorIds 
                     : mapping.extractorId ? [mapping.extractorId] : [];
                   const mappingExtractors = extractors.filter(e => extractorIdsList.includes(e.id));
                   
                   // Get the URL from the URL configuration
                   const urlConfig = urlConfigs.find(config => config.id === mapping.configurationId);
                   const mappingUrl = urlConfig?.url || mapping.url || 'No URL configured';
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

                       {/* URL Column */}
                       <td className="px-6 py-4">
                         <div className="flex items-center gap-2">
                           <LinkIcon className={`h-4 w-4 ${
                             isDarkMode ? 'text-gray-400' : 'text-gray-500'
                           }`} />
                           <div className={`text-sm font-mono ${
                             isDarkMode ? 'text-blue-400' : 'text-blue-600'
                           }`}>
                             {mappingUrl}
                           </div>
                         </div>
                       </td>

                       {/* Mapping Details Column */}
                       <td className="px-6 py-4">
                         <div>
                           <div className={`text-sm font-medium ${
                             isDarkMode ? 'text-white' : 'text-gray-900'
                           }`}>
                             {mapping.name}
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
                       </td>

                       {/* Extractor Column */}
                       <td className="px-6 py-4">
                         {mappingExtractors.length > 0 ? (
                           <div className="flex flex-wrap gap-1">
                             {mappingExtractors.slice(0, 3).map((extractor) => (
                               <span
                                 key={extractor.id}
                                 className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${
                                   extractor.isActive
                                     ? isDarkMode
                                       ? 'bg-green-900 text-green-300 border border-green-700'
                                       : 'bg-green-100 text-green-800 border border-green-200'
                                     : isDarkMode
                                       ? 'bg-gray-700 text-gray-300 border border-gray-600'
                                       : 'bg-gray-100 text-gray-600 border border-gray-300'
                                 }`}
                                 title={`${extractor.name} (${extractor.type}) - ${extractor.isActive ? 'Active' : 'Inactive'}`}
                               >
                                 <span className={`w-2 h-2 rounded-full ${
                                   extractor.isActive
                                     ? 'bg-green-500'
                                     : 'bg-gray-400'
                                 }`} />
                                 {extractor.name}
                               </span>
                             ))}
                             {mappingExtractors.length > 3 && (
                               <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${
                                 isDarkMode
                                   ? 'bg-gray-700 text-gray-300 border border-gray-600'
                                   : 'bg-gray-100 text-gray-600 border border-gray-300'
                               }`}>
                                 +{mappingExtractors.length - 3} more
                               </span>
                             )}
                           </div>
                         ) : (
                           <span className={`text-xs px-2 py-1 rounded ${
                             isDarkMode
                               ? 'bg-red-900 text-red-300'
                               : 'bg-red-100 text-red-600'
                           }`}>
                             No extractors assigned
                           </span>
                         )}
                       </td>

                       {/* Status Column */}
                       <td className="px-6 py-4 whitespace-nowrap">
                         <div className="flex items-center gap-2">
                           <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                             mapping.isActive 
                               ? 'bg-green-100 text-green-800' 
                               : 'bg-red-100 text-red-800'
                           }`}>
                             {mapping.isActive ? 'Active' : 'Inactive'}
                           </span>
                           <button
                             onClick={() => toggleActive(mapping.id)}
                             className={`p-1 rounded transition-all duration-200 hover:scale-110 ${
                               mapping.isActive 
                                 ? 'text-green-600 hover:bg-green-100' 
                                 : 'text-gray-400 hover:bg-gray-100'
                             }`}
                             title={mapping.isActive ? 'Disable mapping' : 'Enable mapping'}
                           >
                             {mapping.isActive ? <Power size={16} /> : <PowerOff size={16} />}
                           </button>
                         </div>
                         <div className={`text-xs mt-1 ${
                           isDarkMode ? 'text-gray-400' : 'text-gray-500'
                         }`}>
                           Rate: {mapping.rateLimit}/min
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