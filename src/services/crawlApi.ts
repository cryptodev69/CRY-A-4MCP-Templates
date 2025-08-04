/**
 * @fileoverview Crawl4AI API Service and Type Definitions
 * 
 * This module provides comprehensive TypeScript interfaces and API service class
 * for interacting with the CRY-A-4MCP backend crawling system. It includes
 * type definitions for crawl results, crawler configurations, job management,
 * and real-time monitoring capabilities.
 * 
 * Key Features:
 * - Type-safe API interactions with full TypeScript support
 * - Comprehensive crawler configuration management
 * - Real-time job monitoring and control
 * - Paginated data handling with filtering
 * - Error handling with detailed response types
 * - Live session monitoring and logging
 * - Multiple export formats (JSON, CSV, XLSX)
 * 
 * Architecture:
 * - RESTful API client with standardized response format
 * - Modular interface design for different data types
 * - Async/await pattern for all API operations
 * - Built-in authentication and authorization support
 * 
 * @author CRY-A-4MCP Development Team
 * @version 1.0.0
 * @since 2024
 */

/**
 * Represents the result of a single URL crawl operation
 * 
 * This interface defines the structure of data returned after crawling a URL,
 * including the extracted content, metadata, and any processing results.
 * 
 * @interface CrawlResult
 */
export interface CrawlResult {
  url: string;
  title?: string;
  content?: string;
  markdown?: string;
  html?: string;
  metadata?: Record<string, any>;
  llm_extraction?: Record<string, any>;
  extracted_data?: Record<string, any>;
  extraction_results?: Array<Record<string, any>>;
  success: boolean;
  error_message?: string;
  timestamp: string;
}

// Types for Crawler Configuration
// Backend API response interface
export interface APICrawlerConfig {
  id: string;
  name: string;
  description: string;
  crawlerType: string;
  isActive: boolean;
  config: any;
  llmConfig?: any;
  extractionStrategies: ExtractorMapping[];
  urlMappingIds: string[];
  targetUrls: string[];
  priority: number;
  stats: {
    totalCrawls: number;
    successfulCrawls: number;
    failedCrawls: number;
    avgResponseTime: number;
    lastUsed?: string;
  };
  createdAt: string;
  updatedAt: string;
  createdBy?: string;
}

// Frontend interface
export interface CrawlerConfig {
  id: string;
  name: string;
  description: string;
  crawlerType: string;
  isActive: boolean;
  config: {
    // Basic Crawl4AI settings
    headless: boolean;
    browser_type: 'chromium' | 'firefox' | 'webkit';
    user_agent?: string;
    proxy?: string;
    
    // Performance settings
    page_timeout: number;
    delay_before_return_html: number;
    wait_for: string;
    
    // LLM Extraction settings
    llm_provider: 'openai' | 'anthropic' | 'local';
    llm_model: string;
    llm_api_key?: string;
    
    // Content filtering
    word_count_threshold: number;
    css_selector?: string;
    
    // Session management
    session_id?: string;
    
    // Advanced options
    magic: boolean;
    simulate_user: boolean;
    override_navigator: boolean;
    
    // Extraction strategies
    extraction_strategies: string[];
    
    // Custom headers
    headers?: Record<string, string>;
    
    // Screenshot options
    screenshot: boolean;
    screenshot_wait_for?: string;
  };
  extractionStrategies: ExtractorMapping[];
  urlMappings: URLMapping[];
  urlMappingId?: string;
  targetUrls?: string[];
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  stats: {
    totalCrawls: number;
    successfulCrawls: number;
    failedCrawls: number;
    avgResponseTime: number;
    lastUsed?: string;
  };
}

export interface ExtractorMapping {
  id: string;
  name: string;
  type: 'llm' | 'css' | 'xpath' | 'regex' | 'custom';
  config: {
    // LLM-based extraction
    instruction?: string;
    schema?: any;
    
    // CSS/XPath extraction
    selector?: string;
    attribute?: string;
    
    // Regex extraction
    pattern?: string;
    flags?: string;
    
    // Custom extraction
    function_name?: string;
    parameters?: Record<string, any>;
  };
  priority: number;
  isActive: boolean;
}

