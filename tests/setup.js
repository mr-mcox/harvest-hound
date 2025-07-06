/**
 * Setup file for cross-service integration tests
 */

// Global test setup
global.console = {
  ...console,
  // Suppress console.log during tests unless DEBUG is set
  log: process.env.DEBUG ? console.log : () => {},
  info: process.env.DEBUG ? console.info : () => {},
  warn: console.warn,
  error: console.error,
};

// Global error handler for unhandled promises
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Set test environment variables
process.env.NODE_ENV = 'test';

// Increase timeout for Docker operations
jest.setTimeout(60000);

// Global test helpers
global.sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

global.retryOperation = async (operation, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(delay);
    }
  }
};

// Clean up any lingering processes on exit
process.on('exit', () => {
  // Cleanup code if needed
});

console.log('Cross-service integration test setup complete');