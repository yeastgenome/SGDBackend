import json

__author__ = 'kpaskov'

Base = None

class JsonMixins(object):
    def update(self, obj_json):
        if self.to_json() != obj_json:
            self.json = json.dumps(obj_json)
            return True
        return False

    def to_json(self):
        return json.loads(self.json)

    def __init__(self, obj_json):
        self.id = obj_json['id']
        self.json = json.dumps(obj_json)