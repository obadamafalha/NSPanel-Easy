# NSPanel Easy - Test Suite

This directory contains comprehensive tests for the NSPanel Easy project.

## Test Structure

### Test Structure: Python Tests

- `test_nspanel_easy_init.py` - Tests for the ESPHome component initialization (`components/nspanel_easy/__init__.py`)
- `test_workflows.py` - Integration tests for GitHub Actions workflows
- `test_config_files.py` - Validation tests for configuration files (YAML, JSON, etc.)

### Test Structure: C++ Tests

- `test_addon_climate.cpp` - Unit tests for climate addon functionality
- `test_addon_upload_tft.cpp` - Unit tests for TFT upload state management
- `test_base.cpp` - Unit tests for base component (flags, utilities)

## Running Tests

### Running Tests: Python Tests

Install dependencies:
```bash
pip install -r requirements.txt
```

Run all Python tests:
```bash
pytest -v
```

Run specific test file:
```bash
pytest test_config_files.py -v
```

Run with coverage:
```bash
pytest --cov=../components/nspanel_easy --cov-report=html
```

### Running Tests: C++ Tests

C++ tests require Google Test framework. To compile and run:

```bash
# Install Google Test
sudo apt-get install libgtest-dev

# Compile tests
g++ -std=c++17 -I.. -lgtest -lgtest_main -pthread test_addon_climate.cpp -o test_addon_climate
g++ -std=c++17 -I.. -lgtest -lgtest_main -pthread test_addon_upload_tft.cpp -o test_addon_upload_tft
g++ -std=c++17 -I.. -lgtest -lgtest_main -pthread test_base.cpp -o test_base

# Run tests
./test_addon_climate
./test_addon_upload_tft
./test_base
```

## Test Coverage

The test suite provides comprehensive coverage for:

1. **Configuration Files**: Validates YAML, JSON, and other config files for correct syntax and structure
2. **GitHub Workflows**: Tests workflow configuration, triggers, and job dependencies
3. **Python Components**: Unit tests for ESPHome component initialization and configuration
4. **C++ Components**: Unit tests for climate control, TFT upload, and base functionality
5. **Documentation**: Validates issue templates and project documentation

## Continuous Integration

These tests are designed to run in CI/CD pipelines. The GitHub workflows in `.github/workflows/` already validate:

- YAML syntax (yamllint)
- Python code (flake8)
- C++ formatting (clang-format)
- Markdown formatting and links
- ESPHome compilation

The tests in this directory provide additional validation beyond the CI checks.

## Writing New Tests

### Python Test Guidelines

- Use pytest framework
- Follow the existing test structure (classes for logical grouping)
- Use descriptive test names (test_should_do_something)
- Add docstrings to test classes and methods
- Use fixtures for shared setup/teardown

### C++ Test Guidelines

- Use Google Test framework
- Use TEST_F for test fixtures
- Group related tests in test fixtures
- Add comments explaining complex test logic
- Test edge cases and boundary conditions

## Test Categories

1. **Unit Tests**: Test individual functions and classes in isolation
2. **Integration Tests**: Test how components work together
3. **Validation Tests**: Test configuration and documentation files
4. **Regression Tests**: Prevent previously fixed bugs from reoccurring

## Contributing

When adding new features or fixing bugs:

1. Write tests first (TDD approach recommended)
2. Ensure all tests pass before submitting PR
3. Add tests for edge cases and error conditions
4. Update this README if adding new test categories
