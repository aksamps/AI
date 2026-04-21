#!/bin/bash
# Verification Script for Phase 1 Implementation

echo "=== Library Management System - Phase 1 Verification ==="
echo ""

# Check directory structure
echo "📁 Verifying Directory Structure..."
directories=(
    "backend"
    "frontend/src"
    "frontend/public"
    "agents"
    "docker"
    "database"
    "docs"
    ".github/workflows"
    "tests/integration"
    "tests/agents"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir"
    else
        echo "❌ $dir (MISSING)"
    fi
done

echo ""
echo "📄 Verifying Critical Files..."
files=(
    "backend/app.py"
    "backend/config.py"
    "backend/requirements.txt"
    "backend/models/models.py"
    "backend/routes/auth.py"
    "backend/routes/books.py"
    "backend/routes/checkouts.py"
    "backend/routes/memberships.py"
    "frontend/package.json"
    "frontend/tsconfig.json"
    "frontend/src/App.tsx"
    "frontend/src/api/client.ts"
    "frontend/public/index.html"
    "agents/base_agent.py"
    "agents/coding_agent.py"
    "agents/pr_review_agent.py"
    "agents/workflow_agent.py"
    "agents/dispatcher.py"
    "docker/Dockerfile.backend"
    "docker/Dockerfile.frontend"
    "docker/Dockerfile.agents"
    "docker/nginx.conf"
    "docker-compose.yml"
    "docker-compose.prod.yml"
    ".github/workflows/ci.yml"
    ".github/workflows/approval-gate.yml"
    ".github/workflows/deploy-staging.yml"
    ".github/workflows/deploy-production.yml"
    ".github/workflows/agent-review.yml"
    ".github/CODEOWNERS"
    ".github/pull_request_template.md"
    "database/seed.py"
    "docs/ARCHITECTURE.md"
    "docs/DEVELOPMENT.md"
    "CONTRIBUTING.md"
    ".env.example"
    ".gitignore"
    ".dockerignore"
    "IMPLEMENTATION_SUMMARY.md"
    "QUICKSTART.md"
)

total=0
found=0

for file in "${files[@]}"; do
    total=$((total + 1))
    if [ -f "$file" ]; then
        found=$((found + 1))
        echo "✅ $file"
    else
        echo "❌ $file (MISSING)"
    fi
done

echo ""
echo "=== Summary ===" 
echo "Directories: ${#directories[@]} ✅"
echo "Files: $found/$total ✓"
echo ""

if [ $found -eq $total ]; then
    echo "🎉 Phase 1 Implementation COMPLETE!"
    echo ""
    echo "Next steps:"
    echo "1. Run: docker-compose up -d"
    echo "2. Read: docs/DEVELOPMENT.md"
    echo "3. Start Phase 2: API Implementation"
else
    echo "⚠️  Some files are missing. Check output above."
    exit 1
fi
