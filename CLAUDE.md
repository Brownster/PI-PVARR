# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Testing Commands
- Run all tests: `pytest`
- Run with coverage: `pytest --cov=src --cov-report=term-missing`
- Run specific test category: `pytest tests/unit/` or `pytest tests/integration/`
- Run a single test file: `pytest tests/unit/test_file.py`
- Run a specific test: `pytest tests/unit/test_file.py::test_function_name`
- Run frontend tests: `cd src/web && npm test`

## Python Style Guidelines
- Follow PEP 8 conventions: 4 spaces indentation
- Function/variable names: snake_case
- Class names: PascalCase
- Constants: UPPER_CASE
- Use type hints for function parameters and return values
- Use docstrings for functions, classes, and modules
- Handle errors with try/except and descriptive messages

## JavaScript Style Guidelines
- Indentation: 2 spaces
- Use modern ES6+ syntax
- Function/variable names: camelCase
- Class names: PascalCase
- Constants: UPPER_CASE
- Use async/await for asynchronous code
- Organize API clients into logical method groups
- Use JSDoc comments for functions

## Bash Scripting Guidelines
- Use `set -euo pipefail` for error handling
- Functions should be snake_case
- Variables should be UPPER_CASE
- Use `[[ ]]` for conditionals (not `[ ]`)
- Document functions with comments
- Use heredocs (`<<EOF`) for multi-line text

## Project Structure
- `/src/api`: Backend API code
- `/src/core`: Core functionality
- `/src/utils`: Utility functions
- `/src/web`: Web UI code
- `/tests/unit`: Unit tests
- `/tests/integration`: Integration tests
- `/config`: Configuration files
- `/docs`: Documentation
- `/scripts`: Shell scripts for installation and setup

## Development Workflow
- Implement features incrementally
- Write tests before implementing features
- Document code and APIs
- Keep functions small and focused on a single responsibility
- Follow the DRY principle