# Future Work
## Features
- We'll need websockets for UC2 and beyond
- Strategy of determining whether to create a new ingredient or re-use something that's close
- When submitting ingredients, we should direct to the inventory page

## Tech Debt
- We're using CORS on backend - nginx within docker-compose is more secure

## Questions
- We've disabled some type checking on python tests. What's the nature of those failed checks and should we address them?
- We're building up a bunch of pyright errors - worth addressing and if so, when?
- We have a script to export types from python to typescript. Should components of that be tested? Can they be generalized?

## Concerns
- There's a lot of extra configuration in the docker setup
- Imports not at the top of the file
- Patching within tests

## Testing improvements
- Revisit mypy overrides and determine whether they are warranted.
- Look for ways to reduce the number of tests while keeping coverage about the same
- Reduce patching within tests
- Reduce imports not at the top of the file

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
