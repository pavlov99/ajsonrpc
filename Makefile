.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile

pipenv:
	@pipenv install --dev

.PHONY: clean
# target: clean - Display callable targets
clean:
	@rm -rf build dist docs/_build
	@find . -name \*.py[co] -delete
	@find . -name *\__pycache__ -delete

.PHONY: build
# target: build - Build package
build: clean
	@pipenv run python setup.py sdist bdist_wheel

.PHONY: test-release
# target: test-release - Release package to test pypi
test-release: build
	@pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

.PHONY: release
# target: release - Release package to pypi
release: build
	@pipenv run twine upload dist/*
