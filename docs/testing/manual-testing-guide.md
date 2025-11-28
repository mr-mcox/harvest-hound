# Manual Testing Guide: WebSocket Real-time Inventory Updates

## Environment Setup

**Start Manual Testing Environment**:
```bash
./scripts/test-manual.sh
```

This script will:
- Start both backend (port 8000) and frontend (port 3000) services
- Configure real LLM integration for complete testing
- Wait for services to become healthy
- Display service URLs and basic testing scenarios

## Quick Start Workflows

### Workflow 1: Basic Real-time Sync Verification
**Duration**: 2-3 minutes
**Purpose**: Verify inventory changes sync across browser tabs

1. **Setup**:
   - Run `./scripts/test-manual.sh` to start services
   - Open Browser Tab A: http://localhost:3000 (stores list)
   - Open Browser Tab B: Navigate to same store's inventory page

2. **Test Steps**:
   - In Tab A: Add new inventory items via bulk upload
   - In Tab B: Verify items appear without page refresh
   - In Tab B: Check real-time indicator shows "Connected" status
   - In Tab A: Verify item count updates in store list

3. **Expected Results**:
   - Changes appear instantly in both tabs
   - Connection status shows green/connected
   - No console errors in browser dev tools

### Workflow 2: Connection Recovery Testing
**Duration**: 3-4 minutes
**Purpose**: Verify WebSocket reconnection handles network interruptions

1. **Setup**:
   - Services running via test-manual.sh
   - Single browser tab open to inventory page
   - Browser dev tools open to Network tab

2. **Test Steps**:
   - Verify initial connection established
   - Stop backend: `docker-compose -f docker-compose.dev.yml down backend`
   - Observe connection status indicator changes
   - Restart backend: `docker-compose -f docker-compose.dev.yml up -d backend`
   - Wait for automatic reconnection
   - Add inventory item via different method
   - Verify real-time updates resume

3. **Expected Results**:
   - Status indicator shows "Disconnected" when server down
   - Status indicator shows "Reconnecting" during recovery
   - Automatic reconnection within 10 seconds of server restart
   - Real-time updates resume without page refresh

### Workflow 3: Mixed Usage Patterns
**Duration**: 4-5 minutes
**Purpose**: Verify REST API and WebSocket work together seamlessly

1. **Setup**:
   - Two browser tabs with same store inventory
   - API documentation open: http://localhost:8000/docs

2. **Test Steps**:
   - Tab A: Add items via frontend form
   - Tab B: Verify real-time updates appear
   - API Docs: POST new items via bulk endpoint
   - Both tabs: Verify REST-added items appear via WebSocket
   - Tab A: Delete items via frontend
   - Tab B: Verify deletions sync in real-time
   - API Docs: Query current inventory
   - Verify REST response matches frontend state

3. **Expected Results**:
   - All changes sync regardless of origin (frontend vs REST)
   - State consistency maintained across all interfaces
   - No duplicate items or stale data

## User Experience Validation

### Visual Feedback Checklist
- [ ] Connection status indicator clearly visible
- [ ] Real-time updates have subtle visual indication
- [ ] Loading states appropriate during reconnection
- [ ] Error states clearly communicated to user

### Performance Perception
- [ ] Updates appear instantaneous (< 500ms)
- [ ] No noticeable lag during bulk operations
- [ ] Smooth scrolling maintained during real-time updates
- [ ] No UI freezing during connection events

### Accessibility Considerations
- [ ] Screen reader announces connection status changes
- [ ] Keyboard navigation unaffected by WebSocket updates
- [ ] High contrast mode preserves status indicators
- [ ] No sudden focus changes during real-time updates

## Troubleshooting Common Issues

### Connection Problems
**Symptom**: Status shows "Disconnected"
**Check**: `docker-compose -f docker-compose.dev.yml logs backend`
**Action**: Restart services, verify containers healthy

**Symptom**: Status stuck on "Reconnecting"
**Check**: Browser console for WebSocket errors
**Action**: Hard refresh page, check network connectivity

### Data Sync Issues
**Symptom**: Changes not appearing in other tabs
**Check**: Backend logs for event publishing
**Action**: Verify event bus integration, check projection handlers

**Symptom**: Duplicate items appearing
**Check**: Frontend state management for duplicate event handling
**Action**: Clear browser cache, verify event deduplication logic

### Performance Issues
**Symptom**: Slow update delivery
**Check**: Browser dev tools Network tab for WebSocket message timing
**Action**: Monitor container resources, check event batching

## Environment Cleanup

**Stop all services**:
```bash
docker-compose -f docker-compose.dev.yml down
```

## Exit Criteria

Manual testing complete when:
- [ ] All three main workflows pass consistently
- [ ] Visual feedback meets quality standards
- [ ] Performance perception acceptable
- [ ] No critical issues identified in troubleshooting
