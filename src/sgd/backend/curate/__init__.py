__author__ = 'kpaskov'

from datetime import datetime
import json
import logging
import uuid
import glob
import os
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

        self.schemas = dict()
        for schema in glob.glob("src/sgd/model/nex/*.json"):
            self.schemas[os.path.basename(schema)[:-5]] = json.load(open(schema, 'r'))

    def update_object(self, class_name, json):

        #Validate json
        if class_name in self.schemas:
            try:
                validate(json, self.schemas[class_name])
            except ValidationError as e:
                return {'status': 'Error',
                        'message': e.message,
                        'json': json,
                        'id': None}
        else:
            return None

        #Get class
        if class_name in self.classes:
            cls = self.classes[class_name]
        else:
            return None

        #Make new object
        newly_created_obj = cls(json)

        #Get object if one already exists
        current_obj = DBSession.query(cls).filter_by(format_name=newly_created_obj.format_name).first()

        if current_obj is None:
            DBSession.add(newly_created_obj)
            transaction.commit()
            return {'status': 'Added',
                    'message': None,
                    'json': newly_created_obj.to_json(),
                    'id': newly_created_obj.id}

        elif newly_created_obj.compare(json):
            current_obj.update(json)
            transaction.commit()
            return {'status': 'Updated',
                    'message': None,
                    'json': current_obj.to_json(),
                    'id': current_obj.id}

        else:
            return {'status': 'No Change',
                    'message': None,
                    'json': current_obj.to_json(),
                    'id': current_obj.id}

        return None if obj is None else json.dumps(obj.to_json())
