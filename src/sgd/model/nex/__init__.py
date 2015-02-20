__author__ = 'kpaskov'

import json
import datetime
import glob
import os

Base = None

locus_types = [
    'ORF',
    'long_terminal_repeat',
    'ARS',
    'tRNA_gene',
    'transposable_element_gene',
    'snoRNA_gene',
    'LTR_retrotransposon',
    'telomere',
    'rRNA_gene',
    'ncRNA_gene',
    'centromere',
    'pseudogene',
    'origin_of_replication',
    'matrix_attachment_site',
    'snRNA_gene',
    'blocked_reading_frame',
    'gene_group',
    'silent_mating_type_cassette_array',
    'mating_type_region',
    'intein_encoding_region',
    'telomerase_RNA_gene']

def create_format_name(display_name):
    format_name = display_name.replace(' ', '_')
    format_name = format_name.replace('/', '-')
    return format_name

class UpdateWithJsonMixin(object):
    def update(self, obj_json, foreign_key_retriever, make_changes=True):
        anything_changed = False
        for key in self.__eq_values__:
            current_value = getattr(self, key)

            if key in obj_json:
                new_value = None if key not in obj_json else obj_json[key]

                if isinstance(new_value, datetime.date):
                    new_value = None if new_value is None else datetime.datetime.strptime(new_value, "%Y-%m-%d")

                if key == 'id' or key == 'date_created' or key == 'created_by' or key == 'json':
                    pass
                elif new_value != current_value:
                    if make_changes:
                        setattr(self, key, new_value)
                    anything_changed = True

        for key, cls, allow_updates in self.__eq_fks__:
            current_value = getattr(self, key)

            if isinstance(current_value, list):
                key_to_current_value = dict([(x.unique_key(), x) for x in current_value])
                keys_not_seen = set(key_to_current_value)

                for new_entry in obj_json[key]:
                    new_object = foreign_key_retriever(new_entry, cls, allow_updates)
                    if new_object.unique_key() in keys_not_seen:
                        keys_not_seen.remove(new_entry)
                    elif new_object.unique_key() in key_to_current_value:
                        raise Exception('Duplicate ' + key)
                    else:
                        if make_changes:
                            current_value.append(new_object)
                        anything_changed = True

                for key in keys_not_seen:
                    if make_changes:
                        current_value.remove(key_to_current_value[key])
                    anything_changed = True

            else:
                new_value = foreign_key_retriever(obj_json[key], cls, allow_updates)
                if new_value is None and current_value is None:
                    pass
                elif new_value is None or current_value is not None or new_value.unique_key() != current_value.unique_key():
                    if make_changes:
                        setattr(self, key, new_value)
                    anything_changed = True

        return anything_changed

    def __init__(self, obj_json, foreign_key_converter):
        self.update(obj_json, foreign_key_converter, make_changes=True)

class ToJsonMixin(object):

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

        for key, cls, allow_updates in self.__eq_fks__:
            fk_obj = getattr(self, key)

            if fk_obj is None:
                obj_json[key] = None
            elif isinstance(fk_obj, list):
                obj_json[key] = [x.to_min_json() for x in fk_obj]
            else:
                obj_json[key] = fk_obj.to_min_json()

        return obj_json
