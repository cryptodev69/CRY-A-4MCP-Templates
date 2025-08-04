export interface URLMapping {
  id: string;
  name: string;
  url: string;
  url_config_id?: string;
  extractor_id: string;
  priority?: number;
  rate_limit?: number;
  config?: string; // JSON string - Extractor-specific configuration
  validation_rules?: string; // JSON string - Technical validation rules
  crawler_settings?: string; // JSON string - Crawler-specific settings
  is_active?: boolean;
  metadata?: string; // JSON string - Technical metadata
  created_at: string;
  updated_at: string;
  // Additional properties expected by crawlApi
  extractionCount: number;
  successRate: number;
  averageResponseTime: number;
  lastError?: string;
  createdAt?: Date;
  lastExtracted?: Date;
}



export interface Extractor {
  id: string;
  name: string;
  description: string;
  schema?: string;
  file_path?: string;
  config?: ExtractorConfig;
  isActive?: boolean;
  createdAt?: Date;
  updatedAt?: Date | string;
  version?: string;
  tags?: string[];
  author?: string;
  usageCount?: number;
  successRate?: number;
}

export interface ExtractorConfig {
  selectors?: Record<string, string>;
  waitConditions?: WaitCondition[];
  customHeaders?: Record<string, string>;
  timeout?: number;
  retryAttempts?: number;
  outputFormat?: 'json' | 'xml' | 'csv';
  postProcessing?: PostProcessingRule[];
  // LLM Strategy specific fields
  schema?: Record<string, any>;
  instruction?: string;
  default_provider?: string;
}

export interface WaitCondition {
  type: 'element' | 'network' | 'timeout';
  selector?: string;
  timeout: number;
}

export interface PostProcessingRule {
  field: string;
  operation: 'trim' | 'lowercase' | 'uppercase' | 'regex' | 'date_format';
  parameters?: Record<string, any>;
}

export interface ExtractionResult {
  id: string;
  mappingId: string;
  extractedData: Record<string, any>;
  timestamp: Date;
  success: boolean;
  error?: string;
  responseTime: number;
  metadata: {
    userAgent: string;
    ipAddress: string;
    extractorVersion: string;
  };
}

export interface TestResult {
  url: string;
  extractorId: string;
  success: boolean;
  data?: Record<string, any>;
  error?: string;
  responseTime: number;
  timestamp: Date;
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
}

export interface DashboardStats {
  totalMappings: number;
  activeMappings: number;
  totalExtractions: number;
  successRate: number;
  averageResponseTime: number;
  recentExtractions: ExtractionResult[];
}

export interface AnalyticsData {
  extractionTrends: {
    date: string;
    count: number;
    successRate: number;
  }[];
  topPerformingExtractors: {
    extractorId: string;
    name: string;
    successRate: number;
    usageCount: number;
  }[];
  errorDistribution: {
    errorType: string;
    count: number;
    percentage: number;
  }[];
  responseTimeMetrics: {
    average: number;
    median: number;
    p95: number;
    p99: number;
  };
}