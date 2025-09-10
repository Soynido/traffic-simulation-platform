# Tasks: Traffic Simulation and Analysis Platform

**Input**: Design documents from `/specs/001-traffic-simulation-platform/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/api-schema.yaml

## Architecture Summary
- **Project Type**: Web application (3 projects)
- **Backend**: Python 3.11+ + FastAPI + PostgreSQL + Redis
- **Frontend**: TypeScript/Node.js 20+ + Next.js + React  
- **Workers**: Python + Playwright + BullMQ
- **Structure**: backend/, frontend/, simulation-workers/

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Phase 3.1: Setup & Project Structure

- [x] T001 Create project structure (backend/, frontend/, simulation-workers/, docker-compose.yml)
- [x] T002 Initialize backend Python project with FastAPI, Alembic, Prisma dependencies in backend/
- [x] T003 [P] Initialize frontend Next.js project with TypeScript, Tailwind, shadcn/ui, Recharts in frontend/
- [x] T004 [P] Initialize simulation-workers Python project with Playwright dependencies
- [x] T005 [P] Configure linting (black, flake8, eslint, prettier)
- [x] T006 [P] Setup Docker containers for PostgreSQL, Redis, development environment
- [x] T007 [P] Configure environment variables (.env.example, .env templates)

## Phase 3.2: Database & Models (TDD - Tests First) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Database Schema Tests
- [x] T008 [P] Database schema test for personas table in backend/tests/contract/test_persona_schema.py
- [x] T009 [P] Database schema test for campaigns table in backend/tests/contract/test_campaign_schema.py  
- [x] T010 [P] Database schema test for sessions table in backend/tests/contract/test_session_schema.py
- [x] T011 [P] Database schema test for page_visits table in backend/tests/contract/test_page_visits_schema.py
- [x] T012 [P] Database schema test for actions table in backend/tests/contract/test_actions_schema.py

### API Contract Tests
- [x] T013 [P] Contract test GET /api/v1/personas in backend/tests/contract/test_personas_get.py
- [x] T014 [P] Contract test POST /api/v1/personas in backend/tests/contract/test_personas_post.py
- [x] T015 [P] Contract test PUT /api/v1/personas/{id} in backend/tests/contract/test_personas_put.py
- [x] T016 [P] Contract test GET /api/v1/campaigns in backend/tests/contract/test_campaigns_get.py
- [x] T017 [P] Contract test POST /api/v1/campaigns in backend/tests/contract/test_campaigns_post.py
- [x] T018 [P] Contract test POST /api/v1/campaigns/{id}/start in backend/tests/contract/test_campaigns_start.py
- [x] T019 [P] Contract test GET /api/v1/sessions/{id} in backend/tests/contract/test_sessions_get.py
- [x] T020 [P] Contract test GET /api/v1/analytics/campaigns/{id} in backend/tests/contract/test_analytics_get.py

### Integration Tests  
- [x] T021 [P] Integration test persona creation workflow in backend/tests/integration/test_persona_workflow.py
- [x] T022 [P] Integration test campaign creation and execution in backend/tests/integration/test_campaign_workflow.py
- [ ] T023 [P] Integration test session simulation end-to-end in simulation-workers/tests/integration/test_session_simulation.py
- [ ] T024 [P] Integration test analytics data processing in backend/tests/integration/test_analytics_processing.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Database Setup
- [x] T025 Create Alembic migrations for database schema in backend/alembic/versions/
- [x] T026 [P] Persona model in backend/src/models/persona.py
- [x] T027 [P] Campaign model in backend/src/models/campaign.py
- [x] T028 [P] Session model in backend/src/models/session.py  
- [x] T029 [P] PageVisit model in backend/src/models/page_visit.py
- [x] T030 [P] Action model in backend/src/models/action.py
- [x] T031 [P] SessionAnalytics model in backend/src/models/session_analytics.py
- [x] T032 [P] CampaignAnalytics model in backend/src/models/campaign_analytics.py

### Service Layer
- [x] T033 [P] PersonaService CRUD in backend/src/services/persona_service.py
- [x] T034 [P] CampaignService with state management in backend/src/services/campaign_service.py  
- [x] T035 [P] SessionService in backend/src/services/session_service.py
- [x] T036 [P] AnalyticsService for data processing in backend/src/services/analytics_service.py
- [x] T037 [P] SimulationOrchestrator for job queue management in backend/src/services/simulation_orchestrator.py

### API Endpoints
- [x] T038 GET /api/v1/personas endpoint in backend/src/api/personas.py
- [x] T039 POST /api/v1/personas endpoint in backend/src/api/personas.py
- [x] T040 PUT /api/v1/personas/{id} endpoint in backend/src/api/personas.py
- [x] T041 DELETE /api/v1/personas/{id} endpoint in backend/src/api/personas.py
- [x] T042 GET /api/v1/campaigns endpoint in backend/src/api/campaigns.py
- [x] T043 POST /api/v1/campaigns endpoint in backend/src/api/campaigns.py
- [x] T044 GET /api/v1/campaigns/{id} endpoint in backend/src/api/campaigns.py
- [x] T045 POST /api/v1/campaigns/{id}/start endpoint in backend/src/api/campaigns.py
- [x] T046 POST /api/v1/campaigns/{id}/pause endpoint in backend/src/api/campaigns.py
- [x] T047 GET /api/v1/sessions/{id} endpoint in backend/src/api/sessions.py
- [x] T048 GET /api/v1/analytics/campaigns/{id} endpoint in backend/src/api/analytics.py
- [x] T049 POST /api/v1/analytics/compare endpoint in backend/src/api/analytics.py

### Simulation Engine
- [x] T050 [P] BrowserManager for Playwright automation in simulation-workers/src/core/browser_manager.py
- [ ] T051 [P] PersonaSimulator for behavioral patterns in simulation-workers/src/core/persona_simulator.py  
- [ ] T052 [P] SessionRunner for executing individual sessions in simulation-workers/src/core/session_runner.py
- [ ] T053 [P] DataCollector for capturing metrics in simulation-workers/src/core/data_collector.py
- [x] T054 SimulationWorker main process in simulation-workers/src/workers/simulation_worker.py

### CLI Commands
- [ ] T055 [P] simulation-cli persona commands in simulation-workers/src/cli/persona_commands.py
- [ ] T056 [P] simulation-cli campaign commands in simulation-workers/src/cli/campaign_commands.py  
- [ ] T057 [P] analytics-cli analyze command in backend/src/cli/analytics_commands.py
- [ ] T058 [P] dashboard-cli dev/build commands in frontend/scripts/cli.js

## Phase 3.4: Frontend Implementation

### Design System Setup
- [x] T059 [P] Design tokens and TailwindCSS config in frontend/tailwind.config.js
- [x] T060 [P] Base UI components (Button, Card, Badge, Input) in frontend/src/components/ui/
- [x] T061 [P] Status badge component with campaign states in frontend/src/components/ui/StatusBadge.tsx

### Dashboard Components (inspired by GA4/Datadog)
- [x] T062 [P] KPI Card component with metrics display in frontend/src/components/dashboard/KPICard.tsx
- [x] T063 [P] Real-time Live Indicator component in frontend/src/components/dashboard/LiveIndicator.tsx
- [x] T064 [P] Progress Bar component for campaigns in frontend/src/components/dashboard/ProgressBar.tsx

### Analytics Components (Recharts integration)
- [x] T065 [P] Session Timeline LineChart in frontend/src/components/analytics/SessionChart.tsx
- [x] T066 [P] Persona Distribution DonutChart in frontend/src/components/analytics/PersonaChart.tsx
- [x] T067 [P] Human vs Simulated Comparison Chart in frontend/src/components/analytics/ComparisonChart.tsx

### Form & Management Components (Supabase-inspired)
- [x] T068 [P] PersonaForm with validation in frontend/src/components/personas/PersonaForm.tsx
- [x] T069 [P] PersonaList with DataTable in frontend/src/components/personas/PersonaTable.tsx
- [x] T070 [P] CampaignForm with URL validation in frontend/src/components/campaigns/CampaignForm.tsx
- [ ] T071 [P] CampaignDashboard with real-time updates in frontend/src/components/campaigns/CampaignDashboard.tsx

### Pages & Layout (GA4/Supabase-inspired)
- [ ] T072 [P] Main dashboard layout with sidebar navigation in frontend/src/components/layout/DashboardLayout.tsx
- [x] T073 [P] Analytics dashboard page with KPI cards in frontend/src/app/analytics/page.tsx
- [x] T074 [P] Personas management page with data table in frontend/src/app/personas/page.tsx
- [x] T075 [P] Campaign management page with status cards in frontend/src/app/campaigns/page.tsx
- [ ] T076 [P] Real-time monitoring page with live feed in frontend/src/pages/monitoring/index.tsx

### API & Data Integration
- [x] T077 [P] API client service with error handling in frontend/src/services/api.ts
- [x] T078 [P] WebSocket client for real-time updates in frontend/src/services/websocket.ts
- [x] T079 [P] Data formatting utilities for charts in frontend/src/utils/chartUtils.ts

## Phase 3.5: Integration & Middleware

- [x] T080 Database connection setup in backend/src/database/connection.py
- [ ] T081 Redis connection and job queue setup in backend/src/queue/redis_client.py
- [ ] T082 Authentication middleware in backend/src/middleware/auth.py
- [x] T083 CORS and security headers in backend/src/middleware/security.py  
- [x] T084 Request/response logging in backend/src/middleware/logging.py
- [ ] T085 Error handling middleware in backend/src/middleware/error_handler.py
- [ ] T086 Input validation middleware in backend/src/middleware/validation.py
- [ ] T087 WebSocket handler for real-time updates in backend/src/websockets/campaign_updates.py

## Phase 3.6: Polish & Performance

### Unit Tests
- [ ] T088 [P] Unit tests for PersonaService in backend/tests/unit/test_persona_service.py
- [ ] T089 [P] Unit tests for CampaignService in backend/tests/unit/test_campaign_service.py
- [ ] T090 [P] Unit tests for SimulationOrchestrator in backend/tests/unit/test_simulation_orchestrator.py  
- [ ] T091 [P] Unit tests for BrowserManager in simulation-workers/tests/unit/test_browser_manager.py
- [ ] T092 [P] Unit tests for PersonaSimulator in simulation-workers/tests/unit/test_persona_simulator.py
- [ ] T093 [P] Frontend component tests for KPI cards, charts in frontend/src/components/__tests__/

### Performance & Documentation
- [x] T094 Performance tests (<200ms API response) in backend/tests/performance/test_performance.py
- [ ] T095 Load testing for concurrent simulations in simulation-workers/tests/performance/test_load.py
- [ ] T096 [P] Update API documentation with design system in docs/api.md
- [ ] T097 [P] Create design system documentation in docs/design-system.md
- [ ] T098 [P] Update deployment documentation in docs/deployment.md
- [ ] T099 [P] Create troubleshooting guide with UI issues in docs/troubleshooting.md
- [ ] T100 Remove code duplication and refactor
- [ ] T101 Run quickstart validation tests from specs/001-traffic-simulation-platform/quickstart.md

## Dependencies

### Critical Path
- Setup (T001-T007) → Database Tests (T008-T012) → API Contract Tests (T013-T020) → Models (T026-T032) → Services (T033-T037) → API Endpoints (T038-T049)

### Parallel Groups
- **Models** (T026-T032): Independent entities can be built in parallel
- **Services** (T033-T037): Dependent on models but independent from each other  
- **API Endpoints** (T038-T049): Dependent on services, can share files so sequential
- **Frontend Components** (T059-T064): Independent components can be built in parallel
- **Unit Tests** (T078-T083): Independent test files can run in parallel

### Blocking Dependencies
- T025 (migrations) blocks T026-T032 (models)
- T026-T032 (models) block T033-T037 (services)  
- T033-T037 (services) block T038-T049 (API endpoints)
- T070-T077 (integration) require T033-T037 (services) to be complete
- T078-T083 (unit tests) require corresponding implementation tasks

## Parallel Execution Examples

### Phase 1: Database Schema Tests (after T007)
```
Task: "Database schema test for personas table in backend/tests/contract/test_persona_schema.py"
Task: "Database schema test for campaigns table in backend/tests/contract/test_campaign_schema.py"  
Task: "Database schema test for sessions table in backend/tests/contract/test_session_schema.py"
Task: "Database schema test for page_visits table in backend/tests/contract/test_page_visits_schema.py"
Task: "Database schema test for actions table in backend/tests/contract/test_actions_schema.py"
```

### Phase 2: API Contract Tests (after T012)
```
Task: "Contract test GET /api/v1/personas in backend/tests/contract/test_personas_get.py"
Task: "Contract test POST /api/v1/personas in backend/tests/contract/test_personas_post.py"
Task: "Contract test GET /api/v1/campaigns in backend/tests/contract/test_campaigns_get.py"
Task: "Contract test POST /api/v1/campaigns in backend/tests/contract/test_campaigns_post.py"
```

### Phase 3: Models (after T025)
```
Task: "Persona model in backend/src/models/persona.py"
Task: "Campaign model in backend/src/models/campaign.py"
Task: "Session model in backend/src/models/session.py"
Task: "PageVisit model in backend/src/models/page_visit.py"
```

## Validation Checklist

**GATE: Must verify before starting implementation**

- [ ] All 15 API endpoints from contract have corresponding tests (T013-T020)
- [x] All 7 database entities have model tasks (T026-T032)  
- [ ] All tests come before implementation (Phase 3.2 → 3.3)
- [x] Parallel tasks are truly independent (different files, no shared dependencies)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [ ] Integration tests cover main user workflows (T021-T024)
- [ ] CLI commands support library requirements (T055-T058)

## Notes

- **TDD Enforcement**: Tests in Phase 3.2 MUST fail before implementing Phase 3.3
- **Parallel Safety**: All [P] tasks modify different files with no shared state
- **File Conflicts**: API endpoints (T038-T049) modify shared files so run sequentially  
- **Performance Goals**: T094-T095 validate <200ms response time requirement
- **Design System**: T059-T071 implement GA4/Datadog-inspired UI with Recharts
- **Real-time UI**: T063, T078, T087 provide live updates with WebSocket integration
- **Constitutional Compliance**: Libraries (T026-T037) have CLI interfaces (T055-T058)
- **Commit Strategy**: Commit after each task completion for clean history
