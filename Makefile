# Prérequis : uv
UV ?= uv

setup:
	$(UV) sync --locked --all-extras

test:             ## 9 tests fermés, sans réseau
	$(UV) run pytest

lint:
	$(UV) run ruff check src tests

all:              ## fetch + lab (réseau requis, ~5 min)
	$(UV) run infc fetch
	$(UV) run infc lab
