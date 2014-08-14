__author__ = 'kpaskov'

import json
import datetime

def create_format_name(display_name):
    format_name = display_name.replace(' ', '_')
    format_name = format_name.replace('/', '-')
    return format_name

Base = None

class UpdateByJsonMixin(object):
    def update(self, json_obj):
        anything_changed = False
        for key in self.__eq_values__:
            current_value = getattr(self, key)
            new_value = None if key not in json_obj else json_obj[key]

            if isinstance(new_value, str) and (key == 'seq_version' or key == 'coord_version' or key == 'date_of_run'):
                new_value = None if new_value is None else datetime.datetime.strptime(new_value, "%Y-%m-%d")

            if key == 'id' or key == 'date_created' or key == 'created_by' or key == 'json':
                pass
            elif new_value != current_value:
                setattr(self, key, new_value)
                anything_changed = True

        for key in self.__eq_fks__:
            current_value = getattr(self, key + '_id')
            new_value = None if (key not in json_obj or json_obj[key] is None) else json_obj[key]['id']

            if new_value != current_value:
                setattr(self, key + '_id', new_value)
                anything_changed = True

        return anything_changed

    def compare(self, json_obj):
        anything_changed = False
        for key in self.__eq_values__:
            current_value = getattr(self, key)
            new_value = json_obj[key]

            if isinstance(new_value, str) and (key == 'seq_version' or key == 'coord_version' or key == 'date_of_run'):
                new_value = None if new_value is None else datetime.datetime.strptime(new_value, "%Y-%m-%d")

            if key == 'id' or key == 'date_created' or key == 'created_by' or key == 'json':
                pass
            elif new_value != current_value:
                anything_changed = True

        for key in self.__eq_fks__:
            current_value = getattr(self, key + '_id')
            new_value = None if (key not in json_obj or json_obj[key] is None) else json_obj[key]['id']

            if new_value != current_value:
                anything_changed = True

        return anything_changed

    def to_min_json(self, include_description=False):
        obj_json = {
            'id': self.id,
            'format_name': self.format_name,
            'display_name': self.display_name,
            'link': self.link,
            }
        if include_description and hasattr(self, 'description'):
            obj_json['description'] = self.description
        return obj_json

    def to_json(self):
        obj_json = {}
        for key in self.__eq_values__:
            if key == 'json':
                pass
            else:
                value = getattr(self, key)
                if value is not None and isinstance(value, datetime.date):
                    obj_json[key] = str(value)
                else:
                    obj_json[key] = value

        for key in self.__eq_fks__:
            fk_obj = getattr(self, key)
            fk_id = getattr(self, key + '_id')
            if fk_obj is not None:
                obj_json[key] = fk_obj.to_min_json()
            elif fk_id is not None:
                obj_json[key] = {'id': fk_id}
            else:
                obj_json[key] = None
        return obj_json

    def __init__(self, obj_json):
        for key in self.__eq_values__:
            if key == 'class_type' and obj_json.get(key) is None:
                self.class_type = self.__mapper_args__['polymorphic_identity']
            else:
                setattr(self, key, obj_json.get(key))

        for key in self.__eq_fks__:
            fk_obj = obj_json.get(key)
            fk_id = obj_json.get(key + '_id')
            if fk_obj is not None:
                setattr(self, key + '_id', fk_obj.id)
            elif fk_id is not None:
                setattr(self, key + '_id', fk_id)
            else:
                setattr(self, key + '_id', None)
