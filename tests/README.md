# Testing Guide for Pi-PVARR

This README contains important information about testing the Pi-PVARR application.

## Running Tests

To run all tests:
```bash
python -m pytest tests/
```

To run a specific test file:
```bash
python -m pytest tests/integration/test_wizard_flow.py
```

To run a specific test class or method:
```bash
python -m pytest tests/integration/test_wizard_flow.py::TestWizardFlow::test_redirect_to_install_when_not_installed
```

## Common Testing Patterns

### Mocking Flask's send_from_directory

When mocking `send_from_directory` in tests, always return a Flask Response object, not a string:

```python
from flask import Response

# GOOD: Return a Flask Response object
mock_response = Response("Mock Content", 200, {"Content-Type": "text/html"})
with patch('src.api.server.send_from_directory', return_value=mock_response):
    # Test code here

# BAD: Don't return a string directly
# This will cause "str object has no attribute headers" errors
with patch('src.api.server.send_from_directory', return_value="Mock Content"):
    # This will fail when the code tries to access response.headers
```

### Testing Multi-Step Processes

For complex tests involving multi-step processes (like the installation wizard flow), 
use `side_effect` with a function rather than a list to have more control over mock behavior:

```python
def get_installation_status_side_effect(*args, **kwargs):
    # Track the call count and return different values based on the call sequence
    nonlocal call_counter
    call_counter += 1
    
    if call_counter == 1:
        return {"status": "not_started"}
    elif call_counter == 2:
        return {"status": "in_progress"}
    else:
        return {"status": "completed"}

with patch('src.core.install_wizard.get_installation_status', 
          side_effect=get_installation_status_side_effect):
    # Test code here
```

## Test Fixtures

The following fixtures are available for use in tests:

- `temp_dir`: Creates a temporary directory for test files
- `mock_config`: Provides a mock configuration for testing

## Test Organization

- `tests/unit/`: Contains unit tests that test individual functions and classes
- `tests/integration/`: Contains integration tests that test how components work together
- `tests/fixtures/`: Contains shared test fixtures and mock data