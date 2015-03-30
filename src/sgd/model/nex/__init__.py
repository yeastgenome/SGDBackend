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

def get_class_from_string(class_string):
    module = class_string.split('.')[0]
    class_name = class_string.split('.')[1]
    mod = __import__('src.sgd.model.nex.' + module, fromlist=[class_name])
    if hasattr(mod, class_name):
        return getattr(mod, class_name)
    else:
        raise Exception('Class not found: ' + class_string)

class UpdateWithJsonMixin(object):

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None

        newly_created_obj = cls(obj_json, session)

        if hasattr(cls, 'format_name'):
            current_obj = session.query(cls).filter_by(format_name=newly_created_obj.format_name).first()

            if current_obj is None:
                return newly_created_obj, 'Created'
            else:
                return current_obj, 'Found'
        else:
            raise Exception('Class ' + cls.__name__ + ' doesn\'t have format name. You need to implement the create_or_find method.')

    def update(self, obj_json, session, make_changes=True):
        anything_changed = False
        for key in self.__eq_values__:
            current_value = getattr(self, key)

            if key in obj_json:
                new_value = None if key not in obj_json else obj_json[key]

                if isinstance(current_value, datetime.date):
                    current_value = datetime.datetime.strftime(current_value, "%Y-%m-%d")

                if self.id is not None and key in self.__no_edit_values__:
                    if (key == 'date_created' or key == 'created_by') and current_value is not None and new_value is None:
                        #Ok because it's either date_created or created_by
                        pass
                    elif current_value is not None and current_value != new_value:
                        print self.__class__.__name__
                        print self.unique_key()
                        print ToJsonMixin.to_json(self)
                        print obj_json
                        raise Exception(key + ' cannot be edited. (Tried to change from ' + str(current_value) + ' to ' + str(new_value) + '.)')
                else:
                    if new_value != current_value:
                        if make_changes:
                            if str(getattr(self.__class__, key).property.columns[0].type) == 'DATE' and new_value is not None:
                                new_value = datetime.datetime.strptime(new_value, "%Y-%m-%d")
                            setattr(self, key, new_value)
                        anything_changed = True

        for key, cls, allow_updates in self.__eq_fks__:
            current_fk_value = getattr(self, key)

            if isinstance(cls, str):
                #We've been given the class as a string due to cyclic dependencies, so find the actual class
                cls = get_class_from_string(cls)

            if key not in obj_json:
                #Do nothing if we haven't been given any information about this foreign key
                pass
            else:
                new_fk_json_obj = obj_json[key]

                if isinstance(current_fk_value, list):
                    #This foreign key is actually a list of objects

                    if not isinstance(new_fk_json_obj, list):
                        raise Exception('Expected a list for key ' + key)

                    key_to_current_value = dict([(x.unique_key(), x) for x in current_fk_value])
                    keys_not_seen = set(key_to_current_value)

                    for new_fk_json_obj_entry in new_fk_json_obj:
                        new_fk_obj, status = cls.create_or_find(new_fk_json_obj_entry, session, parent_obj=self)
                        if make_changes and allow_updates:
                            #If we find an object, and we allow updates, then we update it.
                            updated = new_fk_obj.update(new_fk_json_obj_entry, session, make_changes=True)
                            if updated:
                                anything_changed = True
                        else:
                            #If we find an object, and we don't allow updates, and it differs from the object we've been given, exception
                            should_be_updated = new_fk_obj.update(new_fk_json_obj_entry, session, make_changes=False)
                            if should_be_updated:
                                raise Exception('Update not allowed, but fk differs.')

                        if new_fk_obj.unique_key() in keys_not_seen:
                            #We already have this object, and we've done our update so we're all set. Just a little bit of bookkeeping
                            keys_not_seen.remove(new_fk_obj.unique_key())
                        elif new_fk_obj.unique_key() in key_to_current_value:
                            #We already have this object AND we've already seen it before, so we've been given duplicates - not allowed.
                            raise Exception('Duplicate foreign key ' + key)
                        else:
                            if make_changes:
                                #We haven't seen this object, so add it.
                                current_fk_value.append(new_fk_obj)
                            anything_changed = True

                    for key in keys_not_seen:
                        #We didn't see these keys, so they need to be deleted.
                        if make_changes:
                            current_fk_value.remove(key_to_current_value[key])
                        anything_changed = True

                else:
                    #This foreign key is just a single object
                    new_fk_obj, status = cls.create_or_find(new_fk_json_obj, session, parent_obj=self)
                    if make_changes and allow_updates:
                        #If we find an object, and we allow updates, then we update it.
                        new_fk_obj.update(new_fk_json_obj, session, make_changes=True)
                    else:
                        #If we find an object, and we don't allow updates, and it differs from the object we've been given, exception
                        should_be_updated = new_fk_obj.update(new_fk_json_obj, session, make_changes=False)
                        if should_be_updated:
                            raise Exception('Update not allowed, but fk differs.')

                    if current_fk_value is None or new_fk_obj.unique_key() != current_fk_value.unique_key():
                        #Change the foreign key object
                        if make_changes:
                            setattr(self, key, new_fk_obj)
                        anything_changed = True

        return anything_changed

    def __init__(self, obj_json, session):
        self.update(obj_json, session, make_changes=True)
        self.format_name = create_format_name(self.__create_format_name__())
        self.link = self.__create_link__()

    def __create_format_name__(self):
        return self.display_name

    def __create_link__(self):
        return '/' + self.__class__.__name__.lower() + '/' + self.format_name

class ToJsonMixin(object):

    def to_min_json(self, include_description=False):
        obj_json = dict()
        for key in {'id', 'format_name', 'display_name', 'link'}:
            if hasattr(self, key):
                obj_json[key] = getattr(self, key)

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

    def unique_key(self):
        return self.format_name
