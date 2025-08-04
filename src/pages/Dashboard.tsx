import React from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../contexts/AppContext';
import { Link as LinkIcon, Settings, TestTube, TrendingUp, Activity, Clock, CheckCircle, BarChart3 } from 'lucide-react';
import { format } from 'date-fns';

function Dashboard() {
  const { state } = useApp();
  const { dashboardStats, loading } = state;

  if (loading.dashboard) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-300"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%239C92AC%22%20fill-opacity%3D%220.05%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%222%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-40 dark:opacity-20"></div>
      
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 mb-8">
          <div className="absolute inset-0 bg-black/20"></div>
          <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.1%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%222%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')]"></div>
          
          <div className="relative px-8 py-12 sm:px-12 sm:py-16">
            <div className="flex items-center space-x-4 mb-6">
              <div className="p-3 bg-white/20 backdrop-blur-sm rounded-2xl border border-white/30 shadow-lg">
                <BarChart3 className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-white mb-2">Dashboard</h1>
                <p className="text-xl text-white/90">AI-Powered Web Content Extraction Platform</p>
              </div>
            </div>
            
            <p className="text-white/80 text-lg max-w-2xl mb-6">
              Monitor your extraction performance, manage crawlers, and track system metrics in real-time.
            </p>
            
            <div className="text-sm text-white/70">
              Last updated: {format(new Date(), 'PPpp')}
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            {
              title: 'Total Mappings',
              value: dashboardStats?.totalMappings || 0,
              icon: LinkIcon,
              gradient: 'from-blue-500 to-blue-600',
              bgColor: 'bg-blue-500'
            },
            {
              title: 'Active Mappings',
              value: dashboardStats?.activeMappings || 0,
              icon: CheckCircle,
              gradient: 'from-emerald-500 to-emerald-600',
              bgColor: 'bg-emerald-500'
            },
            {
              title: 'Total Extractions',
              value: dashboardStats?.totalExtractions || 0,
              icon: Activity,
              gradient: 'from-purple-500 to-purple-600',
              bgColor: 'bg-purple-500'
            },
            {
              title: 'Success Rate',
              value: dashboardStats?.successRate ? `${dashboardStats.successRate.toFixed(1)}%` : '0%',
              icon: TrendingUp,
              gradient: 'from-amber-500 to-amber-600',
              bgColor: 'bg-amber-500'
            }
          ].map((stat, index) => {
            const IconComponent = stat.icon;
            return (
              <div
                key={stat.title}
                className="group relative overflow-hidden rounded-2xl bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm border border-white/20 dark:border-gray-700/30 shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 hover:bg-white/80 dark:hover:bg-gray-800/80"
              >
                <div className="absolute inset-0 bg-gradient-to-br opacity-5 group-hover:opacity-10 transition-opacity duration-300" style={{ backgroundImage: `linear-gradient(to bottom right, var(--tw-gradient-stops))` }}></div>
                <div className="relative p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-r ${stat.gradient} shadow-lg`}>
                      <IconComponent className="h-6 w-6 text-white" />
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</div>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">{stat.title}</h3>
                    <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                      <div className={`w-2 h-2 rounded-full ${stat.bgColor} mr-2`}></div>
                      Active
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
      </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Performance Metrics */}
          <div className="group relative overflow-hidden rounded-2xl bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm border border-white/20 dark:border-gray-700/30 shadow-xl hover:shadow-2xl transition-all duration-300 hover:bg-white/80 dark:hover:bg-gray-800/80">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-purple-50/50 dark:from-blue-900/20 dark:to-purple-900/20 opacity-50 group-hover:opacity-70 transition-opacity duration-300"></div>
            <div className="relative p-8">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg">
                  <Activity className="h-5 w-5 text-white" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Performance Metrics</h2>
              </div>
              
              <div className="space-y-4">
                {[
                  { label: 'Response Time', value: dashboardStats?.averageResponseTime ? `${Math.round(dashboardStats.averageResponseTime)}ms` : 'N/A', color: 'text-emerald-600 dark:text-emerald-400' },
                  { label: 'System Status', value: 'Operational', color: 'text-emerald-600 dark:text-emerald-400' },
                  { label: 'Uptime', value: '99.9%', color: 'text-blue-600 dark:text-blue-400' },
                  { label: 'Error Rate', value: '0.1%', color: 'text-amber-600 dark:text-amber-400' }
                ].map((metric, index) => (
                  <div key={metric.label} className="flex items-center justify-between py-3 border-b border-gray-100/50 dark:border-gray-700/50 last:border-b-0">
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-300">{metric.label}</span>
                    <span className={`text-sm font-semibold ${metric.color}`}>{metric.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="group relative overflow-hidden rounded-2xl bg-white/70 dark:bg-gray-800/70 backdrop-blur-sm border border-white/20 dark:border-gray-700/30 shadow-xl hover:shadow-2xl transition-all duration-300 hover:bg-white/80 dark:hover:bg-gray-800/80">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-50/50 to-pink-50/50 dark:from-purple-900/20 dark:to-pink-900/20 opacity-50 group-hover:opacity-70 transition-opacity duration-300"></div>
            <div className="relative p-8">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl shadow-lg">
                  <Settings className="h-5 w-5 text-white" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Quick Actions</h2>
              </div>
              
              <div className="space-y-3">
                {[
                  { label: 'URL Mappings', icon: LinkIcon, to: '/url-mappings', gradient: 'from-blue-500 to-blue-600' },
                  { label: 'Crawlers', icon: Settings, to: '/crawlers', gradient: 'from-purple-500 to-purple-600' },
                  { label: 'Crawl Jobs', icon: Activity, to: '/crawl-jobs', gradient: 'from-emerald-500 to-emerald-600' },
                  { label: 'Test URL', icon: TestTube, to: '/test', gradient: 'from-amber-500 to-amber-600' }
                ].map((action, index) => {
                  const IconComponent = action.icon;
                  return (
                    <Link
                      key={action.label}
                      to={action.to}
                      className="group/item flex items-center space-x-4 p-4 rounded-xl bg-white/50 dark:bg-gray-700/50 backdrop-blur-sm border border-white/30 dark:border-gray-600/30 hover:bg-white/70 dark:hover:bg-gray-700/70 hover:shadow-lg transition-all duration-200 hover:scale-[1.02]"
                    >
                      <div className={`p-2 bg-gradient-to-r ${action.gradient} rounded-lg shadow-md group-hover/item:shadow-lg transition-shadow duration-200`}>
                        <IconComponent className="h-4 w-4 text-white" />
                      </div>
                      <span className="font-medium text-gray-700 dark:text-gray-200 group-hover/item:text-gray-900 dark:group-hover/item:text-white transition-colors duration-200">{action.label}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;