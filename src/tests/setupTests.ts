import '@testing-library/jest-dom';

// Mock window.confirm for tests
Object.defineProperty(window, 'confirm', {
  writable: true,
  value: jest.fn(() => true)
});

// Mock window.alert for tests
Object.defineProperty(window, 'alert', {
  writable: true,
  value: jest.fn()
});

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  // Uncomment to ignore specific console methods in tests
  // log: jest.fn(),
  // debug: jest.fn(),
  // info: jest.fn(),
  // warn: jest.fn(),
  error: jest.fn(),
};

// Setup fetch mock
global.fetch = jest.fn();

// Reset all mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
});