# Implementation Tasks: WebSocket Foundation for Real-time Inventory Updates

**Source TIP**: `docs/development/tips/tip-websocket-foundation.md`  
**Timeline**: 1-2 development iterations  
**Total Scope**: S - Simplified implementation leveraging existing event infrastructure

## Task 1: Event Store Refactoring (TIP Work Stream 1)
**Goal**: Implement async event bus pattern to decouple event store from consumers

### 1.1 Event Bus Infrastructure - **SETUP ONLY**
- [x] **Create EventBus interface** - Define async publish/subscribe contract
- [x] **Create InMemoryEventBus implementation** - Simple pub/sub for development
- [x] **Add EventBusManager dependency** - Injectable service for FastAPI
- [x] **Update event store constructor** - Accept event_bus parameter with default None

### 1.2 Event Store Publishing - **REFACTOR**
- [x] **Add async publish method to event store** - Call event_bus.publish(event) after storage
- [x] **Maintain backward compatibility** - Keep existing projection_registry calls for now
- [x] **Add integration test** - Verify events published to both old and new systems
- [x] **Update event store tests** - Mock event bus to verify publish calls

### 1.3 Projection Handler Migration - **REFACTOR**
- [x] **Refactor projection registry to use app state** - Move from global variable to app.state.projection_registry
- [x] **Convert projection handlers to subscribers** - Subscribe to event bus on startup
- [x] **Add async event handling** - Update handler methods to be async
- [x] **Test projection handlers independently** - Verify they work via event bus subscription
- [x] **Remove projection_registry from event store** - Clean up old coupling after verification

## Task 2: WebSocket Infrastructure (TIP Work Stream 2)
**Goal**: Build WebSocket connection manager with default room pattern and event broadcasting

### 2.1 WebSocket Connection Manager - **SETUP ONLY**
- [x] **Create ConnectionManager class** - Track active connections by room
- [x] **Add room management methods** - join_room, leave_room, broadcast_to_room
- [x] **Create WebSocket message schemas** - Pydantic models for event envelopes
- [x] **Add connection lifecycle methods** - connect, disconnect, cleanup

### 2.2 WebSocket Endpoint - **NEW BEHAVIOR**
- [x] **Implement /ws endpoint** - Accept WebSocket connections with default room
- [x] **Handle connection handshake** - Accept connection and join default room
- [x] **Add connection error handling** - Gracefully handle disconnections
- [x] **Test WebSocket endpoint** - Connect, send message, verify receipt

### 2.3 Event Broadcasting Integration - **NEW BEHAVIOR**
- [x] **Create WebSocket event subscriber** - Subscribe to event bus for domain events
- [x] **Implement event filtering** - Transform domain events to WebSocket messages
- [x] **Add broadcast logic** - Send filtered events to appropriate room connections
- [x] **Test end-to-end flow** - Domain command → event store → event bus → WebSocket → client

## Task 3: Frontend Integration (TIP Work Stream 3)
**Goal**: WebSocket client with simple reconnection and real-time UI updates

### 3.1 WebSocket Client Service - **SETUP ONLY**
- [x] **Create WebSocketService class** - Handle connection lifecycle
- [x] **Add connection state management** - Track connected/disconnected/reconnecting states
- [x] **Define event handling interface** - Type-safe event callback system
- [x] **Create WebSocket store** - Svelte store for connection state and events

### 3.2 WebSocket Connection Logic - **NEW BEHAVIOR** ✅ COMPLETED
- [x] **Implement connection establishment** - Connect to /ws with default room
- [x] **Add simple reconnection logic** - Retry connection after disconnect with backoff
- [x] **Handle incoming events** - Parse WebSocket messages and emit to subscribers
- [x] **Test connection scenarios** - Connect, disconnect, reconnect, message handling
- [x] **WebSocket store refactoring** - Removed overengineered methods, implemented essential Svelte store integration

### 3.3 Real-time UI Updates - **NEW BEHAVIOR** ✅ COMPLETED
- [x] **Subscribe to inventory events** - Listen for InventoryItemAdded events
- [x] **Update inventory store state** - Merge WebSocket updates with local state
- [x] **Add visual feedback** - Show real-time update indicators in UI
- [x] **Test multi-session updates** - Verify changes in one tab appear in another
- [x] **Centralized inventory store** - Created reactive store for inventory data with WebSocket integration
- [x] **Real-time indicator component** - Shows connection status and last update timestamp
- [x] **Updated store pages** - Integrated real-time functionality into stores list and inventory views

### 3.4 Integration with Existing Components - **REFACTOR**
- [ ] **Update InventoryTable component** - React to real-time inventory changes
- [ ] **Enhance StoreList component** - Show real-time item count updates
- [ ] **Add connection status indicator** - Display WebSocket connection state
- [ ] **Test existing functionality** - Ensure REST API workflows remain unaffected

## Task 4: End-to-End Integration & Testing
**Goal**: Verify complete real-time inventory update flow across multiple sessions

### 4.1 Backend Integration Testing - **NEW BEHAVIOR**
- [ ] **Multi-client WebSocket test** - Two connections, verify event broadcast to both
- [ ] **REST to WebSocket flow test** - POST inventory via REST, verify WebSocket event received
- [ ] **Connection lifecycle test** - Connect, disconnect, reconnect scenarios work correctly
- [ ] **Event ordering test** - Rapid updates maintain correct sequence across clients

### 4.2 Frontend E2E Testing - **NEW BEHAVIOR**
- [ ] **Multi-tab update test** - Playwright test with two browser tabs, verify real-time sync
- [ ] **Network interruption test** - Simulate offline/online, verify automatic recovery
- [ ] **Visual feedback test** - Verify real-time indicators appear correctly in UI
- [ ] **Mixed usage test** - Both REST and WebSocket operations work together seamlessly

### 4.3 Manual Testing Documentation - **SETUP ONLY**
- [ ] **Create manual test guide** - Step-by-step workflows for user experience validation
- [ ] **Performance observation checklist** - What to monitor in browser dev tools during testing
- [ ] **Edge case scenarios** - Documented test cases for exploratory testing
- [ ] **Browser compatibility notes** - Which browsers to test manually and expected behavior

## Dependencies and Sequencing

**Critical Path**:
1. **Task 1 (Event Store Refactoring)** must complete before Task 2.3 (Event Broadcasting)
2. **Task 2 (WebSocket Infrastructure)** must complete before Task 3 (Frontend Integration)
3. **Task 3.1-3.2 (WebSocket Client)** must complete before Task 3.3 (Real-time UI)
4. **Task 4 (Integration Testing)** requires completion of all previous tasks

**Parallel Work Opportunities**:
- Task 1.1 (Event Bus Setup) can run parallel with Task 2.1 (Connection Manager Setup)
- Task 3.1 (WebSocket Client Setup) can run parallel with Task 2.2 (WebSocket Endpoint)
- Task 1.3 (Projection Migration) can run parallel with Task 2.3 (Event Broadcasting)

## Success Metrics

**Technical Validation**:
- [ ] Event bus refactoring maintains all existing projection functionality
- [ ] WebSocket connections establish and maintain default room subscriptions
- [ ] Domain events flow from event store → event bus → WebSocket → frontend
- [ ] Simple reconnection logic handles brief network interruptions

**User Validation**:
- [ ] Users see inventory changes in real-time across multiple browser tabs
- [ ] System remains fully functional when WebSocket is unavailable
- [ ] No degradation of existing REST API workflows

**Performance Validation**:
- [ ] Sub-100ms event delivery for single-user scenario
- [ ] Clean connection/disconnection handling without memory leaks