/**
 * URLMappingIntegrationService - Core service for bridging URL mappings with crawler configurations
 * 
 * This service enables seamless integration between URL mappings and crawlers by:
 * - Resolving URL mapping configurations and associated extractors
 * - Inheriting crawler settings from URL metadata (difficulty, priority, rate limits)
 * - Supporting multiple URLs per extractor mapping
 * - Providing dropdown-ready data structures for UI components
 * 
 * @author CRY-A-4MCP Platform
 * @version 1.0.0
 */

import { URLMapping, ExtractorMapping, CrawlerConfig } from './crawlApi';

/**
 * URL configuration interface for pre-configured website profiles
 */
export interface URLConfig {
  id: string;
  name: string;
  base_url: string;
  url_patterns: string[];
  scraping_difficulty: 'easy' | 'medium' | 'hard';
  rate_limit_delay: number;
  requires_js: boolean;
  auth_required: boolean;
  metadata: {
    category: string;
    priority: number;
    tags: string[];
    estimated_pages?: number;
    update_frequency?: string;
  };
}

/**
 * Extractor strategy interface for content extraction
 */
export interface ExtractorStrategy {
  id: string;
  name: string;
  type: 'css' | 'xpath' | 'llm' | 'regex' | 'custom';
  config: Record<string, any>;
  description?: string;
  schema?: Record<string, any>;
}

/**
 * Configuration blueprint generated from URL mapping integration
 */
export interface CrawlerConfigurationBlueprint {
  /** Unique identifier for the blueprint */
  id: string;
  /** Human-readable name derived from URL mapping */
  name: string;
  /** Auto-generated description based on URL mapping metadata */
  description: string;
  /** Recommended crawler type based on URL complexity */
  crawlerType: 'basic' | 'llm' | 'composite';
  /** Inherited technical configuration */
  config: {
    timeout: number;
    retries: number;
    concurrency: number;
    rateLimit?: number;
    headers?: Record<string, string>;
  };
  /** LLM configuration if required */
  llmConfig?: {
    provider: string;
    model: string;
    prompt: string;
  };
  /** Assigned extractor strategies */
  extractionStrategies: string[];
  /** Source URL mapping references */
  urlMappingIds: string[];
  /** Target URLs for crawling */
  targetUrls: string[];
  /** Inherited priority level */
  priority: number;
}

/**
 * Extractor assignment result with metadata
 */
export interface ExtractorAssignment {
  /** Extractor strategy ID */
  extractorId: string;
  /** Extractor name for display */
  extractorName: string;
  /** Associated URLs for this extractor */
  urls: string[];
  /** Assignment confidence score (0-1) */
  confidence: number;
  /** Reason for assignment */
  reason: string;
}

/**
 * Settings inherited from URL mapping metadata
 */
export interface InheritedSettings {
  /** Rate limiting configuration */
  rateLimit?: number;
  /** Retry configuration based on difficulty */
  retries: number;
  /** Timeout based on complexity */
  timeout: number;
  /** Concurrency limits */
  concurrency: number;
  /** Priority level */
  priority: number;
  /** Custom headers if specified */
  headers?: Record<string, string>;
}

/**
 * Dropdown option for URL mapping selection
 */
export interface URLMappingDropdownOption {
  /** Option value (URL mapping ID) */
  value: string;
  /** Display label */
  label: string;
  /** Option description */
  description: string;
  /** Associated URLs count */
  urlCount: number;
  /** Extractor count */
  extractorCount: number;
  /** Extractor names for display */
  extractorNames: string[];
  /** Difficulty indicator */
  difficulty: 'easy' | 'medium' | 'hard';
  /** Category for grouping */
  category: string;
  /** Preview of target URLs */
  urlPreview: string[];
}

/**
 * Error types for URL mapping integration
 */
export class URLMappingIntegrationError extends Error {
  constructor(
    message: string,
    public code: 'MAPPING_NOT_FOUND' | 'EXTRACTOR_NOT_FOUND' | 'INVALID_CONFIG' | 'VALIDATION_ERROR',
    public details?: any
  ) {
    super(message);
    this.name = 'URLMappingIntegrationError';
  }
}

