ENV=$(CURDIR)/.env
BIN=$(ENV)/bin

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile

.PHONY: clean
# target: clean - Display callable targets
clean:
	@rm -rf build dist docs/_build
	@find . -name \*.py[co] -delete
	@find . -name *\__pycache__ -delete

env:
	@python3 -m venv $(ENV)

env-test: env
	$(BIN)/pip install pytest==6.2.1 pytest-asyncio==0.14.0

.PHONY: test
# target: test - test the code
test:
	$(BIN)/pytest

.PHONY: build
# target: build - Build package
build: clean
	$(BIN)/python setup.py sdist bdist_wheel

.PHONY: test-release
# target: test-release - Release package to test pypi
test-release: build
	$(BIN)/twine upload --repository-url https://test.pypi.org/legacy/ dist/*

.PHONY: release
# target: release - Release package to pypi
release: build
	$(BIN)/twine upload dist/*
