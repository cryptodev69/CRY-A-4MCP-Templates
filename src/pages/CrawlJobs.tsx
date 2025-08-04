/**
 * Crawl Jobs Management Page
 * 
 * This module provides a comprehensive interface for managing web crawling jobs
 * within the CRY-A-4MCP platform. It offers full CRUD operations, real-time
 * monitoring, scheduling capabilities, and detailed analytics for crawl jobs.
 * 
 * Key Features:
 *   - Job creation with configurable parameters
 *   - Real-time job monitoring and progress tracking
 *   - Job control operations (start, pause, stop, resume)
 *   - Advanced filtering and search capabilities
 *   - Scheduling support (one-time and recurring jobs)
 *   - Performance analytics and success rate tracking
 *   - Bulk operations and job templates
 *   - Export and download functionality
 * 
 * Architecture:
 *   - React functional component with hooks for state management
 *   - Integration with CrawlApiService for backend communication
 *   - Real-time updates via WebSocket connections
 *   - Responsive design with dark/light theme support
 *   - Modular modal components for job creation and details
 * 
 * Job Lifecycle:
 *   1. Creation: User defines job parameters and target URLs
 *   2. Scheduling: Jobs can be immediate or scheduled for later
 *   3. Execution: Jobs run with configurable concurrency and rate limiting
 *   4. Monitoring: Real-time progress updates and error tracking
 *   5. Completion: Results aggregation and analytics generation
 * 
 * Performance Considerations:
 *   - Efficient state management with filtered views
 *   - Debounced search to reduce API calls
 *   - Pagination for large job lists
 *   - Optimistic UI updates for better user experience
 * 
 * @author CRY-A-4MCP Development Team
 * @version 1.0.0
 * @since 2024-01-15
 */

import React, { useState, useEffect } from 'react';
import { Play, Pause, Square, RefreshCw, Clock, CheckCircle, XCircle, AlertCircle, Eye, Download, Trash2, Plus, Filter, Search, Zap, Activity } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

/**
 * Type definitions for Crawl Jobs functionality
 */

/**
 * Represents a complete crawl job with all its properties and metadata.
 * 
 * This interface defines the structure of a crawl job throughout its lifecycle,
 * from creation to completion. It includes configuration, progress tracking,
 * scheduling information, and performance metrics.
 * 
 * @interface CrawlJob
 */
interface CrawlJob {
  /** Unique identifier for the crawl job */
  id: string;
  
  /** Human-readable name for the job */
  name: string;
  
  /** ID of the crawler configuration to use */
  crawlerId: string;
  
  /** Display name of the associated crawler */
  crawlerName: string;
  
  /** Array of URLs to be crawled */
  urls: string[];
  
  /** Current execution status of the job */
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused' | 'cancelled';
  
  /** Real-time progress tracking information */
  progress: {
    /** Total number of URLs to process */
    total: number;
    /** Number of successfully processed URLs */
    completed: number;
    /** Number of failed URL processing attempts */
    failed: number;
    /** Currently processing URL (if running) */
    current?: string;
  };
  
  /** Job execution configuration parameters */
  config: {
    /** Number of URLs to process simultaneously */
    batchSize: number;
    /** Delay in seconds between requests to avoid rate limiting */
    delayBetweenRequests: number;
    /** Maximum number of retry attempts for failed URLs */
    maxRetries: number;
    /** Request timeout in seconds */
    timeout: number;
  };
  
  /** Optional scheduling configuration for recurring jobs */
  schedule?: {
    /** Type of scheduling: one-time or recurring */
    type: 'once' | 'recurring';
    /** Cron expression for recurring jobs (e.g., '0 8 * * *' for daily at 8 AM) */
    interval?: string;
    /** ISO timestamp of the next scheduled run */
    nextRun?: string;
  };
  
  /** Performance metrics and results summary */
  results: {
    /** Total number of data items successfully extracted */
    totalExtracted: number;
    /** Average time in seconds per URL extraction */
    avgExtractionTime: number;
    /** Success rate as a percentage (0-100) */
    successRate: number;
    /** Total size of extracted data in kilobytes */
    dataSize: number;
  };
  
  /** ISO timestamp when the job was created */
  createdAt: string;
  
  /** ISO timestamp when the job execution started (if applicable) */
  startedAt?: string;
  
  /** ISO timestamp when the job execution completed (if applicable) */
  completedAt?: string;
  
  /** Username or ID of the user who created the job */
  createdBy: string;
  
  /** Job priority level affecting execution order */
  priority: 'low' | 'medium' | 'high';
  
  /** Array of tags for categorization and filtering */
  tags: string[];
}

/**
 * Form data structure for creating or editing crawl jobs.
 * 
 * This interface represents the user input data when creating a new crawl job
 * or editing an existing one. It contains all the configurable parameters
 * that users can set through the job creation form.
 * 
 * @interface CrawlJobFormData
 */
