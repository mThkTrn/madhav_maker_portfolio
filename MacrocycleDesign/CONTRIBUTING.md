# Contributing to Macrocycle Design

Thank you for your interest in contributing to Macrocycle Design! We welcome contributions from the community to help improve this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [Code Review Process](#code-review-process)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How to Contribute

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. Create a new **branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number-description
   ```
4. Make your changes and **commit** them with a clear message
5. **Push** your changes to your fork
6. Open a **pull request** against the `main` branch

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/macrocycle_design.git
   cd macrocycle_design
   ```

2. Create and activate a virtual environment:
   ```bash
   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e .[dev]
   ```

4. Install pre-commit hooks (optional but recommended):
   ```bash
   pre-commit install
   ```

## Code Style

We follow these style guidelines to maintain code quality and consistency:

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for all function arguments and return values
- Write docstrings following [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Keep lines under 88 characters (Black's default)
- Use absolute imports
- Use double quotes for strings (Black's default)

### Code Formatting

We use several tools to maintain code quality. Before committing, run:

```bash
make format  # Runs Black and isort
make lint    # Runs flake8 and mypy
```

## Testing

### Writing Tests

- Write tests for all new features and bug fixes
- Place test files in the `tests/` directory
- Follow the naming convention `test_*.py` for test files
- Use descriptive test function names like `test_function_name_expected_behavior`
- Use fixtures for common test data

### Running Tests

Run the full test suite:

```bash
make test
```

Run a specific test file or test function:

```bash
pytest tests/test_module.py::test_function_name
```

Run tests with coverage report:

```bash
pytest --cov=macrocycle_design --cov-report=term-missing
```

## Documentation

### Building Documentation

To build the documentation locally:

```bash
make docs
```

This will generate HTML documentation in `docs/_build/html/`.

### Documentation Guidelines

- Keep docstrings up to date with code changes
- Document all public classes, methods, and functions
- Include examples in docstrings where helpful
- Update the relevant `.rst` files in `docs/` when adding new features
- Add new examples to `docs/examples.rst`

## Pull Request Process

1. Ensure your code passes all tests and linting checks
2. Update the documentation to reflect your changes
3. Include tests for new features and bug fixes
4. Update the changelog if applicable
5. Ensure your branch is up to date with the latest changes from `main`
6. Submit your pull request with a clear description of the changes

## Reporting Bugs

When reporting bugs, please include:

1. A clear, descriptive title
2. Steps to reproduce the issue
3. Expected vs. actual behavior
4. Version information (Python, package version, OS)
5. Any error messages or logs

## Feature Requests

We welcome feature requests! Please open an issue with:

1. A clear description of the feature
2. The problem it solves
3. Any alternative solutions considered
4. Additional context or examples

## Code Review Process

1. A maintainer will review your pull request
2. You may receive feedback or requested changes
3. Once approved, a maintainer will merge your changes
4. Your contribution will be included in the next release
  ```
- Aim for good test coverage (run `pytest --cov=macrocycle_design` to check)

## Pull Request Guidelines

- Keep pull requests focused on a single feature or bug fix
- Update documentation as needed
- Add tests for new functionality
- Ensure all tests pass before submitting
- Write a clear description of your changes in the PR

## Reporting Issues

When reporting issues, please include:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs. actual behavior
- Version information (Python, package version, etc.)

## License

By contributing to this project, you agree that your contributions will be licensed under the [MIT License](LICENSE).
