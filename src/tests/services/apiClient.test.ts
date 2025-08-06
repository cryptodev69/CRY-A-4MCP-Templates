import { ApiClient, ApiClientError } from '../../services/apiClient';
import { API_CONFIG } from '../../config/api';

describe('ApiClient', () => {
  let apiClient: ApiClient;
  const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    apiClient = new ApiClient('http://localhost:8000');
    mockFetch.mockReset();
  });

  describe('GET requests', () => {
    it('should make successful GET request', async () => {
      const mockData = { id: 1, name: 'test' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => mockData,
      } as Response);

      const result = await apiClient.get('/test');
      
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/test', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: expect.any(AbortSignal),
      });
      expect(result).toEqual(mockData);
    });

    it('should handle 404 errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Resource not found',
      } as Response);

      await expect(apiClient.get('/nonexistent'))
        .rejects
        .toThrow(ApiClientError);
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiClient.get('/test'))
        .rejects
        .toThrow(ApiClientError);
    });

    it('should retry on failure', async () => {
      mockFetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({ success: true }),
        } as Response);

      const result = await apiClient.get('/test');
      
      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(result).toEqual({ success: true });
    });

    it('should timeout after configured time', async () => {
      mockFetch.mockImplementationOnce(() => 
        new Promise(resolve => setTimeout(resolve, API_CONFIG.timeout + 1000))
      );

      await expect(apiClient.get('/test'))
        .rejects
        .toThrow('Request timeout');
    }, API_CONFIG.timeout + 2000);
  });

  describe('POST requests', () => {
    it('should make successful POST request with data', async () => {
      const requestData = { name: 'test', value: 123 };
      const responseData = { id: 1, ...requestData };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        statusText: 'Created',
        json: async () => responseData,
      } as Response);

      const result = await apiClient.post('/test', requestData);
      
      expect(mockFetch).toHaveBeenCalledWith('/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
        signal: expect.any(AbortSignal),
      });
      expect(result).toEqual(responseData);
    });

    it('should handle validation errors (400)', async () => {
      const errorResponse = {
        detail: [{ field: 'name', message: 'Required field' }]
      };
      
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => errorResponse,
      } as Response);

      await expect(apiClient.post('/test', {}))
        .rejects
        .toThrow(ApiClientError);
    });
  });

  describe('PUT requests', () => {
    it('should make successful PUT request', async () => {
      const updateData = { name: 'updated' };
      const responseData = { id: 1, ...updateData };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => responseData,
      } as Response);

      const result = await apiClient.put('/test/1', updateData);
      
      expect(mockFetch).toHaveBeenCalledWith('/test/1', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
        signal: expect.any(AbortSignal),
      });
      expect(result).toEqual(responseData);
    });
  });

  describe('DELETE requests', () => {
    it('should make successful DELETE request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
        statusText: 'No Content',
        text: async () => '',
      } as Response);

      await apiClient.delete('/test/1');
      
      expect(mockFetch).toHaveBeenCalledWith('/test/1', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: expect.any(AbortSignal),
      });
    });

    it('should handle 404 on delete', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Resource not found',
      } as Response);

      await expect(apiClient.delete('/test/999'))
        .rejects
        .toThrow(ApiClientError);
    });
  });

  describe('Error handling', () => {
    it('should create ApiClientError with correct properties', () => {
      const error = new ApiClientError('Test error', 400, 'Bad Request');
      
      expect(error.message).toBe('Test error');
      expect(error.status).toBe(400);
      expect(error.statusText).toBe('Bad Request');
      expect(error.name).toBe('ApiClientError');
    });

    it('should handle JSON parsing errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Headers(),
        json: async () => { throw new Error('Invalid JSON'); },
      } as unknown as Response);

      await expect(apiClient.get('/test'))
        .rejects
        .toThrow(ApiClientError);
    });
  });
});