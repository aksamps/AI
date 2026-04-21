# Architecture

## System Overview

This is a multi-tenant, containerized Book Library Management System built with:
- **Backend**: Python Flask REST API
- **Frontend**: React TypeScript SPA
- **Database**: PostgreSQL (multi-tenant)
- **Cache**: Redis
- **Agents**: Rule-based automation agents (Coding, PR Review, Workflow)
- **Orchestration**: Docker Compose (development), production single-server deployment
- **CI/CD**: GitHub Actions with approval gates

## Architecture Diagram

```
┌─────────────────────────────────────┐
│     GitHub Repository / PR Events   │
└────────────┬────────────────────────┘
             │
             ├─► GitHub Actions (CI)
             │   - Backend tests/lint
             │   - Frontend tests/lint
             │   - Build Docker images
             │   - Security scanning
             │
             └─► Approval Gate
                 - Requires manual approval
                 - All CI checks must pass
                 │
                 └─► Staging Deployment
                     └─► Production (on main merge)

┌─────────────────────────────────────┐
│     Agents (Rule-based)             │
├─────────────────────────────────────┤
│ 1. Coding Agent                     │
│    - Lint checks (flake8)           │
│    - Test execution (pytest)        │
│    - Format checks (black)          │
│                                     │
│ 2. PR Review Agent                  │
│    - PR metadata validation         │
│    - Auto-labeling                  │
│    - Feedback comments              │
│                                     │
│ 3. Workflow Agent                   │
│    - CI/CD orchestration            │
│    - Approval gate enforcement      │
│    - PR lifecycle tracking          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      Application Tier               │
├─────────────────────────────────────┤
│  Frontend (React 3000)              │
│    - Login (OAuth)                  │
│    - Dashboard (checkouts)          │
│    - Browse books                   │
│    - Admin panel                    │
│                                     │
│  Backend (Flask 5000)               │
│    - Auth endpoints (OAuth)         │
│    - Books API (CRUD)               │
│    - Checkouts API                  │
│    - Memberships API                │
│    - AuditLog API                   │
│                                     │
│  Agents (5001)                      │
│    - Webhook listener               │
│    - Event dispatcher               │
│    - Agent handlers                 │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      Data Tier                      │
├─────────────────────────────────────┤
│  PostgreSQL (5432)                  │
│    - organizations (multi-tenant)   │
│    - users (OAuth profiles)         │
│    - memberships (roles)            │
│    - books (catalog)                │
│    - checkouts (tracking)           │
│    - audit_logs (actions)           │
│                                     │
│  Redis (6379)                       │
│    - Session cache                  │
│    - Agent task queue               │
│    - Rate limiting state            │
└─────────────────────────────────────┘
```

## Multi-Tenancy Model

- **Organization-centric**: Each organization has isolated data
- **Shared infrastructure**: All organizations use same backend/database
- **Data isolation**: SQL WHERE clauses enforce org_id filtering
- **Users**: Belong to single organization (can join multiple via additional feature)
- **Books, Checkouts, Memberships**: All scoped to organization_id

### Data Flow

1. User logs in via OAuth (Google/GitHub)
2. User record created if first login
3. Membership record links user to organization
4. All subsequent queries filtered by organization_id
5. Checkouts isolated to user's organization books

## API Layers

### Authentication Layer
- OAuth 2.0 (Google, GitHub)
- JWT tokens for session management
- Rate limiting (Flask-Limiter)

### API Endpoints

**Auth**
- POST `/api/auth/login` — OAuth login initiation
- GET `/api/auth/callback` — OAuth callback
- POST `/api/auth/logout` — Logout
- GET `/api/auth/me` — Current user info

**Books**
- GET `/api/books` (paginated, searchable)
- GET `/api/books/{id}`
- POST `/api/books` (admin)
- PATCH `/api/books/{id}` (admin)
- DELETE `/api/books/{id}` (admin)

**Checkouts**
- POST `/api/checkouts` — Checkout book
- GET `/api/checkouts` — List user's checkouts
- GET `/api/checkouts/{id}` — Checkout details
- POST `/api/checkouts/{id}/return` — Return book

**Memberships** (admin)
- POST `/api/memberships` — Add member
- GET `/api/memberships` — List members
- PATCH `/api/memberships/{id}` — Update role/status
- DELETE `/api/memberships/{id}` — Revoke membership

### Database Schema

**organizations**
- id (UUID)
- name (unique)
- description
- created_at, updated_at

**users**
- id (UUID)
- organization_id (FK)
- email, name
- oauth_provider (google|github)
- oauth_id, oauth_access_token
- avatar_url

**memberships**
- id (UUID)
- user_id (FK), organization_id (FK)
- role (admin|member)
- status (active|revoked)

**books**
- id (UUID)
- organization_id (FK)
- title, author, isbn, edition
- total_quantity, available_quantity

**checkouts**
- id (UUID)
- user_id (FK), book_id (FK), org_id (FK)
- checkout_at, due_date
- returned_at, status (active|returned)

