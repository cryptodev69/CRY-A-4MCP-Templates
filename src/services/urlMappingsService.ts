/**
 * URL Mappings Service
 * 
 * Service layer for managing URL mappings with CRUD operations.
 * Handles communication with the backend API for URL mapping management.
 */

import { ApiClient } from './apiClient';
import { API_BASE_URL, API_ENDPOINTS } from '../config/api';
import {
  URLConfig,
  URLMappingDisplay,
  URLMappingFormData,
  URLMappingCreateRequest,
  URLMappingUpdateRequest,
  Extractor
} from '../types/urlMappings.js';

// Backend API response types (matching backend models)
export interface URLConfigurationResponse {
  id: string;
  name: string;
  url: string;
  profile_type: string;
  category: string;
  description?: string;
  priority: number;
  scraping_difficulty: number;
  has_official_api: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface URLMappingResponse {
  id: string;
  url_config_id: string;
  extractor_ids: string[];
  rate_limit: number;
  priority: number;
  crawler_settings: Record<string, any>;
  validation_rules: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  configuration?: URLConfigurationResponse;
}

export interface ExtractorResponse {
  id: string;
  name: string;
  description: string;
  version: string;
  supported_domains: string[];
  config_schema: Record<string, any>;
  is_active: boolean;
}

// URLMappingCreateRequest and URLMappingUpdateRequest are now imported from types file

export interface URLConfigurationCreateRequest {
  name: string;
  url: string;
  profile_type: string;
  category: string;
  description?: string;
  priority: number;
  scraping_difficulty: number;
  has_official_api: boolean;
}

export interface URLConfigurationUpdateRequest extends Partial<URLConfigurationCreateRequest> {}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

class URLMappingsService {
  private apiClient: ApiClient;

  constructor() {
    this.apiClient = new ApiClient(API_BASE_URL);
  }

  // URL Configurations
  async getURLConfigurations(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    category?: string;
    profile_type?: string;
    is_active?: boolean;
  }): Promise<PaginatedResponse<URLConfigurationResponse>> {
    return this.apiClient.get<PaginatedResponse<URLConfigurationResponse>>(
      API_ENDPOINTS.urlConfigurations,
      params
    );
  }

  async getURLConfiguration(id: string): Promise<URLConfigurationResponse> {
    return this.apiClient.get<URLConfigurationResponse>(
      `${API_ENDPOINTS.urlConfigurations}/${id}`
    );
  }

  async createURLConfiguration(data: URLConfigurationCreateRequest): Promise<URLConfigurationResponse> {
    return this.apiClient.post<URLConfigurationResponse>(
      API_ENDPOINTS.urlConfigurations,
      data
    );
  }

  async updateURLConfiguration(
    id: string,
    data: URLConfigurationUpdateRequest
  ): Promise<URLConfigurationResponse> {
    return this.apiClient.put<URLConfigurationResponse>(
      `${API_ENDPOINTS.urlConfigurations}/${id}`,
      data
    );
  }

  async deleteURLConfiguration(id: string): Promise<void> {
    return this.apiClient.delete<void>(`${API_ENDPOINTS.urlConfigurations}/${id}`);
  }

  // URL Mappings
  async getURLMappings(params?: {
    skip?: number;
    limit?: number;
    configuration_id?: string;
    extractor_ids?: string[];
    is_active?: boolean;
  }): Promise<PaginatedResponse<URLMappingResponse>> {
    // Convert array parameters to query string format
    const queryParams: Record<string, string | number | boolean> = {};
    if (params) {
      if (params.skip !== undefined) queryParams.skip = params.skip;
      if (params.limit !== undefined) queryParams.limit = params.limit;
      if (params.configuration_id !== undefined) queryParams.configuration_id = params.configuration_id;
      if (params.extractor_ids !== undefined && params.extractor_ids.length > 0) {
        // Convert array to comma-separated string for query parameter
        queryParams.extractor_ids = params.extractor_ids.join(',');
      }
      if (params.is_active !== undefined) queryParams.is_active = params.is_active;
    }
    
    return this.apiClient.get<PaginatedResponse<URLMappingResponse>>(
      API_ENDPOINTS.urlMappings,
      queryParams
    );
  }

