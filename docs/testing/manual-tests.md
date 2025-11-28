# Manual Testing Guide

This document provides comprehensive manual testing scenarios for Harvest Hound, focusing on real-world usage patterns and edge cases that complement our automated test suite.

## Overview

Manual testing is essential for:
- **Real LLM Integration**: Testing actual AI parsing behavior with diverse inputs
- **Performance Validation**: Measuring real-world response times under various conditions
- **Edge Case Discovery**: Exploring scenarios that automated tests might miss
- **User Experience**: Validating the complete user workflow end-to-end

## Test Environment Setup

### Option 1: Real LLM Testing
Use actual LLM services for comprehensive testing:
```bash
# Start with real LLM configuration
./scripts/test-manual.sh
```

### Option 2: Mocked LLM Testing
Use mocked responses for consistent baseline testing:
```bash
# Start with mocked LLM for predictable results
./scripts/dev-start.sh
```

## Core Workflow Tests

### Test 1: Basic Store Creation & Inventory Upload
**Objective**: Verify the fundamental user workflow works end-to-end

**Steps**:
1. Navigate to application home page
2. Click "Create New Store"
3. Fill in store details:
   - Name: "Weekly CSA Box"
   - Description: "Fresh vegetables from local farm"
   - Infinite Supply: false
4. Click "Create Store"
5. Verify store appears in store list
6. Navigate to inventory upload page
7. Paste inventory text: "2 lbs carrots, 1 bunch kale, 3 medium tomatoes"
8. Click "Upload Inventory"
9. Verify parsing results appear within 30 seconds
10. Check inventory table shows 3 items with correct quantities

**Expected Results**:
- Store creation completes in < 1 second
- Inventory parsing completes in < 30 seconds
- All items correctly identified and quantified
- No errors or crashes

### Test 2: Multiple Stores with Separate Inventories
**Objective**: Ensure inventory isolation between stores

**Steps**:
1. Create store "CSA Box" with inventory: "2 lbs carrots, 1 bunch kale"
2. Create store "Pantry" with inventory: "1 cup rice, 2 cans beans"
3. Navigate between stores
4. Verify each store shows only its own inventory
5. Add more items to each store
6. Refresh browser and verify data persists

**Expected Results**:
- Each store maintains separate inventory
- No cross-contamination between stores
- Data persists across browser refreshes

### Test 3: Complex Inventory Parsing
**Objective**: Test LLM parsing with diverse input formats

**Sample Inputs to Test**:
```
Mixed formats:
2 lbs carrots, 1 bunch kale, 3 medium tomatoes, 1/2 cup olive oil

Inconsistent spacing:
2lbs carrots,1   bunch kale,   3medium tomatoes

Partial quantities:
half a bunch of kale, couple of tomatoes, some carrots

Multiple languages/terms:
2 lb carrots, 1 bunch of kale, 3 roma tomatoes, 1 head lettuce

Ambiguous items:
green stuff, root vegetables, leafy things
```

**Steps**:
1. Create test store
2. Upload each sample input separately
3. Review parsed results
4. Note any parsing errors or misinterpretations
5. Document unexpected behaviors

**Expected Results**:
- 90%+ accuracy on common formats
- Graceful handling of ambiguous inputs
- Clear error messages for unparseable content

## Performance Testing

### Test 4: Large Inventory Upload
**Objective**: Test system performance with substantial inventory

**Steps**:
1. Create store "Large Farm Share"
2. Upload comprehensive inventory (50+ items):
```
2 lbs carrots, 1 bunch kale, 3 tomatoes, 1 head lettuce, 2 bunches spinach,
1 lb potatoes, 3 onions, 2 bell peppers, 1 bunch cilantro, 1 head cabbage,
4 zucchini, 2 cucumbers, 1 bunch radishes, 1 pint cherry tomatoes,
1 bunch parsley, 2 eggplants, 1 lb green beans, 3 ears corn,
1 head broccoli, 1 head cauliflower, 2 leeks, 1 bunch scallions,
1 lb beets, 1 bunch turnips, 1 acorn squash, 1 butternut squash,
1 bunch swiss chard, 1 head bok choy, 1 bunch arugula, 1 head radicchio,
2 fennel bulbs, 1 bunch dill, 1 bunch basil, 1 bunch oregano,
1 bunch thyme, 1 bunch rosemary, 2 heads garlic, 1 piece ginger,
1 lb apples, 1 lb pears, 1 pint strawberries, 1 lb grapes,
2 avocados, 3 bananas, 1 pineapple, 1 cantaloupe, 1 watermelon,
1 lb walnuts, 1 lb almonds, 1 cup sunflower seeds
```
3. Measure parsing time
4. Verify all items are correctly parsed
5. Test inventory display performance

