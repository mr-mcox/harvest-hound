# Future Work
## Features
- We'll need websockets for UC2 and beyond
- Strategy of determining whether to create a new ingredient or re-use something that's close

## Questions
- We've disabled some type checking on python tests. What's the nature of those failed checks and should we address them?
- We're building up a bunch of pyright errors - worth addressing and if so, when?
- We have a script to export types from python to typescript. Should components of that be tested? Can they be generalized?

## Concerns
- Noticing some smell in how base models are constructed
