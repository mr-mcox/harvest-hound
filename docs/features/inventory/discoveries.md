# Future Work
## Features
- Strategy of determining whether to create a new ingredient or re-use something that's close
- When submitting ingredients, we should direct to the inventory page

## Tech Debt
- We're using CORS on backend - nginx within docker-compose is more secure

## Questions
- We're building up a bunch of pyright errors - worth addressing and if so, when?
- Pyright run as a cli has different errors than within Zed - do they have different configurations?

## Concerns
- There's a lot of extra configuration in the docker setup

## Scratch
### 9.8 Future Work Notes (*No tests needed - planning*)
- [ ] **WebSocket testing infrastructure** (deferred)
  - [ ] Real-time event streaming tests
  - [ ] Connection handling and reconnection
  - [ ] Multi-client event broadcasting
- [ ] **Load testing setup** (deferred)
  - [ ] Large inventory parsing performance
  - [ ] Concurrent user session handling
  - [ ] Database performance under load
- [ ] **Browser automation** (deferred)
  - [ ] Playwright/Puppeteer test suite
  - [ ] Cross-browser compatibility testing
  - [ ] Mobile responsiveness testing
