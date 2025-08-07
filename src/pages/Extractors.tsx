import React, { useState } from 'react';
import { useApp } from '../contexts/AppContext';
import { useTheme } from '../contexts/ThemeContext';
import { Settings, Tag, User, Calendar, Code, FileText, X } from 'lucide-react';
import { format } from 'date-fns';

function Extractors() {
  const { state } = useApp();
  const { extractors, loading } = state;
  const [selectedModal, setSelectedModal] = useState<{ type: 'schema' | 'instruction', data: any, title: string } | null>(null);

  const formatStrategyName = (name: string) => {
    // Remove common suffixes and format for better display
    return name
      .replace(/LLMExtractionStrategy$/, '')
      .replace(/ExtractionStrategy$/, '')
      .replace(/Strategy$/, '')
      .replace(/([A-Z])/g, ' $1')
      .trim();
  };

  const openModal = (type: 'schema' | 'instruction', data: any, extractorName: string) => {
    setSelectedModal({ type, data, title: extractorName });
  };

  const closeModal = () => {
    setSelectedModal(null);
  };

  if (loading.extractors) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-3 border-gray-200 dark:border-gray-700 border-t-blue-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white m-0">
          Extractors
        </h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {extractors.map((extractor) => (
          <div key={extractor.id} className="bg-white dark:bg-gray-800 rounded-xl border border-slate-200 dark:border-gray-700 shadow-sm dark:shadow-gray-900/20 p-6 transition-all duration-200 hover:shadow-md dark:hover:shadow-gray-900/30">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <Settings className="h-6 w-6 text-blue-500 dark:text-blue-400" />
                </div>
                <div className="ml-3 flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white m-0 mb-1 truncate" title={extractor.name}>
                    {formatStrategyName(extractor.name)}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 m-0">
                    v{extractor.version || '1.0'}
                  </p>
                </div>
              </div>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                (extractor.isActive !== false) 
                  ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400' 
                  : 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-400'
              }`}>
                {(extractor.isActive !== false) ? 'Active' : 'Inactive'}
              </span>
            </div>

            <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
              {extractor.description}
            </p>

            <div className="flex flex-col gap-3">
              <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                <User className="h-4 w-4 mr-2" />
                <span>{extractor.author || 'Unknown'}</span>
              </div>
              
              <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                <Calendar className="h-4 w-4 mr-2" />
                <span>Updated {extractor.updatedAt ? format(new Date(extractor.updatedAt), 'MMM dd, yyyy') : 'N/A'}</span>
              </div>

              <div className="flex flex-wrap gap-1">
                {(extractor.tags || []).map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md"
                  >
                    <Tag className="h-3 w-3 mr-1" />
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500 dark:text-gray-400 m-0 mb-1">Usage Count</p>
                  <p className="font-semibold text-gray-900 dark:text-white m-0">
                    {(extractor.usageCount || 0).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500 dark:text-gray-400 m-0 mb-1">Success Rate</p>
                  <p className="font-semibold text-gray-900 dark:text-white m-0">
                    {(extractor.successRate || 0).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-4 flex gap-2">
              {(extractor.schema || extractor.config?.schema) && (
                <button
                  onClick={() => openModal('schema', extractor.schema || extractor.config?.schema, extractor.name)}
                  className="flex items-center px-3 py-2 text-sm font-medium text-blue-500 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 rounded-md transition-colors hover:bg-blue-100 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-300"
                >
                  <Code className="h-4 w-4 mr-1" />
                  View Schema
                </button>
              )}
              {extractor.config?.instruction && (
                <button
                  onClick={() => openModal('instruction', extractor.config?.instruction || '', extractor.name)}
                  className="flex items-center px-3 py-2 text-sm font-medium text-green-500 dark:text-green-400 bg-green-50 dark:bg-green-900/20 rounded-md transition-colors hover:bg-green-100 dark:hover:bg-green-900/30 hover:text-green-600 dark:hover:text-green-300"
                >
                  <FileText className="h-4 w-4 mr-1" />
                  View Instructions
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {extractors.length === 0 && (
        <div className="text-center py-12">
          <Settings className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
            No extractors available
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Extractors will appear here when they are configured.
          </p>
        </div>
      )}

      {/* Modal for Schema and Instructions */}
      {selectedModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                {selectedModal.type === 'schema' ? 'Schema' : 'Instructions'} - {formatStrategyName(selectedModal.title)}
              </h2>
              <button
                onClick={closeModal}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="p-4 overflow-auto max-h-[calc(80vh-80px)]">
              {selectedModal.type === 'schema' ? (
                <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 font-mono bg-gray-50 dark:bg-gray-900/50 p-4 rounded-md overflow-auto">
                  {JSON.stringify(selectedModal.data, null, 2)}
                </pre>
              ) : (
                <div className="prose dark:prose-invert max-w-none">
                  <div className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                    {selectedModal.data}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Extractors;