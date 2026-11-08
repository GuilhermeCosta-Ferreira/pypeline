.PHONY: formatt, lint, test, diagram dev

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

    dev:
	    make diagram formatt lint test