  async getURLMapping(id: string): Promise<URLMappingResponse> {
    return this.apiClient.get<URLMappingResponse>(
      `${API_ENDPOINTS.urlMappings}/${id}`
    );
  }

  async createURLMapping(data: URLMappingCreateRequest): Promise<URLMappingResponse> {
    return this.apiClient.post<URLMappingResponse>(
      API_ENDPOINTS.urlMappings,
      data
    );
  }

  async updateURLMapping(
    id: string,
    data: URLMappingUpdateRequest
  ): Promise<URLMappingResponse> {
    console.log('🔍 ===== BACKEND API UPDATE REQUEST =====');
    console.log('🔍 urlMappingsService.updateURLMapping - Input:');
    console.log('  - ID:', id);
    console.log('  - Data (full object):', JSON.stringify(data, null, 2));
    console.log('  - API Endpoint:', `${API_ENDPOINTS.urlMappings}/${id}`);
    console.log('🔍 REQUEST PAYLOAD BREAKDOWN:');
    console.log('  - name:', data.name);
    console.log('  - url_config_id:', data.url_config_id);
    console.log('  - extractor_ids:', data.extractor_ids);
    console.log('  - rate_limit:', data.rate_limit);
    console.log('  - priority:', data.priority);
    console.log('  - is_active:', data.is_active);
    console.log('  - tags:', data.tags);
    console.log('  - notes:', data.notes);
    console.log('  - category:', data.category);
    console.log('  - crawler_settings:', data.crawler_settings);
    console.log('  - validation_rules:', data.validation_rules);
    console.log('🔍 ===== SENDING TO BACKEND =====');
    
    const response = await this.apiClient.put<URLMappingResponse>(
      `${API_ENDPOINTS.urlMappings}/${id}`,
      data
    );
    
    console.log('🔍 ===== BACKEND API RESPONSE =====');
    console.log('🔍 urlMappingsService.updateURLMapping - Response:');
    console.log('  - Full Response:', JSON.stringify(response, null, 2));
    console.log('  - Response ID:', response.id);
    console.log('  - Response priority:', response.priority);
    console.log('  - Response is_active:', response.is_active);
    console.log('🔍 ===== END BACKEND RESPONSE =====');
    
    return response;
  }

  async deleteURLMapping(id: string): Promise<void> {
    return this.apiClient.delete<void>(`${API_ENDPOINTS.urlMappings}/${id}`);
  }

  // Extractors
  async getExtractors(): Promise<ExtractorResponse[]> {
    return this.apiClient.get<ExtractorResponse[]>(API_ENDPOINTS.extractors);
  }

  async getExtractor(id: string): Promise<ExtractorResponse> {
    return this.apiClient.get<ExtractorResponse>(
      `${API_ENDPOINTS.extractors}/${id}`
    );
  }

  // Data transformation utilities
  transformURLConfigurationToFrontend(config: URLConfigurationResponse): URLConfig {
    
    return {
    id: config.id,
    name: config.name,
    url: config.url,
    baseUrl: config.url,
    profileType: config.profile_type,
    category: config.category,
    description: config.description,
    priority: config.priority,
    scrapingDifficulty: config.scraping_difficulty,
    hasOfficialApi: config.has_official_api,
    hasOfficialAPI: config.has_official_api,
    isActive: config.is_active !== undefined ? config.is_active : true, // Default to true if not provided
    createdAt: config.created_at,
    updatedAt: config.updated_at
  };
  }

  transformURLConfigurationToBackend(config: Partial<URLConfig>): URLConfigurationCreateRequest | URLConfigurationUpdateRequest {
    return {
      name: config.name!,
      url: config.url!,
      profile_type: config.profileType!,
      category: config.category!,
      description: config.description,
      priority: config.priority!,
      scraping_difficulty: config.scrapingDifficulty!,
      has_official_api: config.hasOfficialAPI!
    };
  }

