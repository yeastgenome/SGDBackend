README for SGD Website Project.

There are six packages in this project...

model_new_schema
This is a fairly well-developed SQLAlchemy back-end based off of the new SGD schema available on cherry-vm08, as SPROUT.

model_old_schema
This is a well-developed SQLAlchemy back-end based off of the old SGD schema available on fasolt/pastry, as BUD. 

query
This is a very simple package with common queries used throughout the front-end. I've put them together to make it 
easier to work on query optimization.

schema_conversion
This package pulls data from the old schema and inserts it into the new_schema using the two SQLAlchemy backends in 
model_new_schema and model_old_schema. This package needs to be cleaned up quite a bit. Right now, old_to_new_sequence 
and old_to_new_bioentity are the two best examples of what this package will eventually look like.

sgd2
This package contains the new SGD2.0 web application. The application is built using the Pyramid web framework.

utils
This is a catch all package for any useful methods that may be useful throughout the application.
