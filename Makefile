.PHONY: test test-verbose test-genetics clean install dev lint format

# Run tests using uv
test:
	uv run pytest tests/ -v

# Run tests with more verbose output and coverage
test-verbose:
	uv run pytest tests/ -v --tb=long -s

# Run only genetics KP tests
test-genetics:
	uv run pytest tests/test_genetics_kp.py -v

# Install dependencies
install:
	uv sync

# Install development dependencies
dev:
	uv sync --group dev

# Run linting
lint:
	uv run black --check src/ tests/

# Format code
format:
	uv run black src/ tests/

# Clean up cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage

# Help
help:
	@echo "Available commands:"
	@echo "  make test         - Run all tests"
	@echo "  make test-verbose - Run tests with verbose output"
	@echo "  make test-genetics- Run only genetics KP tests"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Install dev dependencies"
	@echo "  make lint         - Check code formatting"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Clean up cache files"