  async transformURLMappingToFrontend(mapping: any, configurations?: URLConfigurationResponse[]): Promise<URLMappingDisplay> {
    console.log('🔍 transformURLMappingToFrontend - Input mapping:', mapping);
    console.log('  - Input priority:', mapping.priority);
    
    // Handle both backend response formats: url_config_id (actual API) and configuration_id (interface)
    const configurationId = mapping.url_config_id || mapping.configuration_id;
    
    // Handle both single extractor (legacy) and multiple extractors (future)
    const extractorIds = mapping.extractor_ids || [];
    
    // If configuration is missing but we have configurationId, try to find it in provided configurations first
    let configurationData = mapping.configuration;
    let url = mapping.configuration?.url || '';
    let name = mapping.name || `Mapping ${mapping.id}`; // Use mapping.name, not configuration.name!
    
    if (!configurationData && configurationId) {
      // First try to find in provided configurations array (from getAllDataForUI)
      if (configurations) {
        configurationData = configurations.find(config => config.id === configurationId);
        if (configurationData) {
          url = configurationData.url;
          console.log('🔍 Found configuration in provided array:', configurationData);
        }
      }
      
      // If still not found, fetch it individually (fallback)
      if (!configurationData) {
        try {
          console.log('🔍 Configuration missing, fetching for ID:', configurationId);
          configurationData = await this.getURLConfiguration(configurationId);
          url = configurationData.url;
          // Don't override mapping name with configuration name
          console.log('🔍 Fetched configuration:', configurationData);
        } catch (error) {
          console.warn('⚠️ Failed to fetch configuration for ID:', configurationId, error);
          // Try to get URL from cache or existing mappings if fetch fails
          const cachedMapping = this.getCachedMappingById(mapping.id);
          if (cachedMapping?.url) {
            url = cachedMapping.url;
            console.log('🔍 Using cached URL:', url);
          }
        }
      }
    }
    
    // Parse metadata to extract fields that might be stored there
    let parsedMetadata: any = {};
    try {
      if (typeof mapping.metadata === 'string') {
        parsedMetadata = JSON.parse(mapping.metadata);
      } else if (mapping.metadata && typeof mapping.metadata === 'object') {
        parsedMetadata = mapping.metadata;
      }
    } catch (error) {
      console.warn('⚠️ Failed to parse metadata:', mapping.metadata, error);
      parsedMetadata = {};
    }

    // Extract fields with fallback to metadata
    const extractedName = mapping.name || parsedMetadata.name || `Mapping ${mapping.id}`;
    
    // Handle tags - can be array or string in metadata
    let extractedTags = mapping.tags || [];
    if ((!extractedTags || extractedTags.length === 0) && parsedMetadata.tags) {
      if (Array.isArray(parsedMetadata.tags)) {
        extractedTags = parsedMetadata.tags;
      } else if (typeof parsedMetadata.tags === 'string') {
        // Handle comma-separated string or JSON array string
        try {
          extractedTags = JSON.parse(parsedMetadata.tags);
        } catch {
          extractedTags = parsedMetadata.tags.split(',').map((tag: string) => tag.trim()).filter((tag: string) => tag);
        }
      }
    }
    
    const extractedNotes = mapping.notes || parsedMetadata.notes || '';
    const extractedCategory = mapping.category || parsedMetadata.category || '';

    const transformed = {
      id: mapping.id,
      name: extractedName,
      configurationId: configurationId,
      extractorIds: extractorIds, // Multiple extractors support
      rateLimit: mapping.rate_limit,
      priority: mapping.priority,
      crawlerSettings: mapping.crawler_settings,
      validationRules: mapping.validation_rules,
      isActive: mapping.is_active,
      url: url,
      config: mapping.crawler_settings,
      extractionCount: 0,
      successRate: 0,
      lastExtracted: null,
      created_at: mapping.created_at,
      updated_at: mapping.updated_at,
      tags: extractedTags,
      notes: extractedNotes,
      category: extractedCategory,
      metadata: mapping.metadata || {},
      configuration: configurationData ? this.transformURLConfigurationToFrontend(configurationData) : undefined
    };
    
    // Store in cache for future reference
    this.cacheMappingData(transformed);
    
    console.log('🔍 transformURLMappingToFrontend - Output:', transformed);
    console.log('  - Output priority:', transformed.priority);
    console.log('  - Output URL:', transformed.url);
    
    return transformed;
  }

