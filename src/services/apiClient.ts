/**
 * HTTP API Client for CRY-A-4MCP Frontend
 * 
 * Provides a centralized HTTP client with error handling, retry logic,
 * and TypeScript support for all API communications.
 */

import { API_CONFIG } from '../config/api';

export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}

export class ApiClientError extends Error {
  public status?: number;
  public statusText?: string;
  public details?: any;

  constructor(message: string, status?: number, statusText?: string, details?: any) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.statusText = statusText;
    this.details = details;
  }
}

export class ApiClient {
  private baseURL: string;
  private timeout: number;
  private retries: number;
  private retryDelay: number;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.timeout = API_CONFIG.timeout;
    this.retries = API_CONFIG.retries;
    this.retryDelay = API_CONFIG.retryDelay;
  }

  /**
   * Execute HTTP request with retry logic and error handling
   */
  private async executeRequest<T>(
    url: string,
    options: RequestInit,
    attempt: number = 1
  ): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        let errorDetails;

        try {
          const errorBody = await response.text();
          if (errorBody) {
            try {
              errorDetails = JSON.parse(errorBody);
              errorMessage = errorDetails.detail || errorDetails.message || errorMessage;
            } catch {
              errorMessage = errorBody;
            }
          }
        } catch {
          // Ignore error parsing response body
        }

        throw new ApiClientError(errorMessage, response.status, response.statusText, errorDetails);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        return await response.text() as unknown as T;
      }
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof ApiClientError) {
        throw error;
      }

      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiClientError('Request timeout', 408, 'Request Timeout');
      }

      // Retry logic for network errors
      if (attempt < this.retries && this.shouldRetry(error)) {
        await this.delay(this.retryDelay * attempt);
        return this.executeRequest<T>(url, options, attempt + 1);
      }

      throw new ApiClientError(
        error instanceof Error ? error.message : 'Network error',
        0,
        'Network Error',
        error
      );
    }
  }

  /**
   * Determine if request should be retried
   */
  private shouldRetry(error: any): boolean {
    if (error instanceof ApiClientError) {
      // Don't retry client errors (4xx)
      return !error.status || error.status >= 500;
    }
    // Retry network errors
    return true;
  }

  /**
   * Delay utility for retry logic
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, params?: Record<string, string | number | boolean>): Promise<T> {
    let url = `${this.baseURL}${endpoint}`;
    
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        searchParams.set(key, value.toString());
      });
      url += `?${searchParams.toString()}`;
    }

    return this.executeRequest<T>(url, {
      method: 'GET',
    });
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.executeRequest<T>(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.executeRequest<T>(`${this.baseURL}${endpoint}`, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * DELETE request
   */
  async delete<T = void>(endpoint: string): Promise<T> {
    return this.executeRequest<T>(`${this.baseURL}${endpoint}`, {
      method: 'DELETE',
    });
  }
}