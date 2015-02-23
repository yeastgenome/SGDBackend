__author__ = 'kpaskov'

from datetime import datetime
import json
import logging
import uuid
import glob
import os
import traceback
import jsonschema
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

    def update_object(self, class_name, identifier, new_json_obj):
        try:
            #Validate json
            if class_name in self.schemas:
                schema = self.schemas[class_name]
                print jsonschema.RefResolver(self.resolver_path, schema)
                validate(schema, new_json_obj, resolver=jsonschema.RefResolver(self.resolver_path, schema))
            else:
                raise Exception('Schema not found: ' + class_name)

            #Get class
            cls = self._get_class_from_class_name(class_name)
            if cls is None:
                raise Exception('Class not found: ' + class_name)

            #Get object if one already exists
            new_obj = None
            if identifier is None or identifier == 'None':
                #We haven't been given an identifier so we need to create or find the object.
                new_obj, status = cls.create_or_find(new_json_obj, DBSession)
            else:
                #We have been given an identifier, so we need to make sure that we have somthing to update
                #and that we're not updating it to collide with another object
                try:
                    new_obj = DBSession.query(cls).filter_by(id=int(identifier)).first()
                    status = 'Found'
                except:
                    pass
                if new_obj is None:
                    raise Exception(class_name + ' ' + identifier + ' could not be found.')
                new_obj_by_key, new_obj_by_key_status = cls.create_or_find(new_json_obj, DBSession)

                if new_obj_by_key_status == 'Found' and new_obj_by_key.unique_key() != new_obj.unique_key():
                    raise Exception('Your edits cause this ' + class_name + ' to collide with <a href="/' + class_name.lower() + "/" + str(new_obj_by_key.id) + '/edit"> this one</a>.')

            if status == 'Created':
                format_name = new_obj.format_name
                DBSession.add(new_obj)
                transaction.commit()
                newly_created_obj = self._get_object_from_identifier(cls, format_name)
                return json.dumps({'status': 'Added',
                        'message': None,
                        'json': newly_created_obj.to_json(),
                        'id': newly_created_obj.id})
            elif status == 'Found':
                updated = new_obj.update(new_json_obj, DBSession)

                if updated:
                    id = new_obj.id
                    transaction.commit()
                    new_obj = DBSession.query(cls).filter_by(id=id).first()
                    return json.dumps({'status': 'Updated',
                            'message': None,
                            'json': new_obj.to_json(),
                            'id': new_obj.id})
                else:
                    return json.dumps({'status': 'No Change',
                            'message': None,
                            'json': new_obj.to_json(),
                            'id': new_obj.id})
            else:
                raise Exception('Neither found nor created.')

        except Exception as e:
            print traceback.format_exc()
            return json.dumps({'status': 'Error',
                            'message': e.message,
                            'traceback': traceback.format_exc(),
                            'json': str(new_json_obj),
                            'id': None
                            })
