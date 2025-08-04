import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Key, Save, Eye, EyeOff, Trash2 } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

/**
 * Interface for API key configuration
 */
interface ApiKeyConfig {
  provider: string;
  apiKey: string;
  isVisible: boolean;
}

/**
 * Settings page component for managing API keys and application configuration
 */
function Settings() {
  const { isDarkMode } = useTheme();
  const [apiKeys, setApiKeys] = useState<ApiKeyConfig[]>([]);
  const [isLoading, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Available providers for API key configuration
  const availableProviders = [
    { id: 'openai', name: 'OpenAI', description: 'GPT models' },
    { id: 'anthropic', name: 'Anthropic', description: 'Claude models' },
    { id: 'google', name: 'Google', description: 'Gemini models' },
    { id: 'openrouter', name: 'OpenRouter', description: 'Multiple model providers' }
  ];



  /**
   * Load API keys from localStorage on component mount
   */
  useEffect(() => {
    const savedKeys = localStorage.getItem('apiKeys');
    if (savedKeys) {
      try {
        const parsedKeys = JSON.parse(savedKeys);
        setApiKeys(parsedKeys.map((key: any) => ({ ...key, isVisible: false })));
      } catch (error) {
        console.error('Failed to load API keys:', error);
      }
    }
  }, []);

  /**
   * Save API keys to localStorage
   */
  const saveApiKeys = async () => {
    setSaving(true);
    try {
      const keysToSave = apiKeys.map(({ isVisible, ...key }) => key);
      localStorage.setItem('apiKeys', JSON.stringify(keysToSave));
      setMessage({ type: 'success', text: 'API keys saved successfully!' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save API keys' });
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setSaving(false);
    }
  };

  /**
   * Add a new API key configuration
   */
  const addApiKey = (provider: string) => {
    const existingIndex = apiKeys.findIndex(key => key.provider === provider);
    if (existingIndex >= 0) {
      // Update existing key
      const newKeys = [...apiKeys];
      newKeys[existingIndex] = { ...newKeys[existingIndex], apiKey: '', isVisible: true };
      setApiKeys(newKeys);
    } else {
      // Add new key
      setApiKeys([...apiKeys, { provider, apiKey: '', isVisible: true }]);
    }
  };

  /**
   * Update API key value
   */
  const updateApiKey = (provider: string, apiKey: string) => {
    setApiKeys(keys => keys.map(key => 
      key.provider === provider ? { ...key, apiKey } : key
    ));
  };

  /**
   * Toggle API key visibility
   */
  const toggleVisibility = (provider: string) => {
    setApiKeys(keys => keys.map(key => 
      key.provider === provider ? { ...key, isVisible: !key.isVisible } : key
    ));
  };

  /**
   * Remove API key configuration
   */
  const removeApiKey = (provider: string) => {
    setApiKeys(keys => keys.filter(key => key.provider !== provider));
  };

  /**
   * Get provider display information
   */
  const getProviderInfo = (providerId: string) => {
    return availableProviders.find(p => p.id === providerId) || 
           { id: providerId, name: providerId, description: '' };
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <SettingsIcon className="w-8 h-8 text-purple-600 dark:text-purple-400" />
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white m-0">
          Settings
        </h1>
      </div>

      {/* API Key Configuration Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center gap-3 mb-6">
          <Key className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white m-0">
            API Key Configuration
          </h2>
        </div>

        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Configure API keys for different LLM providers. These keys are stored locally in your browser.
        </p>

        {/* Available Providers */}
        <div className="mb-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
            Available Providers
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {availableProviders.map((provider) => {
              const hasKey = apiKeys.some(key => key.provider === provider.id);
              return (
                <div
                  key={provider.id}
                  className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {provider.name}
                    </h4>
                    <button
                      onClick={() => addApiKey(provider.id)}
                      className={`px-3 py-1 text-xs rounded-md transition-colors ${
                        hasKey
                          ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                          : 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-800'
                      }`}
                    >
                      {hasKey ? 'Configured' : 'Add Key'}
                    </button>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {provider.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Configured API Keys */}
        {apiKeys.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
              Configured API Keys
            </h3>
            <div className="space-y-4">
              {apiKeys.map((keyConfig) => {
                const providerInfo = getProviderInfo(keyConfig.provider);
                return (
                  <div
                    key={keyConfig.provider}
                    className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {providerInfo.name}
                      </h4>
                      <button
                        onClick={() => removeApiKey(keyConfig.provider)}
                        className="p-1 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-colors"
                        title="Remove API key"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                    <div className="flex gap-2">
                      <div className="flex-1 relative">
                        <input
                          type={keyConfig.isVisible ? 'text' : 'password'}
                          value={keyConfig.apiKey}
                          onChange={(e) => updateApiKey(keyConfig.provider, e.target.value)}
                          placeholder={`Enter ${providerInfo.name} API key`}
                          className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-colors"
                        />
                        <button
                          type="button"
                          onClick={() => toggleVisibility(keyConfig.provider)}
                          className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                        >
                          {keyConfig.isVisible ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Save Button */}
        <div className="flex items-center justify-between">
          <div>
            {message && (
              <div className={`text-sm ${
                message.type === 'success' 
                  ? 'text-green-600 dark:text-green-400' 
                  : 'text-red-600 dark:text-red-400'
              }`}>
                {message.text}
              </div>
            )}
          </div>
          <button
            onClick={saveApiKeys}
            disabled={isLoading || apiKeys.length === 0}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              isLoading || apiKeys.length === 0
                ? 'bg-gray-400 text-white cursor-not-allowed'
                : 'bg-purple-600 text-white hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800'
            }`}
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Saving...
              </>
            ) : (
              <>
                <Save size={16} />
                Save API Keys
              </>
            )}
          </button>
        </div>
      </div>

      {/* Additional Settings Sections can be added here */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Application Settings
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Additional application settings will be available here in future updates.
        </p>
      </div>
    </div>
  );
}

export default Settings;