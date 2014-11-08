__author__ = 'kpaskov'

def create_format_name(display_name):
    format_name = display_name.replace(' ', '_')
    format_name = format_name.replace('/', '-')
    return format_name

Base = None

class UpdateByJsonMixin():
    def update(self, json_obj):
        anything_changed = False
        for key in self.__keys__:
            current_value = getattr(self, key)
            new_value = None if key not in json_obj else json_obj[key]

            if isinstance(new_value, str) and (key == 'seq_version' or key == 'coord_version' or key == 'date_of_run' or key == 'expiration_date' or key == 'reservation_date'):
                new_value = None if new_value is None else datetime.datetime.strptime(new_value, "%Y-%m-%d")

            if key == 'id' or key == 'date_created' or key == 'created_by' or key == 'json':
                pass
            elif new_value != current_value:
                setattr(self, key, new_value)
                anything_changed = True

        for key in self.__fks__:
            current_value = getattr(self, key + '_id')
            new_value = None if (key not in json_obj or json_obj[key] is None) else json_obj[key]['id']

            if new_value != current_value:
                setattr(self, key + '_id', new_value)
                anything_changed = True

        return anything_changed

    def compare(self, json_obj):
        anything_changed = False
        for key in self.__keys__:
            current_value = getattr(self, key)
            new_value = json_obj[key]

            if isinstance(new_value, str) and (key == 'seq_version' or key == 'coord_version' or key == 'date_of_run' or key == 'expiration_date' or key == 'reservation_date'):
                new_value = None if new_value is None else datetime.datetime.strptime(new_value, "%Y-%m-%d")

            if key == 'id' or key == 'date_created' or key == 'created_by' or key == 'json':
                pass
            elif new_value != current_value:
                anything_changed = True

        for key in self.__fks__:
            current_value = getattr(self, key + '_id')
            new_value = None if (key not in json_obj or json_obj[key] is None) else json_obj[key]['id']

            if new_value != current_value:
                anything_changed = True

        return anything_changed

    def _get_json_from_values(self, keys):
        obj_json = {}
        for key in keys:
            if key == 'json':
                pass
            else:
                value = getattr(self, key)
                if value is not None and isinstance(value, datetime.date):
                    obj_json[key] = str(value)
                else:
                    obj_json[key] = value
        return obj_json

    def _get_json_from_fks(self, fks):
        obj_json = {}
        for key in fks:
            fk_obj = getattr(self, key)
            fk_id = getattr(self, key + '_id')
            if fk_obj is not None:
                obj_json[key] = fk_obj.to_min_json()
            elif fk_id is not None:
                obj_json[key] = {'id': fk_id}
            else:
                obj_json[key] = None
        return obj_json

    def _set_values_from_json(self, keys, obj_json):
        for key in keys:
            if key == 'class_type' and obj_json.get(key) is None:
                self.class_type = self.__mapper_args__['polymorphic_identity']
            else:
                setattr(self, key, obj_json.get(key))

    def _set_fks_from_json(self, fks, obj_json):
        for key in fks:
            fk_obj = obj_json.get(key)
            fk_id = obj_json.get(key + '_id')
            if fk_obj is not None:
                setattr(self, key + '_id', fk_obj.id)
            elif fk_id is not None:
                setattr(self, key + '_id', fk_id)
            else:
                setattr(self, key + '_id', None)
    def to_min_json(self):
        return self._get_json_from_values(self.__min_keys__)

    def to_semi_json(self):
        obj_json = self._get_json_from_values(self.__semi_keys__)
        obj_json.update(self._get_json_from_fks(self.__semi_fks__))
        return obj_json

    def to_json(self):
        obj_json = self._get_json_from_keys(self.__keys__)
        obj_json.update(self._get_json_from_fks(self.__fks__))
        return obj_json

    def __init__(self, obj_json):
        self._set_keys_from_json(self.__keys__, obj_json)
        self._set_fks_from_json(self.__fks__, obj_json)


eco_id_to_category = {'ECO:0000000': None,
                      'ECO:0000046': 'expression',
                      'ECO:0000048': 'expression',
                      'ECO:0000049': 'expression',
                      'ECO:0000055': 'expression',
                      'ECO:0000066': 'binding',
                      'ECO:0000096': 'binding',
                      'ECO:0000104': 'expression',
                      'ECO:0000106': 'expression',
                      'ECO:0000108': 'expression',
                      'ECO:0000110': 'expression',
                      'ECO:0000112': 'expression',
                      'ECO:0000116': 'expression',
                      'ECO:0000126': 'expression',
                      'ECO:0000136': 'binding',
                      'ECO:0000226': 'binding',
                      'ECO:0000229': 'binding',
                      'ECO:0000230': 'binding',
                      'ECO:0000231': 'expression',
                      'ECO:0000295': 'expression'}

number_to_roman = {'01': 'I', '1': 'I',
                   '02': 'II', '2': 'II',
                   '03': 'III', '3': 'III',
                   '04': 'IV', '4': 'IV',
                   '05': 'V', '5': 'V',
                   '06': 'VI', '6': 'VI',
                   '07': 'VII', '7': 'VII',
                   '08': 'VIII', '8': 'VIII',
                   '09': 'IX', '9': 'IX',
                   '10': 'X',
                   '11': 'XI',
                   '12': 'XII',
                   '13': 'XIII',
                   '14': 'XIV',
                   '15': 'XV',
                   '16': 'XVI',
                   '17': 'Mito',
                   }