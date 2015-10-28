SGD_NEX = sgdbackend_development.ini
SGD_PERF = perfbackend_development.ini
BUILDOUT_DEPLOY = buildout_deploy.cfg
BOOTSTRAP = bootstrap.py

build: bootstrap
	./bin/buildout

buid-deploy: bootstrap
	./bin/buildout -c $(BUILDOUT_DEPLOY)

bootstrap:
	python $(BOOTSTRAP)

run-sgd:
	bin/pserve $(SGD_NEX)

run-perf:
	bin/pserve $(SGD_PERF)

test-sgd:
	bin/test src/sgd/backend/tests --model nex

test-perf:
	bin/test src/sgd/backend/tests --model perf

