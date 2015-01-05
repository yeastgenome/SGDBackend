import json

__author__ = 'kpaskov'

'''
All classes in this model inherit from the base class provided by the following variable. In order to use this model,
you must initialize the Base variable before importing any class in this model. For example..

    class Base(object):
        __table_args__ = {'schema': schema, 'extend_existing':True}

    nex.Base = declarative_base(cls=Base)
    engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), pool_recycle=3600)
'''

Base = None

class JsonMixins(object):
    def update(self, obj_json):
        self.json = json.dumps(obj_json)
        return True

    def to_json(self):
        return json.loads(self.json)

    def __init__(self, obj_json):
        self.id = obj_json['id']
        self.json = json.dumps(obj_json)


