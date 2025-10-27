Contributing to Macrocycle Design
===============================

We welcome contributions from the community! Here's how you can help improve Macrocycle Design.

Ways to Contribute
-----------------
- Report bugs
- Develop new features
- Improve documentation
- Submit bug fixes
- Add test cases
- Share ideas and suggestions

Development Setup
----------------
1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/macrocycle_design.git
   cd macrocycle_design
   ```
3. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Install the package in development mode:
   ```bash
   pip install -e .[dev]
   ```
5. Run the tests:
   ```bash
   pytest
   ```

Coding Standards
---------------
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings following the Google style
- Keep lines under 88 characters
- Include unit tests for new features

Pull Request Process
-------------------
1. Ensure tests pass
2. Update documentation as needed
3. Add your name to CONTRIBUTORS.md
4. Submit a pull request with a clear description of changes

Reporting Issues
--------------
When reporting bugs, please include:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs. actual behavior
- Version information (Python, package version, etc.)
- Any error messages or logs

Documentation
------------
To build the documentation locally:

```bash
cd docs
pip install -r requirements-docs.txt
make html
```

Then open `_build/html/index.html` in your browser.

Testing
-------
We use pytest for testing. To run the test suite:

```bash
pytest
```

For test coverage:

```bash
pytest --cov=macrocycle_design tests/
```

Code of Conduct
--------------
By participating in this project, you agree to abide by our Code of Conduct.
