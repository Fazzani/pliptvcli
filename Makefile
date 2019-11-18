SHELL=/bin/bash
TESTS=itests
TESTS_REPORTS_PATH=build/reports
TESTS_PATTERN=*_test.py
HEAD=HEAD~1
PL=https://gist.githubusercontent.com/Fazzani/722f67c30ada8bac4602f62a2aaccff6/raw/playlist1.m3u
PWD = $(shell pwd)

all: check pylint covreport

compile:
	@python -m compileall -fq .

check:
	@flake8 --exclude pliptv/__init__.py --max-complexity 10 pliptv/
	@flake8 itests

pylint:
	@pylint pliptv
	@pylint --load-plugins tests.linter --disable=I,E,W,R,C,F --enable C9999,C9998 $(TESTS)

test:
	@python -m xmlrunner discover -p $(TESTS_PATTERN) -o $(TESTS_REPORTS_PATH)

typecheck:
	@mypy --ignore-missing-imports --follow-imports=skip -p pliptv  --strict-optional --warn-no-return #--disallow-untyped-defs

covreport:
	@coverage erase
	@coverage run -m unittest discover -p $(TESTS_PATTERN)
	@coverage report -m

htmlcov: covreport
	@coverage html
	@open htmlcov/index.html

xmlcov: covreport
	@coverage xml

clean_up_pip:
	@pip freeze | xargs pip uninstall -y

clean_py_cache:
	@find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

create_env:
	@conda create --name pliptv python=3.7

remove_env:
	@conda deactivate && conda remove --name pliptv --all

bv_patch:
	@bumpversion patch && git push origin --tags
bv_min:
	@bumpversion minor && git push origin --tags
bv_maj:
	@bumpversion major && git push origin --tags

git_rebase_r:
	@echo "git rebase -i remote" $(HEAD)
	@git rebase -i origin/master$(HEAD) master do

git_rebase_p:
	@echo "git push origin +master"
	@git push origin +master

docker_b:
	@docker build -t synker/xpl:latest .
docker_r:
	@docker run --rm --env-file ./.envd -v "$(PWD)/data:/data" synker/xpl:latest --export --auto
run:
	PL=$(PL) python main.py --auto
mrproper:
	@rm -rf build
	@rm -rf .coverage
	@rm -rf xpl.egg-info

.PHONY: mrproper docker_b docker_r git_rebase_p git_rebase_r bv_maj bv_min bv_patch remove_env create_env clean_py_cache clean_up_pip xmlcov htmlcov covreport typecheck pylint test check compile all
