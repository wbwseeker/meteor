.PHONY: all

ENV = .venv
SRCDIR = meteor
TESTDIR = tests

PYTHON = python3  # uses version from .python-version if pyenv is installed
VENV_PYTHON = ${ENV}/bin/python
PIP = ${ENV}/bin/pip
POETRY = poetry  # Poetry should be installed globally
PYTEST = ${ENV}/bin/pytest
COVERAGE = ${ENV}/bin/coverage
PRECOMMIT = ${ENV}/bin/pre-commit
MYPY = ${ENV}/bin/mypy
RUFF = ${ENV}/bin/ruff


all: dev


### Build ####################################################################
.PHONY: venv install dev

dev: venv
	${POETRY} install --with dev
	${PRECOMMIT} install

install: venv
	${POETRY} install --only main

venv:
	if [ ! -d "${ENV}" ]; then \
	    ${PYTHON} -m venv ${ENV} ; \
	    ${PIP} install --upgrade pip ; \
	fi


### Testing & Development ####################################################
.PHONY: test coverage mypy check lint format

test:
	${COVERAGE} run --source ${SRCDIR} -m pytest -vvrw ${TESTDIR}

coverage:
	${COVERAGE} report -m
	${COVERAGE} html

mypy:
	${MYPY} --ignore-missing-imports ${SRCDIR}

# Ruff linting (replaces flake8, isort checks)
lint:
	${RUFF} check ${SRCDIR} ${TESTDIR}

# Ruff formatting (replaces black, isort)
format:
	${RUFF} format ${SRCDIR} ${TESTDIR}
	${RUFF} check --fix ${SRCDIR} ${TESTDIR}

# Run all checks (for CI)
check: lint mypy test

### Cleanup ##################################################################
.PHONY: clean clean-env clean-all clean-build clean-test clean-dist

clean: clean-dist clean-test clean-build

clean-all: clean clean-env

clean-env: clean
	-@rm -rf $(ENV)

clean-build:
	@find $(SRCDIR) -name '*.pyc' -delete
	@find $(SRCDIR) -name '__pycache__' -delete
	@find $(TESTDIR) -name '*.pyc' -delete 2>/dev/null || true
	@find $(TESTDIR) -name '__pycache__' -delete 2>/dev/null || true
	-@rm -rf *.egg-info
	-@rm -rf __pycache__
	-@rm -rf .ruff_cache

clean-test:
	-@rm -rf .cache
	-@rm -rf .coverage
	-@rm -rf htmlcov
	-@rm -rf .pytest_cache/
	-@rm -rf .mypy_cache/

clean-dist:
	-@rm -rf dist build
