.DEFAULT_GOAL := all

.PHONY: docs
docs:
	mkdocs build

.PHONY: docs
docs-serve:
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
test: test-setup
	pytest --ignore tests/turbulette_tests/cli
	pytest tests/turbulette_tests/cli/

.PHONY: cov-setup
cov-setup:
	find "$$(poetry env info -p)/lib/python3.9/site-packages/" -iname "turbulette-*.dist-info" -type d -exec rm -rfd {} \;

.PHONY: testcov
testcov: cov-setup
	pytest --cov=turbulette --cov-report=html --ignore tests/turbulette_tests/cli
	pytest --cov=turbulette --cov-report=html --cov-append tests/turbulette_tests/cli/

.PHONY: clean
clean:
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
