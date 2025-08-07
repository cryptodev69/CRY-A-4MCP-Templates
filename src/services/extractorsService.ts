/**
 * Extractors service for fetching and managing extraction strategies
 */

export interface Extractor {
  id: string;
  name: string;
  description: string;
  schema: string | object;
  file_path: string;
}

export interface ExtractorsResponse {
  success: boolean;
  extractors: Extractor[];
  message?: string;
}

/**
 * Extractors service class for managing extractor fetching and filtering
 */
class ExtractorsService {
  private baseUrl = '/api'; // Backend API endpoint

  /**
   * Fetch all available extractors from the backend
   * @returns Promise with all extractors
   */
  async fetchExtractors(): Promise<ExtractorsResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/extractors`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const extractors: Extractor[] = await response.json();
      
      // Parse schema field if it's a valid JSON string
      const processedExtractors = extractors.map(extractor => ({
        ...extractor,
        schema: this.parseSchema(extractor.schema)
      }));

      return {
        success: true,
        extractors: processedExtractors,
      };
    } catch (error) {
      console.error('Failed to fetch extractors:', error);
      return {
        success: false,
        extractors: [],
        message: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  /**
   * Fetch a specific extractor by ID
   * @param id - Extractor ID
   * @returns Promise with specific extractor
   */
  async fetchExtractor(id: string): Promise<{ success: boolean; extractor?: Extractor; message?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/extractors/${id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Extractor '${id}' not found`);
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const extractor: Extractor = await response.json();
      
      // Parse schema field if it's a valid JSON string
      const processedExtractor = {
        ...extractor,
        schema: this.parseSchema(extractor.schema)
      };

      return {
        success: true,
        extractor: processedExtractor,
      };
    } catch (error) {
      console.error(`Failed to fetch extractor ${id}:`, error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  /**
   * Filter extractors based on criteria
   * @param extractors - Array of extractors
   * @param searchQuery - Search query string
   * @param hasSchema - Filter extractors that have schema
   * @returns Filtered array of extractors
   */
  filterExtractors(
    extractors: Extractor[], 
    searchQuery: string = '', 
    hasSchema: boolean = false
  ): Extractor[] {
    let filtered = extractors;

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(extractor => 
        extractor.name.toLowerCase().includes(query) ||
        extractor.description.toLowerCase().includes(query) ||
        extractor.id.toLowerCase().includes(query)
      );
    }

    // Filter extractors that have schema (for LLM extraction)
    if (hasSchema) {
      filtered = filtered.filter(extractor => 
        extractor.schema && 
        (typeof extractor.schema === 'object' || 
         (typeof extractor.schema === 'string' && extractor.schema.trim().length > 0))
      );
    }

    return filtered;
  }

  /**
   * Get extractors suitable for LLM-based extraction
   * @param extractors - Array of extractors
   * @returns Extractors with schema and description suitable for LLM
   */
  getLLMExtractors(extractors: Extractor[]): Extractor[] {
    return this.filterExtractors(extractors, '', true).filter(extractor => 
      extractor.description && extractor.description.trim().length > 0
    );
  }

  /**
   * Parse schema field - convert JSON string to object if valid, otherwise keep as string
   * @param schema - Schema field from API response
   * @returns Parsed schema object or original string
   */
  private parseSchema(schema: string | object): string | object {
    if (typeof schema === 'object') {
      return schema;
    }
    
    if (typeof schema === 'string' && schema.trim()) {
      try {
        // Try to parse as JSON
        const parsed = JSON.parse(schema);
        return parsed;
      } catch {
        // If parsing fails, return as string
        return schema;
      }
    }
    
    return schema;
  }

  /**
   * Extract instruction from extractor description
   * @param extractor - Extractor object
   * @returns Instruction string for LLM
   */
  getInstructionFromExtractor(extractor: Extractor): string {
    // Use description as instruction, or provide a default
    return extractor.description || `Extract data using ${extractor.name} strategy`;
  }

  /**
   * Format schema for display in UI
   * @param schema - Schema object or string
   * @returns Formatted schema string
   */
  formatSchemaForDisplay(schema: string | object): string {
    if (typeof schema === 'object') {
      return JSON.stringify(schema, null, 2);
    }
    return schema || '';
  }
}

// Export singleton instance
export const extractorsService = new ExtractorsService();
export default extractorsService;