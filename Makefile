# NEXUS-RE Makefile
# Note: NEXUS-RE has ZERO runtime dependencies (pure Python 3.11+ stdlib).
# Only dev tools (pytest, flake8, black) are needed for testing/linting.

.PHONY: help install test test-fast lint doctor run docker clean

help:
	@echo "NEXUS-RE Makefile targets:"
	@echo "  install   - (no-op; zero runtime deps)"
	@echo "  test      - Run all 56 tests"
	@echo "  test-fast - Run tests, stop on first failure"
	@echo "  lint      - Run flake8 + black check"
	@echo "  doctor    - Environment health check"
	@echo "  run       - Start CLI"
	@echo "  docker    - Build Docker image"
	@echo "  clean     - Remove caches"

install:
	@echo "NEXUS-RE has zero runtime dependencies."
	@echo "Only dev tools needed:"
	@echo "  pip install -r requirements-dev.txt"

test:
	python -m pytest tests/ -v

test-fast:
	python -m pytest tests/ -x -q

lint:
	flake8 nexus_re_v3.py nexus_agents.py nexus_rag.py doctor.py api_render.py --max-line-length=120
	black --check nexus_re_v3.py nexus_agents.py nexus_rag.py doctor.py api_render.py

doctor:
	python doctor.py

run:
	python nexus_re_v3.py

docker:
	docker build -t nexus-re:latest .

clean:
	rm -rf __pycache__ .pytest_cache build dist *.egg-info
