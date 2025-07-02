# Agentic Meal Planning Application - Design Document

## Purpose

This application solves the mental overhead of meal planning for families receiving CSA (Community Supported Agriculture) deliveries and managing mixed fresh/frozen/pantry inventories. The core challenge is optimizing meal selection to prioritize fresh ingredients while leveraging an AI agent to handle the complex decision-making around ingredient availability, substitutions, and recipe iteration.

The application uses a greedy optimization approach where an AI agent iteratively selects meals, removes used ingredients from available inventory, and adapts subsequent meal selections based on remaining ingredients.

## Core Domain Objects

### Ingredient
- **Purpose**: Represents a single ingredient with standardized naming
- **Properties**: Name, default unit (cups, lbs, whole, etc.)
- **Notes**: Minimal reference object that can be used across recipes and stores

### Recipe
- **Purpose**: Complex aggregate representing a recipe in various states of development
- **States**:
  - **Pitch**: Initial proposal with high-level description and key non-pantry ingredients
  - **Full Recipe**: Complete ingredient list with quantities and full instructions
  - **Enhanced**: Future state with specialized instruction sets (e.g., prep instructions for sous chef)
- **Properties**:
  - Unique identifier
  - Current state (pitch/full/enhanced)
  - Name and description
  - Ingredient requirements (varies by state)
  - Instructions (when in full/enhanced state)
  - Metadata (prep time, cook time, difficulty, cuisine)
  - Source information
  - Parent recipe ID (for lineage tracking)
- **Notes**: Immutable within each state - state transitions create new versions with updated content

### IngredientStore
- **Purpose**: Represents different sources of ingredients with distinct availability semantics
- **Types**:
  - **Perishable**: CSA deliveries, fresh items with explicit quantities that decrease when claimed
  - **Frozen Meat**: Explicit inventory that decreases when claimed
  - **Pantry**: "Infinite" supply of staple ingredients (pasta, spices, canned goods)
  - **Grocery Store**: Infinite supply, lowest priority, represents "can buy anything"
- **Properties**: Store type, current inventory, priority level
- **Behavior**: Different stores handle ingredient claims differently based on their semantics

## Supporting Objects

### IngredientBroker
- **Purpose**: Mediates between recipe planning and ingredient availability across all stores
- **Responsibilities**:
  - Presents unified view of available ingredients with priority indicators
  - Manages current ingredient claims
  - Computes real-time ingredient availability based on active claims
  - Handles negotiation with RecipePlanner about ingredient conflicts
  - Validates ingredient claims against current availability
- **Notes**: Maintains only current state - no transaction history. RecipePlanner handles substitution logic.

### IngredientClaim
- **Purpose**: Immutable reservation of ingredients during planning
- **Properties**: Claimed ingredients, quantities, associated recipe/meal, claim timestamp
- **Behavior**: Can be created, committed, or released - never modified
- **Notes**: Changes require releasing the existing claim and creating a new one

### RecipePlanner
- **Purpose**: AI agent responsible for recipe selection, adaptation, and substitution logic
- **Responsibilities**:
  - Generate recipe proposals based on available ingredients
  - Negotiate with IngredientBroker to resolve conflicts
  - Handle ingredient substitutions and recipe modifications
  - Track retry attempts and abandon recipes when necessary
  - Learn from user feedback and preferences
  - Manage recipe state transitions (pitch → full recipe)

### MealPlanSpec
- **Purpose**: Natural language constraints and preferences for meal planning
- **Properties**: Day-specific requirements, dietary constraints, time limitations, cooking preferences
- **Examples**: "Quick weeknight meal", "Weekend project cooking", "Prep-ahead friendly"
- **Notes**: Flexible natural language that the AI agent interprets

### Meal
- **Purpose**: Container for one or more recipes that comprise a single meal
- **Properties**: Meal ID, associated recipes, planned date/time, meal type
- **Notes**: Enables complex meals like "grilled chicken + Asian coleslaw"

## System Flow

### 1. Inventory Setup
1. User populates IngredientStores through frontend interface
2. Backend parses natural language ingredient lists into structured data
3. IngredientBroker aggregates availability across all stores

