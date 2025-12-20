# Contributing to RIN

Thank you for your interest in contributing to the Rhyzomic Intelligence Node (RIN)!

## Project Philosophy

RIN is built on the principle of **digital sovereignty**. Contributions should maintain:

- **Independence**: Not reliant on any single provider
- **Transparency**: Clear, understandable code and operations
- **Privacy**: User data stays on user infrastructure
- **Extensibility**: Easy to add new capabilities
- **Control**: Users maintain full control

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs
- Include clear steps to reproduce
- Provide system information (OS, Python version, etc.)
- Include relevant logs or error messages

### Suggesting Features

- Open a GitHub Discussion or Issue
- Explain the use case
- Consider how it fits the sovereignty philosophy
- Provide examples if possible

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Add tests** for new functionality
5. **Ensure tests pass**: `pytest tests/`
6. **Update documentation** if needed
7. **Commit with clear messages**
8. **Push to your fork**
9. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Rhyzomic-Intelligence-Node-RIN-.git
cd Rhyzomic-Intelligence-Node-RIN-

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8 pylint

# Run tests
pytest tests/

# Format code
black src/rin

# Lint code
flake8 src/rin
pylint src/rin
```

## Code Style

- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions/classes
- Keep functions focused and modular
- Add comments for complex logic

## Testing Guidelines

- Write tests for all new features
- Maintain or improve test coverage
- Test edge cases and error handling
- Use descriptive test names
- Follow the existing test structure

## Areas for Contribution

### High Priority

- **Sensors**: New web scraping strategies, API integrations
- **Memory**: Vector database integrations (ChromaDB, Pinecone, etc.)
- **Reflexes**: New action types, workflow patterns
- **Documentation**: Tutorials, examples, guides

### Medium Priority

- **Performance**: Optimization, caching strategies
- **Security**: Authentication, sandboxing, validation
- **Testing**: Integration tests, end-to-end tests
- **UI**: Web interface, CLI improvements

### Ideas Welcome

- Multi-agent coordination
- Custom LLM provider integrations
- Tool integrations (databases, APIs, etc.)
- Deployment strategies
- Monitoring and observability

## Pull Request Process

1. **Keep PRs focused**: One feature or fix per PR
2. **Update documentation**: Include relevant doc updates
3. **Add tests**: Cover your changes with tests
4. **Pass CI checks**: Ensure all tests pass
5. **Describe changes**: Clear PR description with context
6. **Respond to feedback**: Address review comments

## Code Review

- All PRs require review before merging
- Reviews focus on:
  - Code quality and style
  - Test coverage
  - Documentation
  - Adherence to project philosophy
  - Security considerations

## Questions?

- Open a GitHub Discussion for questions
- Check existing issues and discussions first
- Be respectful and constructive

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for helping build sovereign AI infrastructure! 🚀
