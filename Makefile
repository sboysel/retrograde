all: cov

build:
	hatch build

test:
	hatch env run test

cov:
	hatch env run cov

lint:
	hatch lint

clean:
	hatch env prune
	hatch clean
	rm -rf tests/__pycache__
	rm -rf src/__pycache__
	rm -rf .pytest_cache
	rm -rf dist/