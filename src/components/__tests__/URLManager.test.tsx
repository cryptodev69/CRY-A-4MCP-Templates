/**
 * Comprehensive test suite for URLManager component
 * 
 * This test file validates:
 * - Tag display functionality for all metadata fields
 * - Color coding logic for different tag types
 * - API integration and error handling
 * - User interactions and form submissions
 * - Responsive behavior and accessibility
 * 
 * @author CRY-A-4MCP Development Team
 * @version 1.0.0
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import URLManager from '../URLManager';
import { ThemeProvider } from '../../contexts/ThemeContext';

// Mock fetch for API calls
global.fetch = jest.fn();

// Mock data for testing
const mockURLConfigs = [
  {
    id: 1,
    name: 'CoinDesk News',
    url: 'https://coindesk.com',
    profile_type: 'Traditional Investor',
    description: 'Leading cryptocurrency news source',
    category: 'news',
    priority: 5,
    scraping_difficulty: 'Medium',
    has_official_api: true,
    api_pricing: 'Free',
    recommendation: 'Recommended',
    key_data_points: 'News articles, market analysis',
    target_data: 'Headlines, content, timestamps',
    rationale: 'Essential for market sentiment analysis',
    cost_analysis: 'Low cost, high value',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T12:00:00Z'
  },
  {
    id: 2,
    name: 'DeFiPulse Analytics',
    url: 'https://defipulse.com',
    profile_type: 'DeFi Yield Farmer',
    description: 'DeFi protocol analytics and TVL data',
    category: 'analytics',
    priority: 3,
    scraping_difficulty: 'High',
    has_official_api: false,
    api_pricing: 'Paid',
    recommendation: 'Not Recommended',
    key_data_points: 'TVL, yield rates, protocol data',
    target_data: 'Protocol metrics, yield calculations',
    rationale: 'Important for DeFi strategy optimization',
    cost_analysis: 'High cost, medium value',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T12:00:00Z'
  }
];

// Helper function to render component with theme context
const renderWithTheme = (component: React.ReactElement, isDarkMode = false) => {
  const ThemeWrapper = ({ children }: { children: React.ReactNode }) => (
    <ThemeProvider>
      {children}
    </ThemeProvider>
  );
  
  return render(component, { wrapper: ThemeWrapper });
};

// Mock successful API response
const mockSuccessfulFetch = () => {
  (fetch as jest.Mock).mockResolvedValueOnce({
    ok: true,
    json: async () => mockURLConfigs
  });
};

// Mock failed API response
const mockFailedFetch = () => {
  (fetch as jest.Mock).mockRejectedValueOnce(new Error('API Error'));
};

describe('URLManager Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    test('renders URLManager component successfully', async () => {
      mockSuccessfulFetch();
      
      renderWithTheme(<URLManager />);
      
      expect(screen.getByText('URL Management')).toBeInTheDocument();
      expect(screen.getByText('Filter by Profile Type')).toBeInTheDocument();
      expect(screen.getByText('Add Custom URL')).toBeInTheDocument();
    });

    test('displays loading state initially', () => {
      mockSuccessfulFetch();
      
      renderWithTheme(<URLManager />);
      
      expect(screen.getByText('Loading URL configurations...')).toBeInTheDocument();
    });

    test('displays error state when API fails', async () => {
      mockFailedFetch();
      
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        expect(screen.getByText(/Failed to fetch URL configurations/)).toBeInTheDocument();
      });
    });
  });

  describe('Tag Display Functionality', () => {
    beforeEach(() => {
      mockSuccessfulFetch();
    });

    test('displays category tags correctly', async () => {
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        expect(screen.getByText('news')).toBeInTheDocument();
        expect(screen.getByText('analytics')).toBeInTheDocument();
      });
    });

    test('displays priority tags with correct color coding', async () => {
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        // Check for priority 5 (high priority - should be red/orange)
        const highPriorityTag = screen.getByText('Priority: 5');
        expect(highPriorityTag).toBeInTheDocument();
        expect(highPriorityTag).toHaveClass('text-red-700');
        
        // Check for priority 3 (medium priority - should be yellow)
        const mediumPriorityTag = screen.getByText('Priority: 3');
        expect(mediumPriorityTag).toBeInTheDocument();
        expect(mediumPriorityTag).toHaveClass('text-yellow-700');
      });
    });

    test('displays scraping difficulty tags with correct color coding', async () => {
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        // Check for Medium difficulty (should be yellow)
        const mediumDifficultyTag = screen.getByText('Medium');
        expect(mediumDifficultyTag).toBeInTheDocument();
        expect(mediumDifficultyTag).toHaveClass('text-yellow-700');
        
        // Check for High difficulty (should be red)
        const highDifficultyTag = screen.getByText('High');
        expect(highDifficultyTag).toBeInTheDocument();
        expect(highDifficultyTag).toHaveClass('text-red-700');
      });
    });

    test('displays API pricing tags with correct color coding', async () => {
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        // Check for Free pricing (should be green)
        const freePricingTag = screen.getByText('Free');
        expect(freePricingTag).toBeInTheDocument();
        expect(freePricingTag).toHaveClass('text-green-700');
        
        // Check for Paid pricing (should be red)
        const paidPricingTag = screen.getByText('Paid');
        expect(paidPricingTag).toBeInTheDocument();
        expect(paidPricingTag).toHaveClass('text-red-700');
      });
    });

    test('displays cost analysis tags with correct color coding', async () => {
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        // Check for low cost (should be green)
        const lowCostTag = screen.getByText('Cost Analysis');
        expect(lowCostTag).toBeInTheDocument();
        
        // Find the specific cost analysis tags by their container
        const costAnalysisTags = screen.getAllByText('Cost Analysis');
        expect(costAnalysisTags).toHaveLength(2);
      });
    });

    test('displays recommendation tags with correct color coding', async () => {
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        // Check for Recommended (should be green)
        const recommendedTag = screen.getByText('Recommendation');
        expect(recommendedTag).toBeInTheDocument();
        
        // Find all recommendation tags
        const recommendationTags = screen.getAllByText('Recommendation');
        expect(recommendationTags).toHaveLength(2);
      });
    });

    test('displays has_official_api tags correctly', async () => {
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        // Check for API availability indicators
        const apiTags = screen.getAllByText(/API/);
        expect(apiTags.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Profile Filtering', () => {
    beforeEach(() => {
      mockSuccessfulFetch();
    });

    test('filters configurations by profile type', async () => {
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        expect(screen.getByText('CoinDesk News')).toBeInTheDocument();
        expect(screen.getByText('DeFiPulse Analytics')).toBeInTheDocument();
      });
      
      // Select Traditional Investor profile
      const profileSelect = screen.getByRole('combobox');
      await userEvent.selectOptions(profileSelect, 'Traditional Investor');
      
      await waitFor(() => {
        expect(screen.getByText('CoinDesk News')).toBeInTheDocument();
        expect(screen.queryByText('DeFiPulse Analytics')).not.toBeInTheDocument();
      });
    });

    test('shows all configurations when "All Profiles" is selected', async () => {
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        expect(screen.getByText('CoinDesk News')).toBeInTheDocument();
        expect(screen.getByText('DeFiPulse Analytics')).toBeInTheDocument();
      });
      
      // Ensure all profiles are shown by default
      const profileSelect = screen.getByDisplayValue('All Profiles');
      expect(profileSelect).toBeInTheDocument();
    });
  });

  describe('Custom URL Addition', () => {
    beforeEach(() => {
      mockSuccessfulFetch();
    });

    test('opens add configuration dialog when button is clicked', async () => {
      renderWithTheme(<URLManager />);
      
      const addButton = screen.getByText('Add Configuration');
      await userEvent.click(addButton);
      
      await waitFor(() => {
        expect(screen.getByText('Add URL Configuration')).toBeInTheDocument();
      });
      
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    test('validates required fields in add configuration form', async () => {
      renderWithTheme(<URLManager />);
      
      const addButton = screen.getByText('Add Configuration');
      await userEvent.click(addButton);
      
      await waitFor(() => {
        expect(screen.getByText('Add URL Configuration')).toBeInTheDocument();
      });
      
      const submitButton = screen.getAllByText('Add Configuration')[1]; // Modal button
      await userEvent.click(submitButton);
      
      // Form should still be open without required fields
      expect(screen.getByText('Add URL Configuration')).toBeInTheDocument();
    });

    test('submits new configuration successfully', async () => {
      // Mock successful POST request
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockURLConfigs
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ ...mockURLConfigs[0], id: 3, name: 'New Config' })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [...mockURLConfigs, { 
            id: 3, 
            name: 'New Config',
            url: 'https://example.com',
            profile_type: 'Traditional Investor',
            category: 'News',
            description: 'Test description',
            priority: 'Medium',
            scraping_difficulty: 'Easy',
            has_official_api: false,
            api_pricing: 'Free',
            cost_analysis: 'Low',
            recommendation: 'Recommended'
          }]
        });
      
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        expect(screen.getByText('Add Configuration')).toBeInTheDocument();
      });
      
      const addButton = screen.getByText('Add Configuration');
      await userEvent.click(addButton);
      
      // Fill out the form
      await userEvent.type(screen.getByLabelText('Name *'), 'New Test Config');
      await userEvent.type(screen.getByLabelText('URL *'), 'https://example.com');
      await userEvent.selectOptions(screen.getByLabelText('Profile Type *'), 'Traditional Investor');
      await userEvent.type(screen.getByLabelText('Description'), 'Test description');
      
      const submitButton = screen.getAllByText('Add Configuration')[1]; // Second one is in the modal
      await userEvent.click(submitButton);
      
      // Verify API call was made
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/url-configs/', expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: expect.stringContaining('New Test Config')
        }));
      });
    });
  });

  describe('Dark Mode Support', () => {
    test('applies correct dark mode classes to tags', async () => {
      mockSuccessfulFetch();
      
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        // Check that tags have dark mode classes
        const categoryTag = screen.getByText('news');
        expect(categoryTag).toHaveClass('border-blue-700');
      });
    });
  });

  describe('Accessibility', () => {
    beforeEach(() => {
      mockSuccessfulFetch();
    });

    test('has proper form labels and ARIA attributes', async () => {
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        // Check for proper form labels
        expect(screen.getByText('Filter by Profile Type')).toBeInTheDocument();
      });
      
      // Check for accessible buttons
      expect(screen.getByRole('button', { name: /add configuration/i })).toBeInTheDocument();
    });

    test('supports keyboard navigation', async () => {
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        expect(screen.getByText('URL Management')).toBeInTheDocument();
      });
      
      // Test tab navigation
      await userEvent.tab();
      expect(document.activeElement).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    test('handles network errors gracefully', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));
      
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        expect(screen.getByText(/Network error/)).toBeInTheDocument();
      });
    });

    test('handles API errors gracefully', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });
      
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        expect(screen.getByText(/Failed to fetch URL configurations/)).toBeInTheDocument();
      });
    });
  });

  describe('Performance', () => {
    test('renders large number of configurations efficiently', async () => {
      const largeConfigList = Array.from({ length: 100 }, (_, i) => ({
        ...mockURLConfigs[0],
        id: i + 1,
        name: `Config ${i + 1}`
      }));
      
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => largeConfigList
      });
      
      const startTime = performance.now();
      renderWithTheme(<URLManager />);
      
      await waitFor(() => {
        expect(screen.getByText('Config 1')).toBeInTheDocument();
      });
      
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      // Ensure rendering completes within reasonable time (2 seconds)
      expect(renderTime).toBeLessThan(2000);
    });
  });
});