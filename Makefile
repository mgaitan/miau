.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean        - remove all build, test, coverage and Python artifacts"
	@echo "clean-build  - remove build artifacts"
	@echo "clean-pyc    - remove Python file artifacts"
	@echo "test         - run tests quickly with the default Python"
	@echo "test-all     - run tests on every Python version with tox"
	@echo "coverage     - check code coverage quickly with the default Python"
	@echo "dist         - package"
	@echo "install      - install the package to the active Python's site-packages"
	@echo "release      - package and upload a release to PyPI"
	@echo "release-test - package and upload a release to PYPI (test)"
	@echo "docs         - generate Sphinx HTML documentation, including API docs"
	@echo "lint         - check style with Pylint"


clean: clean-build clean-pyc clean-test

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/

test:
	python setup.py test

test-all:
	tox

coverage:
	coverage run --source miau setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

release-test: clean
	python setup.py sdist upload --repository https://testpypi.python.org/pypi
	python setup.py bdist_wheel upload --repository https://testpypi.python.org/pypi
	open https://testpypi.python.org/pypi/miau

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean
	python setup.py install

lint:
	pylint miau tests

docs:
	rm -f docs/miau.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ miau
	make -C docs clean
	make -C docs html
	open docs/_build/html/index.html	