### 2. Initial Planning
1. User provides MealPlanSpec (constraints, preferences)
2. RecipePlanner generates initial recipe proposals
3. IngredientBroker validates ingredient availability
4. System presents high-level proposals to user

### 3. Iterative Refinement
1. User selects preferred proposals and provides feedback
2. RecipePlanner creates IngredientClaims for selected recipes
3. IngredientBroker updates available inventory
4. RecipePlanner generates next round of proposals with remaining ingredients
5. Repeat until full week is planned

### 4. Recipe Development
1. For approved meal concepts (in pitch state), system generates full recipes
2. Previous IngredientClaims are released and new claims created for detailed ingredients
3. Recipe transitions from pitch to full state
4. Final ingredient requirements added to grocery shopping list

### 5. Execution Support
1. User views full recipes organized by planning session
2. Grocery list generated for items not available in current stores
3. Future: Recipe completion updates persistent IngredientStore inventories

## Architecture Decisions

### Technology Stack
- **Frontend**: Svelte for reactive UI with real-time updates
- **Backend**: FastAPI (Python) for REST APIs and WebSocket connections
- **AI/LLM**: BAML for completion engine, potential LangGraph for orchestration
- **Database**: SQLite initially (strongly typed, easy development iteration)
- **Communication**: WebSocket-based event bus for real-time planning updates

### Key Architectural Patterns

#### Event-Driven Architecture
- Frontend subscribes to planning events via WebSocket
- Intermediate results stream to frontend for responsive UX
- Events: `recipe_proposed`, `ingredient_conflict`, `planning_complete`, etc.

#### Negotiation Pattern
RecipePlanner ↔ IngredientBroker communication:
```
RecipePlanner: "I propose Recipe X with ingredients [A, B, C]"
IngredientBroker: "Approved" | "Conflict: only 1 cucumber available, need 3" | "Rejected: no prime rib available"
RecipePlanner: [handles substitutions and resubmits] | [abandons recipe after X attempts]
```

#### Claim-Based Planning
- All ingredient claims tracked as immutable objects
- Real-time availability computed from current claims
- Claims released and recreated when recipes change
- Clear separation between proposed and committed plans

## MVP Features

### Core Functionality
1. **IngredientStore Management**: CRUD for different store types with natural language input
2. **Basic Recipe Planning**: LLM-generated recipes from scratch (no catalog initially)
3. **Interactive Selection**: User approval/rejection of proposed recipes
4. **Iterative Planning**: Multi-round planning until week is complete
5. **Recipe Viewing**: Full recipe display organized by planning session
6. **Shopping List**: Automatic generation of needed grocery items

### User Interface
- Store management screen with ingredient input
- Planning interface with real-time proposal updates
- Recipe selection with feedback capabilities
- Final recipe and shopping list views

## Future Enhancements

### Recipe Intelligence
- Recipe catalog with import from external sources
- Recipe lineage tracking and evolution
- User ratings and feedback integration
- Preference learning and recipe weighting

### Advanced Planning
- Multi-day availability modeling (weekend vs weekday stores)
- Parametric recipes (tacos, sheet pan dinners, grain bowls)
- Meal prep optimization and ingredient reuse
- Nutritional analysis and dietary constraint handling

### Integration Features
- Recipe export to standard formats
- Integration with grocery delivery services
- Cooking timer and instruction assistance
- Inventory tracking through completion logging

## Development Breakdown

### Frontend Development
- Component design for store management, planning interface, recipe display
- WebSocket event handling and state management
- Real-time UI updates during planning process

### Backend Development
- REST API design for CRUD operations
- WebSocket event system architecture
- IngredientBroker negotiation logic
- Database schema and ORM setup

### AI/LLM Integration
- Prompt engineering for RecipePlanner
- BAML integration for reliable completions
- Context management for planning sessions
- Error handling and retry logic

### Data Architecture
- Database schema design with future flexibility
- Event sourcing for planning session audit trails
- Ingredient parsing and normalization
- Recipe storage and lineage tracking

This design balances immediate functionality with extensibility, allowing for rapid MVP development while maintaining a foundation for sophisticated future features.
