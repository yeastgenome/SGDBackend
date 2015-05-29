# Description of SGDBackend

This document describes the code organization and general purpose of code within the SGDBackend Repo.  It is relevant after the creation of the nex2 branch, which bridges 4 databases:  BUD (old SGD oracle DB), NEX (current production DB), CURATE (new dev DB, with changes for curation interfaces and collection webservices) and PERF (performance optimization indexed database).

## Top Levels
* /doc this directory, holds .md files
* /go_enrichment - this is a proxy to go enrichment server on batter
* /model - SQLAlchemy models (and JSON Schemas for CURATE) for the 4 databases
* /convert - Scripts to load databases from BUD or flat files (see: http://cherrylab.stanford.edu/wiki/index.php/SGD_NextGen_flatfiles)
* /backend - code for the API for NEX, PERF and CURATE, along with a test database (fixture)

## Sections

### Model

__init__.py contains EqualityByIdMixin class.  Each subdirectory contains a set of Python modules in SQLAlchemy that represent a specific database schema.  Generally there will be >1 Database table per python module.  Specific mixin classes or utility methods are in the __init__.py file for the specific package database.

#### /bud

this is just a straight mapping of the BUD schema.  No SQL files are provided here.

#### /curate

In addition to SQL files describing the tables and triggers, this directory has the python mappings for the CURATE database, plus JSON schema files used for form validation.  The __init__.py file contains a list of locus types, and the following Mixin Classes:
* UpdateWithJsonMixin
* ToJsonMixin

#### /nex
In addition to SQL files describing the tables and triggers, this directory has the python mappings for the NEX database.  The __init__.py file contains a list of locus types and a Mixin class UpdateByJsonMixin

#### /perf
In addition to SQL files describing the tables and triggers, this directory has single Mixin class, JsonMixins in the __init__.py file.

### Convert

The convert package consists of some database connection code in __init__.py, a set of scripts for converting from one DB to another (convert_*.py), and some modules for facilitating this.
* transformers.py - deprecated
* /from_bud - code to load from the BUD database and some flat files into NEX.
* /to_curate - code to load from BUD database and some flat files into CURATE

### Backend

Herein is the code to actually provide the webservices from specific databases (not BUD).   __init__.py contains some generic pyramid routes to collections and single objects, along with some connection and utility functions.   Each package (curate, fixture, nex, perf) has code specific to run that database's API.

* backend_interface.py - deprecated
* /nex - in addition to boilerplate code to return JSON objects from the model, there are more complicated views used to generate JSON objects for specific pages.



