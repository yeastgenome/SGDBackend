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

    @classmethod
    def from_json(cls, obj_json):
        obj = cls(obj_json['id'], json.dumps(obj_json))
        return obj