/**
 * Main service class for URL mapping integration
 */
export class URLMappingIntegrationService {
  private urlMappings: URLMapping[] = [];
  private urlConfigs: URLConfig[] = [];
  private extractors: ExtractorStrategy[] = [];

  /**
   * Initialize the service with data sources
   * @param urlMappings - Available URL mapping configurations
   * @param urlConfigs - Pre-configured URL profiles
   * @param extractors - Available extractor strategies
   */
  constructor(
    urlMappings: URLMapping[],
    urlConfigs: URLConfig[],
    extractors: ExtractorStrategy[]
  ) {
    this.urlMappings = urlMappings;
    this.urlConfigs = urlConfigs;
    this.extractors = extractors;
  }

  /**
   * Get dropdown options for URL mapping selection
   * Provides UI-ready data for crawler creation dropdown
   * @returns Array of dropdown options grouped by category
   */
  public getURLMappingDropdownOptions(): URLMappingDropdownOption[] {
    console.log('URLMappingIntegrationService - Processing mappings:', this.urlMappings);
    return this.urlMappings.map(mapping => {
      console.log('Processing mapping:', mapping);
      const urlConfig = this.urlConfigs.find(config => config.id === mapping.id);
      
      // Handle actual API response structure
      const apiMapping = mapping as any;
      const extractorIds = apiMapping.extractor_ids || mapping.extractorIds || [];
      const extractorCount = extractorIds.length;
      
      // Get extractor names by mapping IDs to names
      const extractorNames = extractorIds.map((id: string) => {
        const extractor = this.extractors.find(e => e.id === id);
        return extractor ? extractor.name : `Unknown Extractor (${id})`;
      });
      
      // Get URLs from API response (uses 'urls' array) or fallback to pattern
      const urls = apiMapping.urls || [mapping.pattern || apiMapping.name].filter(Boolean);
      const primaryUrl = urls[0] || 'Unknown URL';
      const urlCount = urls.length;
      
      // Use 'name' from API response or generate from pattern
      const displayName = apiMapping.name || mapping.pattern || 'Unnamed Mapping';
      const description = apiMapping.description || `URL mapping for ${primaryUrl}`;
      
      return {
        value: mapping.id,
        label: displayName,
        description: description,
        urlCount,
        extractorCount,
        extractorNames,
        difficulty: this.mapDifficultyLevel(urlConfig?.scraping_difficulty || 'medium'),
        category: urlConfig?.metadata?.category || 'General',
        urlPreview: urls.slice(0, 3) // Show first 3 URLs as preview
      };
    });
  }

  /**
   * Resolve URL mapping configuration and create crawler blueprint
   * @param urlMappingId - ID of the URL mapping to resolve
   * @param crawlerRequirements - Optional crawler-specific requirements
   * @param overrideSettings - Optional settings to override inherited values
   * @returns Complete crawler configuration blueprint
   */
  public async resolveURLMapping(
    urlMappingId: string,
    crawlerRequirements?: Partial<CrawlerConfig>,
    overrideSettings?: Partial<InheritedSettings>
  ): Promise<CrawlerConfigurationBlueprint> {
    // Find the URL mapping
    const urlMapping = this.urlMappings.find(mapping => mapping.id === urlMappingId);
    if (!urlMapping) {
      throw new URLMappingIntegrationError(
        `URL mapping not found: ${urlMappingId}`,
        'MAPPING_NOT_FOUND',
        { urlMappingId }
      );
    }

    // Get associated URL config (match by URL pattern)
    // Handle both frontend (pattern) and backend (urls array) formats
    const mappingUrls = (urlMapping as any).urls || [urlMapping.pattern].filter(Boolean);
    const primaryUrl = mappingUrls[0] || '';
    
    const urlConfig = this.urlConfigs.find(config => 
      config.url_patterns.some(pattern => primaryUrl.includes(pattern)) ||
      primaryUrl.includes(config.base_url)
    );
    
    // Inherit settings from URL metadata
    const inheritedSettings = this.inheritCrawlerSettings(urlConfig, urlMapping, overrideSettings);
    
    // Assign extractors
    const extractorAssignments = await this.assignExtractors(urlMapping);
    
    // Determine crawler type based on complexity and extractors
    const crawlerType = this.determineCrawlerType(urlConfig, extractorAssignments);
    
    // Build target URLs list (support multiple URLs per mapping)
    const targetUrls = this.buildTargetUrlsList(urlMapping, urlConfig);
    
    // Generate blueprint
    const blueprint: CrawlerConfigurationBlueprint = {
      id: `crawler_${urlMappingId}_${Date.now()}`,
      name: `${urlConfig?.name || 'Auto-Generated'} Crawler`,
      description: `Auto-generated crawler for ${primaryUrl} using ${extractorAssignments.length} extractor(s)`,
      crawlerType,
      config: {
        timeout: inheritedSettings.timeout,
        retries: inheritedSettings.retries,
        concurrency: inheritedSettings.concurrency,
        rateLimit: inheritedSettings.rateLimit,
        headers: inheritedSettings.headers
      },
      llmConfig: crawlerType === 'llm' ? this.generateLLMConfig(urlConfig, extractorAssignments) : undefined,
      extractionStrategies: extractorAssignments.map(assignment => assignment.extractorId),
      urlMappingIds: [urlMappingId],
      targetUrls,
      priority: inheritedSettings.priority
    };

    // Apply any crawler-specific requirements
    if (crawlerRequirements) {
      this.applyCrawlerRequirements(blueprint, crawlerRequirements);
    }

    return blueprint;
  }

