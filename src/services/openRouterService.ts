/**
 * OpenRouter service for fetching available models and managing API interactions
 */

export interface OpenRouterModel {
  id: string;
  context_length: number | string;
  prompt_price: number;
  completion_price: number;
  prompt_price_formatted: string;
  completion_price_formatted: string;
  is_free: boolean;
}

export interface OpenRouterResponse {
  success: boolean;
  models: OpenRouterModel[];
  message: string;
}

/**
 * OpenRouter service class for managing model fetching and API interactions
 */
class OpenRouterService {
  private baseUrl = '/api'; // Backend API endpoint

  /**
   * Fetch available models from OpenRouter API via backend
   * @param apiKey - OpenRouter API key
   * @param filterFree - Whether to only include free models
   * @returns Promise with OpenRouter response
   */
  async getModels(apiKey: string, filterFree: boolean = false): Promise<OpenRouterResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/openrouter/models`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_key: apiKey,
          filter_free: filterFree
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to fetch OpenRouter models:', error);
      return {
        success: false,
        models: [],
        message: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  /**
   * Filter models based on search query
   * @param models - Array of OpenRouter models
   * @param searchQuery - Search query string
   * @returns Filtered array of models
   */
  filterModels(models: OpenRouterModel[], searchQuery: string): OpenRouterModel[] {
    if (!searchQuery.trim()) {
      return models;
    }

    const query = searchQuery.toLowerCase();
    return models.filter(model => 
      model.id.toLowerCase().includes(query)
    );
  }

  /**
   * Sort models by various criteria
   * @param models - Array of OpenRouter models
   * @param sortBy - Sort criteria
   * @returns Sorted array of models
   */
  sortModels(models: OpenRouterModel[], sortBy: 'name' | 'context' | 'price' = 'name'): OpenRouterModel[] {
    return [...models].sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.id.localeCompare(b.id);
        case 'context':
          const aContext = typeof a.context_length === 'number' ? a.context_length : parseInt(String(a.context_length)) || 0;
          const bContext = typeof b.context_length === 'number' ? b.context_length : parseInt(String(b.context_length)) || 0;
          return bContext - aContext; // Descending order
        case 'price':
          return a.prompt_price - b.prompt_price; // Ascending order
        default:
          return 0;
      }
    });
  }

  /**
   * Get popular/recommended models
   * @returns Array of popular model IDs
   */
  getPopularModels(): string[] {
    return [
      'anthropic/claude-3-opus:beta',
      'anthropic/claude-3-sonnet:beta',
      'anthropic/claude-3-haiku:beta',
      'openai/gpt-4-turbo',
      'openai/gpt-4',
      'openai/gpt-3.5-turbo',
      'google/gemini-pro',
      'meta-llama/llama-3-70b-instruct',
      'mistralai/mistral-large',
      'cohere/command-r-plus'
    ];
  }

  /**
   * Check if API key is stored in localStorage
   * @returns OpenRouter API key if available
   */
  getStoredApiKey(): string | null {
    try {
      const apiKeys = localStorage.getItem('apiKeys');
      if (apiKeys) {
        const parsedKeys = JSON.parse(apiKeys);
        const openRouterKey = parsedKeys.find((key: any) => key.provider === 'openrouter');
        return openRouterKey?.apiKey || null;
      }
    } catch (error) {
      console.error('Failed to retrieve stored API key:', error);
    }
    return null;
  }
}

// Export singleton instance
export const openRouterService = new OpenRouterService();
export default openRouterService;