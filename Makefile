all: cov

cov:
	hatch env run cov

clean:
	hatch env prune
	hatch clean