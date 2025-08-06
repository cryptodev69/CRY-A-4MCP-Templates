/**
 * API Configuration for CRY-A-4MCP Frontend
 * 
 * Centralized configuration for API endpoints and base URL.
 * Supports environment-based configuration for development and production.
 */

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:4000';

export const API_ENDPOINTS = {
  urlConfigurations: '/api/url-configurations',
  urlMappings: '/api/url-mappings',
  extractors: '/api/extractors',
} as const;

export const API_CONFIG = {
  timeout: 30000, // 30 seconds
  retries: 3,
  retryDelay: 1000 // 1 second
} as const;