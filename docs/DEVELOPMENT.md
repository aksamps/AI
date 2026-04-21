# Development Guide

## Prerequisites

- Docker & Docker Compose (v3.8+)
- Python 3.11+ (for local development without Docker)
- Node.js 18+ (for frontend development)
- Git

## Quick Start (5 minutes)

1. **Clone and setup**
```bash
git clone <repo>
cd AI
cp .env.example .env
```

2. **Start services**
```bash
docker-compose up -d
```

3. **Apply migrations and seed data**
```bash
docker-compose exec backend python database/seed.py
```

4. **Access the app**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api
- API Docs: http://localhost:5000/api/docs (when Swagger is configured)

## Development Workflow

### Backend Development

**Setup local environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Run locally without Docker**
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
export DATABASE_URL=postgresql://libraryuser:librarypass@localhost:5432/library_db
flask run --host=0.0.0.0 --port=5000
```

**Run tests**
```bash
pytest tests/ -v --cov=backend
```

**Linting and formatting**
```bash
flake8 backend/ --max-line-length=120
black backend/ --check
black backend/  # Reformat
```

### Frontend Development

**Setup local environment**
```bash
cd frontend
npm install
```

**Run dev server**
```bash
npm start
```

**Run tests**
```bash
npm test
```

**Build for production**
```bash
npm run build
```

### Database Operations

**Run migrations** (if using Alembic)
```bash
docker-compose exec backend alembic upgrade head
```

**Create new migration**
```bash
docker-compose exec backend alembic revision --autogenerate -m "description"
```

**Seed test data**
```bash
docker-compose exec backend python database/seed.py
```

**Reset database** (development only)
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d
docker-compose exec backend python database/seed.py
```

### Agent Development

**Run agents locally**
```bash
cd agents
python -m venv venv
source venv/bin/activate
pip install -r ../backend/requirements.txt
pip install PyGithub requests

# Set environment variables
export GITHUB_TOKEN=your-token
export GITHUB_WEBHOOK_SECRET=your-secret

python dispatcher.py
```

**Test agent event handling**
```bash
# Send test event to webhook
curl -X POST http://localhost:5001/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -d @test_event.json
```

## Docker Compose Commands

**Start all services**
```bash
docker-compose up -d
```

**View logs**
```bash
docker-compose logs -f backend    # Follow backend logs
docker-compose logs frontend      # See frontend logs
docker-compose ps                 # Service status
```

**Run commands in containers**
```bash
docker-compose exec backend python db/seed.py
docker-compose exec frontend npm test
```

**Stop services**
```bash
docker-compose stop
```

**Remove everything** (including volumes)
```bash
docker-compose down -v
```

## Environment Configuration

Copy `.env.example` to `.env` and customize:

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-key-change-in-prod

# Database
DATABASE_URL=postgresql://libraryuser:librarypass@postgres:5432/library_db

# OAuth (set to actual values for testing)
OAUTH_GOOGLE_CLIENT_ID=...
OAUTH_GOOGLE_SECRET=...
OAUTH_GITHUB_CLIENT_ID=...
OAUTH_GITHUB_SECRET=...

# GitHub Integration
GITHUB_TOKEN=...
GITHUB_WEBHOOK_SECRET=...

# Frontend
REACT_APP_API_URL=http://localhost:5000/api
```

## Common Issues

**Port already in use**
```bash
# Find and kill process
lsof -i :3000        # Find what's on port 3000
kill -9 <PID>        # Kill it
```

**PostgreSQL connection issues**
```bash
# Check if postgres is running
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Manually test connection
PGPASSWORD=librarypass psql -h localhost -U libraryuser -d library_db -c "SELECT 1"
```

**Backend migrations fail**
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec postgres pg_isready -U libraryuser
docker-compose up -d backend
```

**Frontend not loading**
```bash
# Clear npm cache
cd frontend && rm -rf node_modules package-lock.json
npm install

# Or rebuild Docker image
docker-compose build --no-cache frontend
docker-compose up frontend
```

**OAuth not working locally**
- Configure OAuth app on Google/GitHub with redirect URL: http://localhost:3000/auth/callback
- Update .env with credentials
- Restart backend

## Code Style & Standards

### Python
- **Formatter**: Black (line length: 120)
- **Linter**: flake8
- **Type hints**: Recommended for function signatures

### JavaScript/TypeScript
- **Formatter**: Prettier
- **Linter**: ESLint
- **Style**: React Hooks (functional components)

### Git Workflow

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit: `git commit -m "feat: description"`
3. Push branch: `git push origin feature/my-feature`
4. Create PR with template
5. Address PR feedback
6. Merge once approved and CI passes

### Commit Message Format

```
<type>: <subject>

<description>

Closes #<issue-number>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat: add book import from CSV

Allow users to bulk import books via CSV file upload
in admin panel. Validates ISBN and deduplicates entries.

Closes #42
```

## Testing

### Backend Tests
```bash
pytest tests/integration -v -s
pytest tests/agents -v
pytest --cov=backend --cov-report=html  # Coverage report
```

### Frontend Tests
```bash
cd frontend
npm test
npm test -- --coverage
```

### E2E/Smoke Tests
```bash
# After starting all services
python tests/e2e/smoke_test.py
```

## Debugging

### Backend Debugging with VS Code

1. Install debugpy: `pip install debugpy`
2. Add to `backend/app.py`:
```python
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()
```
3. Add to `.vscode/launch.json`:
```json
{
  "name": "Python: Flask",
  "type": "python",
  "request": "attach",
  "port": 5678,
  "host": "127.0.0.1"
}
```

### Frontend Debugging

Use React DevTools browser extension and Chrome DevTools

### Database Debugging

Connect directly with pgAdmin or command line:
```bash
psql -h localhost -U libraryuser -d library_db
```

## Performance Optimization

### Backend
- Database indexes on frequently-queried columns (organization_id, user_id)
- Query optimization with eager loading
- Redis caching for frequently accessed data

### Frontend
- Code splitting by route
- Lazy loading components
- Image optimization

## Documentation

- Update API docs in code comments
- Update architecture in `docs/ARCHITECTURE.md`
- Keep `CONTRIBUTING.md` current
- Add docstrings to all functions

## Troubleshooting with Logs

```bash
# View full service logs
docker-compose logs --tail=100 backend

# Follow logs in real-time
docker-compose logs -f frontend

# See startup logs
docker-compose up (without -d flag)
```

## IDE/Editor Setup

### VS Code Extensions
- Python
- Pylance  
- Black Formatter
- ES Lint
- Prettier - Code formatter
- Docker
- REST Client

### PyCharm
- Built-in support for Docker Compose
- Integrated debugging
- Database tools

---

**Need help?** Check GitHub Issues or TROUBLESHOOTING.md
