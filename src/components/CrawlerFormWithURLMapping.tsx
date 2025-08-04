/**
 * CrawlerFormWithURLMapping Component
 * 
 * Enhanced crawler creation form that integrates URL mapping selection
 * with automatic configuration inheritance. This component extends the
 * basic crawler form by providing intelligent defaults based on selected
 * URL mappings and their associated metadata.
 * 
 * Key Features:
 * - URL mapping dropdown with search and filtering
 * - Automatic configuration inheritance from URL mappings
 * - Real-time preview of inherited settings
 * - Manual override capabilities for all auto-configured values
 * - Validation and error handling
 * - Support for both manual and mapping-based crawler creation
 * 
 * Integration Flow:
 * 1. User selects URL mapping from dropdown
 * 2. System generates crawler configuration blueprint
 * 3. Form fields are auto-populated with inherited settings
 * 4. User can review and modify any auto-configured values
 * 5. Final crawler configuration is created with combined settings
 * 
 * @component CrawlerFormWithURLMapping
 * @requires URLMappingDropdown, URLMappingIntegrationService
 */

import React, { useState, useEffect } from 'react';
import { X, Settings, Brain, Globe, Zap, AlertCircle, CheckCircle, Info, RefreshCw } from 'lucide-react';
import URLMappingDropdown from './URLMappingDropdown';
import { URLMapping, CrawlerConfig } from '../services/crawlApi';
import { CrawlerConfigurationBlueprint, ExtractorStrategy } from '../services/URLMappingIntegrationService';

/**
 * Form data interface for crawler creation
 */
interface CrawlerFormData {
  name: string;
  description: string;
  crawlerType: 'basic' | 'llm' | 'composite';
  config: {
    timeout: number;
    maxRetries: number;
    concurrentLimit: number;
    extractionTimeout: number;
    headless: boolean;
    verbose: boolean;
  };
  llmConfig?: {
    provider: string;
    model: string;
    temperature: number;
    systemPrompt: string;
  };
  urlMappingId?: string;
  extractionStrategies?: string[];
  targetUrls?: string[];
}

/**
 * Props interface for CrawlerFormWithURLMapping
 */
interface CrawlerFormWithURLMappingProps {
  /** Whether the modal is open */
  isOpen: boolean;
  
  /** Function to close the modal */
  onClose: () => void;
  
  /** Function to handle crawler creation */
  onSubmit: (formData: CrawlerFormData) => void;
  
  /** Available URL mappings */
  urlMappings: URLMapping[];
  
  /** Available extractors */
  extractors: ExtractorStrategy[];
  
  /** Initial form data for editing */
  initialData?: Partial<CrawlerFormData>;
  
  /** Whether this is an edit operation */
  isEdit?: boolean;
}

/**
 * CrawlerFormWithURLMapping Component
 * 
 * Provides an enhanced form interface for creating crawlers with
 * intelligent URL mapping integration and configuration inheritance.
 */
