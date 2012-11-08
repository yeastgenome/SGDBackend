README for SGD Website Project.

There are four packages in this project...

connection_test
These are a series of simple test cases used to debug the lit-review timeout error. Because the time-out problem would only occur
after an idle time of about 3 hours, these are not true test cases. Instead, they are basic SQLALchemy set-ups, designed to be
instantiated, queried, left idle for 3 hours, and queried again.

model_new_schema
This is an outline of the new schema for the SGD project. I've been implementing some of the ideas I presented in Group Meeting.
Right now, I'm working off a test schema on fasolt under my KPASKOV account. This is very preliminary right now, it's main purpose is
to allow me to get familiar with SQLAlchemy, particularly its inheritance patterns.

model_old_schema
This is an ORM sitting on top of the old SGD schema. It's incomplete and is being developed to be used by the lit-review project.
It covers the Reference area of the database fairly well, with a few other tables included such as seq and feature.

lit-review
This is the lit-review project. RIght now I'm adapting Shuai's code to use the model_old_schema classes I've written completely
in SQLAlchemy.