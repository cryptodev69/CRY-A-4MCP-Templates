import React, { useState, useEffect, useCallback } from 'react';
import { TestTube, Play, CheckCircle, XCircle, Clock, Brain, Search } from 'lucide-react';
import { TestResult } from '../types/models';
import { openRouterService, OpenRouterModel } from '../services/openRouterService';
import { extractorsService, Extractor } from '../services/extractorsService';
import { API_BASE_URL } from '../config/api';

interface LLMTestResult {
  success: boolean;
  data?: {
    title?: string;
    content?: string;
    markdown?: string;
    llm_extraction?: any;
    metadata?: any;
  };
  error?: string;
  response_time?: number;
  timestamp?: string;
}

function TestURL() {
  const [url, setUrl] = useState('');
  const [extractorId, setExtractorId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<TestResult | null>(null);
  
  // Extractors state
  const [extractors, setExtractors] = useState<Extractor[]>([]);
  const [loadingExtractors, setLoadingExtractors] = useState(false);
  const [extractorsError, setExtractorsError] = useState<string | null>(null);
  
  // LLM Configuration
  const [useLLM, setUseLLM] = useState(false);
  const [selectedLLMExtractor, setSelectedLLMExtractor] = useState('');
  const [llmProvider, setLlmProvider] = useState('openai');
  const [llmModel, setLlmModel] = useState('gpt-3.5-turbo');
  const [llmApiKey, setLlmApiKey] = useState('');
  const [llmTemperature, setLlmTemperature] = useState(0.7);
  const [llmMaxTokens, setLlmMaxTokens] = useState(1000);
  const [llmTimeout, setLlmTimeout] = useState(30);
  const [llmInstruction, setLlmInstruction] = useState('Extract the main content and key information from this webpage.');
  const [llmSchema, setLlmSchema] = useState('');
  const [llmResult, setLlmResult] = useState<LLMTestResult | null>(null);
  
  // OpenRouter specific states
  const [openRouterModels, setOpenRouterModels] = useState<OpenRouterModel[]>([]);
  const [modelSearchQuery, setModelSearchQuery] = useState('');
  const [loadingModels, setLoadingModels] = useState(false);
  const [showModelDropdown, setShowModelDropdown] = useState(false);

  // Filter LLM extractors (those with schema and description)
  const llmExtractors = extractorsService.getLLMExtractors(extractors);

  // Load extractors function
  const loadExtractors = async () => {
    setLoadingExtractors(true);
    setExtractorsError(null);
    try {
      const response = await extractorsService.fetchExtractors();
      if (response.success) {
        setExtractors(response.extractors);
      } else {
        setExtractorsError(response.message || 'Failed to load extractors');
      }
    } catch (error) {
      setExtractorsError('Error loading extractors');
      console.error('Error loading extractors:', error);
    } finally {
      setLoadingExtractors(false);
    }
  };

  // Load extractors on component mount
  useEffect(() => {
    loadExtractors();
  }, []);
  
  // Load API keys from localStorage on component mount
  useEffect(() => {
    const storedApiKeys = localStorage.getItem('apiKeys');
    if (storedApiKeys) {
      try {
        const apiKeys = JSON.parse(storedApiKeys);
        const providerKey = apiKeys.find((key: any) => key.provider === llmProvider);
        if (providerKey) {
          setLlmApiKey(providerKey.apiKey);
        }
      } catch (error) {
        console.error('Failed to load API keys:', error);
      }
    }
  }, [llmProvider]);
  
  // Load OpenRouter models when provider changes to OpenRouter
  // Load OpenRouter models function
  const loadOpenRouterModels = useCallback(async () => {
    if (!llmApiKey) {
      console.warn('OpenRouter API key is required');
      return;
    }
    
    setLoadingModels(true);
    try {
      const response = await openRouterService.getModels(llmApiKey, false);
      if (response.success) {
        setOpenRouterModels(response.models);
      } else {
        console.error('Failed to load OpenRouter models:', response.message);
      }
    } catch (error) {
      console.error('Error loading OpenRouter models:', error);
    } finally {
      setLoadingModels(false);
    }
  }, [llmApiKey]);
  
  useEffect(() => {
    if (llmProvider === 'openrouter') {
      loadOpenRouterModels();
    }
  }, [llmProvider, loadOpenRouterModels]);
  
  // Filter models based on search query
  const filteredModels = openRouterService.filterModels(openRouterModels, modelSearchQuery);
  
  // Handle provider change
  const handleProviderChange = (provider: string) => {
    setLlmProvider(provider);
    
    // Load stored API key for the selected provider
    const storedApiKeys = localStorage.getItem('apiKeys');
    if (storedApiKeys) {
      try {
        const apiKeys = JSON.parse(storedApiKeys);
        const providerKey = apiKeys.find((key: any) => key.provider === provider);
        if (providerKey) {
          setLlmApiKey(providerKey.apiKey);
        } else {
          setLlmApiKey('');
        }
      } catch (error) {
        console.error('Failed to load API key for provider:', error);
        setLlmApiKey('');
      }
    }
    
    // Reset model selection when changing providers
    if (provider === 'openrouter') {
      setLlmModel('');
    } else {
      // Set default models for other providers
      const defaultModels = {
        openai: 'gpt-3.5-turbo',
        anthropic: 'claude-3-haiku-20240307',
        google: 'gemini-pro'
      };
      setLlmModel(defaultModels[provider as keyof typeof defaultModels] || '');
    }
  };

  // Handle LLM extractor selection
  const handleLLMExtractorChange = async (extractorId: string) => {
    setSelectedLLMExtractor(extractorId);
    if (extractorId) {
      try {
        // Fetch detailed extractor information
        const response = await extractorsService.fetchExtractor(extractorId);
        if (response.success && response.extractor) {
          const extractor = response.extractor;
          
          // Auto-populate schema from selected extractor
          if (extractor.schema) {
            setLlmSchema(extractorsService.formatSchemaForDisplay(extractor.schema));
          }
          
          // Auto-populate instruction from extractor description
          const instruction = extractorsService.getInstructionFromExtractor(extractor);
          setLlmInstruction(instruction);
        }
      } catch (error) {
        console.error('Error fetching extractor details:', error);
      }
    } else {
      // Reset to defaults when no extractor is selected
      setLlmInstruction('Extract the main content and key information from this webpage.');
      setLlmSchema('');
    }
  };

  const handleTest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url || (!extractorId && !useLLM)) return;

    setIsLoading(true);
    setResult(null);
    setLlmResult(null);
    
    const startTime = Date.now();

    try {
      if (useLLM) {
        // Validate required fields before sending request
        if (!llmApiKey.trim()) {
          throw new Error('API key is required for LLM-based extraction');
        }
        if (!llmModel.trim()) {
          throw new Error('Model selection is required');
        }
        
        // Build request body for crawl4ai 0.7.0 API
        const requestBody: {
          url: string;
          llm_config: {
            provider: string;
            model: string;
            api_key: string;
            temperature: number;
            max_tokens: number;
            timeout: number;
          };
          instruction: string;
          schema?: any;
        } = {
          url: url,
          llm_config: {
            provider: llmProvider,
            model: llmModel,
            api_key: llmApiKey,
            temperature: llmTemperature,
            max_tokens: llmMaxTokens,
            timeout: llmTimeout
          },
          instruction: llmInstruction || 'Extract the main content and key information from this webpage.'
        };
        
        // Only include schema if it's not empty
        if (llmSchema && llmSchema.trim()) {
          try {
            // Validate JSON schema format
            JSON.parse(llmSchema);
            requestBody.schema = JSON.parse(llmSchema);
          } catch (e) {
            throw new Error('Invalid JSON format in schema field');
          }
        }
        
        console.log('Sending crawl4ai 0.7.0 request:', requestBody);
        
        const response = await fetch(`${API_BASE_URL}/api/test-url`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
          let errorMessage = `HTTP error! status: ${response.status}`;
          try {
            const errorData = await response.json();
            if (errorData.detail) {
              errorMessage = errorData.detail;
            }
          } catch (e) {
            // If we can't parse the error response, use the status text
            errorMessage = `HTTP ${response.status}: ${response.statusText}`;
          }
          throw new Error(errorMessage);
        }
        
        const llmTestResult = await response.json();
        const endTime = Date.now();
        
        // Handle crawl4ai 0.7.0 response format
        const processedResult = {
          success: llmTestResult.success !== undefined ? llmTestResult.success : !llmTestResult.error_message,
          data: llmTestResult.extraction_result || llmTestResult.data,
          error: llmTestResult.error_message || llmTestResult.error,
          response_time: endTime - startTime,
          timestamp: new Date().toISOString(),
          metadata: llmTestResult.metadata || {
            extractor_used: llmTestResult.extractor_used || 'LLM',
            model_used: llmModel,
            extraction_time_ms: endTime - startTime
          }
        };
        
        setLlmResult(processedResult);
      } else {
        // Test with existing extractor using crawl4ai 0.7.0 API
        const requestBody = {
          url: url,
          extractor_id: extractorId
        };
        
        const response = await fetch(`${API_BASE_URL}/api/test-url`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
          let errorMessage = `HTTP error! status: ${response.status}`;
          try {
            const errorData = await response.json();
            if (errorData.detail) {
              errorMessage = errorData.detail;
            }
          } catch (e) {
            errorMessage = `HTTP ${response.status}: ${response.statusText}`;
          }
          throw new Error(errorMessage);
        }
        
        const testResult = await response.json();
        const endTime = Date.now();
        
        // Convert to expected format
        const processedResult = {
          url: testResult.url || url,
          extractorId: testResult.extractor_used || extractorId,
          success: testResult.success !== undefined ? testResult.success : !testResult.error_message,
          data: testResult.extraction_result || testResult.data,
          error: testResult.error_message || testResult.error,
          responseTime: endTime - startTime,
          timestamp: new Date(),
          metadata: testResult.metadata || {
            extractor_used: testResult.extractor_used || extractorId,
            extraction_time_ms: endTime - startTime
          }
        };
        
        setResult(processedResult);
      }
    } catch (error) {
      console.error('Test failed:', error);
      if (useLLM) {
        setLlmResult({
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error occurred',
          response_time: 0,
          timestamp: new Date().toISOString()
        });
      } else {
        setResult({
          url,
          extractorId,
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error occurred',
          responseTime: 0,
          timestamp: new Date()
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const selectedExtractor = extractors.find(e => e.id === extractorId);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <TestTube className="w-8 h-8 text-purple-600 dark:text-purple-400" />
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white m-0">
          Test URL Extraction
        </h1>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <form onSubmit={handleTest} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              URL to Test
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/article"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
              required
            />
          </div>

          <div className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-md">
            <input
              type="checkbox"
              id="useLLM"
              checked={useLLM}
              onChange={(e) => setUseLLM(e.target.checked)}
              className="w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500 dark:focus:ring-purple-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
            />
            <label htmlFor="useLLM" className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
              <Brain className="w-4 h-4" />
              Use LLM-based Extraction
            </label>
          </div>

          {!useLLM && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Extractor
              </label>
              <select
                value={extractorId}
                onChange={(e) => setExtractorId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                required={!useLLM}
              >
                <option value="">Select an extractor</option>
                {extractors.map((extractor) => (
                  <option key={extractor.id} value={extractor.id}>
                    {extractor.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {useLLM && (
            <div className="space-y-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md">
              <h3 className="font-medium text-blue-900 dark:text-blue-300 mb-3">
                LLM Configuration
              </h3>
              
              {/* LLM Extractor Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  LLM Extractor (Optional)
                </label>
                <select
                  value={selectedLLMExtractor}
                  onChange={(e) => handleLLMExtractorChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                  disabled={loadingExtractors}
                >
                  <option value="">
                    {loadingExtractors ? 'Loading extractors...' : 'Select a pre-configured LLM extractor or configure manually'}
                  </option>
                  {llmExtractors.map((extractor) => (
                    <option key={extractor.id} value={extractor.id}>
                      {extractor.name}
                    </option>
                  ))}
                </select>
                {selectedLLMExtractor && (
                  <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                    Schema and instruction will be auto-populated from the selected extractor
                  </p>
                )}
                {loadingExtractors && (
                  <div className="flex items-center gap-2 mt-2 text-xs text-gray-500 dark:text-gray-400">
                    <div className="w-3 h-3 border border-gray-300 border-t-purple-600 rounded-full animate-spin"></div>
                    Loading available extractors...
                  </div>
                )}
                {extractorsError && (
                  <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-xs text-red-700 dark:text-red-300">
                    Error loading extractors: {extractorsError}
                  </div>
                )}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Provider
                  </label>
                  <select
                    value={llmProvider}
                    onChange={(e) => handleProviderChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                  >
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="google">Google</option>
                    <option value="openrouter">OpenRouter</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Model
                  </label>
                  {llmProvider === 'openrouter' ? (
                    <div className="relative">
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                        <input
                          type="text"
                          value={modelSearchQuery}
                          onChange={(e) => {
                            setModelSearchQuery(e.target.value);
                            setShowModelDropdown(true);
                          }}
                          onFocus={() => setShowModelDropdown(true)}
                          placeholder="Search models..."
                          className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                        />
                      </div>
                      {showModelDropdown && (
                         <div 
                           className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg max-h-60 overflow-y-auto"
                           onBlur={() => setTimeout(() => setShowModelDropdown(false), 200)}
                         >
                          {loadingModels ? (
                            <div className="p-3 text-center text-gray-500 dark:text-gray-400">
                              <div className="inline-flex items-center gap-2">
                                <div className="w-4 h-4 border-2 border-gray-300 border-t-purple-600 rounded-full animate-spin"></div>
                                Loading models...
                              </div>
                            </div>
                          ) : filteredModels.length > 0 ? (
                            filteredModels.slice(0, 50).map((model) => (
                              <div
                                 key={model.id}
                                 className="p-3 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer border-b border-gray-200 dark:border-gray-600 last:border-b-0"
                                 onClick={() => {
                                   setLlmModel(model.id);
                                   setModelSearchQuery(model.id);
                                   setShowModelDropdown(false);
                                 }}
                               >
                                 <div className="font-medium text-gray-900 dark:text-white text-sm">
                                   {model.id}
                                 </div>
                                 <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                   Context: {model.context_length} | {model.is_free ? 'Free' : model.prompt_price_formatted}
                                 </div>
                               </div>
                            ))
                          ) : (
                            <div className="p-3 text-center text-gray-500 dark:text-gray-400">
                              No models found
                            </div>
                          )}
                        </div>
                      )}
                      {llmModel && (
                        <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-600 rounded text-xs text-gray-600 dark:text-gray-300">
                          Selected: {llmModel}
                        </div>
                      )}
                    </div>
                  ) : (
                    <input
                      type="text"
                      value={llmModel}
                      onChange={(e) => setLlmModel(e.target.value)}
                      placeholder="gpt-3.5-turbo"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                    />
                  )}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  API Key
                </label>
                <input
                  type="password"
                  value={llmApiKey}
                  onChange={(e) => setLlmApiKey(e.target.value)}
                  placeholder="Enter your API key"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                  required={useLLM}
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Temperature
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="2"
                    step="0.1"
                    value={llmTemperature}
                    onChange={(e) => setLlmTemperature(parseFloat(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Max Tokens
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="4000"
                    value={llmMaxTokens}
                    onChange={(e) => setLlmMaxTokens(parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Timeout (s)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="300"
                    value={llmTimeout}
                    onChange={(e) => setLlmTimeout(parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Extraction Instruction
                </label>
                <textarea
                  value={llmInstruction}
                  onChange={(e) => setLlmInstruction(e.target.value)}
                  placeholder="Describe what you want to extract from the webpage..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                  required={useLLM}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  JSON Schema (Optional)
                </label>
                <textarea
                  value={llmSchema}
                  onChange={(e) => setLlmSchema(e.target.value)}
                  placeholder='{
  "title": "string",
  "content": "string",
  "author": "string"
}'
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors font-mono"
                />
              </div>
            </div>
          )}

          {selectedExtractor && (
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-md">
              <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                Extractor Details
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                {selectedExtractor.description}
              </p>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                <p>ID: {selectedExtractor.id}</p>
                <p>File: {selectedExtractor.file_path}</p>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || !url || (!extractorId && !useLLM) || (useLLM && !llmApiKey)}
            className={`w-full py-3 px-4 rounded-md text-sm font-medium text-white transition-colors flex items-center justify-center gap-2 ${
              isLoading || !url || (!extractorId && !useLLM) || (useLLM && !llmApiKey)
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800'
            }`}
          >
            {isLoading ? (
              <>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid transparent',
                  borderTop: '2px solid #ffffff',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                <span>{useLLM ? 'Testing with LLM...' : 'Testing...'}</span>
              </>
            ) : (
              <>
                {useLLM ? <Brain size={16} /> : <Play size={16} />}
                <span>{useLLM ? 'Test with LLM' : 'Test Extraction'}</span>
              </>
            )}
          </button>
        </form>
      </div>

      {(result || llmResult) && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center space-x-3 mb-4">
            {(result?.success || llmResult?.success) ? (
              <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
            ) : (
              <XCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
            )}
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              {llmResult ? 'LLM Test Results' : 'Test Results'}
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
              <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
              <p className={`font-semibold ${
                (result?.success || llmResult?.success)
                  ? 'text-green-600 dark:text-green-400' 
                  : 'text-red-600 dark:text-red-400'
              }`}>
                {(result?.success || llmResult?.success) ? 'Success' : 'Failed'}
              </p>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
              <p className="text-sm text-gray-600 dark:text-gray-400">Response Time</p>
              <p className="font-semibold text-gray-900 dark:text-white flex items-center">
                <Clock className="h-4 w-4 mr-1" />
                {llmResult ? llmResult.response_time : result?.responseTime}ms
              </p>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded">
              <p className="text-sm text-gray-600 dark:text-gray-400">Timestamp</p>
              <p className="font-semibold text-gray-900 dark:text-white">
                {llmResult 
                  ? new Date(llmResult.timestamp || '').toLocaleTimeString()
                  : result?.timestamp.toLocaleTimeString()
                }
              </p>
            </div>
          </div>

          {((result?.success && result.data) || (llmResult?.success && llmResult.data)) ? (
            <div className="space-y-6">
              {/* LLM Extraction Results */}
              {llmResult?.success && llmResult.data?.llm_extraction && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                    <Brain className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                    LLM Extracted Data
                  </h3>
                  <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border border-purple-200 dark:border-purple-700 p-4 rounded-md">
                    <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap overflow-auto">
                      {(() => {
                        try {
                          // If llm_extraction is a string, try to parse it as JSON
                          if (typeof llmResult.data.llm_extraction === 'string') {
                            const parsed = JSON.parse(llmResult.data.llm_extraction);
                            return JSON.stringify(parsed, null, 2);
                          }
                          // If it's already an object, stringify it directly
                          return JSON.stringify(llmResult.data.llm_extraction, null, 2);
                        } catch (error) {
                          // If parsing fails, display the raw string
                          return llmResult.data.llm_extraction;
                        }
                      })()}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* Schema Used */}
              {llmResult?.success && llmSchema && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                    Schema Used for Extraction
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 p-4 rounded-md">
                    <pre className="text-xs text-gray-600 dark:text-gray-400 whitespace-pre-wrap overflow-auto">
                      {llmSchema}
                    </pre>
                  </div>
                </div>
              )}
              
              {/* Page Metadata */}
              {(llmResult?.success || result?.success) && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                    Page Information
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-md space-y-2">
                    {(llmResult?.data?.title || result?.data?.title) && (
                      <div>
                        <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Title: </span>
                        <span className="text-sm text-gray-900 dark:text-white">
                          {llmResult?.data?.title || result?.data?.title}
                        </span>
                      </div>
                    )}
                    {llmResult?.data?.metadata && (
                      <div>
                        <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Provider: </span>
                        <span className="text-sm text-gray-900 dark:text-white">
                          {llmResult.data.metadata.provider} ({llmResult.data.metadata.model})
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {/* Raw Data (Collapsible) */}
              {!llmResult && result?.success && result.data && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                    Extracted Data
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-md overflow-auto">
                    <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {JSON.stringify(result.data, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          ) : (result?.error || llmResult?.error) && (
            <div>
              <h3 className="text-lg font-medium text-red-600 dark:text-red-400 mb-3">
                Error Details
              </h3>
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 rounded-md">
                <p className="text-red-700 dark:text-red-300">{llmResult?.error || result?.error}</p>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-4 rounded-md">
        <h3 className="font-medium text-blue-900 dark:text-blue-300 mb-2">
          How to Use
        </h3>
        <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
          <li>• Enter a valid URL that you want to test extraction on</li>
          <li>• Select an active extractor from the dropdown</li>
          <li>• Click "Test Extraction" to run the extraction process</li>
          <li>• Review the results to see what data was extracted</li>
        </ul>
      </div>
    </div>
  );
}

export default TestURL;