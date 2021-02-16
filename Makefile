.DEFAULT_GOAL := all
isort := isort -rc turbulette tests
black := black .

.PHONY: all
all: lint testcov

.PHONY: install-lint
install-lint: ## Install main deps plus lint deps
	poetry install -E dev_lint

.PHONY: install-test
install-test: ## Install main deps plus tests deps
	poetry install -E dev_test

.PHONY: install-doc
install-doc: ## Install main deps plus doc deps
	poetry install -E dev_doc

.PHONY: install-all
install-all: ## Install main deps, plus every optionals ones
	poetry install -E dev_test -E dev_lint -E dev_doc

.PHONY: install-pre-commit
install-pre-commit: ## Instal pre-commit hooks
	pre-commit install --install-hooks

.PHONY: lint
lint: ## Run linting tools
	prospector turbulette
	$(isort) --check-only -df
	$(black) --check --diff

.PHONY: format
format: ## Run formatting tools
	$(isort)
	$(black)

.PHONY: docs
docs: ## Build documentation
	mkdocs build

.PHONY: docs
docs-serve: ## Build and serve documentation locally
	mkdocs serve

.PHONY: postgres
test-setup:
	[[ $$(docker ps -f "name=turbulette-test" --format '{{.Names}}') == "turbulette-test" ]] || \
	(docker run --rm --name turbulette-test -p 5432:5432/tcp \
		-e POSTGRES_PASSWORD="" \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_HOST_AUTH_METHOD=trust \
		-e POSTGRES_DB=test \
	-d postgres \
	&& sleep 5)

.PHONY: test
test: test-setup ## Run the full test suite
	pytest --ignore tests/turbulette_tests/cli
	pytest tests/turbulette_tests/cli/

.PHONY: test-cli
test-cli: test-setup ## Only run CLI tests
	pytest tests/turbulette_tests/cli/

.PHONY: test-no-cli
test-no-cli: test-setup ## Run every tests excepts CLI ones
	pytest --ignore tests/turbulette_tests/cli

.PHONY: cov-setup
cov-setup:
	find "$$(poetry env info -p)/lib/python$$(poetry env info -p | grep -E "3\..*" -o)/site-packages/" \
		-iname "turbulette-*.dist-info" -type d -exec rm -rfd {} \;

.PHONY: testcov
testcov: test-setup cov-setup ## Run tests with coverage (HTML output)
	pytest --cov=turbulette --cov-report=html --ignore tests/turbulette_tests/cli
	pytest --cov=turbulette --cov-report=html --cov-append tests/turbulette_tests/cli/

.PHONY: testcov-xml
testcov-xml: test-setup cov-setup ## Run tests with coverage (XML output)
	pytest --cov=turbulette --cov-report=xml --ignore tests/turbulette_tests/cli
	pytest --cov=turbulette --cov-report=xml --cov-append tests/turbulette_tests/cli/

.PHONY: clean
clean: ## Clean build / cache directories
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist
	rm -f turbulette/*.c turbulette/*.so
	rm -rf site
	rm -rf docs/_build
	rm -rf docs/.changelog.md docs/.version.md docs/.tmp_schema_mappings.html
	rm -rf codecov.sh
	rm -rf coverage.xml

.PHONY: help
help: ## Print this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {gsub("\\\\n",sprintf("\n%22c",""), $$2);printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
