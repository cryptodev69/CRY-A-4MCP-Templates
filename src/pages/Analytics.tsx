import React, { useState, useEffect } from 'react';
import { BarChart3, Clock, TrendingUp, Award, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import { AnalyticsData } from '../types/models';
import { useTheme } from '../contexts/ThemeContext';

// Add CSS animation for loading spinner
const spinnerStyle = document.createElement('style');
spinnerStyle.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;
if (!document.head.querySelector('style[data-spinner]')) {
  spinnerStyle.setAttribute('data-spinner', 'true');
  document.head.appendChild(spinnerStyle);
}

function Analytics() {
  const { isDarkMode } = useTheme();
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const data = await api.getAnalytics();
        setAnalytics(data);
      } catch (error) {
        console.error('Failed to load analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className={`w-16 h-16 rounded-full animate-spin ${
          isDarkMode 
            ? 'border-4 border-gray-600 border-t-blue-400' 
            : 'border-4 border-gray-200 border-t-blue-600'
        }`}></div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className={`rounded-lg shadow-sm p-12 text-center ${
        isDarkMode ? 'bg-gray-800' : 'bg-white'
      }`}>
        <div className="p-6 bg-gradient-to-br from-red-400 to-pink-500 rounded-2xl inline-block mb-6">
          <AlertTriangle className="w-12 h-12 text-white" />
        </div>
        <h3 className={`text-2xl font-extrabold mb-3 tracking-tight ${
          isDarkMode ? 'text-white' : 'text-gray-900'
        }`}>
          ANALYTICS UNAVAILABLE
        </h3>
        <p className={`font-medium ${
          isDarkMode ? 'text-gray-400' : 'text-gray-500'
        }`}>
          Unable to load analytics data. Please refresh and try again.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Header Section */}
      <div className={`rounded-lg shadow-sm p-10 relative overflow-hidden ${
        isDarkMode ? 'bg-gray-800' : 'bg-white'
      }`}>
        <div className={`absolute inset-0 opacity-60 ${
          isDarkMode 
            ? 'bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10'
            : 'bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-pink-500/5'
        }`}></div>
        <div className="relative flex items-center">
          <div className="p-4 bg-gradient-to-br from-blue-400 to-purple-500 rounded-2xl mr-6">
            <BarChart3 className="w-12 h-12 text-white" />
          </div>
          <div>
            <h1 className={`text-4xl font-extrabold tracking-tight mb-2 ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              📊 ANALYTICS DASHBOARD
            </h1>
            <p className={`font-medium text-lg ${
              isDarkMode ? 'text-gray-400' : 'text-gray-500'
            }`}>
              Real-time Performance Insights & Metrics
            </p>
          </div>
        </div>
      </div>

      {/* Response Time Metrics */}
      <div className={`rounded-lg shadow-sm p-8 ${
        isDarkMode ? 'bg-gray-800' : 'bg-white'
      }`}>
        <div className="flex items-center mb-6">
          <div className="p-3 bg-gradient-to-br from-green-400 to-blue-600 rounded-xl mr-4">
            <Clock className="w-8 h-8 text-white" />
          </div>
          <h2 className={`text-2xl font-extrabold tracking-tight ${
            isDarkMode ? 'text-white' : 'text-gray-900'
          }`}>
            ⚡ Response Time Metrics
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className={`rounded-xl p-6 border ${
            isDarkMode 
              ? 'bg-gray-700 border-gray-600' 
              : 'bg-gray-50 border-gray-200'
          }`}>
            <div className={`text-sm font-medium mb-2 ${
              isDarkMode ? 'text-gray-400' : 'text-gray-500'
            }`}>Average</div>
            <div className={`text-3xl font-extrabold ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>{analytics.responseTimeMetrics?.average || 0}ms</div>
          </div>
          <div className={`rounded-xl p-6 border ${
            isDarkMode 
              ? 'bg-gray-700 border-gray-600' 
              : 'bg-gray-50 border-gray-200'
          }`}>
            <div className={`text-sm font-medium mb-2 ${
              isDarkMode ? 'text-gray-400' : 'text-gray-500'
            }`}>Median</div>
            <div className={`text-3xl font-extrabold ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>{analytics.responseTimeMetrics?.median || 0}ms</div>
          </div>
         <div className={`rounded-xl p-6 border ${
           isDarkMode 
             ? 'bg-gray-700 border-gray-600' 
             : 'bg-gray-50 border-gray-200'
         }`}>
           <div className={`text-sm font-medium mb-2 ${
             isDarkMode ? 'text-gray-400' : 'text-gray-500'
           }`}>95th Percentile</div>
           <div className={`text-3xl font-extrabold ${
             isDarkMode ? 'text-white' : 'text-gray-900'
           }`}>{analytics.responseTimeMetrics?.p95 || 0}ms</div>
         </div>
         <div className={`rounded-xl p-6 border ${
           isDarkMode 
             ? 'bg-gray-700 border-gray-600' 
             : 'bg-gray-50 border-gray-200'
         }`}>
           <div className={`text-sm font-medium mb-2 ${
             isDarkMode ? 'text-gray-400' : 'text-gray-500'
           }`}>99th Percentile</div>
           <div className={`text-3xl font-extrabold ${
             isDarkMode ? 'text-white' : 'text-gray-900'
           }`}>{analytics.responseTimeMetrics?.p99 || 0}ms</div>
         </div>
        </div>
      </div>

      {/* Extraction Trends */}
      <div className={`rounded-lg shadow-sm p-8 ${
        isDarkMode ? 'bg-gray-800' : 'bg-white'
      }`}>
        <div className="flex items-center mb-6">
          <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl mr-4">
            <Award className="w-8 h-8 text-white" />
          </div>
          <h2 className={`text-2xl font-extrabold tracking-tight ${
            isDarkMode ? 'text-white' : 'text-gray-900'
          }`}>
            📈 Extraction Trends (Last 7 Days)
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className={`border-b ${
                isDarkMode ? 'border-gray-600' : 'border-gray-200'
              }`}>
                <th className={`text-left py-2 text-sm font-medium ${
                  isDarkMode ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  Date
                </th>
                <th className={`text-left py-2 text-sm font-medium ${
                  isDarkMode ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  Extractions
                </th>
                <th className={`text-left py-2 text-sm font-medium ${
                  isDarkMode ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  Success Rate
                </th>
                <th className={`text-left py-2 text-sm font-medium ${
                  isDarkMode ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  Trend
                </th>
              </tr>
            </thead>
            <tbody>
              {analytics.extractionTrends?.map((trend, index) => {
                const maxCount = Math.max(...(analytics.extractionTrends?.map(t => t.count) || [1]));
                const barWidth = (trend.count / maxCount) * 100;
                
                return (
                  <tr key={trend.date} className={`border-b ${
                    isDarkMode ? 'border-gray-700' : 'border-gray-100'
                  }`}>
                    <td className={`py-3 text-sm ${
                      isDarkMode ? 'text-gray-300' : 'text-gray-900'
                    }`}>
                      {new Date(trend.date).toLocaleDateString()}
                    </td>
                    <td className={`py-3 text-sm ${
                      isDarkMode ? 'text-gray-300' : 'text-gray-900'
                    }`}>
                      {trend.count}
                    </td>
                    <td className={`py-3 text-sm ${
                      isDarkMode ? 'text-gray-300' : 'text-gray-900'
                    }`}>
                      {trend.successRate.toFixed(1)}%
                    </td>
                    <td className="py-3">
                      <div className={`w-24 h-2 rounded-full ${
                        isDarkMode ? 'bg-gray-600' : 'bg-gray-200'
                      }`}>
                        <div
                          className="h-2 bg-blue-600 rounded-full transition-all duration-300"
                          style={{ width: `${barWidth}%` }}
                        ></div>
                      </div>
                    </td>
                  </tr>
                );
              }) || []}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Top Performing Extractors */}
        <div className={`rounded-lg shadow-sm p-8 ${
          isDarkMode 
            ? 'bg-gray-800 border border-gray-700' 
            : 'bg-white border border-gray-200'
        }`}>
          <div className="flex items-center mb-6">
            <div className="p-3 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl mr-4">
              <TrendingUp className="w-8 h-8 text-white" />
            </div>
            <h2 className={`text-2xl font-extrabold tracking-tight ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              🏆 Top Performing Extractors
            </h2>
          </div>
          <div className="flex flex-col gap-3">
            {analytics.topPerformingExtractors?.map((extractor, index) => (
              <div key={extractor.extractorId} className={`flex items-center justify-between p-3 rounded-lg ${
                isDarkMode ? 'bg-gray-700' : 'bg-gray-50'
              }`}>
                <div>
                  <p className={`font-medium ${
                    isDarkMode ? 'text-gray-200' : 'text-gray-900'
                  }`}>
                    #{index + 1} {extractor.name}
                  </p>
                  <p className={`text-sm ${
                    isDarkMode ? 'text-gray-400' : 'text-gray-500'
                  }`}>
                    {extractor.usageCount.toLocaleString()} uses
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-green-600">
                    {extractor.successRate.toFixed(1)}%
                  </p>
                  <p className={`text-xs ${
                    isDarkMode ? 'text-gray-400' : 'text-gray-500'
                  }`}>
                    success rate
                  </p>
                </div>
              </div>
            )) || []}
          </div>
        </div>

        {/* Error Distribution */}
        <div className={`rounded-lg shadow-sm p-8 ${
          isDarkMode 
            ? 'bg-gray-800 border border-gray-700' 
            : 'bg-white border border-gray-200'
        }`}>
          <div className="flex items-center mb-6">
            <div className="p-3 bg-gradient-to-br from-red-400 to-pink-500 rounded-xl mr-4">
              <AlertTriangle className="w-8 h-8 text-white" />
            </div>
            <h2 className={`text-2xl font-extrabold tracking-tight ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              ⚠️ Error Distribution
            </h2>
          </div>
          <div className="flex flex-col gap-3">
            {analytics.errorDistribution?.map((error) => (
              <div key={error.errorType}>
                <div className="flex justify-between items-center mb-1">
                  <span className={`text-sm font-medium ${
                    isDarkMode ? 'text-gray-200' : 'text-gray-700'
                  }`}>
                    {error.errorType}
                  </span>
                  <span className={`text-sm ${
                    isDarkMode ? 'text-gray-400' : 'text-gray-500'
                  }`}>
                    {error.count} ({error.percentage.toFixed(1)}%)
                  </span>
                </div>
                <div className={`w-full h-2 rounded-full ${
                  isDarkMode ? 'bg-gray-600' : 'bg-gray-200'
                }`}>
                  <div
                    className="h-2 bg-red-500 rounded-full transition-all duration-300"
                    style={{ width: `${error.percentage}%` }}
                  ></div>
                </div>
              </div>
            )) || []}
          </div>
        </div>
      </div>

      <div className={`p-4 rounded-lg border ${
        isDarkMode 
          ? 'bg-yellow-900/20 border-yellow-600 text-yellow-200' 
          : 'bg-yellow-50 border-yellow-200 text-yellow-800'
      }`}>
        <h3 className="font-medium mb-2">
          Analytics Information
        </h3>
        <p className="text-sm opacity-90">
          Analytics data is updated in real-time and shows performance metrics for all extraction operations.
          Use this information to optimize your extractors and identify potential issues.
        </p>
      </div>
    </div>
  );
}

export default Analytics;