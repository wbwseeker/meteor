.PHONY: all

ENV = env
SRCDIR = meteor
TESTDIR = tests

PYTHON = ${ENV}/bin/python
PIP = ${ENV}/bin/pip
VIRTUALENV = virtualenv
POETRY = ${ENV}/bin/poetry
COVERAGE = ${ENV}/bin/coverage
PYTEST = ${COVERAGE} run --source ${SRCDIR} -m pytest -vvrw
PRECOMMIT = ${ENV}/bin/pre-commit
MYPY = ${ENV}/bin/mypy


all: dev


### Build ####################################################################
.PHONY: virtualenv install dev

dev: virtualenv
	${PIP} install -q poetry
	${POETRY} install
	${PRECOMMIT} install

install: virtualenv
	${POETRY} install --no-dev

virtualenv:
	if [ ! -d "${ENV}" ]; then \
	    ${VIRTUALENV} ${ENV} ; \
	    ${PIP} install --upgrade pip ; \
        ${PIP} install poetry ; \
        ${POETRY} config --local virtualenvs.create false ; \
        ${POETRY} config --local virtualenvs.in-project true ; \
	fi


### Testing & Development ####################################################
.PHONY: test coverage mypy

test:
	${PYTEST} ${TESTDIR}

coverage:
	${COVERAGE} report -m

mypy:
	${MYPY} ${SRCDIR}

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

clean-test:
	-@rm -rf .cache
	-@rm -rf .coverage
	-@rm -rf .pytest_cache/
	-@rm -rf .mypy_cache/

clean-dist:
	-@rm -rf dist build
