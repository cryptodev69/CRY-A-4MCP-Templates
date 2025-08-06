import { urlMappingsService } from '../../services/urlMappingsService';
import { ApiClient, ApiClientError } from '../../services/apiClient';
import {
  URLConfigurationResponse,
  URLMappingResponse,
  ExtractorResponse
} from '../../services/urlMappingsService';
import {
  URLMappingCreateRequest,
  URLMappingUpdateRequest
} from '../../types/urlMappings';

// Mock the ApiClient
jest.mock('../../services/apiClient');
const MockedApiClient = ApiClient as jest.MockedClass<typeof ApiClient>;

describe('URLMappingsService', () => {
  let service: typeof urlMappingsService;
  let mockApiClient: jest.Mocked<ApiClient>;

  beforeEach(() => {
    mockApiClient = new MockedApiClient('http://localhost:8000') as jest.Mocked<ApiClient>;
    service = urlMappingsService;
    // Replace the internal apiClient with our mock
    (service as any).apiClient = mockApiClient;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('URL Configurations', () => {
    const mockUrlConfig: URLConfigurationResponse = {
      id: '1',
      name: 'Test Config',
      url: 'https://example.com',
      profile_type: 'web',
      category: 'test',
      description: 'Test description',
      priority: 1,
      scraping_difficulty: 3,
      has_official_api: false,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };

    it('should get all URL configurations', async () => {
      const mockConfigs = [mockUrlConfig];
      mockApiClient.get.mockResolvedValueOnce({ items: mockConfigs, total: 1 });

      const result = await service.getURLConfigurations();

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/url-configurations?page=1&size=100');
      expect(result.items).toEqual(mockConfigs);
      expect(result.total).toBe(1);
    });

    it('should get URL configuration by ID', async () => {
      mockApiClient.get.mockResolvedValueOnce(mockUrlConfig);

      const result = await service.getURLConfiguration('1');

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/url-configurations/1');
      expect(result).toEqual(mockUrlConfig);
    });

    it('should create URL configuration', async () => {
      const createRequest = {
        name: 'New Config',
        url: 'https://newsite.com',
        profile_type: 'web',
        category: 'test',
        description: 'New description',
        priority: 1,
        scraping_difficulty: 1,
        has_official_api: false
      };
      mockApiClient.post.mockResolvedValueOnce(mockUrlConfig);

      const result = await service.createURLConfiguration(createRequest);

      expect(mockApiClient.post).toHaveBeenCalledWith('/api/v1/url-configurations', createRequest);
      expect(result).toEqual(mockUrlConfig);
    });

    it('should update URL configuration', async () => {
      const updateRequest = { name: 'Updated Config' };
      const updatedConfig = { ...mockUrlConfig, name: 'Updated Config' };
      mockApiClient.put.mockResolvedValueOnce(updatedConfig);

      const result = await service.updateURLConfiguration('1', updateRequest);

      expect(mockApiClient.put).toHaveBeenCalledWith('/api/v1/url-configurations/1', updateRequest);
      expect(result).toEqual(updatedConfig);
    });

    it('should delete URL configuration', async () => {
      mockApiClient.delete.mockResolvedValueOnce(undefined);

      await service.deleteURLConfiguration('1');

      expect(mockApiClient.delete).toHaveBeenCalledWith('/api/v1/url-configurations/1');
    });
  });

  describe('URL Mappings', () => {
    const mockUrlMapping: URLMappingResponse = {
      id: '1',
      url_config_id: '1',
      extractor_ids: ['1'],
      rate_limit: 10,
      priority: 10,
      crawler_settings: { field1: 'value1' },
      validation_rules: { rule1: 'value1' },
      is_active: true,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z'
    };

    it('should get all URL mappings', async () => {
      const mockMappings = [mockUrlMapping];
      mockApiClient.get.mockResolvedValueOnce({ items: mockMappings, total: 1 });

      const result = await service.getURLMappings();

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/url-mappings?page=1&size=100');
      expect(result.items).toEqual(mockMappings);
      expect(result.total).toBe(1);
    });

    it('should create URL mapping', async () => {
      const createRequest: URLMappingCreateRequest = {
        url_config_id: '1',
        extractor_ids: ['1'],
        rate_limit: 10,
        crawler_settings: { field1: 'value1' },
        validation_rules: { rule1: 'value1' },
        is_active: true
      };
      mockApiClient.post.mockResolvedValueOnce(mockUrlMapping);

      const result = await service.createURLMapping(createRequest);

      expect(mockApiClient.post).toHaveBeenCalledWith('/api/v1/url-mappings', createRequest);
      expect(result).toEqual(mockUrlMapping);
    });

    it('should update URL mapping', async () => {
      const updateRequest: URLMappingUpdateRequest = {
        is_active: false
      };
      const updatedMapping = { ...mockUrlMapping, is_active: false };
      mockApiClient.put.mockResolvedValueOnce(updatedMapping);

      const result = await service.updateURLMapping('1', updateRequest);

      expect(mockApiClient.put).toHaveBeenCalledWith('/api/v1/url-mappings/1', updateRequest);
      expect(result).toEqual(updatedMapping);
    });

    it('should delete URL mapping', async () => {
      mockApiClient.delete.mockResolvedValueOnce(undefined);

      await service.deleteURLMapping('1');

      expect(mockApiClient.delete).toHaveBeenCalledWith('/api/v1/url-mappings/1');
    });
  });

  describe('Extractors', () => {
    const mockExtractor: ExtractorResponse = {
      id: '1',
      name: 'Test Extractor',
      description: 'Test extractor description',
      version: '1.0.0',
      supported_domains: ['example.com'],
      config_schema: {
        type: 'object',
        properties: {
          field1: { type: 'string' }
        }
      },
      is_active: true
    };

    it('should get all extractors', async () => {
      const mockExtractors = [mockExtractor];
      mockApiClient.get.mockResolvedValueOnce({ items: mockExtractors, total: 1 });

      const result = await service.getExtractors();

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/extractors?page=1&size=100');
      expect(result).toEqual(mockExtractors);
    });

    it('should get extractor by ID', async () => {
      mockApiClient.get.mockResolvedValueOnce(mockExtractor);

      const result = await service.getExtractor('1');

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/extractors/1');
      expect(result).toEqual(mockExtractor);
    });
  });

  describe('Data transformation', () => {
    it('should transform URL configuration from backend to frontend', () => {
      const backendConfig: URLConfigurationResponse = {
        id: '1',
        name: 'Test Config',
        url: 'https://example.com',
        profile_type: 'web',
        category: 'test',
        description: 'Test description',
        priority: 1,
        scraping_difficulty: 3,
        has_official_api: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      const result = service.transformURLConfigurationToFrontend(backendConfig);

      expect(result).toEqual({
        id: '1',
        name: 'Test Config',
        baseUrl: 'https://example.com',
        profileType: 'web',
        category: 'test',
        description: 'Test description',
        priority: 1,
        scrapingDifficulty: 3,
        hasOfficialApi: false,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      });
    });

    it('should transform URL mapping from backend to frontend', async () => {
      const backendMapping: URLMappingResponse = {
        id: '1',
        url_config_id: '1',
        extractor_ids: ['1'],
        rate_limit: 10,
        priority: 10,
        crawler_settings: { field1: 'value1' },
        validation_rules: { rule1: 'value1' },
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      const result = await service.transformURLMappingToFrontend(backendMapping);

      expect(result).toEqual({
        id: '1',
        urlConfigId: '1',
        extractorId: '1',
        urlPattern: 'https://example.com/page/*',
        priority: 10,
        isActive: true,
        extractionConfig: { field1: 'value1' },
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      });
    });

    it('should transform extractor from backend to frontend', () => {
      const backendExtractor: ExtractorResponse = {
        id: '1',
        name: 'Test Extractor',
        description: 'Test extractor description',
        version: '1.0.0',
        supported_domains: ['example.com'],
        config_schema: {
          type: 'object',
          properties: {
            field1: { type: 'string' }
          }
        },
        is_active: true
      };

      const result = service.transformExtractorToFrontend(backendExtractor);

      expect(result).toEqual({
        id: 1,
        name: 'Test Extractor',
        description: 'Test extractor description',
        version: '1.0.0',
        configSchema: {
          type: 'object',
          properties: {
            field1: { type: 'string' }
          }
        },
        isActive: true,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      });
    });
  });

  describe('Combined operations', () => {
    it('should get all data for UI', async () => {
      const mockConfigs = [{
        id: 1,
        name: 'Test Config',
        base_url: 'https://example.com',
        description: 'Test description',
        headers: {},
        query_params: {},
        rate_limit: 10,
        timeout: 30,
        retry_count: 3,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }];

      const mockExtractors = [{
        id: 1,
        name: 'Test Extractor',
        description: 'Test extractor description',
        version: '1.0.0',
        config_schema: { type: 'object' },
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }];

      const mockMappings = [{
        id: '1',
        url_config_id: '1',
        extractor_ids: ['1'],
        url_pattern: 'https://example.com/page/*',
        priority: 10,
        is_active: true,
        extraction_config: {},
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }];

      mockApiClient.get
        .mockResolvedValueOnce({ items: mockConfigs, total: 1 })
        .mockResolvedValueOnce({ items: mockExtractors, total: 1 })
        .mockResolvedValueOnce({ items: mockMappings, total: 1 });

      const result = await service.getAllDataForUI();

      expect(mockApiClient.get).toHaveBeenCalledTimes(3);
      expect(result.urlConfigurations).toHaveLength(1);
      expect(result.extractors).toHaveLength(1);
      expect(result.urlMappings).toHaveLength(1);
    });

    it('should handle errors in getAllDataForUI', async () => {
      mockApiClient.get.mockRejectedValueOnce(new ApiClientError('Network error', 500));

      await expect(service.getAllDataForUI()).rejects.toThrow(ApiClientError);
    });
  });

  describe('Error handling', () => {
    it('should propagate API client errors', async () => {
      const apiError = new ApiClientError('Not found', 404, 'Not Found');
      mockApiClient.get.mockRejectedValueOnce(apiError);

      await expect(service.getURLConfiguration('999')).rejects.toThrow(ApiClientError);
      await expect(service.getURLConfiguration('999')).rejects.toThrow('Not found');
    });

    it('should handle validation errors on create', async () => {
      const validationError = new ApiClientError('Validation failed', 400, 'Bad Request');
      mockApiClient.post.mockRejectedValueOnce(validationError);

      await expect(service.createURLConfiguration({
        name: '',
        url: 'invalid-url',
        profile_type: 'web',
        category: 'test',
        priority: 1,
        scraping_difficulty: 1,
        has_official_api: false
      })).rejects.toThrow(ApiClientError);
    });
  });
});