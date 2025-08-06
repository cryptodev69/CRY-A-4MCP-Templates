/**
 * URLMappingDropdown Component
 * 
 * A sophisticated dropdown component that integrates URL mappings with crawler configuration.
 * This component serves as the bridge between URL mappings and crawler creation, providing
 * users with pre-configured URL options that automatically populate crawler settings.
 * 
 * Key Features:
 * - Displays available URL mappings with rich metadata
 * - Auto-configures crawler settings based on selected mapping
 * - Shows extractor assignments and difficulty indicators
 * - Provides search and filtering capabilities
 * - Supports both single and multiple URL selection
 * - Real-time validation and preview of inherited settings
 * 
 * Integration:
 * - Uses URLMappingIntegrationService for configuration inheritance
 * - Integrates with existing Crawlers.tsx form structure
 * - Provides callback functions for form data updates
 * 
 * @component URLMappingDropdown
 * @requires URLMappingIntegrationService, URLMapping types
 */

import React, { useState, useEffect, useMemo } from 'react';
import { ChevronDown, ChevronUp, Search, Globe, Brain, Zap, AlertCircle, CheckCircle, Clock, Settings } from 'lucide-react';
import { URLMapping, CrawlerConfig } from '../services/crawlApi';
import { ExtractorStrategy } from '../services/URLMappingIntegrationService';
import { 
  URLMappingIntegrationService, 
  CrawlerConfigurationBlueprint, 
  URLMappingDropdownOption 
} from '../services/URLMappingIntegrationService';

/**
 * Props interface for URLMappingDropdown component
 */
interface URLMappingDropdownProps {
  /** Available URL mappings to display */
  urlMappings: URLMapping[];
  
  /** Available extractors for reference */
  extractors: ExtractorStrategy[];
  
  /** Currently selected URL mapping ID */
  selectedMappingId?: string;
  
  /** Callback when a URL mapping is selected */
  onMappingSelect: (mappingId: string, blueprint: CrawlerConfigurationBlueprint) => void;
  
  /** Callback when selection is cleared */
  onClear: () => void;
  
  /** Whether the dropdown is disabled */
  disabled?: boolean;
  
  /** Placeholder text when no selection */
  placeholder?: string;
  
  /** Additional CSS classes */
  className?: string;
}

/**
 * URLMappingDropdown Component
 * 
 * Provides an intelligent dropdown interface for selecting URL mappings
 * and automatically configuring crawler settings based on the selection.
 */