  /**
   * Inherit crawler settings from URL mapping metadata
   * @param urlConfig - URL configuration profile
   * @param urlMapping - URL mapping configuration
   * @param overrides - Optional setting overrides
   * @returns Inherited settings object
   */
  public inheritCrawlerSettings(
    urlConfig?: URLConfig,
    urlMapping?: URLMapping,
    overrides?: Partial<InheritedSettings>
  ): InheritedSettings {
    // Base settings
    const baseSettings: InheritedSettings = {
      timeout: 30000,
      retries: 3,
      concurrency: 1,
      priority: 5
    };

    // Apply URL config metadata
    if (urlConfig) {
      // Adjust settings based on scraping difficulty
      switch (urlConfig.scraping_difficulty) {
        case 'easy':
          baseSettings.timeout = 15000;
          baseSettings.retries = 2;
          baseSettings.concurrency = 3;
          break;
        case 'hard':
          baseSettings.timeout = 60000;
          baseSettings.retries = 5;
          baseSettings.concurrency = 1;
          break;
        default: // medium
          baseSettings.timeout = 30000;
          baseSettings.retries = 3;
          baseSettings.concurrency = 2;
      }

      // Apply priority
      baseSettings.priority = urlConfig.metadata.priority || 5;
    }

    // URLMapping from API doesn't have config property
    // Settings will be inherited from urlConfig instead

    // Apply overrides
    return { ...baseSettings, ...overrides };
  }

  /**
   * Assign extractors based on URL mapping configuration
   * @param urlMapping - URL mapping configuration
   * @returns Array of extractor assignments with metadata
   */
  public async assignExtractors(urlMapping: URLMapping): Promise<ExtractorAssignment[]> {
    const assignments: ExtractorAssignment[] = [];

    // Process explicitly assigned extractors
    if (urlMapping.extractorIds && urlMapping.extractorIds.length > 0) {
      for (const extractorId of urlMapping.extractorIds) {
        const extractor = this.extractors.find(e => e.id === extractorId);
        if (!extractor) {
          throw new URLMappingIntegrationError(
            `Extractor not found: ${extractorId}`,
            'EXTRACTOR_NOT_FOUND',
            { extractorId, urlMappingId: urlMapping.id }
          );
        }

        assignments.push({
          extractorId,
          extractorName: extractor.name,
          urls: this.buildTargetUrlsList(urlMapping),
          confidence: 1.0, // Explicitly assigned = high confidence
          reason: 'Explicitly assigned in URL mapping'
        });
      }
    } else {
      // Auto-assign extractors based on URL patterns and content type
      const autoAssignments = await this.autoAssignExtractors(urlMapping);
      assignments.push(...autoAssignments);
    }

    return assignments;
  }

