#SGD Website Project

This project is a backend webaplication used for the SGD Nextgen Redesign. It returns data in JSON format at a 
variety of URLs.

To install do:
    ORACLE_HOME="__PATH_TO_ORACLE_INSTANT_CLIENT__" LD_LIBRARY_PATH="__PATH_TO_ORACLE_INSTANT_CLIENT__" python bootstrap.py
    bin/buildout

To run nex backend do:
    bin/pserve sgdbackend_development.ini

To run perf backend do:
    bin/pserve perfbackend_development.ini

To run nex backend tests do:
    bin/test src/sgd/backend/tests --model nex

To run perf backend tests do:
    bin/test src/sgd/backend/tests --model perf
