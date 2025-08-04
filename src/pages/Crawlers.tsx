import React, { useState, useEffect } from 'react';
import { Plus, Settings, Play, Pause, Trash2, Edit, Eye, Activity, Globe, Zap, Brain, Clock, AlertCircle, CheckCircle, XCircle, TrendingUp, Database, Cpu, BarChart3 } from 'lucide-react';
import CrawlerFormWithURLMapping, { CrawlerFormData } from '../components/CrawlerFormWithURLMapping';
import { crawlApi } from '../services/crawlApi';
import { api } from '../services/api';
import type { APICrawlerConfig, ExtractorMapping, URLMapping } from '../services/crawlApi';
import type { ExtractorStrategy } from '../services/URLMappingIntegrationService';

// Using CrawlerConfig interface from crawlApi.ts

// CrawlerFormData interface is now imported from CrawlerFormWithURLMapping component

const Crawlers: React.FC = () => {
  const [crawlers, setCrawlers] = useState<APICrawlerConfig[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedCrawler, setSelectedCrawler] = useState<APICrawlerConfig | null>(null);
  
  // State for URL mappings and extractors
  const [urlMappings, setUrlMappings] = useState<URLMapping[]>([]);
  const [extractors, setExtractors] = useState<ExtractorStrategy[]>([]);

  // Load crawlers, URL mappings, and extractors from API
  useEffect(() => {
    const loadCrawlers = async () => {
      try {
        const response = await crawlApi.getCrawlers();
        if (response.success && response.data) {
          // Transform API response to match frontend format
          const transformedCrawlers: APICrawlerConfig[] = (response.data.items || []).map(crawler => ({
            id: crawler.id,
            name: crawler.name,
            description: crawler.description,
            crawlerType: crawler.crawlerType,
            isActive: crawler.isActive,
            config: crawler.config,
            llmConfig: crawler.config ? {
              provider: crawler.config.llm_provider,
              model: crawler.config.llm_model,
              api_key: crawler.config.llm_api_key
            } : undefined,
            extractionStrategies: crawler.extractionStrategies || [],
            urlMappingIds: crawler.urlMappingId ? [crawler.urlMappingId] : [],
            targetUrls: crawler.targetUrls || [],
            priority: 0,
            stats: crawler.stats,
            createdAt: crawler.createdAt,
            updatedAt: crawler.updatedAt,
            createdBy: crawler.createdBy
          }));
          setCrawlers(transformedCrawlers);
        }
      } catch (error) {
        console.error('Failed to load crawlers:', error);
      }
    };

    const loadData = async () => {
      try {
        // Load crawlers
        await loadCrawlers();

        // Load URL mappings using the crawlApi service
        const urlMappingsResponse = await crawlApi.getURLMappings();
        if (urlMappingsResponse.success && urlMappingsResponse.data) {
          console.log('URL Mappings Data:', urlMappingsResponse.data);
          setUrlMappings(urlMappingsResponse.data);
        }

        // Load extractors using the correct API endpoint
        const extractorsData = await api.getExtractors();
        console.log('Extractors Data:', extractorsData);
        // Convert Extractor to ExtractorStrategy format
        const extractorStrategies: ExtractorStrategy[] = extractorsData.map(extractor => ({
          id: extractor.id,
          name: extractor.name,
          type: 'css', // Default type since Extractor doesn't have type property
          config: extractor.config || {},
          description: extractor.description || ''
        }));
        setExtractors(extractorStrategies);
        
      } catch (error) {
        console.error('Error loading data:', error);
        // Fallback to empty arrays on error
        setCrawlers([]);
        setUrlMappings([]);
        setExtractors([]);
      }
    };
    
    loadData();
  }, []);

  const handleCreateCrawler = async (formData: CrawlerFormData) => {
    try {
      // Find the selected URL mapping if one was chosen
      const selectedUrlMapping = formData.urlMappingId 
        ? urlMappings.find(mapping => mapping.id === formData.urlMappingId)
        : null;
      
      const crawlerData = {
        name: formData.name,
        description: formData.description,
        crawlerType: (formData.crawlerType || 'basic') as 'basic' | 'llm' | 'composite',
        isActive: false,
        config: {
          headless: formData.config.headless,
          browser_type: 'chromium' as const,
          page_timeout: formData.config.timeout,
          delay_before_return_html: 2000,
          wait_for: '',
          word_count_threshold: 10,
          magic: false,
          simulate_user: false,
          override_navigator: false,
          extraction_strategies: [formData.crawlerType === 'basic' ? 'css' : 'llm'],
          screenshot: false,
          llm_provider: (formData.llmConfig?.provider || 'openai') as 'openai' | 'anthropic' | 'local',
          llm_model: formData.llmConfig?.model || 'gpt-4'
        },
        extractionStrategies: [{
          id: `${formData.crawlerType}_default`,
          name: formData.crawlerType === 'basic' ? 'CSS Extractor' : 'LLM Extractor',
          type: (formData.crawlerType === 'basic' ? 'css' : 'llm') as 'css' | 'llm',
          config: formData.crawlerType === 'basic' ? { selector: 'body' } : { instruction: 'Extract relevant data' },
          priority: 1,
          isActive: true
        }],
        urlMappingId: selectedUrlMapping?.id || formData.urlMappingId,
        targetUrls: selectedUrlMapping ? 
          // Use the URLs from the mapping
          (selectedUrlMapping.urls || []).filter(Boolean) : 
          formData.targetUrls || [],
        urlMappings: [],
        createdBy: 'user'
      };
      
      const response = await crawlApi.createCrawler(crawlerData);
      if (response.success && response.data) {
        // Reload crawlers to get the updated list
        const crawlersResponse = await crawlApi.getCrawlers();
        if (crawlersResponse.success && crawlersResponse.data) {
          const apiCrawlers: APICrawlerConfig[] = (crawlersResponse.data.items || []).map(crawler => ({
            id: crawler.id,
            name: crawler.name,
            description: crawler.description,
            crawlerType: crawler.crawlerType,
            isActive: crawler.isActive,
            config: crawler.config,
            llmConfig: crawler.config ? {
              provider: crawler.config.llm_provider,
              model: crawler.config.llm_model,
              api_key: crawler.config.llm_api_key
            } : undefined,
            extractionStrategies: crawler.extractionStrategies || [],
            urlMappingIds: crawler.urlMappingId ? [crawler.urlMappingId] : [],
            targetUrls: crawler.targetUrls || [],
            priority: 0,
            stats: crawler.stats,
            createdAt: crawler.createdAt,
            updatedAt: crawler.updatedAt,
            createdBy: crawler.createdBy
          }));
          setCrawlers(apiCrawlers);
        }
      }
      setIsCreateModalOpen(false);
    } catch (error) {
      console.error('Error creating crawler:', error);
    }
  };

  const handleEditCrawler = async (formData: CrawlerFormData) => {
    if (!selectedCrawler) return;

    try {
      // Find the selected URL mapping if one was chosen
      const selectedUrlMapping = formData.urlMappingId 
        ? urlMappings.find(mapping => mapping.id === formData.urlMappingId)
        : null;
      
      const updateData = {
        name: formData.name,
        description: formData.description,
        config: {
          headless: formData.config.headless,
          browser_type: 'chromium' as const,
          page_timeout: formData.config.timeout,
          delay_before_return_html: 2000,
          wait_for: '',
          word_count_threshold: 10,
          magic: false,
          simulate_user: false,
          override_navigator: false,
          extraction_strategies: [formData.crawlerType === 'basic' ? 'css' : 'llm'],
          screenshot: false,
          llm_provider: (formData.llmConfig?.provider || 'openai') as 'openai' | 'anthropic' | 'local',
          llm_model: formData.llmConfig?.model || 'gpt-4'
        },
        extractionStrategies: [{
          id: `${formData.crawlerType}_default`,
          name: formData.crawlerType === 'basic' ? 'CSS Extractor' : 'LLM Extractor',
          type: (formData.crawlerType === 'basic' ? 'css' : 'llm') as 'css' | 'llm',
          config: formData.crawlerType === 'basic' ? { selector: 'body' } : { instruction: 'Extract relevant data' },
          priority: 1,
          isActive: true
        }],
        urlMappingId: selectedUrlMapping?.id || selectedCrawler.urlMappingIds?.[0],
        targetUrls: selectedUrlMapping ? 
          // Use the URLs from the mapping
          (selectedUrlMapping.urls || []).filter(Boolean) : 
          selectedCrawler.targetUrls || []
      };

      const response = await crawlApi.updateCrawler(selectedCrawler.id, updateData);
      if (response.success) {
        // Reload crawlers to get the updated list
        const crawlersResponse = await crawlApi.getCrawlers();
        if (crawlersResponse.success && crawlersResponse.data) {
          const apiCrawlers: APICrawlerConfig[] = (crawlersResponse.data.items || []).map(crawler => ({
            id: crawler.id,
            name: crawler.name,
            description: crawler.description,
            crawlerType: crawler.crawlerType,
            isActive: crawler.isActive,
            config: crawler.config,
            llmConfig: crawler.config ? {
              provider: crawler.config.llm_provider,
              model: crawler.config.llm_model,
              api_key: crawler.config.llm_api_key
            } : undefined,
            extractionStrategies: crawler.extractionStrategies || [],
            urlMappingIds: crawler.urlMappingId ? [crawler.urlMappingId] : [],
            targetUrls: crawler.targetUrls || [],
            priority: 0,
            stats: crawler.stats,
            createdAt: crawler.createdAt,
            updatedAt: crawler.updatedAt,
            createdBy: crawler.createdBy
          }));
          setCrawlers(apiCrawlers);
        }
      }
      setIsEditModalOpen(false);
      setSelectedCrawler(null);
    } catch (error) {
      console.error('Error updating crawler:', error);
    }
  };

  const handleDeleteCrawler = async (id: string) => {
    try {
      const response = await crawlApi.deleteCrawler(id);
      if (response.success) {
        setCrawlers(crawlers.filter(crawler => crawler.id !== id));
      }
    } catch (error) {
      console.error('Error deleting crawler:', error);
    }
  };

  const handleToggleActive = async (id: string) => {
    try {
      const response = await crawlApi.toggleCrawler(id);
      if (response.success && response.data) {
        // Update the local state with the toggled crawler
        setCrawlers(crawlers.map(crawler => 
          crawler.id === id 
            ? { ...crawler, isActive: response.data!.isActive }
            : crawler
        ));
      }
    } catch (error) {
      console.error('Error toggling crawler:', error);
    }
  };

  const openEditModal = (crawler: APICrawlerConfig) => {
    // Debug logging for data state
    console.log('Edit modal attempt:', {
      urlMappingsCount: urlMappings.length,
      extractorsCount: extractors.length,
      urlMappings: urlMappings,
      extractors: extractors
    });
    
    // Ensure urlMappings and extractors are loaded before opening edit modal
    if (urlMappings.length === 0 || extractors.length === 0) {
      console.warn('Cannot open edit modal: URL mappings or extractors not yet loaded');
      console.warn('Current state:', { urlMappingsLength: urlMappings.length, extractorsLength: extractors.length });
      return;
    }
    setSelectedCrawler(crawler);
    setIsEditModalOpen(true);
  };

  // Convert crawler data to form data for editing
  const getInitialFormData = (crawler: APICrawlerConfig): Partial<CrawlerFormData> => {
    // Find the active URL mapping ID from urlMappingIds array
    const activeUrlMappingId = crawler.urlMappingIds?.[0];
    const activeUrlMapping = activeUrlMappingId ? urlMappings.find(mapping => mapping.id === activeUrlMappingId) : undefined;
    
    return {
      name: crawler.name,
      description: crawler.description,
      crawlerType: crawler.crawlerType as 'basic' | 'llm' | 'composite',
      config: {
        timeout: (crawler.config?.page_timeout || 30000) / 1000, // Convert to seconds
        maxRetries: crawler.config?.max_retries || 3,
        concurrentLimit: crawler.config?.concurrent_limit || 5,
        extractionTimeout: crawler.config?.extraction_timeout || 45000,
        headless: crawler.config?.headless ?? true,
        verbose: crawler.config?.verbose ?? false
      },
      llmConfig: {
        provider: (crawler.llmConfig?.provider || crawler.config?.llm_provider || 'openai') as 'openai' | 'anthropic' | 'local',
        model: crawler.llmConfig?.model || crawler.config?.llm_model || 'gpt-4',
        temperature: crawler.llmConfig?.temperature || 0.7,
        systemPrompt: crawler.llmConfig?.systemPrompt || 'Extract relevant information from web pages.'
      },
      urlMappingId: activeUrlMappingId,
      targetUrls: crawler.targetUrls || (activeUrlMapping ? 
        // Use the URLs from the mapping
        (activeUrlMapping.urls || []).filter(Boolean) : 
        [])
    };
  };



  // Helper functions
  const getCrawlerTypeIcon = (type: string) => {
    switch (type) {
      case 'basic': return <Globe className="w-6 h-6" />;
      case 'llm': return <Brain className="w-6 h-6" />;
      case 'composite': return <Zap className="w-6 h-6" />;
      default: return <Activity className="w-6 h-6" />;
    }
  };

  // Get applied extractors for a crawler from its URL mappings
  const getAppliedExtractors = (crawler: APICrawlerConfig) => {
    const extractorIds = new Set<string>();
    
    // Get extractor IDs from URL mappings associated with this crawler
    if (crawler.urlMappingIds && crawler.urlMappingIds.length > 0) {
      crawler.urlMappingIds.forEach((mappingId: string) => {
        const mapping = urlMappings.find(m => m.id === mappingId && m.isActive);
        if (mapping && mapping.extractor_ids) {
          mapping.extractor_ids.forEach(extractorId => {
            extractorIds.add(extractorId);
          });
        }
      });
    }
    
    // Get extractor IDs from extraction strategies
    // Handle both string IDs and object formats
    if (crawler.extractionStrategies && Array.isArray(crawler.extractionStrategies)) {
      crawler.extractionStrategies.forEach(strategy => {
        if (typeof strategy === 'string') {
          // Strategy is just an extractor ID string
          extractorIds.add(strategy);
        } else if (typeof strategy === 'object' && strategy && strategy.id) {
          // Strategy is an object with an id property
          extractorIds.add(strategy.id);
        }
      });
    }
    
    // Find matching extractors from the available extractors
    const appliedExtractors = Array.from(extractorIds)
      .map(id => extractors.find(extractor => extractor.id === id))
      .filter((extractor): extractor is ExtractorStrategy => extractor !== undefined);
    
    return appliedExtractors;
  };

  const getCrawlerTypeColor = (type: string) => {
    switch (type) {
      case 'basic': return 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white';
      case 'llm': return 'bg-gradient-to-r from-purple-500 to-pink-500 text-white';
      case 'composite': return 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white';
      default: return 'bg-gradient-to-r from-gray-500 to-gray-600 text-white';
    }
  };

  const getStatusIcon = (isActive: boolean, successRate?: number) => {
    if (isActive) {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    }
    return <XCircle className="w-5 h-5 text-gray-400" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Header */}
      <div className="relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 dark:from-indigo-800 dark:via-purple-800 dark:to-pink-800">
          <div className="absolute inset-0 opacity-30">
            <div className="absolute inset-0" style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
            }}></div>
          </div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            {/* Hero Icon */}
            <div className="flex justify-center mb-8">
              <div className="relative">
                <div className="absolute inset-0 bg-white bg-opacity-20 rounded-3xl blur-xl"></div>
                <div className="relative p-6 bg-white bg-opacity-10 backdrop-blur-xl rounded-3xl border border-white border-opacity-20 shadow-2xl">
                  <Activity className="w-16 h-16 text-white" />
                </div>
              </div>
            </div>
            
            {/* Hero Text */}
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 tracking-tight">
              🚀 Web Crawlers
              <span className="block text-3xl md:text-4xl font-light text-indigo-200 mt-2">
                Intelligent Data Extraction
              </span>
            </h1>
            <p className="text-xl text-indigo-100 mb-12 max-w-3xl mx-auto leading-relaxed">
              Harness the power of AI-driven web crawling with advanced extraction strategies,
              real-time monitoring, and intelligent data processing capabilities.
            </p>
            
            {/* Enhanced Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16">
              <div className="group relative">
                <div className="absolute inset-0 bg-gradient-to-r from-green-400 to-emerald-500 rounded-2xl blur-lg opacity-25 group-hover:opacity-40 transition-opacity duration-300"></div>
                <div className="relative bg-white bg-opacity-10 backdrop-blur-xl rounded-2xl p-6 border border-white border-opacity-20 hover:bg-opacity-15 transition-all duration-300">
                  <div className="flex items-center justify-center mb-4">
                    <div className="p-3 bg-green-400 bg-opacity-20 rounded-xl">
                      <CheckCircle className="w-7 h-7 text-green-300" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-white mb-2">{crawlers.filter(c => c.isActive).length}</div>
                  <div className="text-sm text-green-200 font-medium">Active Crawlers</div>
                </div>
              </div>
              
              <div className="group relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-2xl blur-lg opacity-25 group-hover:opacity-40 transition-opacity duration-300"></div>
                <div className="relative bg-white bg-opacity-10 backdrop-blur-xl rounded-2xl p-6 border border-white border-opacity-20 hover:bg-opacity-15 transition-all duration-300">
                  <div className="flex items-center justify-center mb-4">
                    <div className="p-3 bg-blue-400 bg-opacity-20 rounded-xl">
                      <BarChart3 className="w-7 h-7 text-blue-300" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-white mb-2">
                    {crawlers.length > 0 ? (crawlers.reduce((acc, c) => {
                      const successRate = (c.stats?.totalCrawls || 0) > 0 ? ((c.stats?.successfulCrawls || 0) / (c.stats?.totalCrawls || 1)) * 100 : 0;
                      return acc + successRate;
                    }, 0) / crawlers.length).toFixed(1) : '0.0'}%
                  </div>
                  <div className="text-sm text-blue-200 font-medium">Success Rate</div>
                </div>
              </div>
              
              <div className="group relative">
                <div className="absolute inset-0 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-2xl blur-lg opacity-25 group-hover:opacity-40 transition-opacity duration-300"></div>
                <div className="relative bg-white bg-opacity-10 backdrop-blur-xl rounded-2xl p-6 border border-white border-opacity-20 hover:bg-opacity-15 transition-all duration-300">
                  <div className="flex items-center justify-center mb-4">
                    <div className="p-3 bg-yellow-400 bg-opacity-20 rounded-xl">
                      <Globe className="w-7 h-7 text-yellow-300" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-white mb-2">
                    {crawlers.reduce((acc, c) => acc + (c.stats?.totalCrawls || 0), 0).toLocaleString()}
                  </div>
                  <div className="text-sm text-yellow-200 font-medium">Total Crawls</div>
                </div>
              </div>
              
              <div className="group relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-400 to-pink-500 rounded-2xl blur-lg opacity-25 group-hover:opacity-40 transition-opacity duration-300"></div>
                <div className="relative bg-white bg-opacity-10 backdrop-blur-xl rounded-2xl p-6 border border-white border-opacity-20 hover:bg-opacity-15 transition-all duration-300">
                  <div className="flex items-center justify-center mb-4">
                    <div className="p-3 bg-purple-400 bg-opacity-20 rounded-xl">
                      <Zap className="w-7 h-7 text-purple-300" />
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-white mb-2">
                    {crawlers.length > 0 ? (crawlers.reduce((acc, c) => acc + (c.stats?.avgResponseTime || 0), 0) / crawlers.length).toFixed(1) : '0.0'}ms
                  </div>
                  <div className="text-sm text-purple-200 font-medium">Avg Speed</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Your Crawlers</h2>
            <p className="text-gray-600 dark:text-gray-300 mt-1">Manage and monitor your web crawling configurations</p>
          </div>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="group relative px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 font-medium shadow-lg hover:shadow-xl hover:scale-105"
          >
            <div className="flex items-center space-x-2">
              <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
              <span>Create Crawler</span>
            </div>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {/* Crawlers Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {crawlers.map((crawler) => {
            return (
            <div key={crawler.id} className="group relative">
              {/* Card Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-3xl blur-xl opacity-0 group-hover:opacity-20 transition-opacity duration-500"></div>
              
              <div className="relative bg-white dark:bg-gray-800 bg-opacity-60 dark:bg-opacity-80 backdrop-blur-xl rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-500 overflow-hidden border border-white dark:border-gray-600 border-opacity-50 dark:border-opacity-50 hover:bg-opacity-70 hover:-translate-y-2">
                {/* Card Header */}
                <div className="p-8 border-b border-gray-100 dark:border-gray-700 border-opacity-50">
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className="relative">
                        <div className="absolute inset-0 bg-gradient-to-r from-indigo-400 to-purple-400 rounded-2xl blur-md opacity-30"></div>
                        <div className={`relative p-4 rounded-2xl ${getCrawlerTypeColor(crawler.crawlerType)} shadow-lg`}>
                          {getCrawlerTypeIcon(crawler.crawlerType)}
                        </div>
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">{crawler.name}</h3>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-600 dark:text-gray-300 capitalize font-medium">{crawler.crawlerType} Crawler</span>
                          <div className={`w-2 h-2 rounded-full ${
                            crawler.isActive ? 'bg-green-400 animate-pulse' : 'bg-gray-300'
                          }`}></div>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                       {getStatusIcon(crawler.isActive)}
                     </div>
                  </div>
                  
                  <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">{crawler.description}</p>
                </div>

                {/* Card Content */}
                <div className="p-8">
                  {/* Performance Stats */}
                  <div className="grid grid-cols-2 gap-6 mb-8">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                        {(crawler.stats?.totalCrawls || 0) > 0 
                          ? (((crawler.stats?.successfulCrawls || 0) / (crawler.stats?.totalCrawls || 1)) * 100).toFixed(1)
                          : '0.0'
                        }%
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 font-medium">Success Rate</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{(crawler.stats?.totalCrawls || 0).toLocaleString()}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 font-medium">Total Crawls</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-6 mb-8">
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-900 dark:text-white mb-1">{(crawler.stats?.avgResponseTime || 0).toFixed(1)}s</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 font-medium">Avg Time</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-900 dark:text-white mb-1">{crawler.stats?.successfulCrawls || 0}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 font-medium">Successful</div>
                    </div>
                  </div>

                  {/* Extraction Strategies */}
                  <div className="mb-8">
                    <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">Extraction Strategies</div>
                    <div className="flex flex-wrap gap-2">
                      {(crawler.extractionStrategies?.length || 0) > 0 ? (
                        crawler.extractionStrategies?.map((strategy, index) => (
                          <span key={index} className="px-3 py-1 bg-gradient-to-r from-indigo-50 to-purple-50 text-indigo-700 text-xs font-medium rounded-full border border-indigo-100">
                            {typeof strategy === 'object' ? strategy.name : strategy}
                          </span>
                        ))
                      ) : (
                        <span className="text-gray-500 dark:text-gray-400 text-xs">No strategies configured</span>
                      )}
                    </div>
                  </div>

                  {/* Applied Extractors from URL Mappings */}
                  <div className="mb-8">
                    <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">Applied Extractors</div>
                    <div className="flex flex-wrap gap-2">
                      {(() => {
                        const appliedExtractors = getAppliedExtractors(crawler);
                        return appliedExtractors.length > 0 ? (
                          appliedExtractors.map((extractor, index) => (
                            <span
                              key={index}
                              className="px-3 py-1 bg-gradient-to-r from-blue-50 to-cyan-50 text-blue-700 text-xs font-medium rounded-full border border-blue-100 flex items-center gap-1"
                              title={`Type: ${extractor.type} | Description: ${extractor.description}`}
                            >
                              <span className="w-1.5 h-1.5 bg-blue-400 rounded-full"></span>
                              {extractor.name}
                            </span>
                          ))
                        ) : (
                          <span className="text-gray-500 dark:text-gray-400 text-xs">No extractors applied</span>
                        );
                      })()}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <button
                      onClick={() => openEditModal(crawler)}
                      className="flex-1 group relative px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 rounded-xl hover:from-blue-100 hover:to-indigo-100 transition-all duration-300 font-medium text-sm border border-blue-100 hover:border-blue-200"
                    >
                      <div className="flex items-center justify-center gap-2">
                        <Edit className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" />
                        <span>Edit</span>
                      </div>
                    </button>
                    <button
                      onClick={() => handleToggleActive(crawler.id)}
                      className={`flex-1 group relative px-4 py-3 rounded-xl transition-all duration-300 font-medium text-sm border ${
                        crawler.isActive
                          ? 'bg-gradient-to-r from-red-50 to-pink-50 text-red-700 hover:from-red-100 hover:to-pink-100 border-red-100 hover:border-red-200'
                          : 'bg-gradient-to-r from-green-50 to-emerald-50 text-green-700 hover:from-green-100 hover:to-emerald-100 border-green-100 hover:border-green-200'
                      }`}
                    >
                      <div className="flex items-center justify-center gap-2">
                        {crawler.isActive ? (
                          <>
                            <Pause className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" />
                            <span>Pause</span>
                          </>
                        ) : (
                          <>
                            <Play className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" />
                            <span>Start</span>
                          </>
                        )}
                      </div>
                    </button>
                    <button
                      onClick={() => handleDeleteCrawler(crawler.id)}
                      className="group relative px-4 py-3 bg-gradient-to-r from-red-50 to-pink-50 text-red-700 rounded-xl hover:from-red-100 hover:to-pink-100 transition-all duration-300 font-medium text-sm border border-red-100 hover:border-red-200"
                    >
                      <Trash2 className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" />
                    </button>
                  </div>
                </div>
                
                {/* Card Footer */}
                <div className="px-8 py-4 bg-gray-50 dark:bg-gray-700 bg-opacity-50 border-t border-gray-100 dark:border-gray-600 border-opacity-50 rounded-b-3xl">
                  <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                    <div className="flex items-center gap-2">
                      <Clock className="w-3 h-3" />
                      <span>Last used: {crawler.stats?.lastUsed ? new Date(crawler.stats.lastUsed).toLocaleDateString() : 'Never'}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className={`w-2 h-2 rounded-full ${
                        crawler.isActive ? 'bg-green-400 animate-pulse' : 'bg-gray-300'
                      }`}></div>
                      <span className="font-medium">{crawler.isActive ? 'Active' : 'Inactive'}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            );
          })}
        </div>
      </div>

      {/* Create/Edit Modal */}
      <CrawlerFormWithURLMapping
        isOpen={isCreateModalOpen || isEditModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          setIsEditModalOpen(false);
          setSelectedCrawler(null);
        }}
        onSubmit={isCreateModalOpen ? handleCreateCrawler : handleEditCrawler}
        urlMappings={urlMappings}
        extractors={extractors}
        initialData={selectedCrawler ? getInitialFormData(selectedCrawler) : undefined}
        isEdit={isEditModalOpen}
      />
    </div>
  );
};

export default Crawlers;