__author__ = 'kpaskov'

'''
This package contains a partial bud schema model implemented as a group of SQLAlchemy classes. This model has been
built up on an as-needed basis, so it is not guaranteed to be complete. It is used by the convert package to transfer
data from the bud to the nex schema. Since this package will be retired after all data is transfered into nex,
it is minimally documented.
'''

'''
All classes in this model inherit from the base class provided by the following variable. In order to use this model,
you must initialize the Base variable before importing any class in this model. For example

    class Base(object):
        __table_args__ = {'schema': schema, 'extend_existing':True}

    nex.Base = declarative_base(cls=Base)
    engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), pool_recycle=3600)

    from feature import Feature
    etc.
'''

Base = None
