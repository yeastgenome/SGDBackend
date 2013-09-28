#SGD Website Project

This project is a backend webaplication used for the SGD Nextgen Redesign. It returns data in JSON format at a 
variety of URLs.

There are seven packages in this project...

1. **model_new_schema**

 This is a well-developed SQLAlchemy back-end based off of the new SGD schema available on cherry-vm08, as SPROUT.

2. **model_old_schema**

 This is a well-developed SQLAlchemy back-end based off of the old SGD schema available on fasolt/pastry, as BUD. 

3. **query**

 This is a very simple package with all queries used throughout the front-end. I've put them together to make it 
easier to work on query optimization.

4. **schema_conversion**

 This package pulls data from the old schema and inserts it into the new_schema using the two SQLAlchemy backends in 
model_new_schema and model_old_schema. All of the convert_X scripts work by reading in data from the BUD schema,
transforming the data into SPROUT objects, then comparing these objects to the objects already in the SPROUT database.
If a transformed object matches a stored object (matching done using unique keys), then the stored object is updated
to match the transformed object. If a transformed object does not match any of the stored objects, then it is inserted
into the database.

5. **sgdbackend**

 This package uses the Pyramid webframework to serve JSON.
 
6. **loading_scripts**

 This package will eventually be used for scripts that load data from other sources (flat files for example) into
 the SPROUT database.