  transformURLMappingToBackend(mapping: URLMappingFormData): URLMappingCreateRequest {
    console.log('🔍 transformURLMappingToBackend - Input mapping:', mapping);
    console.log('🔍 ALL INPUT FIELDS:');
    console.log('  - name:', mapping.name);
    console.log('  - configurationId:', mapping.configurationId);
    console.log('  - extractorId:', mapping.extractorId);
    console.log('  - extractorIds:', mapping.extractorIds);
    console.log('  - rateLimit:', mapping.rateLimit);
    console.log('  - priority:', mapping.priority);
    console.log('  - isActive:', mapping.isActive);
    console.log('  - tags:', mapping.tags);
    console.log('  - notes:', mapping.notes);
    console.log('  - category:', mapping.category);
    console.log('  - metadata:', mapping.metadata);
    console.log('  - crawlerSettings:', mapping.crawlerSettings);
    console.log('  - validationRules:', mapping.validationRules);
    
    // Validate and get extractor IDs array
    let extractorIds: string[] = [];
    
    // Check extractorIds array first (new multiple selection)
    if (mapping.extractorIds && Array.isArray(mapping.extractorIds) && mapping.extractorIds.length > 0) {
      const validIds = mapping.extractorIds.filter(id => id && id.toString().trim() !== '');
      if (validIds.length > 0) {
        extractorIds = validIds;
        console.log('🔍 Using extractors from array:', extractorIds);
      }
    }
    // Fallback to legacy extractorId field
    else if (mapping.extractorId) {
      extractorIds = [mapping.extractorId.toString().trim()];
      console.log('🔍 Using legacy extractorId as array:', extractorIds);
    }
    
    // Validation: ensure we have valid extractor IDs
    if (extractorIds.length === 0) {
      console.error('❌ No valid extractor IDs found in mapping data:', {
        extractorIds: mapping.extractorIds,
        extractorId: mapping.extractorId
      });
      throw new Error('At least one extractor must be selected');
    }

    // Validate configurationId (should be UUID string)
    if (!mapping.configurationId || mapping.configurationId === null || mapping.configurationId === undefined) {
      console.error('❌ No valid configuration ID found in mapping data:', {
        configurationId: mapping.configurationId
      });
      throw new Error('A URL configuration must be selected');
    }

    // Backend expects url_config_id as string (UUID)
    const configId = mapping.configurationId.toString().trim();
    if (!configId) {
      console.error('❌ Invalid configuration ID - empty string:', {
        configurationId: mapping.configurationId
      });
      throw new Error('Invalid URL configuration selected');
    }

    // Backend expects url_config_id as string and extractor_ids as array
    const transformedData = {
      name: mapping.name,
      url_config_id: configId,
      extractor_ids: extractorIds,
      rate_limit: mapping.rateLimit,
      priority: mapping.priority,
      crawler_settings: typeof mapping.crawlerSettings === 'string' ? JSON.parse(mapping.crawlerSettings || '{}') : mapping.crawlerSettings,
      validation_rules: typeof mapping.validationRules === 'string' ? JSON.parse(mapping.validationRules || '{}') : mapping.validationRules,
      is_active: mapping.isActive,
      tags: mapping.tags || [],
      notes: mapping.notes || '',
      category: mapping.category || '',
      metadata: typeof mapping.metadata === 'string' ? JSON.parse(mapping.metadata || '{}') : mapping.metadata || {}
    };
    
    console.log('🔍 ===== FINAL UPDATE REQUEST DATA =====');
    console.log('🔍 transformURLMappingToBackend - Output data:', JSON.stringify(transformedData, null, 2));
    console.log('🔍 Field validation:');
    console.log('  - name:', transformedData.name, typeof transformedData.name);
    console.log('  - url_config_id:', transformedData.url_config_id, typeof transformedData.url_config_id);
    console.log('  - extractor_ids:', transformedData.extractor_ids, typeof transformedData.extractor_ids);
    console.log('  - rate_limit:', transformedData.rate_limit, typeof transformedData.rate_limit);
    console.log('  - priority:', transformedData.priority, typeof transformedData.priority);
    console.log('  - is_active:', transformedData.is_active, typeof transformedData.is_active);
    console.log('  - tags:', transformedData.tags, typeof transformedData.tags);
    console.log('  - notes:', transformedData.notes, typeof transformedData.notes);
    console.log('  - category:', transformedData.category, typeof transformedData.category);
    console.log('  - metadata:', transformedData.metadata, typeof transformedData.metadata);
    console.log('🔍 ===== END UPDATE REQUEST DATA =====');
    
    return transformedData;
  }

