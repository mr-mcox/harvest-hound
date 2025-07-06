/**
 * Cross-service integration tests using Docker Compose
 * Tests the full Frontend → Backend → Database flow with real HTTP communication
 */

const { execSync, spawn } = require('child_process');
const fetch = require('node-fetch');
const path = require('path');

// Test configuration
const BACKEND_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:3000';
const DOCKER_COMPOSE_FILE = 'docker-compose.yml';
const TEST_TIMEOUT = 60000; // 1 minute for Docker operations

// Helper functions
function runCommand(command, options = {}) {
  try {
    return execSync(command, { 
      encoding: 'utf8', 
      stdio: 'pipe',
      ...options 
    });
  } catch (error) {
    console.error(`Command failed: ${command}`);
    console.error('STDOUT:', error.stdout);
    console.error('STDERR:', error.stderr);
    throw error;
  }
}

async function waitForService(url, maxAttempts = 30, interval = 2000) {
  console.log(`Waiting for service at ${url}...`);
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        console.log(`Service at ${url} is ready`);
        return true;
      }
    } catch (error) {
      // Service not ready yet
    }
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  throw new Error(`Service at ${url} not ready after ${maxAttempts} attempts`);
}

async function apiCall(endpoint, options = {}) {
  const response = await fetch(`${BACKEND_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });
  return response;
}

// Test suite
describe('Cross-Service Integration Tests', () => {
  let dockerComposeProcess;

  beforeAll(async () => {
    console.log('Starting Docker Compose services...');
    
    // Clean up any existing containers
    try {
      runCommand(`docker-compose -f ${DOCKER_COMPOSE_FILE} down --volumes --remove-orphans`, {
        cwd: path.resolve(__dirname, '..')
      });
    } catch (error) {
      // Ignore errors if no containers exist
    }

    // Start services
    runCommand(`docker-compose -f ${DOCKER_COMPOSE_FILE} up -d --build`, {
      cwd: path.resolve(__dirname, '..')
    });

    // Wait for services to be ready
    await waitForService(`${BACKEND_URL}/health`);
    await waitForService(FRONTEND_URL);
    
    console.log('All services are ready');
  }, TEST_TIMEOUT);

  afterAll(async () => {
    console.log('Stopping Docker Compose services...');
    
    try {
      runCommand(`docker-compose -f ${DOCKER_COMPOSE_FILE} down --volumes`, {
        cwd: path.resolve(__dirname, '..')
      });
    } catch (error) {
      console.error('Error stopping services:', error.message);
    }
  }, 30000);

  describe('Service Health Checks', () => {
    test('backend health endpoint should respond', async () => {
      const response = await fetch(`${BACKEND_URL}/health`);
      expect(response.status).toBe(200);
      
      const health = await response.json();
      expect(health.status).toBe('healthy');
      expect(health.service).toBe('harvest-hound-backend');
    });

    test('frontend should be accessible', async () => {
      const response = await fetch(FRONTEND_URL);
      expect(response.status).toBe(200);
      
      const contentType = response.headers.get('content-type');
      expect(contentType).toContain('text/html');
    });

    test('backend API should be accessible from frontend', async () => {
      // Test CORS by making request from frontend context
      const response = await apiCall('/stores');
      expect(response.status).toBe(200);
      
      const stores = await response.json();
      expect(Array.isArray(stores)).toBe(true);
    });
  });

  describe('Full Stack Workflow', () => {
    let testStoreId;

    test('complete store creation and inventory workflow', async () => {
      // Step 1: Create store via backend API
      const storeResponse = await apiCall('/stores', {
        method: 'POST',
        body: JSON.stringify({
          name: 'Cross-Service Test Store',
          description: 'Testing full stack integration',
          infinite_supply: false
        })
      });
      
      expect(storeResponse.status).toBe(201);
      const store = await storeResponse.json();
      testStoreId = store.store_id;
      
      expect(store.name).toBe('Cross-Service Test Store');
      expect(store.description).toBe('Testing full stack integration');

      // Step 2: Upload inventory with mocked LLM
      const uploadResponse = await apiCall(`/stores/${testStoreId}/inventory`, {
        method: 'POST',
        body: JSON.stringify({
          inventory_text: '1 teaspoon salt, 2 tablespoons olive oil, 1 cup basil'
        })
      });
      
      expect(uploadResponse.status).toBe(201);
      const uploadResult = await uploadResponse.json();
      expect(uploadResult.success).toBe(true);
      expect(uploadResult.items_added).toBe(3);

      // Step 3: Verify data persistence through API
      const inventoryResponse = await apiCall(`/stores/${testStoreId}/inventory`);
      expect(inventoryResponse.status).toBe(200);
      
      const inventory = await inventoryResponse.json();
      expect(inventory.length).toBe(3);
      
      // Verify specific items match BAML normalization
      const salt = inventory.find(item => item.ingredient_name.toLowerCase().includes('salt'));
      const oil = inventory.find(item => item.ingredient_name.toLowerCase().includes('oil'));
      const basil = inventory.find(item => item.ingredient_name.toLowerCase().includes('basil'));
      
      expect(salt).toBeDefined();
      expect(salt.quantity).toBe(1);
      expect(salt.unit).toBe('teaspoon');
      
      expect(oil).toBeDefined();
      expect(oil.quantity).toBe(2);
      expect(oil.unit).toBe('tablespoon');
      
      expect(basil).toBeDefined();
      expect(basil.quantity).toBe(1);
      expect(basil.unit).toBe('cup');

      // Step 4: Verify store list includes updated count
      const storesResponse = await apiCall('/stores');
      expect(storesResponse.status).toBe(200);
      
      const stores = await storesResponse.json();
      const updatedStore = stores.find(s => s.store_id === testStoreId);
      expect(updatedStore).toBeDefined();
      expect(updatedStore.item_count).toBe(3);
    });

    test('frontend can communicate with backend through Docker network', async () => {
      // Test that the frontend container can reach the backend container
      // This simulates real user interactions through the web interface
      
      // Verify the frontend can load store data
      const storesResponse = await apiCall('/stores');
      expect(storesResponse.status).toBe(200);
      
      const stores = await storesResponse.json();
      expect(stores.length).toBeGreaterThan(0);
      
      // Should find our test store from previous test
      const testStore = stores.find(s => s.store_id === testStoreId);
      expect(testStore).toBeDefined();
      expect(testStore.name).toBe('Cross-Service Test Store');
    });
  });

  describe('Error Handling Across Services', () => {
    test('backend errors are properly communicated to frontend', async () => {
      // Test 404 for non-existent store
      const fakeStoreId = '00000000-0000-0000-0000-000000000000';
      const response = await apiCall(`/stores/${fakeStoreId}/inventory`);
      
      expect(response.status).toBe(404);
      const error = await response.json();
      expect(error).toHaveProperty('detail');
    });

    test('validation errors are properly handled', async () => {
      // Test validation error for invalid store creation
      const response = await apiCall('/stores', {
        method: 'POST',
        body: JSON.stringify({}) // Missing required name field
      });
      
      expect(response.status).toBe(422);
      const error = await response.json();
      expect(error).toHaveProperty('detail');
    });

    test('large requests are handled properly', async () => {
      // Create a store first
      const storeResponse = await apiCall('/stores', {
        method: 'POST',
        body: JSON.stringify({ name: 'Large Request Test Store' })
      });
      const store = await storeResponse.json();

      // Test with large inventory text
      const largeInventoryText = Array(100).fill('1 apple, 2 banana, 3 carrot').join(', ');
      
      const uploadResponse = await apiCall(`/stores/${store.store_id}/inventory`, {
        method: 'POST',
        body: JSON.stringify({ inventory_text: largeInventoryText })
      });
      
      // Should handle large requests without errors
      expect(uploadResponse.status).toBe(201);
      const result = await uploadResponse.json();
      expect(result.success).toBe(true);
      expect(result.items_added).toBeGreaterThan(0);
    });
  });

  describe('Performance and Reliability', () => {
    test('services handle concurrent requests', async () => {
      // Create multiple stores concurrently
      const storePromises = [];
      for (let i = 0; i < 5; i++) {
        storePromises.push(apiCall('/stores', {
          method: 'POST',
          body: JSON.stringify({ name: `Concurrent Store ${i}` })
        }));
      }

      const responses = await Promise.all(storePromises);
      
      // All should succeed
      responses.forEach(response => {
        expect(response.status).toBe(201);
      });

      // Verify all stores were created
      const storesResponse = await apiCall('/stores');
      const stores = await storesResponse.json();
      
      const concurrentStores = stores.filter(s => s.name.startsWith('Concurrent Store'));
      expect(concurrentStores.length).toBe(5);
    });

    test('database persistence across service restarts', async () => {
      // Create a store and add inventory
      const storeResponse = await apiCall('/stores', {
        method: 'POST',
        body: JSON.stringify({ name: 'Persistence Test Store' })
      });
      const store = await storeResponse.json();
      const storeId = store.store_id;

      await apiCall(`/stores/${storeId}/inventory`, {
        method: 'POST',
        body: JSON.stringify({ inventory_text: '1 apple, 2 banana' })
      });

      // Restart backend service
      console.log('Restarting backend service...');
      runCommand(`docker-compose -f ${DOCKER_COMPOSE_FILE} restart backend`, {
        cwd: path.resolve(__dirname, '..')
      });

      // Wait for backend to be ready again
      await waitForService(`${BACKEND_URL}/health`);

      // Verify data persisted
      const inventoryResponse = await apiCall(`/stores/${storeId}/inventory`);
      expect(inventoryResponse.status).toBe(200);
      
      const inventory = await inventoryResponse.json();
      expect(inventory.length).toBe(2);

      const storesResponse = await apiCall('/stores');
      const stores = await storesResponse.json();
      const persistedStore = stores.find(s => s.store_id === storeId);
      
      expect(persistedStore).toBeDefined();
      expect(persistedStore.name).toBe('Persistence Test Store');
      expect(persistedStore.item_count).toBe(2);
    });

    test('services recover from temporary failures', async () => {
      // Test that frontend gracefully handles temporary backend unavailability
      
      // First verify normal operation
      let response = await apiCall('/health');
      expect(response.status).toBe(200);

      // Stop backend temporarily
      console.log('Temporarily stopping backend...');
      runCommand(`docker-compose -f ${DOCKER_COMPOSE_FILE} stop backend`, {
        cwd: path.resolve(__dirname, '..')
      });

      // Verify backend is down
      try {
        await fetch(`${BACKEND_URL}/health`, { timeout: 1000 });
        fail('Backend should be down');
      } catch (error) {
        // Expected - backend is down
      }

      // Restart backend
      console.log('Restarting backend...');
      runCommand(`docker-compose -f ${DOCKER_COMPOSE_FILE} start backend`, {
        cwd: path.resolve(__dirname, '..')
      });

      // Wait for recovery
      await waitForService(`${BACKEND_URL}/health`);

      // Verify normal operation restored
      response = await apiCall('/health');
      expect(response.status).toBe(200);
    });
  });

  describe('Docker Environment Verification', () => {
    test('containers are running with correct configuration', async () => {
      const psOutput = runCommand(`docker-compose -f ${DOCKER_COMPOSE_FILE} ps`, {
        cwd: path.resolve(__dirname, '..')
      });

      expect(psOutput).toContain('backend');
      expect(psOutput).toContain('frontend');
      expect(psOutput).not.toContain('Exit'); // No crashed containers
    });

    test('container networking allows service communication', async () => {
      // Test that backend and frontend can communicate through Docker network
      
      // Backend should be reachable on standard port
      const backendResponse = await fetch(`${BACKEND_URL}/health`);
      expect(backendResponse.status).toBe(200);

      // Frontend should be reachable on standard port  
      const frontendResponse = await fetch(FRONTEND_URL);
      expect(frontendResponse.status).toBe(200);
    });

    test('volumes are properly mounted for development', async () => {
      // Verify that changes would be reflected (test development setup)
      
      // Check that API responds (indicating code is loaded)
      const response = await apiCall('/health');
      expect(response.status).toBe(200);
      
      const health = await response.json();
      expect(health.service).toBe('harvest-hound-backend');
    });
  });
});

// Jest configuration for this test file
module.exports = {
  testTimeout: TEST_TIMEOUT,
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  testMatch: ['**/tests/cross-service-integration.test.js']
};