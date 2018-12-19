PYTHON = python3.7
VENV = .venv
VENV_PIP = $(VENV)/bin/pip
VENV_PYTHON = $(VENV)/bin/python
VENV_PY_TEST = $(VENV)/bin/py.test
VENV_DONE = $(VENV)/.done

$(VENV_DONE): $(MAKEFILE_LIST) setup.py $(wildcard *-requirements.txt)
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install -r setup-requirements.txt
	$(VENV_PIP) install -e '.[dev, test]'
	touch $@

.PHONY: venv
venv: $(VENV_DONE)

.PHONY: dist
dist: $(VENV_DONE)
	$(VENV_PYTHON) setup.py sdist bdist_wheel

.PHONY: test
test: $(VENV_DONE)
	$(VENV_PY_TEST) $(pytest)

.PHONY: clean
clean:
	git clean -ffdX