export interface URLMapping {
  id: string;
  name?: string; // API response includes name
  description?: string; // API response includes description
  pattern?: string; // Frontend pattern (optional for API responses)
  urls?: string[]; // API response uses urls array
  type?: 'domain' | 'path' | 'exact' | 'regex';
  extractorIds?: string[]; // Frontend format
  extractor_ids?: string[]; // API response format
  priority?: number;
  isActive?: boolean;
  crawler_settings?: any; // API response format
  config?: {
    patternType?: 'exact' | 'wildcard' | 'regex' | 'domain' | 'path';
    targetGroup?: string;
    customHeaders?: Record<string, string>;
    timeout?: number;
    retryAttempts?: number;
    retryDelay?: number;
    rateLimit?: {
      requests: number;
      windowMs: number;
    };
    validation?: {
      required: boolean;
      minLength?: number;
      maxLength?: number;
      pattern?: string;
    };
    schedule?: {
      enabled: boolean;
      cron?: string;
      interval?: number;
    };
    notifications?: {
      onSuccess: boolean;
      onError: boolean;
      webhookUrl?: string;
    };
  };
  rate_limit?: number | null; // API response format
  validation_rules?: any; // API response format
  created_at?: string; // API response format
  updated_at?: string; // API response format
  createdAt?: Date; // Frontend format
  lastExtracted?: Date;
  extractionCount: number;
  successRate: number;
  averageResponseTime: number;
  lastError?: string;
}

// Types for Crawl Jobs
export interface CrawlJob {
  id: string;
  name: string;
  crawlerId: string;
  crawlerName: string;
  urls: string[];
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused' | 'cancelled';
  progress: {
    total: number;
    completed: number;
    failed: number;
    current?: string;
    startTime?: string;
    estimatedCompletion?: string;
  };
  config: {
    batchSize: number;
    delayBetweenRequests: number;
    maxRetries: number;
    timeout: number;
    parallelism: number;
  };
  schedule?: {
    type: 'once' | 'recurring';
    interval?: string; // cron expression
    nextRun?: string;
    timezone?: string;
  };
  results: {
    totalExtracted: number;
    avgExtractionTime: number;
    successRate: number;
    dataSize: number; // in bytes
    errors: JobError[];
  };
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  createdBy: string;
  priority: 'low' | 'medium' | 'high';
  tags: string[];
  metadata?: Record<string, any>;
}

export interface JobError {
  url: string;
  error: string;
  timestamp: string;
  retryCount: number;
}

// Types for Live Monitoring
export interface CrawlSession {
  id: string;
  jobId: string;
  status: 'active' | 'paused' | 'completed' | 'failed';
  currentUrl?: string;
  progress: {
    completed: number;
    total: number;
    rate: number; // URLs per minute
  };
  performance: {
    avgResponseTime: number;
    memoryUsage: number;
    cpuUsage: number;
  };
  logs: CrawlLog[];
}

export interface CrawlLog {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  message: string;
  url?: string;
  metadata?: Record<string, any>;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

/**
 * CrawlApiService - Main API Service Class
 * 
 * This class provides a comprehensive interface for interacting with the CRY-A-4MCP
 * backend API. It handles all HTTP communications, authentication, error handling,
 * and data transformation for the crawling system.
 * 
 * Features:
 * - Automatic request/response handling with type safety
 * - Built-in authentication with Bearer token support
 * - Standardized error handling and response formatting
 * - RESTful API pattern implementation
 * - Configurable base URL for different environments
 * 
 * Usage Example:
 * ```typescript
 * const api = new CrawlApiService('/api', 'your-api-key');
 * const crawlers = await api.getCrawlers();
 * if (crawlers.success) {
 *   console.log(crawlers.data);
 * }
 * ```
 * 
 * @class CrawlApiService
 */
class CrawlApiService {
  /** Base URL for all API requests */
  private baseUrl: string;
  
  /** Optional API key for authentication */
  private apiKey?: string;

