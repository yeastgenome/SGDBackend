import json

__author__ = 'kpaskov'

Base = None

class JsonMixins(object):
    def update(self, obj_json):
        new_json = json.dumps(obj_json)
        if new_json == self.json:
            return False
        else:
            self.json = new_json
            return True

    def to_json(self):
        return json.loads(self.json)

    def __init__(self, obj_json):
        self.id = obj_json['id']
        self.json = json.dumps(obj_json)