const CrawlerFormWithURLMapping: React.FC<CrawlerFormWithURLMappingProps> = ({
  isOpen,
  onClose,
  onSubmit,
  urlMappings,
  extractors,
  initialData,
  isEdit = false
}) => {
  // Form state
  const [formData, setFormData] = useState<CrawlerFormData>({
    name: '',
    description: '',
    crawlerType: 'basic',
    config: {
      timeout: 30,
      maxRetries: 3,
      concurrentLimit: 5,
      extractionTimeout: 60,
      headless: true,
      verbose: false
    },
    llmConfig: {
      provider: 'openai',
      model: 'gpt-4',
      temperature: 0.7,
      systemPrompt: 'Extract structured data from the provided HTML content.'
    }
  });

  // UI state
  const [selectedMappingId, setSelectedMappingId] = useState<string>('');
  const [inheritedBlueprint, setInheritedBlueprint] = useState<CrawlerConfigurationBlueprint | null>(null);
  const [showInheritedSettings, setShowInheritedSettings] = useState(false);
  const [isAutoConfigured, setIsAutoConfigured] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  /**
   * Reset form state when modal closes to prevent state sharing between instances
   * Only reset when transitioning from open to closed, not during form submission
   */
  const [wasOpen, setWasOpen] = useState(false);
  
  useEffect(() => {
    if (isOpen && !wasOpen) {
      // Modal is opening - track state but don't reset
      setWasOpen(true);
    } else if (!isOpen && wasOpen) {
      // Modal is closing - reset all state only for new crawler creation
      setWasOpen(false);
      
      if (!isEdit) {
        // Only reset state for new crawler creation, not editing
        setSelectedMappingId('');
        setInheritedBlueprint(null);
        setShowInheritedSettings(false);
        setIsAutoConfigured(false);
        setValidationErrors({});
        
        setFormData({
          name: '',
          description: '',
          crawlerType: 'basic',
          config: {
            timeout: 30,
            maxRetries: 3,
            concurrentLimit: 5,
            extractionTimeout: 60,
            headless: true,
            verbose: false
          },
          llmConfig: {
            provider: 'openai',
            model: 'gpt-4',
            temperature: 0.7,
            systemPrompt: 'Extract structured data from the provided HTML content.'
          }
        });
      }
    }
  }, [isOpen, wasOpen, isEdit]);

  /**
   * Initialize form data and URL mapping selection when editing
   */
  useEffect(() => {
    if (initialData) {
      // Always set form data first
      setFormData(prev => ({ ...prev, ...initialData }));
      
      // Handle URL mapping selection only when we have both initialData and urlMappings
      if (initialData.urlMappingId && urlMappings.length > 0) {
        const selectedMapping = urlMappings.find(mapping => mapping.id === initialData.urlMappingId);
        if (selectedMapping) {
          console.log('CrawlerForm - Setting selectedMappingId for editing:', initialData.urlMappingId);
          // Set the selected mapping ID to ensure dropdown shows correct selection
          setSelectedMappingId(initialData.urlMappingId);
          
          // Create a blueprint from the selected mapping
          const blueprint: CrawlerConfigurationBlueprint = {
            id: selectedMapping.id,
            name: initialData.name || '',
            description: initialData.description || '',
            crawlerType: initialData.crawlerType || 'basic',
            config: {
              timeout: (initialData.config?.timeout || 30) * 1000, // Convert to milliseconds
              retries: initialData.config?.maxRetries || 3,
              concurrency: initialData.config?.concurrentLimit || 5
            },
            llmConfig: initialData.llmConfig ? {
              provider: initialData.llmConfig.provider,
              model: initialData.llmConfig.model,
              prompt: initialData.llmConfig.systemPrompt
            } : undefined,
            extractionStrategies: selectedMapping.extractorIds || [],
            urlMappingIds: [selectedMapping.id],
            priority: 1,
            targetUrls: initialData.targetUrls || (selectedMapping.pattern ? [selectedMapping.pattern] : [])
          };
          
          setInheritedBlueprint(blueprint);
          setIsAutoConfigured(true);
          setShowInheritedSettings(false); // Don't show by default when editing
        } else {
          console.log('CrawlerForm - URL mapping not found for ID:', initialData.urlMappingId);
        }
      } else if (initialData.urlMappingId && urlMappings.length === 0) {
        console.log('CrawlerForm - URL mappings not loaded yet, will retry when available');
        // Set the ID anyway so it's ready when options load
        setSelectedMappingId(initialData.urlMappingId);
      }
    }
  }, [initialData, urlMappings]);

  /**
   * Handle URL mapping selection and configuration inheritance
   */
  const handleMappingSelect = (mappingId: string, blueprint: CrawlerConfigurationBlueprint) => {
    setSelectedMappingId(mappingId);
    setInheritedBlueprint(blueprint);
    setIsAutoConfigured(true);
    setShowInheritedSettings(true);

    // Apply inherited configuration to form
    setFormData(prev => {
      const newFormData: CrawlerFormData = {
        name: blueprint.name,
        description: blueprint.description,
        crawlerType: blueprint.crawlerType,
        config: {
          timeout: blueprint.config.timeout / 1000, // Convert to seconds for UI
          maxRetries: blueprint.config.retries,
          concurrentLimit: blueprint.config.concurrency,
          extractionTimeout: prev.config.extractionTimeout,
          headless: prev.config.headless,
          verbose: prev.config.verbose
        },
        llmConfig: blueprint.llmConfig ? {
           provider: blueprint.llmConfig.provider,
           model: blueprint.llmConfig.model,
           temperature: ('temperature' in blueprint.llmConfig ? blueprint.llmConfig.temperature : 0.7) as number,
           systemPrompt: ('systemPrompt' in blueprint.llmConfig ? blueprint.llmConfig.systemPrompt : ('prompt' in blueprint.llmConfig ? blueprint.llmConfig.prompt : '')) as string
         } : prev.llmConfig,
        urlMappingId: mappingId,
        targetUrls: blueprint.targetUrls
      };
      return newFormData;
    });

    // Clear validation errors
    setValidationErrors({});
  };

  /**
   * Handle clearing URL mapping selection
   */
  const handleMappingClear = () => {
    setSelectedMappingId('');
    setInheritedBlueprint(null);
    setIsAutoConfigured(false);
    setShowInheritedSettings(false);
    
    // Reset form to defaults
    setFormData(prev => ({
      ...prev,
      name: '',
      description: '',
      crawlerType: 'basic',
      urlMappingId: undefined,
      targetUrls: undefined
    }));
  };

  /**
   * Validate form data
   */
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) {
      errors.name = 'Crawler name is required';
    }

    if (!formData.description.trim()) {
      errors.description = 'Description is required';
    }

    if (formData.config.timeout < 5) {
      errors.timeout = 'Timeout must be at least 5 seconds';
    }

    if (formData.config.maxRetries < 0) {
      errors.maxRetries = 'Max retries cannot be negative';
    }

    if (formData.config.concurrentLimit < 1) {
      errors.concurrentLimit = 'Concurrent limit must be at least 1';
    }

    if ((formData.crawlerType === 'llm' || formData.crawlerType === 'composite') && formData.llmConfig) {
      if (!formData.llmConfig.model.trim()) {
        errors.llmModel = 'LLM model is required';
      }
      if (!formData.llmConfig.systemPrompt.trim()) {
        errors.systemPrompt = 'System prompt is required';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      // Prepare crawler data with proper field mapping for backend compatibility
      const crawlerData = {
        ...formData,
        target_urls: formData.targetUrls, // Backend compatibility
        url_mapping_id: selectedMappingId || null,
        url_mapping_ids: selectedMappingId ? [selectedMappingId] : [],
        urlMappingIds: selectedMappingId ? [selectedMappingId] : []
      };
      onSubmit(crawlerData);
    }
  };

  /**
   * Handle form reset
   */
  const handleReset = () => {
    handleMappingClear();
    setValidationErrors({});
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-600">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {isEdit ? 'Edit Crawler' : 'Create New Crawler'}
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mt-1">
              {isAutoConfigured ? 'Auto-configured from URL mapping' : 'Configure your web crawler settings'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          <form id="crawler-form" onSubmit={handleSubmit} className="p-6 space-y-8">
            {/* URL Mapping Selection */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Globe className="w-6 h-6 text-indigo-600" />
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">URL Mapping Integration</h3>
                </div>
                {isAutoConfigured && (
                  <button
                    type="button"
                    onClick={() => setShowInheritedSettings(!showInheritedSettings)}
                    className="flex items-center gap-2 px-3 py-1 text-sm text-indigo-600 hover:text-indigo-700 transition-colors"
                  >
                    <Info className="w-4 h-4" />
                    {showInheritedSettings ? 'Hide' : 'Show'} Inherited Settings
                  </button>
                )}
              </div>
              
              <URLMappingDropdown
                urlMappings={urlMappings}
                extractors={extractors}
                selectedMappingId={selectedMappingId}
                onMappingSelect={handleMappingSelect}
                onClear={handleMappingClear}
                placeholder="Select a URL mapping to auto-configure crawler settings..."
                className="w-full"
              />

              {/* Inherited Settings Preview */}
              {showInheritedSettings && inheritedBlueprint && (
                <div className="mt-4 p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl border border-indigo-200 dark:border-indigo-700">
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircle className="w-5 h-5 text-indigo-600" />
                    <h4 className="font-medium text-indigo-900 dark:text-indigo-100">Inherited Configuration</h4>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-indigo-600 dark:text-indigo-400 font-medium">Type:</span>
                      <span className="ml-2 text-gray-700 dark:text-gray-300">{inheritedBlueprint.crawlerType}</span>
                    </div>
                    <div>
                      <span className="text-indigo-600 dark:text-indigo-400 font-medium">Timeout:</span>
                      <span className="ml-2 text-gray-700 dark:text-gray-300">{inheritedBlueprint.config.timeout / 1000}s</span>
                    </div>
                    <div>
                      <span className="text-indigo-600 dark:text-indigo-400 font-medium">Retries:</span>
                      <span className="ml-2 text-gray-700 dark:text-gray-300">{inheritedBlueprint.config.retries}</span>
                    </div>
                    <div>
                      <span className="text-indigo-600 dark:text-indigo-400 font-medium">Concurrency:</span>
                      <span className="ml-2 text-gray-700 dark:text-gray-300">{inheritedBlueprint.config.concurrency}</span>
                    </div>
                  </div>
                  {inheritedBlueprint.targetUrls && inheritedBlueprint.targetUrls.length > 0 && (
                    <div className="mt-3">
                      <span className="text-indigo-600 dark:text-indigo-400 font-medium">Target URLs:</span>
                      <div className="mt-1 space-y-1">
                        {inheritedBlueprint.targetUrls.map((url, index) => (
                          <div key={index} className="text-sm text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-800 px-2 py-1 rounded">
                            {url}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Basic Configuration */}
            <div className="space-y-6">
              <div className="flex items-center gap-3 pb-4 border-b border-gray-200 dark:border-gray-600">
                <Settings className="w-6 h-6 text-purple-600" />
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Basic Configuration</h3>
                {isAutoConfigured && (
                  <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                    Auto-configured
                  </span>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Crawler Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      validationErrors.name ? 'border-red-300' : 'border-gray-200 dark:border-gray-600'
                    }`}
                    placeholder="Enter crawler name"
                  />
                  {validationErrors.name && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.name}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Crawler Type
                  </label>
                  <select
                    value={formData.crawlerType}
                    onChange={(e) => setFormData({ ...formData, crawlerType: e.target.value as 'basic' | 'llm' | 'composite' })}
                    className="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="basic">Basic Crawler - Simple HTML extraction</option>
                    <option value="llm">LLM-Powered Crawler - AI-enhanced extraction</option>
                    <option value="composite">Composite Crawler - Multi-strategy approach</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Description *
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                    validationErrors.description ? 'border-red-300' : 'border-gray-200 dark:border-gray-600'
                  }`}
                  rows={3}
                  placeholder="Describe the purpose and scope of this crawler"
                />
                {validationErrors.description && (
                  <p className="mt-1 text-sm text-red-600">{validationErrors.description}</p>
                )}
              </div>
            </div>

            {/* Advanced Configuration */}
            <div className="space-y-6">
              <div className="flex items-center gap-3 pb-4 border-b border-gray-200 dark:border-gray-600">
                <Zap className="w-6 h-6 text-purple-600" />
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Advanced Configuration</h3>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Timeout (seconds)
                  </label>
                  <input
                    type="number"
                    value={formData.config.timeout}
                    onChange={(e) => setFormData({ 
                      ...formData, 
                      config: { ...formData.config, timeout: parseInt(e.target.value) }
                    })}
                    className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      validationErrors.timeout ? 'border-red-300' : 'border-gray-200 dark:border-gray-600'
                    }`}
                  />
                  {validationErrors.timeout && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.timeout}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Max Retries
                  </label>
                  <input
                    type="number"
                    value={formData.config.maxRetries}
                    onChange={(e) => setFormData({ 
                      ...formData, 
                      config: { ...formData.config, maxRetries: parseInt(e.target.value) }
                    })}
                    className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      validationErrors.maxRetries ? 'border-red-300' : 'border-gray-200 dark:border-gray-600'
                    }`}
                  />
                  {validationErrors.maxRetries && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.maxRetries}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Concurrent Limit
                  </label>
                  <input
                    type="number"
                    value={formData.config.concurrentLimit}
                    onChange={(e) => setFormData({ 
                      ...formData, 
                      config: { ...formData.config, concurrentLimit: parseInt(e.target.value) }
                    })}
                    className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      validationErrors.concurrentLimit ? 'border-red-300' : 'border-gray-200 dark:border-gray-600'
                    }`}
                  />
                  {validationErrors.concurrentLimit && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.concurrentLimit}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Extraction Timeout
                  </label>
                  <input
                    type="number"
                    value={formData.config.extractionTimeout}
                    onChange={(e) => setFormData({ 
                      ...formData, 
                      config: { ...formData.config, extractionTimeout: parseInt(e.target.value) }
                    })}
                    className="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              <div className="flex items-center gap-6">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.config.headless}
                    onChange={(e) => setFormData({ 
                      ...formData, 
                      config: { ...formData.config, headless: e.target.checked }
                    })}
                    className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Headless Mode</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.config.verbose}
                    onChange={(e) => setFormData({ 
                      ...formData, 
                      config: { ...formData.config, verbose: e.target.checked }
                    })}
                    className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Verbose Logging</span>
                </label>
              </div>
            </div>

            {/* LLM Configuration */}
            {(formData.crawlerType === 'llm' || formData.crawlerType === 'composite') && (
              <div className="space-y-6">
                <div className="flex items-center gap-3 pb-4 border-b border-gray-200 dark:border-gray-600">
                  <Brain className="w-6 h-6 text-purple-600" />
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">LLM Configuration</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Provider
                    </label>
                    <select
                      value={formData.llmConfig?.provider || 'openai'}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        llmConfig: { ...formData.llmConfig!, provider: e.target.value }
                      })}
                      className="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="openai">OpenAI</option>
                      <option value="anthropic">Anthropic</option>
                      <option value="openrouter">OpenRouter</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Model
                    </label>
                    <input
                      type="text"
                      value={formData.llmConfig?.model || ''}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        llmConfig: { ...formData.llmConfig!, model: e.target.value }
                      })}
                      className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                        validationErrors.llmModel ? 'border-red-300' : 'border-gray-200 dark:border-gray-600'
                      }`}
                      placeholder="gpt-4"
                    />
                    {validationErrors.llmModel && (
                      <p className="mt-1 text-sm text-red-600">{validationErrors.llmModel}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Temperature
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      max="2"
                      value={formData.llmConfig?.temperature || 0.7}
                      onChange={(e) => setFormData({ 
                        ...formData, 
                        llmConfig: { ...formData.llmConfig!, temperature: parseFloat(e.target.value) }
                      })}
                      className="w-full px-4 py-3 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    System Prompt
                  </label>
                  <textarea
                    value={formData.llmConfig?.systemPrompt || ''}
                    onChange={(e) => setFormData({ 
                      ...formData, 
                      llmConfig: { ...formData.llmConfig!, systemPrompt: e.target.value }
                    })}
                    className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      validationErrors.systemPrompt ? 'border-red-300' : 'border-gray-200 dark:border-gray-600'
                    }`}
                    rows={3}
                    placeholder="Enter system prompt for LLM extraction"
                  />
                  {validationErrors.systemPrompt && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.systemPrompt}</p>
                  )}
                </div>
              </div>
            )}
          </form>
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 flex justify-between items-center p-6 border-t border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700">
          <div className="flex items-center gap-4">
            {isAutoConfigured && (
              <div className="flex items-center gap-2 text-sm text-green-600">
                <CheckCircle className="w-4 h-4" />
                <span>Auto-configured from URL mapping</span>
              </div>
            )}
            <button
              type="button"
              onClick={handleReset}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Reset
            </button>
          </div>
          <div className="flex gap-4">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-600 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-500 transition-all duration-200 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              form="crawler-form"
              className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 font-medium shadow-lg hover:shadow-xl"
            >
              {isEdit ? 'Save Changes' : 'Create Crawler'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CrawlerFormWithURLMapping;
export type { CrawlerFormWithURLMappingProps, CrawlerFormData };