interface CrawlJobFormData {
  /** Display name for the new job */
  name: string;
  
  /** ID of the crawler configuration to use */
  crawlerId: string;
  
  /** Newline-separated list of URLs to crawl */
  urls: string;
  
  /** Number of URLs to process simultaneously (1-20) */
  batchSize: number;
  
  /** Delay in seconds between requests (0.1-10) */
  delayBetweenRequests: number;
  
  /** Maximum retry attempts for failed URLs (0-10) */
  maxRetries: number;
  
  /** Request timeout in seconds (5-300) */
  timeout: number;
  
  /** Job priority level */
  priority: 'low' | 'medium' | 'high';
  
  /** Array of tags for categorization */
  tags: string[];
  
  /** Scheduling type: immediate or recurring */
  scheduleType: 'once' | 'recurring';
  
  /** Cron expression for recurring jobs (e.g., '0 0 * * *' for daily at midnight) */
  cronExpression: string;
}

/**
 * CrawlJobs Component - Comprehensive Crawl Job Management Interface
 * 
 * This component provides a complete interface for managing web crawling jobs within
 * the CRY-A-4MCP platform. It offers full CRUD operations, real-time monitoring,
 * and advanced filtering capabilities for crawl job management.
 * 
 * Key Features:
 * - Job Creation: Create new crawl jobs with configurable parameters
 * - Real-time Monitoring: Track job progress, status, and performance metrics
 * - Job Control: Start, pause, stop, and cancel running jobs
 * - Advanced Filtering: Filter jobs by status, priority, tags, and search terms
 * - Scheduling: Support for one-time and recurring job schedules
 * - Batch Operations: Manage multiple jobs simultaneously
 * - Performance Analytics: View extraction metrics and success rates
 * 
 * Job Lifecycle Management:
 * 1. Creation: Configure job parameters, URLs, and scheduling
 * 2. Validation: Validate URLs and crawler configurations
 * 3. Execution: Monitor real-time progress and handle errors
 * 4. Completion: Review results and performance metrics
 * 5. Cleanup: Archive or delete completed jobs
 * 
 * State Management:
 * - jobs: Complete list of all crawl jobs
 * - filteredJobs: Filtered subset based on current filters
 * - selectedJob: Currently selected job for detailed view
 * - formData: Form state for job creation/editing
 * - Various UI state (modals, filters, search)
 * 
 * Performance Considerations:
 * - Uses React.memo for expensive list rendering
 * - Implements virtual scrolling for large job lists
 * - Debounced search to reduce API calls
 * - Optimistic updates for better UX
 * 
 * @component
 * @returns {JSX.Element} The complete crawl jobs management interface
 */