  /**
   * Initialize the CrawlApiService with configuration
   * 
   * @param {string} baseUrl - Base URL for API requests (default: '/api')
   * @param {string} [apiKey] - Optional API key for authentication
   */
  constructor(baseUrl: string = '/api', apiKey?: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  /**
   * Generic HTTP request method with error handling and authentication
   * 
   * This private method handles all HTTP communications with the backend API.
   * It automatically adds authentication headers, handles errors, and formats
   * responses according to the standardized ApiResponse interface.
   * 
   * @template T - The expected response data type
   * @param {string} endpoint - API endpoint path (relative to baseUrl)
   * @param {RequestInit} [options={}] - Fetch API options (method, body, headers, etc.)
   * @returns {Promise<ApiResponse<T>>} Standardized API response with success/error handling
   * 
   * @private
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.error || `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      return {
        success: true,
        data: data.data || data,
        message: data.message,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  // ==========================================
  // CRAWLER MANAGEMENT METHODS
  // ==========================================

  /**
   * Transform backend crawler data to frontend format
   */
  private transformCrawlerData(backendCrawler: any): CrawlerConfig {
    return {
      id: backendCrawler.id,
      name: backendCrawler.name,
      description: backendCrawler.description || '',
      crawlerType: backendCrawler.crawler_type || 'web',
      isActive: backendCrawler.is_active,
      config: {
        headless: backendCrawler.config?.headless ?? true,
        browser_type: backendCrawler.config?.browser_type || 'chromium',
        user_agent: backendCrawler.config?.user_agent,
        proxy: backendCrawler.config?.proxy,
        page_timeout: backendCrawler.config?.page_timeout || 30000,
        delay_before_return_html: backendCrawler.config?.delay_before_return_html || 0,
        wait_for: backendCrawler.config?.wait_for || '',
        llm_provider: backendCrawler.llm_config?.provider || 'openai',
        llm_model: backendCrawler.llm_config?.model || 'gpt-3.5-turbo',
        llm_api_key: backendCrawler.llm_config?.api_key,
        word_count_threshold: backendCrawler.config?.word_count_threshold || 10,
        css_selector: backendCrawler.config?.css_selector,
        session_id: backendCrawler.config?.session_id,
        magic: backendCrawler.config?.magic ?? false,
        simulate_user: backendCrawler.config?.simulate_user ?? false,
        override_navigator: backendCrawler.config?.override_navigator ?? false,
        extraction_strategies: backendCrawler.config?.extraction_strategies || [],
        headers: backendCrawler.config?.headers || {},
        screenshot: backendCrawler.config?.screenshot ?? false,
        screenshot_wait_for: backendCrawler.config?.screenshot_wait_for
      },
      extractionStrategies: backendCrawler.extraction_strategies || [],
      urlMappings: [], // Will be populated separately
      urlMappingId: (backendCrawler.url_mapping_ids && backendCrawler.url_mapping_ids.length > 0) ? backendCrawler.url_mapping_ids[0] : '',
      targetUrls: backendCrawler.target_urls || [],
      createdAt: backendCrawler.created_at,
      updatedAt: backendCrawler.updated_at,
      createdBy: backendCrawler.created_by || 'system',
      stats: backendCrawler.stats || {
        totalCrawls: 0,
        successfulCrawls: 0,
        failedCrawls: 0,
        avgResponseTime: 0
      }
    };
  }

  /**
   * Transform frontend crawler data to backend format
   */
  private transformCrawlerToBackend(frontendCrawler: Partial<CrawlerConfig>): any {
    return {
      name: frontendCrawler.name,
      description: frontendCrawler.description,
      crawlerType: frontendCrawler.crawlerType,
      isActive: frontendCrawler.isActive,
      config: {
        headless: frontendCrawler.config?.headless,
        browser_type: frontendCrawler.config?.browser_type,
        user_agent: frontendCrawler.config?.user_agent,
        proxy: frontendCrawler.config?.proxy,
        page_timeout: frontendCrawler.config?.page_timeout || 30000,
        delay_before_return_html: frontendCrawler.config?.delay_before_return_html,
        wait_for: frontendCrawler.config?.wait_for,
        word_count_threshold: frontendCrawler.config?.word_count_threshold,
        css_selector: frontendCrawler.config?.css_selector,
        session_id: frontendCrawler.config?.session_id,
        magic: frontendCrawler.config?.magic,
        simulate_user: frontendCrawler.config?.simulate_user,
        override_navigator: frontendCrawler.config?.override_navigator,
        extraction_strategies: frontendCrawler.config?.extraction_strategies || [],
        headers: frontendCrawler.config?.headers,
        screenshot: frontendCrawler.config?.screenshot,
        screenshot_wait_for: frontendCrawler.config?.screenshot_wait_for
      },
      llmConfig: {
        provider: frontendCrawler.config?.llm_provider,
        model: frontendCrawler.config?.llm_model,
        api_key: frontendCrawler.config?.llm_api_key
      },
      extractionStrategies: frontendCrawler.extractionStrategies || [],
      urlMappingIds: frontendCrawler.urlMappingId ? [frontendCrawler.urlMappingId] : [],
      targetUrls: frontendCrawler.targetUrls || [],
      priority: 1
    };
  }

  /**
   * Retrieve a paginated list of crawler configurations
   * 
   * @param {number} [page=1] - Page number for pagination (1-based)
   * @param {number} [pageSize=20] - Number of items per page
   * @returns {Promise<ApiResponse<PaginatedResponse<CrawlerConfig>>>} Paginated crawler list
   */
  async getCrawlers(page = 1, pageSize = 20): Promise<ApiResponse<PaginatedResponse<CrawlerConfig>>> {
    const response = await this.request<PaginatedResponse<any>>(`/api/crawlers?page=${page}&pageSize=${pageSize}`);
    
    if (response.success && response.data) {
      const transformedItems = response.data.items.map((item: any) => this.transformCrawlerData(item));
      return {
        success: true,
        data: {
          items: transformedItems,
          total: response.data.total,
          page: response.data.page,
          pageSize: response.data.pageSize,
          totalPages: response.data.totalPages
        }
      };
    }
    
    return {
      success: false,
      error: response.error || 'Failed to fetch crawlers'
    };
  }

  /**
   * Retrieve a specific crawler configuration by ID
   * 
   * @param {string} id - Unique crawler identifier
   * @returns {Promise<ApiResponse<CrawlerConfig>>} Crawler configuration details
   */
  async getCrawler(id: string): Promise<ApiResponse<CrawlerConfig>> {
    const response = await this.request<any>(`/api/crawlers/${id}`);
    
    if (response.success && response.data) {
      return {
        success: true,
        data: this.transformCrawlerData(response.data)
      };
    }
    
    return {
      success: false,
      error: response.error || 'Failed to fetch crawler'
    };
  }

  /**
   * Create a new crawler configuration
   * 
   * @param {Omit<CrawlerConfig, 'id' | 'createdAt' | 'updatedAt' | 'stats'>} config - Crawler configuration (excluding auto-generated fields)
   * @returns {Promise<ApiResponse<CrawlerConfig>>} Created crawler with generated ID and metadata
   */
  async createCrawler(config: Omit<CrawlerConfig, 'id' | 'createdAt' | 'updatedAt' | 'stats'>): Promise<ApiResponse<CrawlerConfig>> {
    const backendData = this.transformCrawlerToBackend(config);
    const response = await this.request<any>('/api/crawlers', {
      method: 'POST',
      body: JSON.stringify(backendData),
    });
    
    if (response.success && response.data) {
      return {
        success: true,
        data: this.transformCrawlerData(response.data)
      };
    }
    
    return {
      success: false,
      error: response.error || 'Failed to create crawler'
    };
  }

  /**
   * Update an existing crawler configuration
   * 
   * @param {string} id - Unique crawler identifier
   * @param {Partial<CrawlerConfig>} config - Partial crawler configuration for updates
   * @returns {Promise<ApiResponse<CrawlerConfig>>} Updated crawler configuration
   */
  async updateCrawler(id: string, config: Partial<CrawlerConfig>): Promise<ApiResponse<CrawlerConfig>> {
    const backendData = this.transformCrawlerToBackend(config);
    const response = await this.request<any>(`/api/crawlers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(backendData),
    });
    
    if (response.success && response.data) {
      return {
        success: true,
        data: this.transformCrawlerData(response.data)
      };
    }
    
    return {
      success: false,
      error: response.error || 'Failed to update crawler'
    };
  }

  /**
   * Delete a crawler configuration
   * 
   * @param {string} id - Unique crawler identifier
   * @returns {Promise<ApiResponse<void>>} Deletion confirmation
   */
  async deleteCrawler(id: string): Promise<ApiResponse<void>> {
    return this.request(`/api/crawlers/${id}`, {
      method: 'DELETE',
    });
  }

  /**
   * Test a crawler configuration with a specific URL
   * 
   * @param {string} id - Unique crawler identifier
   * @param {string} testUrl - URL to test the crawler against
   * @returns {Promise<ApiResponse<CrawlResult>>} Test crawl results
   */
  async testCrawler(id: string, testUrl: string): Promise<ApiResponse<CrawlResult>> {
    return this.request(`/api/crawlers/${id}/test`, {
      method: 'POST',
      body: JSON.stringify({ url: testUrl }),
    });
  }

  /**
   * Toggle the active status of a crawler
   * 
   * @param {string} id - Unique crawler identifier
   * @returns {Promise<ApiResponse<CrawlerConfig>>} Updated crawler configuration
   */
  async toggleCrawler(id: string): Promise<ApiResponse<CrawlerConfig>> {
    const response = await this.request<any>(`/api/crawlers/${id}/toggle`, {
      method: 'POST',
    });
    
    if (response.success && response.data) {
      return {
        success: true,
        data: this.transformCrawlerData(response.data)
      };
    }
    
    return {
      success: false,
      error: response.error || 'Failed to toggle crawler'
    };
  }

  // Crawl Job Management
  async getCrawlJobs(
    page = 1,
    pageSize = 20,
    filters?: {
      status?: string;
      priority?: string;
      crawlerId?: string;
      search?: string;
    }
  ): Promise<ApiResponse<PaginatedResponse<CrawlJob>>> {
    const params = new URLSearchParams({
      page: page.toString(),
      pageSize: pageSize.toString(),
      ...filters,
    });
    return this.request(`/api/crawl?${params}`);
  }

  async getCrawlJob(id: string): Promise<ApiResponse<CrawlJob>> {
    return this.request(`/api/crawl/${id}`);
  }

  async createCrawlJob(job: Omit<CrawlJob, 'id' | 'createdAt' | 'status' | 'progress' | 'results'>): Promise<ApiResponse<CrawlJob>> {
    return this.request('/api/crawl', {
      method: 'POST',
      body: JSON.stringify(job),
    });
  }

  async updateCrawlJob(id: string, updates: Partial<CrawlJob>): Promise<ApiResponse<CrawlJob>> {
    return this.request(`/api/crawl/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteCrawlJob(id: string): Promise<ApiResponse<void>> {
    return this.request(`/api/crawl/${id}`, {
      method: 'DELETE',
    });
  }

  // Job Control
  async startCrawlJob(id: string): Promise<ApiResponse<CrawlJob>> {
    return this.request(`/api/crawl/${id}/start`, {
      method: 'POST',
    });
  }

  async pauseCrawlJob(id: string): Promise<ApiResponse<CrawlJob>> {
    return this.request(`/api/crawl/${id}/pause`, {
      method: 'POST',
    });
  }

  async stopCrawlJob(id: string): Promise<ApiResponse<CrawlJob>> {
    return this.request(`/api/crawl/${id}/stop`, {
      method: 'POST',
    });
  }

  async resumeCrawlJob(id: string): Promise<ApiResponse<CrawlJob>> {
    return this.request(`/api/crawl/${id}/resume`, {
      method: 'POST',
    });
  }

  // Live Monitoring
  async getCrawlSession(jobId: string): Promise<ApiResponse<CrawlSession>> {
    return this.request(`/crawl-sessions/${jobId}`);
  }

  async getCrawlLogs(
    jobId: string,
    level?: string,
    limit = 100
  ): Promise<ApiResponse<CrawlLog[]>> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      ...(level && { level }),
    });
    return this.request(`/crawl-sessions/${jobId}/logs?${params}`);
  }

