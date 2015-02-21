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

    def update_object(self, class_name, new_json_obj):
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

            #Get object if one already exists
            new_obj, status = cls.create_or_find(new_json_obj, DBSession)
            if status == 'Created':
                DBSession.add(new_obj)
                transaction.commit()
                newly_created_obj = self._get_object_from_identifier(cls, new_obj.format_name)
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

        except Exception as e:
            print traceback.format_exc()
            return json.dumps({'status': 'Error',
                            'message': e.message,
                            'traceback': traceback.format_exc(),
                            'json': str(new_json_obj),
                            'id': None
                            })
