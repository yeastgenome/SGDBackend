__author__ = 'kpaskov'

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
            new_value = json_obj[key]

            if new_value != current_value:
                setattr(self, key, new_value)
                anything_changed = True

        for key in self.__eq_fks__:
            current_value = getattr(self, key + '_id')
            new_value = json_obj[key]['id']

            if new_value != current_value:
                setattr(self, key + '_id', new_value)
                anything_changed = True

        return anything_changed

    def to_min_json(self):
        return {
            'id': self.id,
            'format_name': self.format_name,
            'display_name': self.display_name,
            'link': self.link,
            }