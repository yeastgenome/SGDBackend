__author__ = 'kpaskov'

from datetime import datetime
import json
import logging
import uuid
import glob
import os
import traceback
from math import ceil

from pyramid.response import Response
from sqlalchemy import func, distinct
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from src.sgd.backend.nex import SGDBackend
from src.sgd.model import nex
import random
from sqlalchemy.orm import joinedload
from contextlib import contextmanager
import transaction

__author__ = 'kpaskov'

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
query_limit = 25000

class CurateBackend(SGDBackend):
    def __init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory):
        SGDBackend.__init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory)

    def foreign_key_retriever(self, obj_json, cls, allow_updates):
        if obj_json is None:
            return None

        if isinstance(cls, str):
            mod = __import__('src.sgd.model.nex.' + cls.split('.')[0], fromlist=[cls.split('.')[1]])
            if hasattr(mod, cls.split('.')[1]):
                cls = getattr(mod, cls.split('.')[1])
            else:
                raise Exception('Class not found: ' + cls)

        newly_created_obj = cls(obj_json, self.foreign_key_retriever)

        current_obj =

        if current_obj is None:
            return newly_created_obj
        else:
            if allow_updates:
                current_obj.update(obj_json, self.foreign_key_retriever, make_changes=True)
                return current_obj
            else:
                was_different = current_obj.update(obj_json, self.foreign_key_retriever, make_changes=False)
                if was_different:
                    raise Exception('Cannot make changes to ' + cls.__name__ + ' from this interface. Please update from here: <a href="/' + cls.__name__.lower() + '/' + current_obj.id + '/edit">' + current_obj.display_name + '</a>')


    def update_object(self, class_name, identifier, new_json_obj, allow_update_for_add=False):
        try:
            #Validate json
            if class_name in self.schemas:
                validate(new_json_obj, self.schemas[class_name])
            else:
                raise Exception('Schema not found: ' + class_name)

            #Get class
            cls = self._get_class_from_class_name(class_name)
            if cls is None:
                raise Exception('Class not found: ' + class_name)

            #Convert foreign keys
            for fk in cls.__eq_fks__:
                if fk in new_json_obj:
                    fk_cls = self._get_class_from_class_name(fk)
                    if fk_cls is None:
                        raise Exception('Could not find class ' + fk_cls)

                    fk_obj = self._get_object_from_identifier(fk_cls, new_json_obj[fk]['format_name'])
                    if fk_obj is None:
                        raise Exception(fk.title() + ' "' + new_json_obj[fk]['format_name'] + '" does not exist.')
                    new_json_obj[fk]['id'] = fk_obj.id

            newly_created_obj = cls(new_json_obj, self.foreign_key_retriever)
            format_name = newly_created_obj.format_name

            #Get object if one already exists
            if identifier is not None and identifier != 'None':
                current_obj = self._get_object_from_identifier(cls, identifier)
            else:
                #If identifier is None we're doing an add, but if an object already exists send message
                #that we should be doing an update
                current_obj = self._get_object_from_identifier(cls, format_name)
                if current_obj is not None and not allow_update_for_add:
                    edit_url = '/' + class_name.lower() + '/' + str(current_obj.id) + '/edit'
                    return json.dumps({'status': 'No Change',
                                'message': 'This ' + class_name + ' already exists. You can update it <a href="' + edit_url + '">here</a>.',
                                'json': new_json_obj,
                                'id': None})

            if current_obj is None:
                #Make new object
                DBSession.add(newly_created_obj)
                transaction.commit()

                #Get new ID
                newly_created_obj = self._get_object_from_identifier(cls, format_name)
                return json.dumps({'status': 'Added',
                        'message': None,
                        'json': newly_created_obj.to_json(),
                        'id': newly_created_obj.id})
            else:
                #IDs much match - you can't edit an ID
                if 'id' in new_json_obj and new_json_obj['id'] is not None and new_json_obj['id'] != current_obj.id:
                    raise Exception('ID field cannot be edited.')

                obj_json = current_obj.to_json()
                updated = current_obj.update(new_json_obj)

                if updated:
                    obj_json = current_obj.to_json()
                    transaction.commit()
                    return json.dumps({'status': 'Updated',
                            'message': None,
                            'json': obj_json,
                            'id': obj_json['id']})
                else:
                    return json.dumps({'status': 'No Change',
                            'message': None,
                            'json': obj_json,
                            'id': obj_json['id']})
        except Exception as e:
            print traceback.format_exc()
            return json.dumps({'status': 'Error',
                            'message': e.message,
                            'traceback': traceback.format_exc(),
                            'json': str(new_json_obj),
                            'id': None
                            })
