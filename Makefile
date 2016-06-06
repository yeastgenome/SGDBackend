SGD_NEX = sgdbackend_development.ini
SGD_PERF = perfbackend_development.ini
BUILDOUT_DEPLOY = buildout_deploy.cfg
BOOTSTRAP = bootstrap.py

dev-deploy:
	. dev_deploy_variables.sh && cap dev deploy

prod-deploy:
	. prod_deploy_variables.sh && cap prod deploy

build: bootstrap
	./bin/buildout

build-deploy: bootstrap
	./bin/buildout -c $(BUILDOUT_DEPLOY)

bootstrap:
	python $(BOOTSTRAP)

run-sgd:
	bin/pserve $(SGD_NEX) --reload

run-perf:
	bin/pserve $(SGD_PERF) --reload

test-sgd:
	bin/test src/sgd/backend/tests --model nex

test-perf:
	bin/test src/sgd/backend/tests --model perf

