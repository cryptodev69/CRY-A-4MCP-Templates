import { URLMapping, Extractor, ExtractionResult, TestResult, DashboardStats, AnalyticsData } from '../types/models';

// Mock data for development
const mockExtractors: Extractor[] = [
  {
    id: 'ext-1',
    name: 'News Article Extractor',
    description: 'Extracts title, content, author, and publication date from news articles',
    config: {
      selectors: {
        title: 'h1, .article-title, .headline',
        content: '.article-content, .post-content, main p',
        author: '.author, .byline, [rel="author"]',
        publishDate: '.publish-date, .date, time[datetime]'
      },
      waitConditions: [{
        type: 'element',
        selector: '.article-content',
        timeout: 5000
      }],
      timeout: 10000,
      retryAttempts: 3,
      outputFormat: 'json' as const,
      postProcessing: [{
        field: 'publishDate',
        operation: 'date_format',
        parameters: { format: 'ISO' }
      }]
    },
    isActive: true,
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-01-20'),
    version: '1.2.0',
    tags: ['news', 'articles', 'content'],
    author: 'CRY-A-4MCP Team',
    usageCount: 1250,
    successRate: 94.5
  },
  {
    id: 'ext-2',
    name: 'E-commerce Product Extractor',
    description: 'Extracts product information from e-commerce sites',
    config: {
      selectors: {
        name: '.product-title, h1.product-name',
        price: '.price, .product-price, .cost',
        description: '.product-description, .description',
        images: '.product-images img, .gallery img',
        rating: '.rating, .stars, .review-score'
      },
      timeout: 8000,
      retryAttempts: 2,
      outputFormat: 'json' as const
    },
    isActive: true,
    createdAt: new Date('2024-01-10'),
    updatedAt: new Date('2024-01-18'),
    version: '1.1.0',
    tags: ['ecommerce', 'products', 'shopping'],
    author: 'CRY-A-4MCP Team',
    usageCount: 890,
    successRate: 91.2
  }
];

