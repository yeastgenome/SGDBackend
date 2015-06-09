import json
import uuid
import os
import traceback

from pyramid.response import Response

from sqlalchemy import func
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from jsonschema import Draft4Validator

from src.sgd.backend.nex import set_up_logging
from src.sgd.model import curate
from src.sgd.model.curate import ToJsonMixin
from src.sgd.model.curate.schema_utils import load_schema

__author__ = 'kpaskov'

DBSession = scoped_session(sessionmaker(autocommit=False))
query_limit = 25000

class CurateBackend():
    def __init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory):

        class Base(object):
            __table_args__ = {'schema': schema, 'extend_existing':True}

        curate.Base = declarative_base(cls=Base)
        engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), pool_recycle=3600)

        DBSession.configure(bind=engine, autocommit=False)
        curate.Base.metadata.bind = engine

        #Load classes
        self.classes = dict()
        self.schemas = dict()
        pathname = os.path.dirname(curate.__file__) + '/'
        for file in os.listdir(pathname):
            if file.endswith('.json'):
                module = os.path.basename(file)[:-5]
                self.classes[module] = curate.get_class_from_string(module + '.' + module.title().replace('_', ''))
                self.schemas[module] = load_schema(module + '.json')

        self.log = set_up_logging(log_directory, 'curate')

    def response_wrapper(self, method_name, request):
        request_id = str(uuid.uuid4())
        callback = None if 'callback' not in request.GET else request.GET['callback']
        self.log.info(request_id + ' ' + method_name + ('' if 'identifier' not in request.matchdict else ' ' + request.matchdict['identifier']))
        def f(data):
            self.log.info(request_id + ' end')
            if callback is not None:
                return Response(body="%s(%s)" % (callback, json.dumps(data)), content_type='application/json')
            else:
                return Response(body=json.dumps(data), content_type='application/json')
        return f

    def all_classes(self):
        return sorted(self.schemas.keys())

    def schema(self, class_type):
        schema = load_schema
        return None if class_type not in self.schemas else self.schemas[class_type]

    def get_object(self, class_name, identifier, filter_options):
        '''
        Get an object of a particular type with the given identifier.
        '''
        obj = None
        try:
            #Find object
            obj = self.find_object(class_name, identifier)

            size = 'large'
            if 'size' in filter_options:
                size = filter_options['size']

            return None if obj is None else obj.to_json(size=size)
        except Exception as e:
            print traceback.format_exc()
            return {'status': 'Error',
                    'message': e.message,
                    'traceback': traceback.format_exc(),
                    'json': None if obj is None else str(obj),
                    'id': None
            }

    def get_all_objects(self, class_name, filter_options):
        '''
        Get all objects of a particular type, with limit, offset, and size. Size refers to the amount of information
        returned for each object.
        '''
        try:
            #Get class
            if class_name in self.classes:
                cls = self.classes[class_name]
            else:
                return None

            query = DBSession.query(cls)

            limit = None
            offset = None
            size = 'small'

            for key, value in filter_options.items():
                if key == 'limit':
                    limit = value
                elif key == 'offset':
                    offset = value
                elif key == 'size':
                    size = value
                elif key in cls.__filter_values__:
                    query = query.filter(getattr(cls, key) == value)

            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)

            return [obj.to_json(size) for obj in query.all()]
        except Exception as e:
            print traceback.format_exc()
            return {'status': 'Error',
                    'message': e.message,
                    'traceback': traceback.format_exc(),
                    'json': None,
                    'id': None
            }
        finally:
            DBSession.remove()

    def update_object(self, class_name, identifier, new_json_obj):
        '''
        Updates a single object of a particular class.
        '''

        try:
            if class_name in self.schemas:
                schema = self.schemas[class_name]
            else:
                raise Exception('Schema not found: ' + class_name)

            #Validate json
            Draft4Validator(schema).validate(new_json_obj)

            #Get class
            cls = self._get_class_from_class_name(class_name)
            if cls is None:
                raise Exception('Class: ' + class_name + ' not found.')

            #Find object by id
            new_obj = DBSession.query(cls).filter_by(id=identifier).first()
            if new_obj is None:
                raise Exception(class_name + ' with uuid ' + identifier + ' does not exist.')

            #Create object using json
            new_obj_by_key, new_obj_by_key_status = cls.create_or_find(new_json_obj, DBSession)

            if new_obj_by_key.id != new_obj.id:
                raise Exception('Your edits cause this ' + class_name + ' to collide with <a href="/' + class_name.lower() + "/" + str(new_obj_by_key.id) + '/edit"> this one</a>.')

            updated, warnings = new_obj.update(new_json_obj, DBSession)

            if updated:
                response = {'status': 'Updated',
                            'message': None,
                            'json': str(ToJsonMixin.__to_large_json__(new_obj)),
                            'id': new_obj.id,
                            'warnings': warnings}
                DBSession.commit()
                return response
            else:
                return {'status': 'No Change',
                        'message': None,
                        'json': str(ToJsonMixin.__to_large_json__(new_obj)),
                        'id': new_obj.id,
                        'warnings': warnings}

        except Exception as e:
            print traceback.format_exc()
            return {'status': 'Error',
                    'message': e.message,
                    'traceback': traceback.format_exc(),
                    'json': str(new_json_obj),
                    'id': None
            }
        finally:
            DBSession.remove()

    def add_object(self, class_name, new_json_obj, update_ok=False):
        '''
        Can add a single object or a list of objects of a particular class. If update_ok is set to true, then
        if the object is already in the database, this method updates the object with any new information. If
        update_ok is set to false, thn an exception is raised if the object is already in the database.
        '''
        if isinstance(new_json_obj, list):
            return [self.add_object(class_name, x, update_ok=update_ok) for x in new_json_obj]
        else:
            try:
                #Validate json
                if class_name in self.schemas:
                    schema = self.schemas[class_name]
                    Draft4Validator(schema).validate(new_json_obj)
                else:
                    raise Exception('Schema not found: ' + class_name)

                #Get class
                cls = self._get_class_from_class_name(class_name)
                if cls is None:
                    raise Exception('Class not found: ' + class_name)

                #Get object if one already exists
                new_obj, status = cls.create_or_find(new_json_obj, DBSession)

                if status == 'Found':
                    if update_ok:
                        return self.update_object(class_name, new_obj.id, new_json_obj)
                    else:
                        raise Exception('A ' + class_name + ' like this already exists <a href="/' + class_name.lower() + "/" + str(new_obj.id) + '/edit"> here</a>.')
                elif status == 'Created':
                    DBSession.add(new_obj)
                    response = {'status': 'Added',
                                'message': None,
                                'json': str(ToJsonMixin.__to_large_json__(new_obj)),
                                'id': new_obj.id,
                                'warnings': []}
                    DBSession.commit()
                    return response
                else:
                    raise Exception('Neither found nor created.')

            except Exception as e:
                print traceback.format_exc()
                return {'status': 'Error',
                        'message': e.message,
                        'traceback': traceback.format_exc(),
                        'json': str(new_json_obj),
                        'id': None,
                        'warnings': []
                }
            finally:
                DBSession.remove()

    def delete_object(self, class_name, identifier):
        try:
            #Get class
            cls = self._get_class_from_class_name(class_name)
            if cls is None:
                raise Exception('Class: ' + class_name + ' not found.')

            #Find object by id
            new_obj = DBSession.query(cls).filter_by(id=identifier).first()
            if new_obj is None:
                raise Exception(class_name + ' with uuid ' + identifier + ' does not exist.')

            DBSession.delete(new_obj)
            response = {'status': 'Deleted',
                        'message': None,
                        'json': None,
                        'id': new_obj.id,
                        'warnings': []}
            DBSession.commit()
            return response
        except Exception as e:
            print traceback.format_exc()
            return {'status': 'Error',
                    'message': e.message,
                    'traceback': traceback.format_exc(),
                    'json': None,
                    'id': None,
                    'warnings': []
            }
        finally:
            DBSession.remove()

    def find_object(self, class_name, identifier):
        #Get class
        cls = self._get_class_from_class_name(class_name)
        if cls is None:
            raise Exception('Class: ' + class_name + ' not found.')

        #Look for object
        query = DBSession.query(cls)
        for id_value in cls.__id_values__:
            obj = query.filter(func.lower(getattr(cls, id_value)) == identifier.lower()).first()
            if obj is not None:
                return obj

        return None

    def _get_class_from_class_name(self, class_name):
        if class_name in self.classes:
            return self.classes[class_name]
        else:
            return None

