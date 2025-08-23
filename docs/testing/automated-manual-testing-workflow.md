# Automated Manual Testing Workflow (Future Enhancement)

## Overview

This document outlines a potential automated workflow for manual testing with real LLM integration, based on the debugging process we used to identify the inventory upload issue.

## Proposed Workflow

### Script: `scripts/test-integration-e2e.sh`
```bash
#!/bin/bash
# Full integration test with real LLM + E2E automation

set -e

echo "🚀 Starting automated integration test..."

# 1. Start manual testing environment
./scripts/test-manual.sh

# 2. Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
timeout 60s bash -c 'until curl -f http://localhost:3000 > /dev/null 2>&1; do sleep 2; done'
timeout 60s bash -c 'until curl -f http://localhost:8000/health > /dev/null 2>&1; do sleep 2; done'

# 3. Run Playwright E2E tests against real environment
echo "🧪 Running E2E tests against real LLM..."
cd packages/frontend
pnpm test:e2e:integration

# 4. Cleanup
echo "🧹 Cleaning up..."
cd ../..
docker-compose -f docker-compose.dev.yml down

echo "✅ Integration test complete!"
```

### Playwright Test: `packages/frontend/e2e/integration-real-llm.spec.ts`
```typescript
import { test, expect } from '@playwright/test';

test.describe('Real LLM Integration Tests', () => {
  test('should upload and parse inventory with real LLM', async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:3000');
    
    // Create a new store
    await page.click('[data-testid="create-store-button"]');
    await page.fill('[data-testid="store-name-input"]', 'Test CSA Box');
    await page.fill('[data-testid="store-description-input"]', 'Integration test store');
    await page.click('[data-testid="create-store-submit"]');
    
    // Navigate to inventory upload
    await page.click('[data-testid="upload-inventory-button"]');
    
    // Upload inventory text
    const inventoryText = '2 lbs carrots, 1 bunch kale, 3 tomatoes';
    await page.fill('[data-testid="inventory-text-input"]', inventoryText);
    await page.click('[data-testid="upload-submit-button"]');
    
    // Verify success message
    await expect(page.locator('[data-testid="upload-success"]')).toContainText('Successfully added');
    await expect(page.locator('[data-testid="upload-success"]')).not.toContainText('0 items');
    
    // Verify inventory items appear
    await expect(page.locator('[data-testid="inventory-item"]')).toHaveCount.greaterThan(0);
    
    // Check specific items were parsed correctly
    await expect(page.locator('[data-testid="inventory-item"]')).toContainText('carrots');
    await expect(page.locator('[data-testid="inventory-item"]')).toContainText('kale');
    await expect(page.locator('[data-testid="inventory-item"]')).toContainText('tomatoes');
    
    // Verify real-time updates work
    await expect(page.locator('[data-testid="connection-status"]')).toContainText('Connected');
  });
  
  test('should handle parsing errors gracefully', async ({ page }) => {
    // Similar setup...
    
    // Try to upload malformed inventory
    await page.fill('[data-testid="inventory-text-input"]', 'invalid nonsense text');
    await page.click('[data-testid="upload-submit-button"]');
    
    // Should show helpful error message, not generic HTTP error
    await expect(page.locator('[data-testid="upload-error"]')).toContainText('Failed to parse inventory text');
    await expect(page.locator('[data-testid="upload-error"]')).not.toContainText('HTTP error! status: 400');
  });
});
```

### Package.json script:
```json
{
  "scripts": {
    "test:e2e:integration": "playwright test e2e/integration-real-llm.spec.ts",
    "test:integration:full": "../scripts/test-integration-e2e.sh"
  }
}
```

## Benefits

1. **Catch Real Issues**: Tests actual LLM integration, not just mocked responses
2. **Debugging Helper**: Can be run during development to verify fixes
3. **Regression Prevention**: Ensures environment configuration stays correct
4. **Documentation**: Serves as executable documentation of expected behavior

## Considerations

1. **Cost**: Uses real LLM API calls, so should be run judiciously
2. **Speed**: Slower than unit tests due to Docker startup and LLM calls
3. **Flakiness**: Real LLM responses can vary, may need retry logic
4. **Environment**: Requires proper API keys and environment setup

## When to Use

- **Before major releases** to validate end-to-end functionality
- **When debugging integration issues** (like the one we just solved)
- **After environment/infrastructure changes** to ensure deployment works
- **Manual trigger only** - not part of regular CI/CD pipeline

## Implementation Priority

- **Phase 1**: Create basic script that starts/stops environment
- **Phase 2**: Add simple Playwright tests for happy path
- **Phase 3**: Add error handling and edge case testing
- **Phase 4**: Add retry logic and better reporting

This workflow would have caught the environment variable issue we just debugged much faster than manual clicking!