# Contributing Guide

Thank you for contributing to Maestro Tuya IR Bridge! This guide will help you get started.

## Quick Start

```bash
# Clone and setup
git clone <your-fork>
cd maestro-tuya-ir-bridge

# Install dependencies and build C++ extensions
make install

# Run tests
make test

# Run linter
make lint

# Auto-fix formatting
make format
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feat/my-new-feature
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Write code
- Add/update tests
- Update documentation if needed

### 3. Run Quality Checks Locally

```bash
# Run all checks (recommended before push)
make check

# Or run individually:
make test          # Tests (MUST pass)
make lint          # Linting (MUST pass)
make format        # Auto-format code
```

### 4. Commit Your Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
# Format: <type>[optional scope]: <description>

git commit -m "feat: add support for LG HVAC protocol"
git commit -m "fix(api): correct Fujitsu header timing"
git commit -m "docs: update deployment guide"
git commit -m "test: add integration tests for Tuya codes"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `test`: Adding/updating tests
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feat/my-new-feature
```

**PR Title MUST Follow Conventional Commits:**

✅ Good:
```
feat: add Panasonic AC protocol support
fix(decoder): handle invalid Tuya codes gracefully
docs: add examples for protocol detection
```

❌ Bad:
```
Add new feature
Fixed bugs
Update README
```

### 6. Wait for CI Checks

Your PR will automatically trigger:

- ✅ **Tests** - All tests must pass
- ✅ **Lint** - Code must pass ruff checks
- ✅ **PR Title Check** - Title must follow conventional commits
- ✅ **Deployment Gate** - All above must pass

**Vercel deployment is blocked until all checks pass!**

## Code Quality Standards

### Python Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check for issues
make lint

# Auto-fix issues
make fix

# Format code
make format
```

### Tests

- **All tests must pass** before merging
- **C++ bindings are REQUIRED** - tests will fail without them
- Aim for >80% code coverage
- Write tests for:
  - New features
  - Bug fixes
  - Edge cases

```bash
# Run all tests
make test

# Run specific test file
uv run pytest tests/test_protocols.py -v

# Run with coverage
uv run pytest --cov=app tests/
```

### C++ Extensions

- C++ bindings are **REQUIRED** for the application
- Rebuild after pulling changes:
  ```bash
  make clean
  make install
  ```

- Verify bindings are working:
  ```bash
  uv run python -c "from app.core.protocols import IRREMOTE_AVAILABLE; print('C++ bindings:', IRREMOTE_AVAILABLE)"
  ```

## Common Tasks

### Adding a New Protocol

1. Add protocol definition to `bindings/irremote/irremote_bindings.cpp`
2. Rebuild C++ extensions: `make build-ext`
3. Add test in `tests/test_protocols.py`
4. Update documentation

### Fixing a Bug

1. Write a failing test that reproduces the bug
2. Fix the bug
3. Ensure test passes
4. Create PR with title: `fix: description of what was fixed`

### Updating Documentation

1. Update relevant `.md` files
2. Create PR with title: `docs: description of changes`

## Troubleshooting

### Tests Fail with "C++ bindings not available"

```bash
make clean
make install
make test
```

### Linting Errors

```bash
# Auto-fix most issues
make fix

# Check what's still wrong
make lint
```

### PR Title Check Fails

Edit your PR title on GitHub to match:
```
<type>: <description>
```

Examples:
- `feat: add new protocol`
- `fix: correct timing calculation`
- `docs: update API examples`

### Vercel Deployment Blocked

1. Go to your PR on GitHub
2. Click "Checks" tab
3. Fix any failing checks
4. Push fixes
5. Vercel will auto-deploy once checks pass

## Need Help?

- 📖 Read [BRANCH_PROTECTION.md](.github/BRANCH_PROTECTION.md)
- 📖 Check [README.md](../README.md)
- 💬 Open an issue for questions
- 💬 Ask in PR comments

## Review Process

1. Create PR with proper title (conventional commits)
2. All CI checks must pass (tests, lint, title)
3. Request review from maintainers
4. Address review feedback
5. Once approved + checks pass → Merge!

## Release Process

Releases are automated:

1. Merge to `main` triggers production deployment
2. Vercel builds only if all checks pass
3. C++ extensions must compile successfully
4. Tests must pass in CI

---

**Remember:** Quality over speed. Take time to write good tests and documentation!
