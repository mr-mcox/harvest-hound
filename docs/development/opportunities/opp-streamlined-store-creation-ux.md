# Opportunity Brief: Streamlined Store Creation UX

**Problem Statement**

Users experience unnecessary friction in the store creation and inventory population workflow. The current system artificially separates store creation from inventory upload, requiring multiple navigation steps and context switches that don't match users' mental model of "setting up my ingredient sources."

Evidence from user feedback:
- "When I start out, I want to see a list of stores and then create store at the bottom"
- "I think we're unnecessarily dividing up the store 'creation' and populating with inventory - I should have knowledge to do both at the same time"
- "When I upload items, I don't care that it's successful and I shouldn't be prompted to upload more - I should be taken to the full set of items uploaded"

**User Stories**

**Story 1: New User Setup**
As a new user setting up my meal planning system, I want to see all my stores in one view with the ability to create new ones inline so that I can quickly establish my ingredient ecosystem without losing context.

**Story 2: CSA Delivery Day**
As a user who just received my weekly CSA box, I want to create a new store and immediately upload the contents in a single form so that I can move directly from "I got ingredients" to "let me plan meals" without workflow interruption.

**Story 3: Inventory Upload Completion**
As a user who just uploaded ingredients, I want to immediately see the complete inventory list for that store so that I can verify what was processed and understand what's available for meal planning.

**Current Experience**

1. User navigates to stores section
2. System shows store list or empty state
3. User clicks "Create Store" → separate creation form
4. User fills store details, saves → success message
5. User navigates to inventory upload (separate flow)
6. User uploads inventory → success confirmation with "Upload More?"
7. User must navigate elsewhere to see actual inventory results

**Impact**: 6-7 steps with multiple context switches for what feels like a single logical operation.

**Desired Outcomes**

**User Success**:
- Store creation and inventory population feels like one natural workflow
- Users see immediate results of their inventory uploads
- Dashboard view shows complete ingredient ecosystem at a glance

**Measurable Impact**:
- Reduce store setup time from ~5 minutes to ~2 minutes
- Eliminate "where did my inventory go?" confusion after upload
- Increase completion rate of initial setup flow

**Behavioral Change**:
- Users establish complete ingredient ecosystem in first session
- Users naturally update inventories when deliveries arrive
- Reduced friction leads to more frequent inventory updates

**Non-Goals**:
- Advanced inventory management features
- Changes to underlying domain model or API structure
- Multi-user or permission systems

**Constraints & Considerations**

**Must Preserve**:
- Existing API contracts for store creation and inventory upload
- Event sourcing patterns for domain changes
- Current domain model boundaries

**User Expectations**:
- Single form should handle both store metadata and inventory
- Immediate feedback when uploading inventory
- Dashboard view for managing multiple stores

**Technical Boundaries**:
- Must work within current FastAPI/Svelte architecture
- Maintain separation between write operations and read projections
- Support WebSocket events for real-time updates

**Related Opportunities**

- **Description-Based Stores**: Complementary opportunity addressing different store types and object design
- **Inventory Normalization**: Quality of ingredient parsing affects user confidence in upload flow

**Open Questions**

1. **Form Design**: Should the single form be tabs (Store Info | Inventory) or a single scrollable form with sections?

2. **Upload Methods**: Should we support both file upload and manual entry in the unified form?

3. **Error Handling**: How do we handle partial success scenarios (store created, inventory upload fails) in a single form context?

4. **Navigation**: After successful creation + upload, should users land on the store detail view or return to the store list?

**Success Criteria**

- Users complete store creation and inventory population without navigation confusion
- Post-upload, users immediately see their inventory in context
- Workflow feels natural: "I have ingredients → I upload them → I see what's available"
- Reduced time-to-value for new user onboarding