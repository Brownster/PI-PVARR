# Developer Guide

This guide provides instructions for developers working on the Pi-PVARR project.

## Development Philosophy

Pi-PVARR follows these principles:

1. **Test-Driven Development**: Write tests first, then implement features
2. **Modularity**: Each component should have a single responsibility
3. **DRY (Don't Repeat Yourself)**: Avoid code duplication
4. **Documentation**: Document all code, APIs, and user workflows

## Project Structure

```
Pi-PVARR/
├── config/              # Configuration files
├── docs/                # Documentation
├── scripts/             # Shell scripts for installation and setup
├── src/                 # Source code
│   ├── api/             # Backend API
│   ├── core/            # Core functionality
│   ├── utils/           # Utility functions
│   └── web/             # Web UI
└── tests/               # Tests
    ├── integration/     # Integration tests
    └── unit/            # Unit tests
```

## Development Workflow

1. **Feature Planning**
   - Create an issue describing the feature
   - Break down the feature into manageable tasks

2. **Test First Approach**
   - Write unit tests for each component
   - Write integration tests for the feature

3. **Implementation**
   - Implement the feature following the requirements
   - Ensure all tests pass

4. **Documentation**
   - Update relevant documentation
   - Add inline code comments

5. **Code Review**
   - Submit a pull request
   - Address review feedback

## Setting Up the Development Environment

### Prerequisites

- Python 3.8+
- Node.js 14+
- Docker and Docker Compose

### Installation

```bash
# Clone the repository
git clone https://github.com/username/Pi-PVARR.git
cd Pi-PVARR

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Install frontend dependencies
cd src/web
npm install
cd ../..
```

## Running Tests

### Python Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit

# Run with coverage
pytest --cov=src

# Run a specific test file
pytest tests/unit/test_core.py
```

### JavaScript Tests

```bash
cd src/web
npm test
```

## Code Style

### Python

- Follow PEP 8
- Use 4 spaces for indentation
- Use docstrings for all functions, classes, and modules
- Use type hints

### JavaScript

- Use ESLint with recommended settings
- Use 2 spaces for indentation
- Use JSDoc for function documentation

## Commit Guidelines

- Use clear commit messages
- Reference issue numbers when relevant
- Each commit should represent a logical unit of change