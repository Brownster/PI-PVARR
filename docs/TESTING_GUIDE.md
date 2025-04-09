# Pi-PVARR Testing Guide

This document provides instructions and best practices for testing the Pi-PVARR application, with a focus on the Installation Wizard.

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Test Environment Setup](#test-environment-setup)
3. [Backend Testing](#backend-testing)
   - [Unit Tests](#unit-tests)
   - [API Tests](#api-tests)
   - [Integration Tests](#integration-tests)
4. [Frontend Testing](#frontend-testing)
   - [JavaScript Unit Tests](#javascript-unit-tests)
   - [UI Component Tests](#ui-component-tests)
   - [End-to-End Tests](#end-to-end-tests)
5. [Manual Testing](#manual-testing)
6. [Test Coverage](#test-coverage)
7. [Continuous Integration](#continuous-integration)
8. [Test Reporting](#test-reporting)

## Testing Overview

Pi-PVARR follows a comprehensive testing strategy, including:

- **Unit Tests**: Testing individual functions and classes
- **API Tests**: Testing API endpoints
- **Integration Tests**: Testing interactions between components
- **UI Tests**: Testing frontend components and user interactions
- **End-to-End Tests**: Testing complete user flows
- **Manual Testing**: For UX validation and edge cases

Our testing requirements include:

- Backend code coverage of at least 70%
- Frontend code coverage of at least 70%
- All critical paths tested with integration tests
- All API endpoints covered with tests
- Successful tests for different hardware environments (Raspberry Pi, x86)

## Test Environment Setup

### Prerequisites

- Python 3.7+
- Node.js 14+
- Docker and Docker Compose
- pytest and dependencies (`pip install -r requirements-test.txt`)
- Jest and dependencies (`npm install` in the web-ui directory)

### Setting Up a Test Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/Pi-PVARR/Pi-PVARR.git
   cd Pi-PVARR
   ```

2. Install test dependencies:
   ```bash
   pip install -r requirements-test.txt
   cd web-ui
   npm install
   cd ..
   ```

3. Configure test environment variables:
   ```bash
   export PIPVARR_TEST_MODE=True
   export PIPVARR_TEST_DIR=/tmp/pipvarr-test
   ```

## Backend Testing

### Unit Tests

Unit tests verify the functionality of individual Python functions and classes.

#### Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_install_wizard.py

# Run specific test class
pytest tests/unit/test_install_wizard.py::TestInstallationStatus

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html
```

#### Writing Unit Tests

- Each module should have a corresponding test file (e.g., `src/core/install_wizard.py` → `tests/unit/test_install_wizard.py`)
- Use pytest fixtures for setup and teardown
- Mock external dependencies
- Test both success and failure paths
- Aim for >70% code coverage

Example unit test:

```python
def test_check_system_compatibility():
    """Test system compatibility check."""
    # Setup mocks
    with patch('src.core.system_info.get_system_info') as mock_get_system_info:
        mock_get_system_info.return_value = {
            "memory": {"total_gb": 4},
            "disk": {"free_gb": 20},
            "docker_installed": True
        }
        
        # Call the function
        result = install_wizard.check_system_compatibility()
        
        # Assertions
        assert result["status"] == "success"
        assert "compatible" in result
        assert "system_info" in result
        assert "checks" in result
```

### API Tests

API tests verify that the API endpoints return expected responses.

#### Running API Tests

```bash
# Run all API tests
pytest tests/unit/test_api_*.py

# Run specific API test file
pytest tests/unit/test_api_install.py
```

#### Writing API Tests

- Each API endpoint should have corresponding tests
- Use pytest fixtures to set up test clients
- Mock backend functions
- Test HTTP status codes and response content
- Test both valid and invalid inputs

Example API test:

```python
def test_check_system_compatibility(client, mock_compatibility_check):
    """Test checking system compatibility."""
    with patch('src.core.install_wizard.check_system_compatibility', 
              return_value=mock_compatibility_check):
        response = client.get('/api/install/compatibility')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert data["compatible"] is True
        assert "system_info" in data
        assert "checks" in data
```

### Integration Tests

Integration tests verify that different components work together correctly.

#### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run specific integration test file
pytest tests/integration/test_api_flows.py
```

#### Writing Integration Tests

- Focus on workflows that span multiple components
- Use real components where possible, mock external services
- Consider setup and teardown carefully
- Test complete user flows

Example integration test:

```python
def test_complete_installation_flow():
    """Test complete installation flow from start to finish."""
    # System setup
    with tempdir() as test_dir:
        # Configure test environment
        os.environ["PIPVARR_CONFIG_DIR"] = test_dir
        os.environ["PIPVARR_TEST_MODE"] = "True"
        
        # Start API server
        app = create_app({"TESTING": True})
        with app.test_client() as client:
            # Step 1: Check compatibility
            resp1 = client.get('/api/install/compatibility')
            assert resp1.status_code == 200
            
            # Step 2: Basic config
            config_data = {"puid": 1000, "pgid": 1000, "timezone": "UTC"}
            resp2 = client.post('/api/install/config', json=config_data)
            assert resp2.status_code == 200
            
            # ... additional steps
            
            # Final step: Run installation
            resp_final = client.post('/api/install/run', json=complete_config)
            assert resp_final.status_code == 200
            assert json.loads(resp_final.data)["status"] == "completed"
```

## Frontend Testing

### JavaScript Unit Tests

JavaScript unit tests verify the functionality of individual JavaScript functions and classes.

#### Running JavaScript Tests

```bash
# From the web-ui directory
npm test

# Run with coverage
npm test -- --coverage
```

#### Writing JavaScript Tests

- Create test files with `.test.js` extension
- Use Jest for testing
- Mock API calls
- Test both success and error cases

Example JavaScript test:

```javascript
describe('System Compatibility Check', () => {
  it('should display compatible results when system meets requirements', async () => {
    // Mock API response
    mockApi.setResponse('checkSystemCompatibility', {
      status: 'success',
      compatible: true,
      // ... other properties
    });
    
    // Trigger action
    const runCheck = document.getElementById('btn-run-system-check');
    runCheck.click();
    
    // Wait for API call
    await waitForApiCall();
    
    // Check DOM
    const resultsDiv = document.getElementById('system-check-results');
    expect(resultsDiv.classList.contains('hidden')).toBe(false);
    expect(resultsDiv.innerHTML).toContain('System is compatible');
  });
});
```

### UI Component Tests

UI component tests verify that UI components render and behave correctly.

#### Running UI Component Tests

```bash
# From the web-ui directory
npm test -- -t "UI Components"
```

#### Writing UI Component Tests

- Focus on component rendering and interactions
- Test appearance and behavior changes based on props/state
- Test user interactions (clicks, inputs, etc.)
- Use snapshots for complex components

Example UI component test:

```javascript
describe('Progress Bar Component', () => {
  it('should update width based on progress value', () => {
    // Setup
    document.body.innerHTML = `<div id="wizard-progress-fill"></div>`;
    const progressBar = document.getElementById('wizard-progress-fill');
    
    // Call function
    updateProgressBar(50);
    
    // Check result
    expect(progressBar.style.width).toBe('50%');
  });
});
```

### End-to-End Tests

End-to-end tests verify complete user flows through the application.

#### Running End-to-End Tests

```bash
# From the web-ui directory
npm run test:e2e
```

#### Writing End-to-End Tests

- Focus on entire user workflows
- Test realistic user scenarios
- Consider different device sizes
- Verify both UI appearance and backend effects

Example end-to-end test:

```javascript
describe('Installation Wizard Flow', () => {
  it('should complete full installation process', async () => {
    // Navigate to installation page
    await page.goto('http://localhost:8080/install');
    
    // Step 1: Run compatibility check
    await page.click('#btn-run-system-check');
    await page.waitForSelector('#system-check-results:not(.hidden)');
    await page.click('#btn-system-check-next');
    
    // Step 2: Fill basic config
    await page.fill('#puid', '1000');
    await page.fill('#pgid', '1000');
    await page.selectOption('#timezone', 'Europe/London');
    await page.click('#btn-basic-config-next');
    
    // ... additional steps
    
    // Final step: Start installation
    await page.click('#btn-start-install');
    
    // Wait for completion
    await page.waitForSelector('#install-complete:not(.hidden)', { timeout: 120000 });
    
    // Verify installation completed
    const completionText = await page.textContent('.step-header h2');
    expect(completionText).toContain('Installation Complete');
  });
});
```

## Manual Testing

Manual testing complements automated tests for UX validation and edge cases.

### Installation Wizard Manual Test Checklist

1. **System Compatibility Check**
   - [ ] Compatibility check properly detects system specifications
   - [ ] Compatible and incompatible results are displayed correctly
   - [ ] Next button is enabled/disabled appropriately

2. **Basic Configuration**
   - [ ] Form displays default values correctly
   - [ ] Validation works for required fields
   - [ ] Configuration is saved correctly

3. **Network Configuration**
   - [ ] VPN toggle shows/hides additional fields
   - [ ] Tailscale toggle shows/hides additional fields
   - [ ] Network configuration is saved correctly

4. **Storage Configuration**
   - [ ] Available drives are detected and displayed
   - [ ] Drive selection updates directory fields
   - [ ] File sharing options work correctly
   - [ ] Add share button creates new share form

5. **Service Selection**
   - [ ] All service toggle switches work
   - [ ] Service selection is saved correctly

6. **Installation**
   - [ ] Summary shows correct configuration choices
   - [ ] Progress bar updates during installation
   - [ ] Stage updates are displayed correctly
   - [ ] Installation log displays detailed information
   - [ ] Completion screen shows service URLs

### Device Testing Matrix

Test the installation wizard on:

- [ ] Raspberry Pi 4 (4GB+)
- [ ] Raspberry Pi 3
- [ ] x86 Linux desktop
- [ ] x86 Linux server
- [ ] Various screen sizes (desktop, tablet, mobile)
- [ ] Different browsers (Chrome, Firefox, Safari)

## Test Coverage

We aim for high test coverage to ensure code quality.

### Backend Coverage Targets

- Overall coverage: ≥70%
- Core modules: ≥80%
- Installation wizard: ≥85%

### Frontend Coverage Targets

- Overall coverage: ≥70%
- Critical components: ≥80%
- Wizard UI: ≥85%

### Measuring Coverage

For backend:
```bash
pytest --cov=src --cov-report=html
```

For frontend:
```bash
cd web-ui
npm test -- --coverage
```

Coverage reports are generated in:
- Backend: `htmlcov/index.html`
- Frontend: `web-ui/coverage/lcov-report/index.html`

## Continuous Integration

We use GitHub Actions for continuous integration testing.

### CI Workflow

1. On every pull request and push to main:
   - Run backend tests
   - Run frontend tests
   - Generate coverage reports
   - Verify coverage thresholds
   - Run linting checks

2. For releases:
   - Run end-to-end tests
   - Build Docker images
   - Test Docker images

### CI Configuration

CI is configured in `.github/workflows/` with separate workflows for:
- Backend testing
- Frontend testing
- End-to-end testing
- Docker image building

## Test Reporting

Test results are reported in multiple ways:

1. **CI Results**: Available in GitHub Actions tab
2. **Coverage Reports**: Generated during CI and available as artifacts
3. **Pull Request Checks**: Tests must pass for PR approval
4. **Badge in README**: Shows current test status

### Interpreting Test Failures

When tests fail:

1. Check the specific test that failed
2. Review the error message and stack trace
3. Check if recent code changes might have caused the failure
4. Run the test locally to debug
5. Fix the issue and verify with a re-run

## Conclusion

Comprehensive testing is essential for maintaining Pi-PVARR's quality and reliability. By following the testing practices in this guide, we ensure that the application provides a smooth experience for users while maintaining high code quality.