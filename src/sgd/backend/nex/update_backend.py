__author__ = 'kpaskov'

import json
import traceback

from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from jsonschema import Draft4Validator

from src.sgd.backend.nex import SGDBackend
import transaction

__author__ = 'kpaskov'

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
query_limit = 25000

class UpdateBackend(SGDBackend):
    def __init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory):
        SGDBackend.__init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory)
        
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
                if class_name == 'sgdid':
                    new_obj = DBSession.query(cls).filter_by(id=identifier).first()
                else:
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
