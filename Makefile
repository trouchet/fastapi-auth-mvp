.PHONY: build run stop ps host

OMIT_PATHS := "*/__init__.py,backend/tests/*"

define PRINT_HELP_PYSCRIPT
import re, sys

regex_pattern = r'^([a-zA-Z_-]+):.*?## (.*)$$'

for line in sys.stdin:
	match = re.match(regex_pattern, line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

sanitize: # Remove dangling images and volumes
	docker system prune --volumes -f
	docker images --filter 'dangling=true' -q --no-trunc | xargs -r docker rmi

clean-logs: # Removes log info. Usage: make clean-logs
	rm -fr build/ dist/ .eggs/
	find . -name '*.log' -o -name '*.log' -exec rm -fr {} +

clean-test: # Remove test and coverage artifacts
	rm -fr .tox/ .testmondata* .coverage coverage.* htmlcov/ .pytest_cache

clean-cache: # remove test and coverage artifacts
	find . -name '*pycache*' -exec rm -rf {} +

clean: clean-logs clean-test clean-cache ## Add a rule to remove unnecessary assets. Usage: make clean

env: ## Creates a virtual environment. Usage: make env
	pip install virtualenv
	virtualenv .venv

install: ## Installs the python requirements. Usage: make install
	pip install uv
	uv pip install -r requirements.txt
	uv pip install -r requirements-dev.txt

run: ## Run the application. Usage: make run
	uvicorn backend.app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000

search: ## Searchs for a token in the code. Usage: make search token=your_token
	grep -rnw . --exclude-dir=venv --exclude-dir=.git --exclude=poetry.lock -e "$(token)"

replace: ## Replaces a token in the code. Usage: make replace token=your_token
	sed -i 's/$(token)/$(new_token)/g' $$(grep -rl "$(token)" . \
		--exclude-dir=venv \
		--exclude-dir=.git \
		--exclude=poetry.lock)

codecov: # Send coverage report to codecov
	curl -Os https://cli.codecov.io/latest/linux/codecov
	chmod +x codecov 

ip: ## Get the IP of a container. Usage: make ip container="db-cron-task"
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(container)

ip-db: ## Get the database IP. Usage: make db-ip
	$(MAKE) ip container=auth-db

kill-container: ## Kill the database container. Usage: make kill-db
	docker inspect --format '{{.State.Pid}}' $(container) | sudo xargs kill -9

kill-db: ## Kill the database container. Usage: make kill-db
	$(MAKE) kill-container container=auth-db

kill-redis: ## Kill the database container. Usage: make kill-db
	$(MAKE) kill-container container=auth-redis

kill-app: ## Kill the database container. Usage: make kill-db
	$(MAKE) kill-container container=auth-app

kill: kill-db kill-app kill-nginx ## Kill the database and cron containers. Usage: make kill

test: ## Test the application. Usage: make test
	poetry run coverage run --rcfile=.coveragerc -m pytest

test-watch: ## Run tests on watchdog mode. Usage: make ptw-watch
	ptw --quiet --spool 200 --clear --nobeep --config pytest.ini --ext=.py --onfail="echo Tests failed, fix the issues"

minimal-requirements: ## Generates minimal requirements. Usage: make requirements
	python3 scripts/clean_packages.py requirements.txt requirements.txt

lint: ## perform inplace lint fixes
	@ruff check --unsafe-fixes --fix .
	@black $(shell git ls-files '*.py')

pylint:
	@pylint backend/

report: test ## Generate coverage report. Usage: make report
	coverage report --omit=$(OMIT_PATHS) --show-missing

ps: ## List all containers. Usage: make ps
	docker ps -a

build: ## Build the application. Usage: make build
	docker-compose build

down: ## Down the application. Usage: make down
	docker-compose down

up: ## Up the application. Usage: make up
	docker-compose up --build -d
