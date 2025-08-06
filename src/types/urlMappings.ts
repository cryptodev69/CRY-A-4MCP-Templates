// Frontend types for URL mappings functionality

export interface URLConfig {
  id: string;
  name: string;
  url: string;
  baseUrl: string;
  profileType: string;
  category: string;
  description?: string;
  priority: number;
  scrapingDifficulty: number;
  hasOfficialApi: boolean;
  hasOfficialAPI: boolean;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface URLMappingDisplay {
  id: string;
  name: string;
  configurationId: string;
  extractorId?: string; // Legacy single extractor support
  extractorIds?: string[]; // Multiple extractors support
  rateLimit: number;
  priority: number;
  crawlerSettings: Record<string, any>;
  validationRules: Record<string, any>;
  isActive: boolean;
  url: string;
  config: Record<string, any>;
  extractionCount: number;
  successRate: number;
  lastExtracted: string | null;
  created_at: string;
  updated_at: string;
  tags?: string[];
  notes?: string;
  category?: string;
  metadata?: Record<string, any>;
  configuration?: URLConfig;
}

export interface Extractor {
  id: string;
  name: string;
  type: string;
  description: string;
  version?: string;
  supportedDomains?: string[];
  configSchema?: Record<string, any>;
  isActive: boolean;
}

export interface URLMappingFormData {
  name: string;
  configurationId: string | null;
  extractorId?: string | null; // Legacy single extractor support
  extractorIds: string[]; // Multiple extractors support
  rateLimit: number;
  priority: number;
  crawlerSettings: string;
  validationRules: string;
  isActive: boolean;
  metadata: string;
  tags: string[];
  notes: string;
  category: string;
}

export interface URLMappingCreateRequest {
  url_config_id: string;
  extractor_ids: string[];
  rate_limit: number;
  priority?: number;
  crawler_settings?: Record<string, any>;
  validation_rules?: Record<string, any>;
  is_active: boolean;
  name?: string;
  tags?: string[];
  notes?: string;
  category?: string;
}

export interface URLMappingUpdateRequest {
  url_config_id?: string;
  extractor_ids?: string[];
  rate_limit?: number;
  priority?: number;
  crawler_settings?: Record<string, any>;
  validation_rules?: Record<string, any>;
  is_active?: boolean;
  name?: string;
  tags?: string[];
  notes?: string;
  category?: string;
}