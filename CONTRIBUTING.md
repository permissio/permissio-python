# Contributing to Permis.io Python SDK

Thank you for your interest in contributing to the Permis.io Python SDK! This document provides guidelines and steps for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/permisio/permis-python/issues)
2. If not, create a new issue with:
   - A clear, descriptive title
   - Steps to reproduce the bug
   - Expected vs actual behavior
   - Python version and SDK version
   - Any relevant code snippets or error messages

### Suggesting Features

1. Check existing issues for similar suggestions
2. Create a new issue with the `enhancement` label
3. Describe the feature and its use case

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Write or update tests as needed
5. Ensure all tests pass: `pytest`
6. Run linting: `ruff check .`
7. Run type checking: `mypy permisio`
8. Format code: `black .`
9. Commit with clear messages following [Conventional Commits](https://www.conventionalcommits.org/)
10. Push to your fork and create a Pull Request

## Development Setup

### Prerequisites

- Python 3.9 or later
- pip or poetry

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/permis-python.git
cd permis-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=permisio --cov-report=term-missing

# Run specific test file
pytest tests/test_client.py

# Run tests in verbose mode
pytest -v
```

### Code Quality

```bash
# Run linter
ruff check .

# Fix linting issues
ruff check . --fix

# Run type checker
mypy permisio

# Format code
black .

# Check formatting without changing files
black . --check
```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all public functions
- Document public APIs with docstrings (Google style)
- Keep functions focused and small
- Write meaningful test cases

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Example: `feat: add tenant filtering to role assignment`

## Release Process

Releases are managed by the maintainers. Version bumps follow [Semantic Versioning](https://semver.org/).

## Questions?

Feel free to open an issue for any questions or reach out to the maintainers.

Thank you for contributing! 🎉