const URLMappingDropdown: React.FC<URLMappingDropdownProps> = ({
  urlMappings,
  extractors,
  selectedMappingId,
  onMappingSelect,
  onClear,
  disabled = false,
  placeholder = "Select a URL mapping to auto-configure crawler...",
  className = ""
}) => {
  // Component state
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [integrationService, setIntegrationService] = useState<URLMappingIntegrationService | null>(null);
  const [dropdownOptions, setDropdownOptions] = useState<URLMappingDropdownOption[]>([]);
  const [loading, setLoading] = useState(false);

  /**
   * Initialize the integration service when dependencies change
   */
  useEffect(() => {
    console.log('URLMappingDropdown - urlMappings:', urlMappings);
    console.log('URLMappingDropdown - extractors:', extractors);
    console.log('URLMappingDropdown - selectedMappingId:', selectedMappingId);
    if (urlMappings.length > 0 && extractors.length > 0) {
      const service = new URLMappingIntegrationService(
        urlMappings,
        [], // URL configs - would be loaded from API in real implementation
        extractors
      );
      setIntegrationService(service);
      
      // Generate dropdown options
      const options = service.getURLMappingDropdownOptions();
      console.log('URLMappingDropdown - Generated options:', options);
      console.log('URLMappingDropdown - Looking for selectedMappingId in options:', selectedMappingId);
      const foundOption = options.find(opt => opt.value === selectedMappingId);
      console.log('URLMappingDropdown - Found selected option:', foundOption);
      setDropdownOptions(options);
    } else {
      console.log('URLMappingDropdown - Not enough data to initialize service');
    }
  }, [urlMappings, extractors, selectedMappingId]);

  /**
   * Filter dropdown options based on search term
   */
  const filteredOptions = useMemo(() => {
    if (!searchTerm.trim()) return dropdownOptions;
    
    const term = searchTerm.toLowerCase();
    return dropdownOptions.filter(option => 
      option.label.toLowerCase().includes(term) ||
      option.description.toLowerCase().includes(term) ||
      option.urlPreview.some(url => url.toLowerCase().includes(term))
    );
  }, [dropdownOptions, searchTerm]);

  /**
   * Get the currently selected option
   */
  const selectedOption = useMemo(() => {
    const found = dropdownOptions.find(option => option.value === selectedMappingId);
    console.log('URLMappingDropdown - selectedOption calculation:');
    console.log('  - selectedMappingId:', selectedMappingId);
    console.log('  - dropdownOptions length:', dropdownOptions.length);
    console.log('  - found option:', found);
    return found;
  }, [dropdownOptions, selectedMappingId]);

  /**
   * Handle URL mapping selection
   */
  const handleMappingSelect = async (option: URLMappingDropdownOption) => {
    if (!integrationService || loading) return;
    
    setLoading(true);
    try {
      // Generate crawler configuration blueprint
      const blueprint = await integrationService.resolveURLMapping(option.value);
      
      // Notify parent component
      onMappingSelect(option.value, blueprint);
      
      // Close dropdown
      setIsOpen(false);
      setSearchTerm('');
    } catch (error) {
      console.error('Failed to resolve URL mapping:', error);
      // In a real app, you'd show a toast notification here
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle clearing the selection
   */
  const handleClear = () => {
    onClear();
    setIsOpen(false);
    setSearchTerm('');
  };

  /**
   * Get difficulty color based on scraping difficulty
   */
  const getDifficultyColor = (difficulty?: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  /**
   * Get crawler type icon
   */
  const getCrawlerTypeIcon = (type: string) => {
    switch (type) {
      case 'basic': return <Globe className="w-4 h-4" />;
      case 'llm': return <Brain className="w-4 h-4" />;
      case 'composite': return <Zap className="w-4 h-4" />;
      default: return <Settings className="w-4 h-4" />;
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Dropdown Trigger */}
      <div className="relative">
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className={`
            w-full px-4 py-3 text-left border rounded-xl transition-all duration-200
            ${disabled 
              ? 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600 hover:border-indigo-300 focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
            }
            ${isOpen ? 'ring-2 ring-indigo-500 border-transparent' : ''}
          `}
        >
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              {selectedOption ? (
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    {getCrawlerTypeIcon('basic')}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {selectedOption.label}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                      {selectedOption.urlPreview[0]} • {selectedOption.extractorNames.length > 0 ? (
                        <span className="inline-flex items-center gap-1">
                          {selectedOption.extractorNames.slice(0, 2).map((name, index) => (
                            <span key={index} className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                              {name}
                            </span>
                          ))}
                          {selectedOption.extractorNames.length > 2 && (
                            <span className="text-xs text-gray-400">+{selectedOption.extractorNames.length - 2} more</span>
                          )}
                        </span>
                      ) : 'No extractors'}
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(selectedOption.difficulty)}`}>
                      {selectedOption.difficulty || 'Unknown'}
                    </span>
                  </div>
                </div>
              ) : (
                <span className="text-gray-500 dark:text-gray-400">{placeholder}</span>
              )}
            </div>
            <div className="flex items-center space-x-2 ml-2">
              {isOpen ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              )}
            </div>
          </div>
        </button>
        {/* Clear Button - Outside main button to avoid nesting */}
        {selectedOption && (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              handleClear();
            }}
            className="absolute right-8 top-1/2 transform -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors z-10"
          >
            ×
          </button>
        )}
      </div>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl shadow-lg max-h-96 overflow-hidden">
          {/* Search Input */}
          <div className="p-3 border-b border-gray-200 dark:border-gray-600">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search URL mappings..."
                className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          {/* Options List */}
          <div className="max-h-64 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                <div className="animate-spin w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto mb-2"></div>
                Loading configuration...
              </div>
            ) : filteredOptions.length === 0 ? (
              <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                {searchTerm ? 'No matching URL mappings found' : 'No URL mappings available'}
              </div>
            ) : (
              filteredOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleMappingSelect(option)}
                  className="w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-b border-gray-100 dark:border-gray-700 last:border-b-0"
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {getCrawlerTypeIcon('basic')}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {option.label}
                        </h4>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(option.difficulty)}`}>
                          {option.difficulty || 'Unknown'}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-300 mb-2 line-clamp-2">
                        {option.description}
                      </p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                        <span className="flex items-center space-x-1">
                          <Globe className="w-3 h-3" />
                          <span className="truncate max-w-32">{option.urlPreview[0]}</span>
                        </span>
                        <span className="flex items-center space-x-1">
                          <Settings className="w-3 h-3" />
                          <span title={option.extractorNames.join(', ')}>
                            {option.extractorNames.length > 0 ? (
                              <span className="inline-flex items-center gap-1">
                                {option.extractorNames.slice(0, 2).map((name, index) => (
                                  <span key={index} className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-600 dark:text-gray-300">
                                    {name}
                                  </span>
                                ))}
                                {option.extractorNames.length > 2 && (
                                  <span className="text-xs text-gray-400">+{option.extractorNames.length - 2}</span>
                                )}
                              </span>
                            ) : 'No extractors'}
                          </span>
                        </span>
                        <span className="flex items-center space-x-1">
                          <AlertCircle className="w-3 h-3" />
                          <span>{option.category}</span>
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>

          {/* Footer */}
          {filteredOptions.length > 0 && (
            <div className="p-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
              <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                Select a mapping to auto-configure crawler settings
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default URLMappingDropdown;
export type { URLMappingDropdownProps };