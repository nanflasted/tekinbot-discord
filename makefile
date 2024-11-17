.PHONY: all

all: venv

clean:
	poetry env remove python3
	rm -rf .venv

venv:
	poetry install --no-root
	poetry env use python3

install-hooks:
	pre-commit install -f --install-hooks

server: venv 
	poetry run python3 -m tekinbot.neo_tekin

dev: install-hooks
	poetry install --with=dev --no-root
	poetry env use python3
	poetry run python3 -m tekinbot.neo_tekin --dry-run --no-db

test:
	poetry run pytest tests/