**audit_logs**
- id (UUID)
- organization_id (FK)
- action_type (agent actions)
- actor (agent name or user)
- resource_type, resource_id
- details (JSON)

## Agent Architecture

### Agent Framework
- **BaseAgent**: Abstract base class for all agents
- **EventDispatcher**: Routes GitHub events to agents
- **Agent Handler**: Implements event processing logic

### Agents

**1. Coding Agent**
- Triggered: On push (commits to PR branches)
- Actions:
  - Run flake8 linting
  - Execute pytest tests
  - Check black formatting
- Output: PR comment with results

**2. PR Review Agent**
- Triggered: On pull_request (opened, synchronize, reopened)
- Actions:
  - Validate PR description
  - Check for linked issues
  - Auto-label (type/backend, type/frontend, etc.)
- Output: PR labels and comments

**3. Workflow Agent**
- Triggered: On workflow_run (CI completion)
- Actions:
  - Monitor CI status
  - Enforce approval requirement
  - Track PR lifecycle
  - Update merge eligibility
- Output: PR comments, branch protection updates

### Event Flow

```
GitHub Event → Webhook → Dispatcher → Agent → Handle → Log to DB → Response
(PR created)   POST            (route)  (match)  (process) (audit_log)
             /webhooks/github
```

### Webhook Signature Verification
- Uses HMAC-SHA256
- Secret: `GITHUB_WEBHOOK_SECRET` env var
- Header: `X-Hub-Signature-256`

## CI/CD Pipeline

### Workflow: Continuous Integration (ci.yml)

**Triggers**: On push (all branches), PR

**Jobs** (parallel):
1. Backend Tests
   - Lint (flake8)
   - Format check (black)
   - Tests (pytest with coverage)
   - Coverage upload to Codecov

2. Frontend Tests
   - Lint (ESLint)
   - Format check (Prettier)
   - Tests (Jest)

3. Build Backend
   - Docker multi-stage build
   - Tag with commit SHA
   - Push to GHCR

4. Build Frontend
   - Docker multi-stage build with nginx
   - Tag with commit SHA
   - Push to GHCR

5. Security Scan
   - Trivy vulnerability scan
   - Upload to GitHub Security

### Workflow: Approval Gate (approval-gate.yml)

**Triggers**: On CI completion

**Steps**:
1. Check CI passed
2. Get current PR approval count
3. If < 1 approval: comment "Awaiting Approval"
4. If ≥ 1 approval: comment "Ready to Merge"
5. Fail if no approval (blocks merge)

### Workflow: Staging Deployment

**Triggers**: Manual dispatch, Approval gate completion

**Steps**:
1. Pull Docker images
2. Deploy with docker-compose
3. Run smoke tests
4. Comment PR with staging URL

### Workflow: Production Deployment

**Triggers**: Push to main, manual dispatch

**Steps**:
1. Pull Docker images
2. Tag with version/timestamp
3. Deploy to prod
4. Health checks
5. DB migrations
6. Slack notification

## Deployment

### Development (docker-compose.yml)
- All services: backend, frontend, postgres, redis, agents
- Hot-reload enabled
- Local volumes for code
- Test database connectivity

### Production (docker-compose.prod.yml)
- Optimized images (no source code)
- Resource limits
- Health checks
- Nginx reverse proxy
- TLS/SSL (on reverse proxy)
- Database backups
- Logging configuration

## Security Considerations

1. **Secrets Management**: All secrets in GitHub Settings (not in .env)
2. **OAuth**: No password storage (OAuth2 only)
3. **CORS**: Configured to frontend origin only
4. **JWT**: Signed tokens, expiring at 30 days
5. **Rate Limiting**: Flask-Limiter on API endpoints
6. **Webhook Verification**: HMAC-SHA256 signature check
7. **SQL Injection**: SQLAlchemy ORM (parameterized queries)
8. **CSRF**: Token validation on forms (in Phase 2)

## Scaling Considerations

**Current Limits** (Docker Compose single-server):
- ~5-20 concurrent users
- ~10,000 books
- ~100 checkouts/day

**Scaling Path to Kubernetes**:
1. Move to Kubernetes cluster
2. Use same Docker images
3. Create Helm charts from docker-compose
4. Add ingress controller
5. Database: Managed PaaS (AWS RDS, Azure Database)
6. Cache: Managed Redis (AWS ElastiCache)
7. Monitoring: Prometheus + Grafana

## Monitoring & Logging

**Logging Metrics**:
- Application logs: stdout/stderr (Container logs)
- Audit logs: Database (audit_logs table)
- GitHub Actions: Workflow logs, status

**Health Checks**:
- Endpoint: GET `/api/health`
- Docker Compose: 30s interval, 5s timeout

## Disaster Recovery

1. **Database Backups**: Daily (production)
2. **Code**: GitHub (version control)
3. **Container Images**: GHCR (registry)
4. **Configuration**: Environment variables (GitHub Settings)
5. **Rollback**: Deploy previous stable image from registry

---

For development setup, see [DEVELOPMENT.md](DEVELOPMENT.md)
For deployment, see [DEPLOYMENT.md](DEPLOYMENT.md)
