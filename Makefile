TESTS=itests
TESTS_REPORTS_PATH=build/reports
TESTS_PATTERN=*_test.py

all: check pylint covreport

compile:
	python -m compileall -fq .

check:
	flake8 --exclude pliptv/__init__.py --max-complexity 10 pliptv/
	flake8 itests

pylint:
	pylint dags
	pylint --load-plugins tests.linter --disable=I,E,W,R,C,F --enable C9999,C9998 $(TESTS)

test:
	python -m xmlrunner discover -p $(TESTS_PATTERN) -o $(TESTS_REPORTS_PATH)

typecheck:
	mypy --ignore-missing-imports --follow-imports=skip -p dags  --strict-optional --warn-no-return #--disallow-untyped-defs

covreport:
	coverage erase
	coverage run -m unittest discover -p $(TESTS_PATTERN)
	coverage report -m

htmlcov: covreport
	coverage html
	open htmlcov/index.html

xmlcov: covreport
	coverage xml

clean_up_pip:
	pip freeze | xargs pip uninstall -y

clean_py_cache:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

create_env:
	conda create --name pliptv python=3.7

remove_env:
	conda deactivate && conda remove --name pliptv --all

.PHONY: mrproper

mrproper:
	@rm -rf build
	@rm -rf .coverage