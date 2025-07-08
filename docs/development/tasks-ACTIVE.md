# Test Quality Improvement - Active Tasks

## Purpose

Address critical code smells in the test suite that indicate fundamental architectural problems:

1. **Excessive @patch usage** (8+ decorators per file) masking poor dependency injection
2. **Typing overrides in pyproject.toml** hiding interface design issues
3. **Import disorganization** violating PEP8 and obscuring dependencies
4. **Test duplication** across multiple integration test files
5. **Complex multi-concern tests** mixing API, event sourcing, and view model testing

**Goal**: Eliminate code smells through proper architecture, not configuration workarounds. Reduce total test count by 30-40% while maintaining coverage.

## Current State Assessment

### ✅ Foundation Work Completed
- Created typed service interfaces (`app/interfaces/`)
- Implemented dependency injection (`app/dependencies.py`)
- Demonstrated zero-patch approach (`tests/test_dependency_injection.py`)
- Validated strict mypy compliance is achievable

### ⚠️ Critical Issues Discovered
- **Database integration failure**: `items_added=2` but `inventory=[]` in tests
- **Legacy test files unchanged**: Still using @patch decorators and poor typing
- **Parallel infrastructure**: Created new files without removing old ones
- **Root cause unclear**: Dependency injection may have broken event sourcing or view projections

### 📁 Files Created (Some Placeholders)
```
app/interfaces/           # Keep - core typed interfaces
app/dependencies.py       # Keep - DI implementation
tests/conftest.py        # Keep - centralized fixtures
tests/implementations/   # Review - may consolidate
tests/utils/             # Review - api_helpers useful, fixtures redundant
tests/test_dependency_injection.py  # Keep - working example
tests/test_integration_typed.py     # REMOVE - placeholder with DB issues
```

## Systematic Plan Forward

### Phase 1: Root Cause Analysis & Database Fix (HIGH PRIORITY)
**Objective**: Understand why integration tests are failing and fix fundamental issues

#### 1.1 Diagnose Database Integration Issues
- [x] Investigate why `items_added=2` but inventory retrieval returns `[]`
- [x] Verify event sourcing is working correctly with dependency injection
- [x] Check if view store projections are being triggered
- [x] Validate database session management in test environment

#### 1.2 Fix Dependency Injection Architecture
- [x] Ensure event store projection registry is properly initialized
- [x] Fix database session scoping for tests vs production
- [x] Verify that FastAPI dependency overrides work correctly
- [x] Test with simplified end-to-end scenario

#### 1.3 Validate Core Functionality
- [x] Get one complete integration test working: create store → upload → verify items
- [x] Ensure test uses dependency injection (no @patch)
- [x] Confirm proper typing throughout the stack

### Phase 2: Systematic Migration (One File at a Time)
**Objective**: Replace problematic test files with improved versions

#### 2.1 Consolidate Integration Tests
**Target**: Replace 4 files with 1 comprehensive file
- Current files: `test_integration_mocked_llm.py`, `test_backend_integration.py`, `test_happy_path_integration.py`, `test_error_handling_integration.py`
- New file: `test_integration_comprehensive.py`

**Process**:
- [x] Catalog all unique test scenarios across the 4 files
- [x] Design consolidated test structure with typed fixtures
- [x] Implement using dependency injection (zero @patch decorators)
- [x] Ensure comprehensive coverage of happy path, error cases, edge cases
- [x] Validate with strict mypy compliance
- [x] **Remove the 4 original files**

#### 2.2 Update Remaining Test Files
- [x] `test_store_service.py` - Update to use dependency injection
- [x] `test_view_stores.py` - Remove patches, add proper typing
- [x] Other files - Audit and update systematically

### Phase 3: Cleanup & Optimization
**Objective**: Remove redundancy and temporary files

#### 3.1 Remove Placeholder Files
- [x] Delete `tests/test_integration_typed.py` (failed placeholder)
- [x] Consolidate `tests/implementations/` (keep only necessary mocks)
- [x] Remove `tests/utils/typed_fixtures.py` (content moved to conftest.py)
- [x] Clean up any other duplicate/placeholder files

#### 3.2 Optimize Test Architecture
- [x] Ensure `tests/utils/api_helpers.py` is used across all integration tests
- [x] Consolidate mock implementations - keep only essential ones
- [x] Review test organization for logical grouping

#### 3.3 Remove Legacy Compatibility Layer
- [x] Remove backward compatibility globals from `api.py`
- [x] Ensure all tests use proper dependency injection

### Phase 4: Validation & Typing Compliance
**Objective**: Achieve full typing compliance and validate improvements

#### 4.1 Remove Typing Overrides
```toml
# Remove from pyproject.toml:
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_incomplete_defs = false
```

#### 4.2 Validate Success Criteria
- [x] **Zero @patch decorators** in entire test suite
- [x] **All imports at file tops** (PEP8 compliant)
- [x] **30-40% reduction in test count** while maintaining coverage
- [ ] **Full mypy compliance** for all test files
- [ ] **Clear separation of concerns** in test architecture

#### 4.3 Final Validation
- [ ] Run complete test suite with coverage analysis
- [ ] Verify mypy passes with strict settings on all files
- [ ] Confirm performance improvement (faster test execution)
- [ ] Document the new testing patterns for future development

## Risk Management

### High Risk Issues
1. **Database integration problems** - Could indicate fundamental architecture issues
2. **Test coverage regression** - Must maintain existing coverage during consolidation
3. **Integration complexity** - Event sourcing + view projections + dependency injection

### Mitigation Strategies
- Fix database issues before any major migrations
- Run coverage reports before/after each phase
- Implement changes incrementally with validation
- Keep working tests as reference during migration

## Success Metrics

### Quantitative Goals
- **Zero** @patch decorators across test suite
- **30-40% reduction** in total test file count
- **Full mypy compliance** without typing overrides
- **Maintain or improve** test coverage percentage

### Qualitative Goals
- Tests serve as clear documentation of system behavior
- Easy to add new tests following established patterns
- Debugging test failures provides clear insights
- Type safety prevents common testing mistakes

## Next Immediate Actions

1. **PRIORITY 1**: Investigate and fix the database integration issues in Phase 1.1
2. **PRIORITY 2**: Get one complete integration test working end-to-end
3. **PRIORITY 3**: Begin systematic migration of integration test files

The foundation work was valuable, but the real value comes from completing the migration and cleanup phases.
