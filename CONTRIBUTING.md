# Contributing Guide

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## Getting Started

1. Fork and clone the repository
2. Follow setup in [DEVELOPMENT.md](DEVELOPMENT.md)
3. Create a branch from `develop` branch

## Branch Naming

- `feature/*` — New features: `feature/add-late-fees-tracking`
- `bugfix/*` — Bug fixes: `bugfix/fix-datetime-parsing`
- `hotfix/*` — Production fixes: `hotfix/critical-security-patch`
- `docs/*` — Documentation: `docs/update-api-reference`
- `chore/*` — Maintenance: `chore/upgrade-dependencies`

## Commit Messages

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance, deps
- `ci`: CI/CD changes

### Scope
- `backend` — Python/Flask changes
- `frontend` — React changes
- `agents` — Agent changes
- `docker` — Docker/Compose changes
- `db` — Database/migrations

### Subject
- Imperative mood ("add" not "adds")
- Don't capitalize first letter
- No period at end
- Max 50 characters

### Example
```
feat(backend): add book import from CSV

Allow admins to import books in bulk via CSV upload.
- Parse CSV file and validate fields
- Check for duplicate ISBNs
- Create book records in database

Closes #123
```

## Pull Request Process

### Before Creating PR

1. **Create feature branch** from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/my-feature
   ```

2. **Make changes** with proper code style:
   ```bash
   # Backend
   black backend/
   flake8 backend/
   pytest tests/
   
   # Frontend
   cd frontend
   npm run lint -- --fix
   npm test
   ```

3. **Commit regularly** with clear messages
   ```bash
   git add .
   git commit -m "feat: describe what you did"
   ```

4. **Keep up with main**:
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

### Creating PR

1. Push your branch:
   ```bash
   git push origin feature/my-feature
   ```

2. Go to GitHub and create Pull Request

3. Fill out PR template:
   - Clear description of changes
   - Link related issues: `Closes #123`
   - Detail testing performed
   - Highlight any breaking changes

### PR Requirements

- ✅ All CI checks pass (tests, lint, build)
- ✅ Code review approval from 1+ maintainer
- ✅ Tests included for new features
- ✅ Documentation updated
- ✅ No uncommitted changes

### PR Review Process

**Reviewers will check:**
- Code quality and style
- Test coverage
- Backward compatibility
- Documentation
- Security implications

**Addressing feedback:**
- Reply to comments
- Make requested changes
- Push commits (don't force-push if under review)
- Request re-review

### Merging

Once approved and CI passes:
1. Squash and merge (preferred) or rebase and merge
2. Delete branch after merge
3. Close related issues

## Code Style

### Python

**Black Formatter** (non-negotiable)
```bash
black backend/ --line-length=120
```

**Flake8 Linter**
```bash
flake8 backend/ --max-line-length=120
```

**Type Hints** (recommended)
```python
def checkout_book(user_id: str, book_id: str) -> Dict[str, Any]:
    """Check out a book for a user."""
    pass
```

**Docstrings** (Google style)
```python
def calculate_due_date(days: int) -> datetime:
    """Calculate due date for book checkout.
    
    Args:
        days: Number of days to checkout (default: 14)
    
    Returns:
        Datetime object for due date
        
    Raises:
        ValueError: If days is negative
    """
    pass
```

### JavaScript/TypeScript

**Prettier** (automatic formatting)
```bash
npm run format
```

**ESLint** (style checking)
```bash
npm run lint -- --fix
```

**React Conventions**
- Functional components with hooks
- One component per file
- Props interface exported
- Clear, descriptive names

```typescript
interface BookCardProps {
  book: Book;
  onCheckout: (bookId: string) => Promise<void>;
}

const BookCard: React.FC<BookCardProps> = ({ book, onCheckout }) => {
  const handleClick = async () => {
    await onCheckout(book.id);
  };
  
  return <div>...</div>;
};

export default BookCard;
```

## Testing Requirements

### Backend

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Minimum coverage: 80%

```bash
pytest tests/ -v --cov=backend --cov-report=term-missing
```

**Example test**:
```python
def test_checkout_book_decrements_quantity(app, db):
    """Test that checking out a book decrements available quantity."""
    book = create_test_book(quantity=3)
    db.session.add(book)
    db.session.commit()
    
    with app.test_client() as client:
        response = client.post('/api/checkouts', 
            json={'book_id': str(book.id)},
            headers={'Authorization': 'Bearer test-token'})
    
    assert response.status_code == 201
    assert book.available_quantity == 2
```

### Frontend

- Unit tests: `frontend/src/**/*.test.tsx`
- React Testing Library (prefer user-centric tests)

```typescript
test('displays checkout button when book available', () => {
  const book = { id: '1', title: 'Test', available_quantity: 1 };
  render(<BookCard book={book} onCheckout={jest.fn()} />);
  
  expect(screen.getByRole('button', { name: /checkout/i })).toBeEnabled();
});
```

## Documentation Requirements

- **New feature**: Update API docs, architecture docs, README
- **Bug fix**: Add clarification comment if fix is non-obvious
- **Breaking change**: Document migration path
- **New endpoint**: Add to API reference with examples

## Agents & Automation

### For Agent Contributions

- Implement `BaseAgent` interface
- Register with `dispatcher` in `dispatcher.py`
- Include docstring explaining:
  - Event type(s) handled
  - Actions performed
  - Output/results
  - Example usage

```python
class MyCustomAgent(BaseAgent):
    """Custom agent for specific automation."""
    
    def __init__(self):
        super().__init__('MyCustomAgent')
    
    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GitHub event and return results."""
        # Implementation
        return {'status': 'success', 'message': 'Action completed'}
```

## GitHub Actions Workflows

- New workflows in `.github/workflows/`
- Document trigger conditions and jobs
- Use appropriate permissions/environments
- Avoid hardcoding secrets (use GitHub Settings)

## Security

- Never commit `.env` files or secrets
- Use `secrets.GITHUB_TOKEN` for GitHub actions
- Report security issues privately (see SECURITY.md)
- Keep dependencies up to date
- Run security scans locally: `trivy fs .`

## Review Checklist

Before requesting review, verify:

- [ ] Code follows style guide
- [ ] Tests written and passing
- [ ] No console warnings/errors
- [ ] No hardcoded passwords/keys
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No large unrelated changes
- [ ] Branch is up to date with main

## Questions?

- Check [DEVELOPMENT.md](DEVELOPMENT.md) for setup help
- Read [ARCHITECTURE.md](../ARCHITECTURE.md) for system design
- Check existing issues/PRs for similar questions
- Open a discussion for design questions

---

**Thank you for contributing!** 🙌