  /**
   * Build list of target URLs from mapping configuration
   * Supports both single URL from URLConfig and multiple URLs from URLMappingConfig
   * @param urlMapping - URL mapping configuration
   * @param urlConfig - Optional URL configuration profile
   * @returns Array of target URLs
   */
  private buildTargetUrlsList(urlMapping: URLMapping, urlConfig?: URLConfig): string[] {
    const urls: string[] = [];

    // Handle both frontend (pattern) and backend (urls array) formats
    const mappingUrls = (urlMapping as any).urls || [urlMapping.pattern].filter(Boolean);
    urls.push(...mappingUrls);

    // Add URL from config if not already included
    if (urlConfig?.base_url && !urls.includes(urlConfig.base_url)) {
      urls.push(urlConfig.base_url);
    }

    // Validate URLs
    const validUrls = urls.filter(url => this.isValidUrl(url));
    
    if (validUrls.length === 0) {
      throw new URLMappingIntegrationError(
        'No valid URLs found in mapping configuration',
        'VALIDATION_ERROR',
        { urlMapping, urlConfig }
      );
    }

    return validUrls;
  }

  /**
   * Auto-assign extractors based on URL patterns and heuristics
   * @param urlMapping - URL mapping configuration
   * @returns Array of auto-assigned extractors
   */
  private async autoAssignExtractors(urlMapping: URLMapping): Promise<ExtractorAssignment[]> {
    const assignments: ExtractorAssignment[] = [];
    const targetUrls = this.buildTargetUrlsList(urlMapping);

    // Simple heuristic-based assignment
    // In a real implementation, this could use ML or pattern matching
    for (const url of targetUrls) {
      const domain = new URL(url).hostname;
      
      // Find extractors that match domain patterns or are generic
      const matchingExtractors = this.extractors.filter(extractor => {
        // Check if extractor name or description mentions the domain
        const extractorText = `${extractor.name} ${extractor.description || ''}`.toLowerCase();
        const domainParts = domain.split('.');
        
        return domainParts.some(part => extractorText.includes(part)) ||
               extractor.name.toLowerCase().includes('generic') ||
               extractor.name.toLowerCase().includes('universal');
      });

      if (matchingExtractors.length > 0) {
        // Use the first matching extractor
        const extractor = matchingExtractors[0];
        assignments.push({
          extractorId: extractor.id,
          extractorName: extractor.name,
          urls: [url],
          confidence: 0.7, // Auto-assigned = medium confidence
          reason: `Auto-assigned based on domain pattern: ${domain}`
        });
      }
    }

    // Fallback to generic extractor if no matches found
    if (assignments.length === 0) {
      const genericExtractor = this.extractors.find(e => 
        e.name.toLowerCase().includes('generic') || 
        e.name.toLowerCase().includes('universal')
      );
      
      if (genericExtractor) {
        assignments.push({
          extractorId: genericExtractor.id,
          extractorName: genericExtractor.name,
          urls: targetUrls,
          confidence: 0.5, // Fallback = low confidence
          reason: 'Fallback to generic extractor'
        });
      }
    }

    return assignments;
  }

  /**
   * Determine optimal crawler type based on URL complexity and extractors
   * @param urlConfig - URL configuration profile
   * @param extractorAssignments - Assigned extractors
   * @returns Recommended crawler type
   */
  private determineCrawlerType(
    urlConfig?: URLConfig,
    extractorAssignments: ExtractorAssignment[] = []
  ): 'basic' | 'llm' | 'composite' {
    // Check if any extractors require LLM
    const hasLLMExtractor = extractorAssignments.some(assignment => 
      assignment.extractorName.toLowerCase().includes('llm') ||
      assignment.extractorName.toLowerCase().includes('ai')
    );

    if (hasLLMExtractor) {
      return 'llm';
    }

    // Check URL complexity
    if (urlConfig?.scraping_difficulty === 'hard' || extractorAssignments.length > 2) {
      return 'composite';
    }

    return 'basic';
  }

