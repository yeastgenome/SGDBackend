__author__ = 'kpaskov'

import json
from pkg_resources import resource_stream

def local_handler(filename):
    schema = json.load(resource_stream(__name__, 'nex/' + filename))
    return schema

def resolve_references(schema):
    for prop, value in schema['properties'].iteritems():
        if isinstance(value, dict):
            if '$ref' in value:
                subschema = local_handler(value['$ref'])
                schema['properties'][prop] = subschema
            elif value["type"] == "object":
                schema['properties'][prop] = resolve_references(schema['properties'][prop])
            elif "items" in value:
                schema["properties"][prop]["items"] = resolve_references(schema["properties"][prop]["items"])

    return schema

def load_schema(filename):
    schema = local_handler(filename)
    schema = resolve_references(schema)
    return schema