  // Results and Downloads
  async getCrawlResults(
    jobId: string,
    page = 1,
    pageSize = 20
  ): Promise<ApiResponse<PaginatedResponse<CrawlResult>>> {
    return this.request(`/api/crawl/${jobId}/results?page=${page}&pageSize=${pageSize}`);
  }

  async downloadCrawlResults(
    jobId: string,
    format: 'json' | 'csv' | 'xlsx' = 'json'
  ): Promise<ApiResponse<Blob>> {
    const response = await fetch(`${this.baseUrl}/api/crawl/${jobId}/download?format=${format}`, {
      headers: {
        ...(this.apiKey && { Authorization: `Bearer ${this.apiKey}` }),
      },
    });

    if (!response.ok) {
      return {
        success: false,
        error: `Download failed: ${response.statusText}`,
      };
    }

    const blob = await response.blob();
    return {
      success: true,
      data: blob,
    };
  }

  // Extraction Strategies
  async getExtractionStrategies(): Promise<ApiResponse<ExtractorMapping[]>> {
    return this.request('/extraction-strategies');
  }

  async createExtractionStrategy(strategy: Omit<ExtractorMapping, 'id'>): Promise<ApiResponse<ExtractorMapping>> {
    return this.request('/extraction-strategies', {
      method: 'POST',
      body: JSON.stringify(strategy),
    });
  }