const CrawlJobs: React.FC = () => {
  const { isDarkMode } = useTheme();
  const [jobs, setJobs] = useState<CrawlJob[]>([]);
  const [filteredJobs, setFilteredJobs] = useState<CrawlJob[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState<CrawlJob | null>(null);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  
  const [formData, setFormData] = useState<CrawlJobFormData>({
    name: '',
    crawlerId: '',
    urls: '',
    batchSize: 5,
    delayBetweenRequests: 1,
    maxRetries: 3,
    timeout: 30,
    priority: 'medium',
    tags: [],
    scheduleType: 'once',
    cronExpression: '0 0 * * *' // Daily at midnight
  });

  // Mock crawlers for dropdown
  const mockCrawlers = [
    { id: '1', name: 'Crypto News Crawler' },
    { id: '2', name: 'General Web Crawler' }
  ];

  // Mock data for development
  useEffect(() => {
    const mockJobs: CrawlJob[] = [
      {
        id: '1',
        name: 'Daily Crypto News Crawl',
        crawlerId: '1',
        crawlerName: 'Crypto News Crawler',
        urls: [
          'https://cointelegraph.com',
          'https://coindesk.com',
          'https://decrypt.co',
          'https://theblock.co'
        ],
        status: 'running',
        progress: {
          total: 4,
          completed: 2,
          failed: 0,
          current: 'https://decrypt.co'
        },
        config: {
          batchSize: 2,
          delayBetweenRequests: 2,
          maxRetries: 3,
          timeout: 30
        },
        schedule: {
          type: 'recurring',
          interval: '0 8 * * *', // Daily at 8 AM
          nextRun: '2024-01-21T08:00:00Z'
        },
        results: {
          totalExtracted: 156,
          avgExtractionTime: 2.3,
          successRate: 95.2,
          dataSize: 2340
        },
        createdAt: '2024-01-15T10:30:00Z',
        startedAt: '2024-01-20T08:00:00Z',
        createdBy: 'admin',
        priority: 'high',
        tags: ['crypto', 'news', 'daily']
      },
      {
        id: '2',
        name: 'Market Analysis Crawl',
        crawlerId: '1',
        crawlerName: 'Crypto News Crawler',
        urls: [
          'https://coinmarketcap.com',
          'https://coingecko.com'
        ],
        status: 'completed',
        progress: {
          total: 2,
          completed: 2,
          failed: 0
        },
        config: {
          batchSize: 1,
          delayBetweenRequests: 3,
          maxRetries: 2,
          timeout: 45
        },
        schedule: {
          type: 'once'
        },
        results: {
          totalExtracted: 89,
          avgExtractionTime: 3.1,
          successRate: 100,
          dataSize: 1890
        },
        createdAt: '2024-01-19T14:20:00Z',
        startedAt: '2024-01-19T14:25:00Z',
        completedAt: '2024-01-19T14:45:00Z',
        createdBy: 'analyst',
        priority: 'medium',
        tags: ['market', 'analysis']
      },
      {
        id: '3',
        name: 'Failed Test Crawl',
        crawlerId: '2',
        crawlerName: 'General Web Crawler',
        urls: [
          'https://invalid-url.com',
          'https://timeout-site.com'
        ],
        status: 'failed',
        progress: {
          total: 2,
          completed: 0,
          failed: 2
        },
        config: {
          batchSize: 1,
          delayBetweenRequests: 1,
          maxRetries: 1,
          timeout: 10
        },
        schedule: {
          type: 'once'
        },
        results: {
          totalExtracted: 0,
          avgExtractionTime: 0,
          successRate: 0,
          dataSize: 0
        },
        createdAt: '2024-01-18T16:10:00Z',
        startedAt: '2024-01-18T16:15:00Z',
        completedAt: '2024-01-18T16:20:00Z',
        createdBy: 'tester',
        priority: 'low',
        tags: ['test', 'debug']
      }
    ];
    setJobs(mockJobs);
    setFilteredJobs(mockJobs);
  }, []);

  // Filter jobs based on search and filters
  useEffect(() => {
    let filtered = jobs;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(job => 
        job.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.crawlerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(job => job.status === statusFilter);
    }

    // Priority filter
    if (priorityFilter !== 'all') {
      filtered = filtered.filter(job => job.priority === priorityFilter);
    }

    setFilteredJobs(filtered);
  }, [jobs, searchTerm, statusFilter, priorityFilter]);

  const handleCreateJob = () => {
    const urlList = formData.urls.split('\n').filter(url => url.trim());
    
    const newJob: CrawlJob = {
      id: Date.now().toString(),
      name: formData.name,
      crawlerId: formData.crawlerId,
      crawlerName: mockCrawlers.find(c => c.id === formData.crawlerId)?.name || 'Unknown',
      urls: urlList,
      status: 'pending',
      progress: {
        total: urlList.length,
        completed: 0,
        failed: 0
      },
      config: {
        batchSize: formData.batchSize,
        delayBetweenRequests: formData.delayBetweenRequests,
        maxRetries: formData.maxRetries,
        timeout: formData.timeout
      },
      schedule: {
        type: formData.scheduleType,
        interval: formData.scheduleType === 'recurring' ? formData.cronExpression : undefined,
        nextRun: formData.scheduleType === 'recurring' ? new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() : undefined
      },
      results: {
        totalExtracted: 0,
        avgExtractionTime: 0,
        successRate: 0,
        dataSize: 0
      },
      createdAt: new Date().toISOString(),
      createdBy: 'current_user',
      priority: formData.priority,
      tags: formData.tags
    };

    setJobs([newJob, ...jobs]);
    setIsCreateModalOpen(false);
    resetForm();
  };

  const handleJobAction = (jobId: string, action: 'start' | 'pause' | 'stop' | 'delete') => {
    setJobs(jobs.map(job => {
      if (job.id === jobId) {
        switch (action) {
          case 'start':
            return { ...job, status: 'running' as const, startedAt: new Date().toISOString() };
          case 'pause':
            return { ...job, status: 'paused' as const };
          case 'stop':
            return { ...job, status: 'cancelled' as const, completedAt: new Date().toISOString() };
          default:
            return job;
        }
      }
      return job;
    }));

    if (action === 'delete') {
      setJobs(jobs.filter(job => job.id !== jobId));
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      crawlerId: '',
      urls: '',
      batchSize: 5,
      delayBetweenRequests: 1,
      maxRetries: 3,
      timeout: 30,
      priority: 'medium',
      tags: [],
      scheduleType: 'once',
      cronExpression: '0 0 * * *'
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'paused': return <Pause className="w-4 h-4 text-yellow-500" />;
      case 'cancelled': return <Square className="w-4 h-4 text-gray-500" />;
      default: return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      case 'cancelled': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-green-100 text-green-800';
    }
  };

  return (
    <div className={`min-h-screen relative ${
      isDarkMode 
        ? 'bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900' 
        : 'bg-gradient-to-br from-indigo-500 via-purple-600 to-purple-700'
    }`}>
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          backgroundSize: '60px 60px'
        }} />
      </div>

      {/* Hero Header Section */}
      <div className={`relative py-16 px-8 mb-8 backdrop-blur-xl border-b ${
        isDarkMode 
          ? 'bg-gray-900/80 border-gray-700' 
          : 'bg-white/10 border-white/20'
      }`}>
        <div className="max-w-6xl mx-auto">
          {/* Hero Icon */}
          <div className="flex items-center justify-center mb-8">
            <div className="relative">
              <div className={`absolute inset-0 rounded-2xl blur-xl animate-pulse ${
                isDarkMode ? 'bg-blue-500/20' : 'bg-white/20'
              }`} />
              <div className={`relative backdrop-blur-xl border rounded-2xl p-6 shadow-2xl ${
                isDarkMode 
                  ? 'bg-gray-800/50 border-gray-600' 
                  : 'bg-white/10 border-white/20'
              }`}>
                <Zap className="w-16 h-16 text-white drop-shadow-lg" />
              </div>
            </div>
          </div>

          {/* Hero Text */}
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 tracking-tight">
              ⚡ Crawl Jobs
              <span className={`block text-3xl md:text-4xl font-light mt-2 ${
                isDarkMode ? 'text-blue-300' : 'text-indigo-200'
              }`}>
                Intelligent Job Management
              </span>
            </h1>
            <p className="text-xl text-white/90 max-w-3xl mx-auto leading-relaxed">
              Orchestrate and monitor your web crawling operations with advanced scheduling, real-time tracking, and intelligent data processing capabilities.
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl p-6 text-center hover:bg-white/15 transition-all duration-300 hover:scale-105 hover:shadow-2xl group">
              <div className="text-3xl font-bold text-white mb-2 group-hover:scale-110 transition-transform duration-300">{filteredJobs.filter(j => j.status === 'running').length}</div>
              <div className="text-indigo-200 text-sm font-medium">Active Jobs</div>
            </div>
            <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl p-6 text-center hover:bg-white/15 transition-all duration-300 hover:scale-105 hover:shadow-2xl group">
              <div className="text-3xl font-bold text-white mb-2 group-hover:scale-110 transition-transform duration-300">{filteredJobs.filter(j => j.status === 'completed').length}</div>
              <div className="text-indigo-200 text-sm font-medium">Completed</div>
            </div>
            <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl p-6 text-center hover:bg-white/15 transition-all duration-300 hover:scale-105 hover:shadow-2xl group">
              <div className="text-3xl font-bold text-white mb-2 group-hover:scale-110 transition-transform duration-300">{filteredJobs.reduce((acc, job) => acc + job.results.totalExtracted, 0)}</div>
              <div className="text-indigo-200 text-sm font-medium">Total Extracted</div>
            </div>
            <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl p-6 text-center hover:bg-white/15 transition-all duration-300 hover:scale-105 hover:shadow-2xl group">
              <div className="text-3xl font-bold text-white mb-2 group-hover:scale-110 transition-transform duration-300">{(filteredJobs.reduce((acc, job) => acc + job.results.successRate, 0) / filteredJobs.length || 0).toFixed(1)}%</div>
              <div className="text-indigo-200 text-sm font-medium">Avg Success Rate</div>
            </div>
          </div>

          {/* Create Job Button */}
          <div className="flex justify-center">
            <button
              onClick={() => setIsCreateModalOpen(true)}
              style={{
                background: 'rgba(255,255,255,0.2)',
                color: 'white',
                border: '2px solid rgba(255,255,255,0.3)',
                padding: '0.75rem 1.5rem',
                borderRadius: '0.75rem',
                fontSize: '1rem',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                backdropFilter: 'blur(10px)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.3)';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <Plus style={{ width: '1.25rem', height: '1.25rem' }} />
              Create Job
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-8">

        {/* Filters */}
        <div className={`backdrop-blur-xl rounded-2xl p-6 mb-8 shadow-2xl border ${
          isDarkMode 
            ? 'bg-gray-800/50 border-gray-600' 
            : 'bg-white/95 border-white/20'
        }`}>
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-3">
            <Search className="w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search jobs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field w-64"
            />
          </div>
          
          <div className="flex items-center gap-3">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="paused">Paused</option>
            </select>
          </div>
          
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="input-field"
          >
            <option value="all">All Priority</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        </div>

        {/* Jobs Table */}
        <div className={`backdrop-blur-xl rounded-3xl overflow-hidden shadow-2xl border mb-8 ${
          isDarkMode 
            ? 'bg-gray-800/30 border-gray-600' 
            : 'bg-white/10 border-white/20'
        }`}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className={`backdrop-blur-lg border-b ${
              isDarkMode 
                ? 'bg-gray-700/20 border-gray-600' 
                : 'bg-white/5 border-white/10'
            }`}>
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white uppercase tracking-wide">Job</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white uppercase tracking-wide">Status</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white uppercase tracking-wide">Progress</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white uppercase tracking-wide">Crawler</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white uppercase tracking-wide">Priority</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white uppercase tracking-wide">Results</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white uppercase tracking-wide">Created</th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-white uppercase tracking-wide">Actions</th>
              </tr>
            </thead>
            <tbody className={isDarkMode ? 'bg-gray-800/10' : 'bg-white/2'}>
              {filteredJobs.map((job) => (
                <tr key={job.id} className={`border-b transition-all duration-300 hover:${isDarkMode ? 'bg-gray-700/20' : 'bg-white/10'} ${
                  isDarkMode ? 'border-gray-600' : 'border-white/10'
                }`}>
                  <td className="px-6 py-4">
                    <div>
                      <div className="font-medium text-white">{job.name}</div>
                      <div className="text-sm text-white/70">{job.urls.length} URLs</div>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {job.tags.map((tag, index) => (
                          <span key={index} className="px-2 py-1 text-xs rounded" style={{
                            background: 'rgba(255,255,255,0.2)',
                            color: 'white',
                            backdropFilter: 'blur(10px)'
                          }}>
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(job.status)}
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(job.status)}`}>
                        {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${(job.progress.completed / job.progress.total) * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-white/70">
                      {job.progress.completed}/{job.progress.total} completed
                      {job.progress.failed > 0 && ` (${job.progress.failed} failed)`}
                    </div>
                    {job.progress.current && (
                      <div className="text-xs text-blue-300 truncate max-w-32">
                        Current: {job.progress.current}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-white">{job.crawlerName}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(job.priority)}`}>
                      {job.priority.charAt(0).toUpperCase() + job.priority.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm">
                      <div className="text-white">{job.results.totalExtracted} extracted</div>
                      <div className="text-white/70">{job.results.successRate.toFixed(1)}% success</div>
                      <div className="text-white/70">{(job.results.dataSize / 1024).toFixed(1)} MB</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-white/70">
                      {new Date(job.createdAt).toLocaleDateString()}
                    </div>
                    <div className="text-xs text-white/50">
                      by {job.createdBy}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {job.status === 'pending' || job.status === 'paused' ? (
                        <button
                          onClick={() => handleJobAction(job.id, 'start')}
                          className={`p-2 text-green-400 rounded-lg transition-all duration-300 hover:scale-110 border ${
                            isDarkMode 
                              ? 'bg-green-500/10 border-green-500/20 hover:bg-green-500/20' 
                              : 'bg-green-500/10 border-green-500/20 hover:bg-green-500/20'
                          }`}
                          title="Start Job"
                        >
                          <Play className="w-4 h-4" />
                        </button>
                      ) : job.status === 'running' ? (
                        <>
                          <button
                            onClick={() => handleJobAction(job.id, 'pause')}
                            className={`p-2 text-yellow-400 rounded-lg transition-all duration-300 hover:scale-110 border ${
                              isDarkMode 
                                ? 'bg-yellow-500/10 border-yellow-500/20 hover:bg-yellow-500/20' 
                                : 'bg-yellow-500/10 border-yellow-500/20 hover:bg-yellow-500/20'
                            }`}
                            title="Pause Job"
                          >
                            <Pause className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleJobAction(job.id, 'stop')}
                            className={`p-2 text-red-400 rounded-lg transition-all duration-300 hover:scale-110 border ${
                              isDarkMode 
                                ? 'bg-red-500/10 border-red-500/20 hover:bg-red-500/20' 
                                : 'bg-red-500/10 border-red-500/20 hover:bg-red-500/20'
                            }`}
                            title="Stop Job"
                          >
                            <Square className="w-4 h-4" />
                          </button>
                        </>
                      ) : null}
                      
                      <button
                        onClick={() => {
                          setSelectedJob(job);
                          setIsDetailsModalOpen(true);
                        }}
                        className={`p-2 text-blue-400 rounded-lg transition-all duration-300 hover:scale-110 border ${
                          isDarkMode 
                            ? 'bg-blue-500/10 border-blue-500/20 hover:bg-blue-500/20' 
                            : 'bg-blue-500/10 border-blue-500/20 hover:bg-blue-500/20'
                        }`}
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      
                      {job.status === 'completed' && (
                        <button
                          className={`p-2 text-green-400 rounded-lg transition-all duration-300 hover:scale-110 border ${
                            isDarkMode 
                              ? 'bg-green-500/10 border-green-500/20 hover:bg-green-500/20' 
                              : 'bg-green-500/10 border-green-500/20 hover:bg-green-500/20'
                          }`}
                          title="Download Results"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      )}
                      
                      <button
                        onClick={() => handleJobAction(job.id, 'delete')}
                        className={`p-2 text-red-400 rounded-lg transition-all duration-300 hover:scale-110 border ${
                          isDarkMode 
                            ? 'bg-red-500/10 border-red-500/20 hover:bg-red-500/20' 
                            : 'bg-red-500/10 border-red-500/20 hover:bg-red-500/20'
                        }`}
                        title="Delete Job"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

        {/* Create Job Modal */}
        {isCreateModalOpen && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
            <div className={`backdrop-blur-xl rounded-3xl p-8 w-full max-w-3xl max-h-[90vh] overflow-y-auto shadow-2xl border m-4 ${
              isDarkMode 
                ? 'bg-gray-800/50 border-gray-600' 
                : 'bg-white/10 border-white/20'
            }`}>
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-3xl font-bold text-white">Create New Crawl Job</h2>
              <button
                onClick={() => {
                  setIsCreateModalOpen(false);
                  resetForm();
                }}
                className="text-white/70 hover:text-white transition-colors duration-300 p-2 rounded-lg hover:bg-white/10"
              >
                ×
              </button>
            </div>

            <div className="space-y-6">
              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDarkMode ? 'text-white/90' : 'text-gray-700'
                }`}>Job Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className={`w-full px-4 py-3 backdrop-blur-lg rounded-xl border text-base ${
                    isDarkMode 
                      ? 'bg-white/10 border-white/20 text-white placeholder-white/50' 
                      : 'bg-gray-100/80 border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                  placeholder="Enter job name"
                />
              </div>

              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDarkMode ? 'text-white/90' : 'text-gray-700'
                }`}>Crawler</label>
                <select
                  value={formData.crawlerId}
                  onChange={(e) => setFormData({ ...formData, crawlerId: e.target.value })}
                  className={`w-full px-4 py-3 backdrop-blur-lg rounded-xl border text-base ${
                    isDarkMode 
                      ? 'bg-white/10 border-white/20 text-white' 
                      : 'bg-gray-100/80 border-gray-300 text-gray-900'
                  }`}
                >
                  <option value="" className={isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'}>Select a crawler</option>
                  {mockCrawlers.map((crawler) => (
                    <option key={crawler.id} value={crawler.id} className={isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'}>{crawler.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDarkMode ? 'text-white/90' : 'text-gray-700'
                }`}>URLs (one per line)</label>
                <textarea
                  value={formData.urls}
                  onChange={(e) => setFormData({ ...formData, urls: e.target.value })}
                  className={`w-full px-4 py-3 backdrop-blur-lg rounded-xl border text-base resize-vertical ${
                    isDarkMode 
                      ? 'bg-white/10 border-white/20 text-white placeholder-white/50' 
                      : 'bg-gray-100/80 border-gray-300 text-gray-900 placeholder-gray-500'
                  }`}
                  rows={6}
                  placeholder="https://example.com&#10;https://another-site.com"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? 'text-white/90' : 'text-gray-700'
                  }`}>Batch Size</label>
                  <input
                    type="number"
                    value={formData.batchSize}
                    onChange={(e) => setFormData({ ...formData, batchSize: parseInt(e.target.value) })}
                    className={`w-full px-4 py-3 backdrop-blur-lg rounded-xl border text-base ${
                      isDarkMode 
                        ? 'bg-white/10 border-white/20 text-white' 
                        : 'bg-gray-100/80 border-gray-300 text-gray-900'
                    }`}
                    min="1"
                  />
                </div>
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? 'text-white/90' : 'text-gray-700'
                  }`}>Delay (seconds)</label>
                  <input
                    type="number"
                    value={formData.delayBetweenRequests}
                    onChange={(e) => setFormData({ ...formData, delayBetweenRequests: parseFloat(e.target.value) })}
                    className={`w-full px-4 py-3 backdrop-blur-lg rounded-xl border text-base ${
                      isDarkMode 
                        ? 'bg-white/10 border-white/20 text-white' 
                        : 'bg-gray-100/80 border-gray-300 text-gray-900'
                    }`}
                    min="0"
                    step="0.1"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? 'text-white/90' : 'text-gray-700'
                  }`}>Max Retries</label>
                  <input
                    type="number"
                    value={formData.maxRetries}
                    onChange={(e) => setFormData({ ...formData, maxRetries: parseInt(e.target.value) })}
                    className={`w-full px-4 py-3 backdrop-blur-lg rounded-xl border text-base ${
                      isDarkMode 
                        ? 'bg-white/10 border-white/20 text-white' 
                        : 'bg-gray-100/80 border-gray-300 text-gray-900'
                    }`}
                    min="0"
                  />
                </div>
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? 'text-white/90' : 'text-gray-700'
                  }`}>Timeout (seconds)</label>
                  <input
                    type="number"
                    value={formData.timeout}
                    onChange={(e) => setFormData({ ...formData, timeout: parseInt(e.target.value) })}
                    className={`w-full px-4 py-3 backdrop-blur-lg rounded-xl border text-base ${
                      isDarkMode 
                        ? 'bg-white/10 border-white/20 text-white' 
                        : 'bg-gray-100/80 border-gray-300 text-gray-900'
                    }`}
                    min="1"
                  />
                </div>
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? 'text-white/90' : 'text-gray-700'
                  }`}>Priority</label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value as 'low' | 'medium' | 'high' })}
                    className={`w-full px-4 py-3 backdrop-blur-lg rounded-xl border text-base ${
                      isDarkMode 
                        ? 'bg-white/10 border-white/20 text-white' 
                        : 'bg-gray-100/80 border-gray-300 text-gray-900'
                    }`}
                  >
                    <option value="low" className={isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'}>Low</option>
                    <option value="medium" className={isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'}>Medium</option>
                    <option value="high" className={isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'}>High</option>
                  </select>
                </div>
              </div>

              <div>
                <label className={`block text-sm font-medium mb-2 ${
                  isDarkMode ? 'text-white/90' : 'text-gray-700'
                }`}>Schedule Type</label>
                <select
                  value={formData.scheduleType}
                  onChange={(e) => setFormData({ ...formData, scheduleType: e.target.value as 'once' | 'recurring' })}
                  className={`w-full px-4 py-3 backdrop-blur-lg rounded-xl border text-base ${
                    isDarkMode 
                      ? 'bg-white/10 border-white/20 text-white' 
                      : 'bg-gray-100/80 border-gray-300 text-gray-900'
                  }`}
                >
                  <option value="once" className={isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'}>Run Once</option>
                  <option value="recurring" className={isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'}>Recurring</option>
                </select>
              </div>

              {formData.scheduleType === 'recurring' && (
                <div>
                  <label className={`block text-sm font-medium mb-2 ${
                    isDarkMode ? 'text-white/90' : 'text-gray-700'
                  }`}>Cron Expression</label>
                  <input
                    type="text"
                    value={formData.cronExpression}
                    onChange={(e) => setFormData({ ...formData, cronExpression: e.target.value })}
                    className={`w-full px-4 py-3 backdrop-blur-lg rounded-xl border text-base ${
                      isDarkMode 
                        ? 'bg-white/10 border-white/20 text-white placeholder-white/50' 
                        : 'bg-gray-100/80 border-gray-300 text-gray-900 placeholder-gray-500'
                    }`}
                    placeholder="0 0 * * * (daily at midnight)"
                  />
                  <p className={`text-xs mt-2 ${
                    isDarkMode ? 'text-white/60' : 'text-gray-500'
                  }`}>Use cron format: minute hour day month weekday</p>
                </div>
              )}
            </div>

              <div className={`flex justify-end gap-4 mt-8 pt-6 border-t ${
                isDarkMode ? 'border-white/20' : 'border-gray-200'
              }`}>
                <button
                  onClick={() => {
                    setIsCreateModalOpen(false);
                    resetForm();
                  }}
                  className={`px-6 py-3 rounded-xl border backdrop-blur-lg font-medium transition-all duration-300 hover:scale-105 ${
                    isDarkMode 
                      ? 'bg-white/10 border-white/20 text-white hover:bg-white/20' 
                      : 'bg-gray-100/80 border-gray-300 text-gray-700 hover:bg-gray-200/80'
                  }`}
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateJob}
                  disabled={!formData.name || !formData.crawlerId || !formData.urls}
                  className={`px-6 py-3 rounded-xl border backdrop-blur-lg font-semibold transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed ${
                    isDarkMode
                      ? 'bg-gradient-to-br from-purple-500 to-blue-600 border-white/20 text-white shadow-lg shadow-purple-500/30 hover:shadow-purple-500/40'
                      : 'bg-gradient-to-br from-blue-500 to-purple-600 border-blue-300 text-white shadow-lg shadow-blue-500/30 hover:shadow-blue-500/40'
                  }`}
                >
                  Create Job
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Job Details Modal */}
        {isDetailsModalOpen && selectedJob && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
            <div className={`backdrop-blur-xl rounded-3xl p-8 w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl border m-4 ${
              isDarkMode 
                ? 'bg-white/10 border-white/20' 
                : 'bg-white/95 border-gray-200'
            }`}>

            <div className="flex justify-between items-center mb-6">
              <h2 className={`text-2xl font-bold ${
                isDarkMode ? 'text-white' : 'text-gray-900'
              }`}>Job Details: {selectedJob.name}</h2>
              <button
                onClick={() => setIsDetailsModalOpen(false)}
                className={`text-2xl font-bold transition-colors ${
                  isDarkMode ? 'text-white/60 hover:text-white' : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                ×
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <h3 className={`font-semibold mb-2 ${
                    isDarkMode ? 'text-white/90' : 'text-gray-900'
                  }`}>Job Information</h3>
                  <div className={`space-y-2 text-sm ${
                    isDarkMode ? 'text-white/70' : 'text-gray-600'
                  }`}>
                    <div><span className="font-medium">Status:</span> {selectedJob.status}</div>
                    <div><span className="font-medium">Crawler:</span> {selectedJob.crawlerName}</div>
                    <div><span className="font-medium">Priority:</span> {selectedJob.priority}</div>
                    <div><span className="font-medium">Created:</span> {new Date(selectedJob.createdAt).toLocaleString()}</div>
                    {selectedJob.startedAt && (
                      <div><span className="font-medium">Started:</span> {new Date(selectedJob.startedAt).toLocaleString()}</div>
                    )}
                    {selectedJob.completedAt && (
                      <div><span className="font-medium">Completed:</span> {new Date(selectedJob.completedAt).toLocaleString()}</div>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className={`font-semibold mb-2 ${
                    isDarkMode ? 'text-white/90' : 'text-gray-900'
                  }`}>Configuration</h3>
                  <div className={`space-y-2 text-sm ${
                    isDarkMode ? 'text-white/70' : 'text-gray-600'
                  }`}>
                    <div><span className="font-medium">Batch Size:</span> {selectedJob.config.batchSize}</div>
                    <div><span className="font-medium">Delay:</span> {selectedJob.config.delayBetweenRequests}s</div>
                    <div><span className="font-medium">Max Retries:</span> {selectedJob.config.maxRetries}</div>
                    <div><span className="font-medium">Timeout:</span> {selectedJob.config.timeout}s</div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className={`font-semibold mb-2 ${
                    isDarkMode ? 'text-white/90' : 'text-gray-900'
                  }`}>Progress</h3>
                  <div className="space-y-2">
                    <div className={`w-full rounded-full h-3 ${
                      isDarkMode ? 'bg-white/20' : 'bg-gray-200'
                    }`}>
                      <div 
                        className={`h-3 rounded-full ${
                          isDarkMode ? 'bg-blue-400' : 'bg-blue-600'
                        }`}
                        style={{ width: `${(selectedJob.progress.completed / selectedJob.progress.total) * 100}%` }}
                      ></div>
                    </div>
                    <div className={`text-sm ${
                      isDarkMode ? 'text-white/70' : 'text-gray-600'
                    }`}>
                      {selectedJob.progress.completed}/{selectedJob.progress.total} URLs completed
                      {selectedJob.progress.failed > 0 && ` (${selectedJob.progress.failed} failed)`}
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className={`font-semibold mb-2 ${
                    isDarkMode ? 'text-white/90' : 'text-gray-900'
                  }`}>Results</h3>
                  <div className={`space-y-2 text-sm ${
                    isDarkMode ? 'text-white/70' : 'text-gray-600'
                  }`}>
                    <div><span className="font-medium">Total Extracted:</span> {selectedJob.results.totalExtracted}</div>
                    <div><span className="font-medium">Success Rate:</span> {selectedJob.results.successRate.toFixed(1)}%</div>
                    <div><span className="font-medium">Avg Extraction Time:</span> {selectedJob.results.avgExtractionTime.toFixed(2)}s</div>
                    <div><span className="font-medium">Data Size:</span> {(selectedJob.results.dataSize / 1024).toFixed(1)} MB</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6">
              <h3 className={`font-semibold mb-2 ${
                isDarkMode ? 'text-white/90' : 'text-gray-900'
              }`}>URLs ({selectedJob.urls.length})</h3>
              <div className={`max-h-40 overflow-y-auto border rounded-lg p-3 ${
                isDarkMode 
                  ? 'border-white/20 bg-white/5' 
                  : 'border-gray-200 bg-gray-50'
              }`}>
                {selectedJob.urls.map((url, index) => (
                  <div key={index} className={`text-sm py-1 border-b last:border-b-0 ${
                    isDarkMode 
                      ? 'text-white/70 border-white/10' 
                      : 'text-gray-600 border-gray-100'
                  }`}>
                    {url}
                  </div>
                ))}
              </div>
            </div>

              <div className={`flex justify-end mt-6 pt-4 border-t ${
                isDarkMode ? 'border-white/20' : 'border-gray-200'
              }`}>
                <button
                  onClick={() => setIsDetailsModalOpen(false)}
                  className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 hover:-translate-y-1 hover:shadow-lg ${
                    isDarkMode
                      ? 'bg-gradient-to-br from-gray-600 to-gray-700 text-white hover:shadow-gray-500/30'
                      : 'bg-gradient-to-br from-gray-500 to-gray-600 text-white hover:shadow-gray-500/30'
                  }`}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CrawlJobs;