const mockMappings: URLMapping[] = [
  {
    id: 'map-1',
    name: 'News Article Mapping',
    url: 'https://example-news.com/*',
    url_config_id: 'config-1',
    extractor_id: 'ext-1',
    priority: 1,
    rate_limit: 10,
    config: JSON.stringify({
      timeout: 30000,
      retries: 3,
      delay: 1000
    }),
    validation_rules: JSON.stringify({ required: true }),
     crawler_settings: JSON.stringify({
       timeout: 30000,
       retries: 3,
       delay: 1000
     }),
     is_active: true,
     metadata: JSON.stringify({}),
    created_at: '2024-01-15T00:00:00Z',
    updated_at: '2024-01-20T00:00:00Z',
    extractionCount: 45,
    successRate: 95.6,
    averageResponseTime: 2340,
    lastError: undefined,
    createdAt: new Date('2024-01-15'),
    lastExtracted: new Date('2024-01-22')
  },
  {
    id: 'map-2',
    name: 'E-commerce Product Mapping',
    url: 'https://shop-example.com/products/*',
    url_config_id: 'config-2',
    extractor_id: 'ext-2',
    priority: 2,
    rate_limit: 5,
    config: JSON.stringify({
      timeout: 45000,
      retries: 2,
      delay: 2000
    }),
    validation_rules: JSON.stringify({ required: true }),
     crawler_settings: JSON.stringify({
       timeout: 45000,
       retries: 2,
       delay: 2000
     }),
     is_active: true,
     metadata: JSON.stringify({}),
    created_at: '2024-01-12T00:00:00Z',
    updated_at: '2024-01-21T00:00:00Z',
    extractionCount: 23,
    successRate: 87.0,
    averageResponseTime: 3120,
    lastError: 'Timeout after 8000ms',
    createdAt: new Date('2024-01-12'),
    lastExtracted: new Date('2024-01-21')
  }
];

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const api = {
  // URL Mappings
  async getMappings(): Promise<URLMapping[]> {
    try {
      // Fetch both URL mappings and URL configurations
      const [mappingsResponse, configsResponse] = await Promise.all([
        fetch('/api/url-mappings/'),
        fetch('/api/url-configurations/')
      ]);
      
      if (!mappingsResponse.ok) {
        throw new Error(`HTTP error! status: ${mappingsResponse.status}`);
      }
      
      const mappingsData = await mappingsResponse.json();
      let configsData = [];
      
      if (configsResponse.ok) {
        configsData = await configsResponse.json();
      }
      
      // Create a map of config IDs to URLs for quick lookup
      const configMap = new Map();
      configsData.forEach((config: any) => {
        configMap.set(config.id, {
          url: config.url,
          name: config.name
        });
      });
      
      // Transform backend response to frontend format
      return mappingsData.map((backendMapping: any) => {
        const configInfo = configMap.get(backendMapping.url_config_id);
        
        return {
          id: backendMapping.id,
          name: backendMapping.name || configInfo?.name || 'Unnamed Mapping',
          url: configInfo?.url || backendMapping.url || 'Unknown URL',
          url_config_id: backendMapping.url_config_id,
          extractor_id: backendMapping.extractor_id || '',
          priority: backendMapping.priority || 1,
          rate_limit: backendMapping.rate_limit || 60,
          config: JSON.stringify({
            timeout: backendMapping.crawler_settings?.timeout || 30000,
            retries: backendMapping.crawler_settings?.retries || 3,
            delay: backendMapping.crawler_settings?.delay || 1000
          }),
          validation_rules: typeof backendMapping.validation_rules === 'string' ? backendMapping.validation_rules : JSON.stringify(backendMapping.validation_rules || { required: true }),
           crawler_settings: typeof backendMapping.crawler_settings === 'string' ? backendMapping.crawler_settings : JSON.stringify(backendMapping.crawler_settings || {
             timeout: 30000,
             retries: 3,
             delay: 1000
           }),
           is_active: backendMapping.is_active !== undefined ? backendMapping.is_active : true,
           metadata: typeof backendMapping.metadata === 'string' ? backendMapping.metadata : JSON.stringify(backendMapping.metadata || {}),
          created_at: backendMapping.created_at,
          updated_at: backendMapping.updated_at,
          createdAt: new Date(backendMapping.created_at || Date.now()),
          lastExtracted: undefined,
          extractionCount: 0,
          successRate: 95,
          averageResponseTime: 1500,
          lastError: undefined
        };
      });
    } catch (error) {
      console.error('Failed to fetch mappings from API, falling back to mock:', error);
      // Fallback to mock data
      await delay(500);
      return mockMappings;
    }
  },

  async createMapping(mapping: Omit<URLMapping, 'id' | 'createdAt' | 'extractionCount' | 'successRate' | 'averageResponseTime'>): Promise<URLMapping> {
    try {
      // Transform frontend mapping to backend format
      const backendMapping: any = {
        name: mapping.name,
        url_config_id: mapping.url_config_id,
        extractor_id: mapping.extractor_id || '',
        priority: mapping.priority || 1,
        rate_limit: mapping.rate_limit || 60,
        is_active: mapping.is_active !== undefined ? mapping.is_active : true
      };
      
      // Handle config as string or object
      let configData;
      if (typeof mapping.config === 'string') {
        try {
          configData = JSON.parse(mapping.config);
        } catch {
          configData = { timeout: 30000, retries: 3, delay: 1000 };
        }
      } else {
        configData = mapping.config || { timeout: 30000, retries: 3, delay: 1000 };
      }
      
      backendMapping.crawler_settings = {
        timeout: configData.timeout || 30000,
        retries: configData.retries || 3,
        delay: configData.delay || 1000
      };
      
      backendMapping.validation_rules = typeof mapping.validation_rules === 'string' ? JSON.parse(mapping.validation_rules) : (mapping.validation_rules || { required: true });
       backendMapping.metadata = typeof mapping.metadata === 'string' ? JSON.parse(mapping.metadata) : (mapping.metadata || {});
      
      const response = await fetch('/api/url-mappings/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backendMapping),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
      
      const createdMapping = await response.json();
      
      // Get the URL from the config for the pattern
      let pattern = createdMapping.url_config_id || '';
      try {
        const configResponse = await fetch('/api/url-configurations/');
        if (configResponse.ok) {
          const configs = await configResponse.json();
          const config = configs.find((c: any) => c.id === createdMapping.url_config_id);
          if (config) {
            pattern = config.url;
          }
        }
      } catch (error) {
        console.warn('Failed to fetch URL configuration for pattern resolution:', error);
      }
      
      // Transform backend response back to frontend format
      return {
        id: createdMapping.id,
        name: createdMapping.name || 'Unnamed Mapping',
        url: pattern,
        url_config_id: createdMapping.url_config_id,
        extractor_id: createdMapping.extractor_id || '',
        priority: createdMapping.priority || 1,
        rate_limit: createdMapping.rate_limit || 60,
        config: JSON.stringify({
          timeout: createdMapping.crawler_settings?.timeout || 30000,
          retries: createdMapping.crawler_settings?.retries || 3,
          delay: createdMapping.crawler_settings?.delay || 1000
        }),
        validation_rules: typeof createdMapping.validation_rules === 'string' ? createdMapping.validation_rules : JSON.stringify(createdMapping.validation_rules || { required: true }),
         crawler_settings: typeof createdMapping.crawler_settings === 'string' ? createdMapping.crawler_settings : JSON.stringify(createdMapping.crawler_settings || {
           timeout: 30000,
           retries: 3,
           delay: 1000
         }),
         is_active: createdMapping.is_active !== undefined ? createdMapping.is_active : true,
         metadata: typeof createdMapping.metadata === 'string' ? createdMapping.metadata : JSON.stringify(createdMapping.metadata || {}),
        created_at: createdMapping.created_at,
        updated_at: createdMapping.updated_at,
        createdAt: new Date(createdMapping.created_at || Date.now()),
        lastExtracted: undefined,
        extractionCount: 0,
        successRate: 95,
        averageResponseTime: 1500,
        lastError: undefined
      };
    } catch (error) {
      console.error('Failed to create mapping via API:', error);
      throw error; // Re-throw the error so the UI can handle it properly
    }
  },

  async updateMapping(id: string, updates: Partial<URLMapping>): Promise<URLMapping> {
    try {
      // Transform frontend updates to backend format
      const backendUpdates: any = {};
      
      // Map all possible fields from frontend to backend format
      if (updates.extractor_id !== undefined) {
        backendUpdates.extractor_id = updates.extractor_id;
      }
      
      if (updates.name !== undefined) {
        backendUpdates.name = updates.name;
      }
      
      if (updates.url !== undefined) {
        backendUpdates.url = updates.url;
      }
      
      if (updates.url_config_id !== undefined) {
        backendUpdates.url_config_id = updates.url_config_id;
      }
      
      if (updates.priority !== undefined) {
        backendUpdates.priority = updates.priority;
      }
      
      if (updates.rate_limit !== undefined) {
        backendUpdates.rate_limit = updates.rate_limit;
      }
      
      if (updates.is_active !== undefined) {
        backendUpdates.is_active = updates.is_active;
      }
      
      if (updates.validation_rules !== undefined) {
        backendUpdates.validation_rules = updates.validation_rules;
      }
      
      if (updates.crawler_settings !== undefined) {
        backendUpdates.crawler_settings = updates.crawler_settings;
      }
      
      if (updates.metadata !== undefined) {
        backendUpdates.metadata = updates.metadata;
      }
      
      // Handle config field (can be string or object)
      if (updates.config !== undefined) {
        if (typeof updates.config === 'string') {
          backendUpdates.config = updates.config;
        } else {
          backendUpdates.config = JSON.stringify(updates.config);
        }
      }
      
      // Support direct backend field updates (for comprehensive editing)
      const directFieldMappings = {
        name: 'name',
        url_pattern: 'url_pattern', 
        url: 'url',
        profile_type: 'profile_type',
        category: 'category',
        scraping_difficulty: 'scraping_difficulty',
        has_official_api: 'has_official_api',
        api_pricing: 'api_pricing',
        recommendation: 'recommendation',
        key_data_points: 'key_data_points',
        target_data: 'target_data',
        rationale: 'rationale',
        cost_analysis: 'cost_analysis',
        description: 'description'
      };
      
      // Add any direct backend fields that are provided
      Object.entries(directFieldMappings).forEach(([frontendKey, backendKey]) => {
        if ((updates as any)[frontendKey] !== undefined) {
          backendUpdates[backendKey] = (updates as any)[frontendKey];
        }
      });
      
      const response = await fetch(`/api/url-mappings/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backendUpdates),
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
      
      const updatedMapping = await response.json();
      
      // Transform backend response to frontend format
      return {
        id: updatedMapping.id,
        name: updatedMapping.name,
        url: updatedMapping.url,
        url_config_id: updatedMapping.url_config_id,
        extractor_id: updatedMapping.extractor_id,
        priority: updatedMapping.priority || 1,
        rate_limit: updatedMapping.rate_limit || 60,
        config: typeof updatedMapping.config === 'string' ? updatedMapping.config : JSON.stringify(updatedMapping.config || {}),
        validation_rules: updatedMapping.validation_rules,
        crawler_settings: updatedMapping.crawler_settings,
        is_active: updatedMapping.is_active !== undefined ? updatedMapping.is_active : true,
        metadata: updatedMapping.metadata,
        created_at: updatedMapping.created_at,
        updated_at: updatedMapping.updated_at,
        extractionCount: 0,
        successRate: 95,
        averageResponseTime: 1500,
        lastError: undefined,
        createdAt: new Date(updatedMapping.created_at || Date.now()),
        lastExtracted: undefined
      };
    } catch (error) {
      console.error('Failed to update mapping via API, falling back to mock:', error);
      // Fallback to mock implementation
      await delay(300);
      const index = mockMappings.findIndex(m => m.id === id);
      if (index === -1) throw new Error('Mapping not found');
      
      const updatedMapping = { ...mockMappings[index], ...updates };
      mockMappings[index] = updatedMapping;
      return updatedMapping;
    }
  },

  async deleteMapping(id: string): Promise<void> {
    try {
      const response = await fetch(`/api/url-mappings/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to delete mapping via API, falling back to mock:', error);
      // Fallback to mock implementation
      await delay(300);
      const index = mockMappings.findIndex(m => m.id === id);
      if (index === -1) throw new Error('Mapping not found');
      
      mockMappings.splice(index, 1);
    }
  },

  // Extractors
  async getExtractors(): Promise<Extractor[]> {
    try {
      const response = await fetch('/api/extractors');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const extractors = await response.json();
      return extractors;
    } catch (error) {
      console.error('Failed to fetch extractors from API, falling back to mock data:', error);
      // Fallback to mock data if API fails
      await delay(400);
      return [...mockExtractors];
    }
  },

  async getExtractor(id: string): Promise<Extractor> {
    await delay(300);
    const extractor = mockExtractors.find(e => e.id === id);
    if (!extractor) throw new Error('Extractor not found');
    return extractor;
  },

  // Test URL
  async testUrl(url: string, extractorId: string): Promise<TestResult> {
    await delay(2000); // Simulate extraction time
    
    const extractor = mockExtractors.find(e => e.id === extractorId);
    if (!extractor) throw new Error('Extractor not found');

    // Simulate success/failure
    const success = Math.random() > 0.1; // 90% success rate
    
    if (success) {
      return {
        url,
        extractorId,
        success: true,
        data: {
          title: 'Sample Article Title',
          content: 'This is sample extracted content from the URL...',
          author: 'John Doe',
          publishDate: new Date().toISOString()
        },
        responseTime: Math.floor(Math.random() * 3000) + 1000,
        timestamp: new Date()
      };
    } else {
      return {
        url,
        extractorId,
        success: false,
        error: 'Failed to extract content: Element not found',
        responseTime: Math.floor(Math.random() * 2000) + 500,
        timestamp: new Date()
      };
    }
  },

  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    await delay(600);
    return {
      totalMappings: mockMappings.length,
      activeMappings: mockMappings.filter(m => m.is_active).length,
      totalExtractions: mockMappings.reduce((sum, m) => sum + (m.extractionCount || 0), 0),
      successRate: mockMappings.reduce((sum, m) => sum + (m.successRate || 0), 0) / mockMappings.length,
      averageResponseTime: mockMappings.reduce((sum, m) => sum + (m.averageResponseTime || 0), 0) / mockMappings.length,
      recentExtractions: [] // Would be populated with recent extraction results
    };
  },

  // Analytics
  async getAnalytics(): Promise<AnalyticsData> {
    await delay(800);
    return {
      extractionTrends: [
        { date: '2024-01-15', count: 45, successRate: 94.5 },
        { date: '2024-01-16', count: 52, successRate: 96.2 },
        { date: '2024-01-17', count: 38, successRate: 91.8 },
        { date: '2024-01-18', count: 61, successRate: 93.4 },
        { date: '2024-01-19', count: 47, successRate: 95.1 },
        { date: '2024-01-20', count: 55, successRate: 92.7 },
        { date: '2024-01-21', count: 49, successRate: 94.9 }
      ],
      topPerformingExtractors: mockExtractors.map(e => ({
        extractorId: e.id,
        name: e.name,
        successRate: e.successRate || 0,
        usageCount: e.usageCount || 0
      })),
      errorDistribution: [
        { errorType: 'Timeout', count: 12, percentage: 45.2 },
        { errorType: 'Element Not Found', count: 8, percentage: 30.1 },
        { errorType: 'Network Error', count: 4, percentage: 15.1 },
        { errorType: 'Parse Error', count: 3, percentage: 9.6 }
      ],
      responseTimeMetrics: {
        average: 2730,
        median: 2450,
        p95: 4200,
        p99: 5800
      }
    };
  }
};