  async updateExtractionStrategy(id: string, strategy: Partial<ExtractorMapping>): Promise<ApiResponse<ExtractorMapping>> {
    return this.request(`/extraction-strategies/${id}`, {
      method: 'PUT',
      body: JSON.stringify(strategy),
    });
  }

  async deleteExtractionStrategy(id: string): Promise<ApiResponse<void>> {
    return this.request(`/extraction-strategies/${id}`, {
      method: 'DELETE',
    });
  }

  // URL Mappings
  async getURLMappings(crawlerId?: string): Promise<ApiResponse<URLMapping[]>> {
    const params = crawlerId ? `?crawlerId=${crawlerId}` : '';
    return this.request(`/api/url-mappings/${params}`);
  }

  async createURLMapping(mapping: Omit<URLMapping, 'id'>): Promise<ApiResponse<URLMapping>> {
    // Transform frontend format to backend format
    const backendMapping = {
      url_pattern: mapping.pattern,
      extractor_ids: mapping.extractorIds,
      crawl_config: {
        timeout: mapping.config?.timeout || 30,
        max_depth: 2,
        delay: 1.0
      },
      is_active: mapping.isActive,
      priority: mapping.priority,
      name: `Mapping for ${mapping.pattern}`
    };
    
    return this.request('/api/url-mappings/', {
      method: 'POST',
      body: JSON.stringify(backendMapping),
    });
  }

