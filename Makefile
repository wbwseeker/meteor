.PHONY: all

SRCDIR = meteor
TESTDIR = tests

POETRY = poetry
RUN = ${POETRY} run


all: dev


### Build ####################################################################
.PHONY: install dev

dev:
	${POETRY} install --with dev
	${RUN} pre-commit install

install:
	${POETRY} install --only main


### Testing & Development ####################################################
.PHONY: test coverage mypy check lint format

test:
	${RUN} coverage run --source ${SRCDIR} -m pytest -vvrw ${TESTDIR}

coverage:
	${RUN} coverage report -m
	${RUN} coverage html

mypy:
	${RUN} mypy --ignore-missing-imports ${SRCDIR}

lint:
	${RUN} ruff check ${SRCDIR} ${TESTDIR}

format:
	${RUN} ruff format ${SRCDIR} ${TESTDIR}
	${RUN} ruff check --fix ${SRCDIR} ${TESTDIR}

check: lint mypy test


### Cleanup ##################################################################
.PHONY: clean clean-env clean-all clean-build clean-test clean-dist

clean: clean-dist clean-test clean-build

clean-all: clean clean-env

clean-env:
	${POETRY} env remove --all

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
