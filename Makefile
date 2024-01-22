all: cov

test:
	hatch env run test

cov:
	hatch env run cov

clean:
	hatch env prune
	hatch clean