  transformExtractorToFrontend(extractor: ExtractorResponse): Extractor {
    // Determine type based on extractor name or use default
    let type = 'content';
    const name = extractor.name.toLowerCase();
    if (name.includes('api') || name.includes('json')) {
      type = 'api';
    } else if (name.includes('social') || name.includes('twitter') || name.includes('facebook')) {
      type = 'social';
    } else if (name.includes('product') || name.includes('ecommerce') || name.includes('shop')) {
      type = 'ecommerce';
    } else if (name.includes('html') || name.includes('web')) {
      type = 'html';
    } else if (name.includes('image') || name.includes('media') || name.includes('video')) {
      type = 'media';
    }

    return {
      id: extractor.id, // Keep as string
      name: extractor.name,
      type: type,
      description: extractor.description,
      version: extractor.version || '1.0.0',
      supportedDomains: extractor.supported_domains || [],
      configSchema: extractor.config_schema || {},
      isActive: extractor.is_active !== undefined ? extractor.is_active : true // Default to true if not provided
    };
  }

  // Cache for mapping data to preserve URLs during updates
  private mappingCache = new Map<string, URLMappingDisplay>();
  
  private getCachedMappingById(id: string): URLMappingDisplay | undefined {
    return this.mappingCache.get(id);
  }
  
  private cacheMappingData(mapping: URLMappingDisplay): void {
    this.mappingCache.set(mapping.id, mapping);
  }
  
  // Combined operations for the frontend
  async getAllDataForUI(): Promise<{
    urlConfigurations: URLConfig[];
    urlMappings: URLMappingDisplay[];
    extractors: Extractor[];
  }> {
    try {
      console.log('🔍 getAllDataForUI: Starting API calls...');
      
      const [configurationsResponse, mappingsResponse, extractorsResponse] = await Promise.all([
        this.getURLConfigurations({ limit: 1000 }), // Remove is_active=false to get all active data
        this.getURLMappings({ limit: 1000 }), // Remove is_active=false to get all active data
        this.getExtractors()
      ]);

      console.log('🔍 Raw API responses:');
      console.log('  - Configurations response:', configurationsResponse);
      console.log('  - Mappings response:', mappingsResponse);
      console.log('  - Extractors response:', extractorsResponse);

      // Handle both response formats: paginated (with items) and direct array
      const configurations = Array.isArray(configurationsResponse) 
        ? configurationsResponse 
        : (configurationsResponse?.items || []);
      const mappings = Array.isArray(mappingsResponse) 
        ? mappingsResponse 
        : (mappingsResponse?.items || []);
      const extractors = Array.isArray(extractorsResponse) 
        ? extractorsResponse 
        : [];

      console.log('🔍 Extracted data arrays:');
      console.log('  - Configurations count:', configurations.length);
      console.log('  - Mappings count:', mappings.length);
      console.log('  - Extractors count:', extractors.length);

      const transformedData = {
        urlConfigurations: configurations.map(config => 
          this.transformURLConfigurationToFrontend(config)
        ),
        urlMappings: await Promise.all(mappings.map(mapping => 
          this.transformURLMappingToFrontend(mapping, configurations)
        )),
        extractors: extractors.map((extractor: ExtractorResponse) => 
          this.transformExtractorToFrontend(extractor)
        )
      };

      console.log('🔍 Transformed data:');
      console.log('  - URL Configurations:', transformedData.urlConfigurations.length);
      console.log('  - URL Mappings:', transformedData.urlMappings.length);
      console.log('  - Extractors:', transformedData.extractors.length);

      return transformedData;
    } catch (error) {
      console.error('❌ Error fetching data for UI:', error);
      // Return empty arrays instead of throwing to prevent UI crashes
      return {
        urlConfigurations: [],
        urlMappings: [],
        extractors: []
      };
    }
  }
}

export const urlMappingsService = new URLMappingsService();
export default urlMappingsService;