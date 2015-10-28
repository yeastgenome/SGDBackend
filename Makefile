build:
	python bootstrap.py
	./bin/buildout

run-sgd:
	bin/pserve sgdbackend_development.ini

run-perf:
	bin/pserve perfbackend_development.ini

test-sgd:
	bin/test src/sgd/backend/tests --model nex

test-perf:
	bin/test src/sgd/backend/tests --model perf

