__author__ = 'kpaskov'

import codecs
import collections
import json
from pkg_resources import resource_stream
from jsonschema import RefResolver, Draft4Validator

def local_handler(filename):
    schema = json.load(resource_stream(__name__, 'nex/' + filename))
    return schema

def resolve_references(schema):
    for prop, value in schema['properties'].iteritems():
        if isinstance(value, dict) and '$ref' in value:
            subschema = local_handler(value['$ref'])
            schema['properties'][prop] = subschema

    return schema

def load_schema(filename):
    schema = local_handler(filename)
    schema = resolve_references(schema)
    return schema