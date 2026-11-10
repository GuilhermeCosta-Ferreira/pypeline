.PHONY: formatt lint test diagram status dev

formatt:
	-poetry run docformatter src/pypeline
	-poetry run docformatter tests
	poetry run black src/pypeline
	poetry run black tests

lint:
	-poetry run pylint src/pypeline
	-poetry run pylint tests

test:
	-poetry run pytest

diagram:
	poetry run classpy sync
	plantuml -tpng docs/class.puml

status:
	@echo "\n== Implementation ==" && poetry run classpy status || true
	@echo "\n== Tests ==" && poetry run pytest -q --cov=pypeline --cov-report=term-missing:skip-covered || true
	@echo "\n== Doc coverage ==" && poetry run interrogate src/pypeline || true
	@echo "\n== Docstrings ==" && poetry run pydoclint --quiet src/pypeline || true
	@echo "\n== Types ==" && poetry run pyright src || true
	@echo "\n== Lint ==" && poetry run pylint src/pypeline --reports=n || true

dev:
	$(MAKE) diagram formatt lint test
