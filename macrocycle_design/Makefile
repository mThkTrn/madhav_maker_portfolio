.PHONY: install test lint format clean build publish docs help

# Variables
PYTHON = python
PIP = pip
PYTEST = pytest
BLACK = black
ISORT = isort
FLAKE8 = flake8
MYPY = mypy
SPHINX_BUILD = sphinx-build
DOCS_DIR = docs
BUILDDIR = $(DOCS_DIR)/_build

# Default target
all: install

# Install the package in development mode
install:
	$(PIP) install -e .[dev]

# Install documentation dependencies
docs-install:
	$(PIP) install -r $(DOCS_DIR)/requirements-docs.txt

# Run tests
test:
	$(PYTEST) tests/ -v --cov=macrocycle_design --cov-report=term-missing

# Run linter
lint:
	$(FLAKE8) src/macrocycle_design tests/
	$(MYPY) src/macrocycle_design tests/

# Format code
format:
	$(BLACK) src/macrocycle_design tests/
	$(ISORT) src/macrocycle_design tests/

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/ $(BUILDDIR)
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete

# Build the package
build:
	$(PYTHON) setup.py sdist bdist_wheel

# Publish to PyPI (requires twine)
publish: clean build
	twine upload dist/*

# Build documentation
docs: docs-install
	@echo "Building documentation..."
	@$(SPHINX_BUILD) -M html "$(DOCS_DIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo "\nDocumentation built. Open $(BUILDDIR)/html/index.html in your browser."

# Serve documentation locally
docs-serve: docs
	python -m http.server 8000 --directory "$(BUILDDIR)/html/"

# Run all checks (test, lint, format)
check: lint test

# Show help
help:
	@echo "\nMacrocycle Design - Development Makefile\n"
	@echo "Available targets:\n"
	@echo "  install         Install the package in development mode"
	@echo "  docs-install    Install documentation dependencies"
	@echo "  test            Run tests with coverage"
	@echo "  lint            Run code linter and type checker"
	@echo "  format          Format code with Black and isort"
	@echo "  clean           Remove build artifacts and caches"
	@echo "  build           Build source and wheel package"
	@echo "  publish         Build and publish to PyPI"
	@echo "  docs            Build HTML documentation"
	@echo "  docs-serve      Serve documentation locally"
	@echo "  check           Run all checks (lint, test)"
	@echo "  help            Show this help message\n"
	@echo "Example usage:"
	@echo "  make install    # Install in development mode"
	@echo "  make test       # Run tests"
	@echo "  make docs       # Build documentation"
	@echo "  make clean      # Clean up build artifacts\n"
