__author__ = 'kpaskov'

import json
import uuid
import os
import traceback
import transaction

from pyramid.response import Response

from sqlalchemy import func
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from jsonschema import Draft4Validator

from src.sgd.backend.nex import set_up_logging
from src.sgd.model import curate
from src.sgd.model.curate.schema_utils import load_schema

__author__ = 'kpaskov'

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
query_limit = 25000

class CurateBackend():
    def __init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory):

        class Base(object):
            __table_args__ = {'schema': schema, 'extend_existing':True}

        curate.Base = declarative_base(cls=Base)
        engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), pool_recycle=3600)

        DBSession.configure(bind=engine)
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
                return Response(body="%s(%s)" % (callback, data), content_type='application/json')
            else:
                return Response(body=data, content_type='application/json')
        return f

    def all_classes(self):
        return json.dumps(sorted(self.schemas.keys()))

    def schema(self, class_type):
        schema = load_schema
        return None if class_type not in self.schemas else json.dumps(self.schemas[class_type])

    def get_object(self, class_name, identifier):
        #Get class
        cls = self._get_class_from_class_name(class_name)
        if cls is None:
            return None

        #Get object
        obj = self._get_object_from_identifier(cls, identifier)

        return None if obj is None else json.dumps(obj.to_json())

    def _get_class_from_class_name(self, class_name):
        if class_name in self.classes:
            return self.classes[class_name]
        else:
            return None

    def _get_object_from_identifier(self, cls, identifier):
        int_identifier = None
        try:
            int_identifier = int(identifier)
        except:
            pass

        obj = None
        query = DBSession.query(cls)
        for id_value in cls.__id_values__:
            if id_value == 'id':
                if int_identifier is not None:
                    obj = query.filter(getattr(cls, id_value) == int_identifier).first()
            else:
                obj = query.filter(func.lower(getattr(cls, id_value)) == identifier.lower()).first()
            if obj is not None:
                return obj
        return None

    def _get_object_from_json(self, cls, obj_json):
        obj, status = cls.create_or_find(obj_json, DBSession)
        if status == 'Found':
            return obj
        else:
            print obj_json
            return None

    def get_all_objects(self, class_name, limit, offset, size):
        #Get class
        if class_name in self.classes:
            cls = self.classes[class_name]
        else:
            return None

        query = DBSession.query(cls).limit(limit).offset(offset)

        if size == 'mini':
            json_extract_f = lambda obj: (obj.id, obj.display_name, obj.format_name)
        elif size == 'small':
            json_extract_f = lambda obj: obj.to_min_json()
        elif size == 'medium':
            json_extract_f = lambda obj: obj.to_semi_json()
        elif size == 'large':
            json_extract_f = lambda obj: obj.to_json()

        return json.dumps([json_extract_f(obj) for obj in query.all()])

    def update_object(self, class_name, identifier, new_json_obj):
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
                raise Exception('Class not found: ' + class_name)

            try:
                new_obj = DBSession.query(cls).filter_by(id=int(identifier)).first()
            except:
                raise Exception(class_name + ' ' + identifier + ' could not be found.')

            new_obj_by_key, new_obj_by_key_status = cls.create_or_find(new_json_obj, DBSession)

            if new_obj_by_key.id != new_obj.id:
                raise Exception('Your edits cause this ' + class_name + ' to collide with <a href="/' + class_name.lower() + "/" + str(new_obj_by_key.id) + '/edit"> this one</a>.')

            updated, warnings = new_obj.update(new_json_obj, DBSession)

            if updated:
                id = new_obj.id
                transaction.commit()
                new_obj = DBSession.query(cls).filter_by(id=id).first()
                return json.dumps({'status': 'Updated',
                                   'message': None,
                                   'json': new_obj.to_json(),
                                   'id': new_obj.id,
                                   'warnings': warnings})
            else:
                return json.dumps({'status': 'No Change',
                                   'message': None,
                                   'json': new_obj.to_json(),
                                   'id': new_obj.id,
                                   'warnings': warnings})

        except Exception as e:
            print traceback.format_exc()
            return json.dumps({'status': 'Error',
                            'message': e.message,
                            'traceback': traceback.format_exc(),
                            'json': str(new_json_obj),
                            'id': None
                            })

    def add_object(self, class_name, new_json_obj, update_ok=False):
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
                if hasattr(new_obj, 'format_name'):
                    format_name = new_obj.format_name
                    DBSession.add(new_obj)
                    transaction.commit()
                    newly_created_obj = self._get_object_from_identifier(cls, format_name)
                    return json.dumps({'status': 'Added',
                            'message': None,
                            'json': newly_created_obj.to_json(),
                            'id': newly_created_obj.id,
                            'warnings': []})
                else:
                    DBSession.add(new_obj)
                    transaction.commit()
                    newly_created_obj = self._get_object_from_json(cls, new_json_obj)
                    return json.dumps({'status': 'Added',
                            'message': None,
                            'json': newly_created_obj.to_json(),
                            'id': newly_created_obj.id,
                            'warnings': []})
            else:
                raise Exception('Neither found nor created.')

        except Exception as e:
            print traceback.format_exc()
            return json.dumps({'status': 'Error',
                            'message': e.message,
                            'traceback': traceback.format_exc(),
                            'json': str(new_json_obj),
                            'id': None,
                            'warnings': []
                            })
