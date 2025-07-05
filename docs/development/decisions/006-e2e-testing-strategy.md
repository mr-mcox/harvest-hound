# Three-Tier E2E Testing Strategy with Docker Compose Coordination

## Context and Problem Statement

Harvest Hound's event-driven architecture with AI/LLM integration presents unique testing challenges. The system includes real-time WebSocket communication, multiple service coordination, and expensive LLM API calls. We need an E2E testing strategy that balances comprehensive coverage with cost control and development velocity while handling the complexity of event sourcing patterns and AI agent interactions.

## Considered Options

* Full integration testing with real LLM APIs and all services
* Pure unit testing with heavy mocking at all boundaries
* Three-tier testing strategy with selective mocking and service coordination
* Container-based testing with full service replicas for each test

## Decision Outcome

Chosen option: "Three-tier testing strategy with selective mocking and service coordination", because it provides 80% coverage with manageable complexity while controlling LLM costs and enabling rapid development iteration.

### Consequences

* Good, because Docker Compose provides realistic service coordination without infrastructure complexity
* Good, because LLM response fixtures enable predictable testing of AI agent behavior
* Good, because integration tests with mocked LLM verify actual API behavior without costs
* Good, because phased approach allows incremental implementation (phases 1 & 2 first)
* Good, because maintains development velocity with fast feedback cycles
* Bad, because WebSocket testing is deferred, potentially missing real-time interaction bugs
* Bad, because LLM fixture maintenance adds overhead as agent capabilities evolve
* Bad, because some integration edge cases may only surface in production

## Implementation Details

### Three-Tier Testing Strategy

**Tier 1: Unit Tests**
- Domain model behavior testing
- Event sourcing aggregate logic
- Individual service components
- LLM response parsing and validation

**Tier 2: Integration Tests**
- Real FastAPI + SQLite + Frontend coordination
- Mocked LLM responses using fixtures
- Event stream validation
- API contract verification

**Tier 3: E2E Tests**
- Docker Compose service orchestration
- LLM response fixtures for predictable scenarios
- User journey testing (inventory upload → meal planning → recipe generation)
- Cross-service event propagation

### Service Coordination Pattern

```yaml
# docker-compose.test.yml
services:
  backend:
    build: ./packages/backend
    environment:
      - DATABASE_URL=sqlite:///test.db
      - LLM_MODE=fixture
  frontend:
    build: ./packages/frontend
    environment:
      - VITE_API_URL=http://backend:8000
```

### LLM Response Fixtures

```python
# tests/fixtures/llm_responses.py
RECIPE_GENERATION_FIXTURES = {
    "csa_vegetable_focus": {
        "request_pattern": "vegetable.*seasonal.*fresh",
        "response": {
            "recipes": [
                {
                    "name": "Roasted Root Vegetable Medley",
                    "ingredients": [
                        {"name": "carrots", "quantity": 2, "unit": "lbs"},
                        {"name": "beets", "quantity": 1, "unit": "bunch"}
                    ]
                }
            ]
        }
    }
}
```

### Test Phases

**Phase 1 (Current Focus):**
- Unit tests for domain aggregates
- Integration tests with mocked LLM
- Basic Docker Compose E2E setup

**Phase 2 (Next Sprint):**
- LLM fixture library expansion
- Cross-service event testing
- User journey automation

**Future Considerations:**
- WebSocket real-time testing
- Performance/load testing
- Production-like LLM interaction testing
- Cost monitoring and optimization

### Cost Control Measures

- LLM fixtures for 95% of test scenarios
- Real LLM calls only for critical integration validation
- Configurable test modes (fixture/real/hybrid)
- Test execution budgets and monitoring

This approach enables comprehensive testing while maintaining development velocity and controlling operational costs, with a clear migration path to more sophisticated testing as the system matures.