  /**
   * Generate LLM configuration for LLM-based crawlers
   * @param urlConfig - URL configuration profile
   * @param extractorAssignments - Assigned extractors
   * @returns LLM configuration object
   */
  private generateLLMConfig(
    urlConfig?: URLConfig,
    extractorAssignments: ExtractorAssignment[] = []
  ) {
    return {
      provider: 'openai',
      model: 'gpt-4',
      prompt: `Extract structured data from ${urlConfig?.name || 'web page'}. Focus on: ${urlConfig?.metadata?.tags?.join(', ') || 'relevant content'}.`
    };
  }

  /**
   * Generate human-readable description for the crawler
   * @param urlMapping - URL mapping configuration
   * @param urlConfig - URL configuration profile
   * @param extractorAssignments - Assigned extractors
   * @returns Generated description
   */
  private generateCrawlerDescription(
    urlMapping: URLMapping,
    urlConfig?: URLConfig,
    extractorAssignments: ExtractorAssignment[] = []
  ): string {
    const extractorNames = extractorAssignments.map(a => a.extractorName).join(', ');
    const urlCount = this.buildTargetUrlsList(urlMapping, urlConfig).length;
    
    // Handle both frontend (pattern) and backend (urls array) formats
    const mappingUrls = (urlMapping as any).urls || [urlMapping.pattern].filter(Boolean);
    const primaryUrl = mappingUrls[0] || 'web scraping';
    
    return `Auto-generated crawler for ${urlConfig?.name || primaryUrl} ` +
           `targeting ${urlCount} URL${urlCount > 1 ? 's' : ''} ` +
           `using extractors: ${extractorNames || 'auto-assigned'}.`;
  }

  /**
   * Apply crawler-specific requirements to the blueprint
   * @param blueprint - Crawler configuration blueprint to modify
   * @param requirements - Crawler requirements to apply
   */
  private applyCrawlerRequirements(
    blueprint: CrawlerConfigurationBlueprint,
    requirements: Partial<CrawlerConfig>
  ): void {
    if (requirements.name) blueprint.name = requirements.name;
    if (requirements.description) blueprint.description = requirements.description;
    if (requirements.config) {
      blueprint.config = { ...blueprint.config, ...requirements.config };
    }
  }

  /**
   * Map difficulty string to standardized levels
   * @param difficulty - Difficulty string from URL config
   * @returns Standardized difficulty level
   */
  private mapDifficultyLevel(difficulty: string): 'easy' | 'medium' | 'hard' {
    const normalized = difficulty.toLowerCase();
    if (normalized.includes('easy') || normalized.includes('low')) return 'easy';
    if (normalized.includes('hard') || normalized.includes('high') || normalized.includes('difficult')) return 'hard';
    return 'medium';
  }

  /**
   * Validate URL format
   * @param url - URL string to validate
   * @returns True if URL is valid
   */
  private isValidUrl(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Update service data sources
   * @param urlMappings - Updated URL mappings
   * @param urlConfigs - Updated URL configs
   * @param extractors - Updated extractors
   */
  public updateDataSources(
    urlMappings: URLMapping[],
    urlConfigs: URLConfig[],
    extractors: ExtractorStrategy[]
  ): void {
    this.urlMappings = urlMappings;
    this.urlConfigs = urlConfigs;
    this.extractors = extractors;
  }

  /**
   * Get service statistics for monitoring
   * @returns Service statistics object
   */
  public getServiceStats() {
    return {
      urlMappingsCount: this.urlMappings.length,
      urlConfigsCount: this.urlConfigs.length,
      extractorsCount: this.extractors.length,
      totalUrls: this.urlMappings.length
    };
  }
}

/**
 * Factory function to create a new URLMappingIntegrationService instance
 * 
 * @param urlMappings - Available URL mapping configurations
 * @param urlConfigs - Pre-configured URL profiles  
 * @param extractors - Available extraction strategies
 * @returns Configured URLMappingIntegrationService instance
 */
export function createURLMappingIntegrationService(
  urlMappings: URLMapping[],
  urlConfigs: URLConfig[],
  extractors: ExtractorStrategy[]
): URLMappingIntegrationService {
  return new URLMappingIntegrationService(urlMappings, urlConfigs, extractors);
}