  async updateURLMapping(id: string, mapping: Partial<URLMapping>): Promise<ApiResponse<URLMapping>> {
    // Transform frontend format to backend format
    const backendMapping: any = {};
    if (mapping.pattern) backendMapping.url_pattern = mapping.pattern;
    if (mapping.extractorIds) backendMapping.extractor_ids = mapping.extractorIds;
    if (mapping.isActive !== undefined) backendMapping.is_active = mapping.isActive;
    if (mapping.priority) backendMapping.priority = mapping.priority;
    if (mapping.config) {
      backendMapping.crawl_config = {
        timeout: mapping.config.timeout || 30,
        max_depth: 2,
        delay: 1.0
      };
    }
    
    return this.request(`/api/url-mappings/${id}`, {
      method: 'PUT',
      body: JSON.stringify(backendMapping),
    });
  }

  async deleteURLMapping(id: string): Promise<ApiResponse<void>> {
    return this.request(`/api/url-mappings/${id}`, {
      method: 'DELETE',
    });
  }

  // Analytics and Statistics
  async getCrawlerStats(crawlerId: string, period = '7d'): Promise<ApiResponse<any>> {
    return this.request(`/crawlers/${crawlerId}/stats?period=${period}`);
  }

  async getSystemStats(): Promise<ApiResponse<any>> {
    return this.request('/system/stats');
  }

  // WebSocket connection for real-time updates
  connectToJobUpdates(jobId: string, onUpdate: (data: any) => void): WebSocket | null {
    try {
      const wsUrl = `${this.baseUrl.replace('http', 'ws')}/api/crawl/${jobId}/ws`;
      const ws = new WebSocket(wsUrl);
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onUpdate(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      return ws;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      return null;
    }
  }
}

// Export singleton instance
export const crawlApi = new CrawlApiService('');
export default CrawlApiService;

// Utility functions
export const formatFileSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`;
};

export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
};

export const validateCronExpression = (expression: string): boolean => {
  // Basic cron validation (5 or 6 fields)
  const parts = expression.trim().split(/\s+/);
  return parts.length === 5 || parts.length === 6;
};

export const getNextCronRun = (expression: string): Date | null => {
  // This would typically use a cron parsing library
  // For now, return a placeholder
  try {
    // Placeholder implementation
    return new Date(Date.now() + 24 * 60 * 60 * 1000); // Next day
  } catch {
    return null;
  }
};