**Expected Results**:
- Parsing completes in < 45 seconds
- All items correctly identified
- Inventory display loads in < 2 seconds
- No performance degradation

### Test 5: Concurrent Usage Simulation
**Objective**: Test system under concurrent load

**Steps**:
1. Open multiple browser tabs/windows
2. Create different stores simultaneously
3. Upload inventory in each store at the same time
4. Monitor for conflicts or errors
5. Verify all data is correctly saved

**Expected Results**:
- No data corruption
- All stores maintain separate state
- Reasonable performance under load

## Error Handling Tests

### Test 6: Network Interruption Handling
**Objective**: Test graceful error handling

**Steps**:
1. Start inventory upload
2. Disconnect network during upload
3. Reconnect network
4. Retry upload
5. Verify error messages are user-friendly

**Expected Results**:
- Clear error messages
- Ability to retry failed operations
- No data loss or corruption

### Test 7: Invalid Input Handling
**Objective**: Test system robustness with edge cases

**Test Cases**:
```
Empty input: ""
Non-food items: "2 lbs rocks, 1 toy car, 3 pencils"
Nonsense text: "alkdfjlaksjdf laksjdf laskjdf"
Very long text: [1000+ character string]
Special characters: "2 lbs carrots!@#$%^&*()_+"
```

**Steps**:
1. Upload each test case
2. Review parsing results
3. Verify no system crashes
4. Document error handling behavior

**Expected Results**:
- System remains stable
- Appropriate error messages
- Ability to correct and retry

## Edge Case Exploration

### Test 8: Browser Compatibility
**Objective**: Verify cross-browser functionality

**Browsers to Test**:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

**Test Steps**:
1. Complete basic workflow in each browser
2. Test file upload functionality
3. Verify responsive design
4. Check for JavaScript errors

### Test 9: Mobile Device Testing
**Objective**: Test mobile user experience

**Steps**:
1. Open application on mobile device
2. Complete store creation workflow
3. Test inventory upload with mobile keyboard
4. Verify touch interactions work correctly

### Test 10: Data Persistence Testing
**Objective**: Verify data integrity over time

**Steps**:
1. Create stores with substantial inventory
2. Close browser completely
3. Restart browser and navigate to application
4. Verify all data is preserved
5. Add new inventory items
6. Refresh page and verify persistence

## Performance Benchmarks

### Baseline Performance Targets
- **Store Creation**: < 1 second
- **Inventory Parsing**: < 30 seconds (real LLM), < 100ms (mocked)
- **Inventory Display**: < 2 seconds
- **Page Load**: < 3 seconds on standard connection

### Performance Testing Protocol
1. Clear browser cache
2. Use standard broadband connection
3. Measure from user action to completion
4. Record results for trending analysis
5. Test under various network conditions

## Reporting Issues

### Issue Documentation Template
When reporting issues discovered during manual testing:

```
**Issue**: [Brief description]
**Severity**: [Critical/High/Medium/Low]
**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result**: [What should happen]
**Actual Result**: [What actually happened]
**Environment**: [Browser, OS, network conditions]
**Additional Notes**: [Any other relevant information]
```

### Issue Categories
- **Functional**: Feature doesn't work as expected
- **Performance**: Slower than acceptable benchmarks
- **Usability**: Confusing or difficult user experience
- **Cosmetic**: Visual or layout issues

## Test Coverage Areas

### Functional Coverage
- ✅ Store creation workflow
- ✅ Inventory upload and parsing
- ✅ Data persistence
- ✅ Multi-store management
- ✅ Error handling

### Performance Coverage
- ✅ Response time benchmarks
- ✅ Large data set handling
- ✅ Concurrent user simulation
- ✅ Network condition variations

### Usability Coverage
- ✅ User workflow completion
- ✅ Error message clarity
- ✅ Mobile responsiveness
- ✅ Browser compatibility

### Edge Case Coverage
- ✅ Invalid input handling
- ✅ Network interruption recovery
- ✅ Browser refresh behavior
- ✅ Complex parsing scenarios

## Automation Opportunities

Based on manual testing discoveries, consider automating:
- Common edge cases that prove problematic
- Performance regression testing
- Cross-browser compatibility checks
- Mobile device testing scenarios

Manual testing remains crucial for:
- Exploratory testing of new features
- User experience validation
- Real-world performance assessment
- Discovery of unexpected edge cases
