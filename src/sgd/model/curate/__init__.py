import datetime
import traceback
import uuid

__author__ = 'kpaskov'

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
    mod = __import__('src.sgd.model.curate.' + module, fromlist=[class_name])
    if hasattr(mod, class_name):
        return getattr(mod, class_name)
    else:
        raise Exception('Class not found: ' + class_string)


class UpdateWithJsonMixin(object):

    @classmethod
    def create_or_find(cls, obj_json, session, parent_obj=None):
        if obj_json is None:
            return None, 'Found'

        current_obj = None
        for key in getattr(cls, '__id_values__'):
            if key in obj_json:
                current_obj = session.query(cls).filter(getattr(cls, key) == obj_json[key]).first()

            if current_obj is not None:
                break

        if current_obj is None:
            current_obj = cls.specialized_find(obj_json, session)

        if current_obj is None:
            return cls(obj_json, session), 'Created'
        else:
            return current_obj, 'Found'

    @classmethod
    def specialized_find(cls, obj_json, session):
        return None

    def update(self, obj_json, session, make_changes=True):
        warnings = []
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
                        warnings.append(key + ' cannot be edited. (Tried to change from ' + str(current_value) + ' to ' + str(new_value) + '.)')
                        #print self.__class__.__name__
                        #print self.unique_key()
                        #print ToJsonMixin.to_json(self)
                        #print obj_json
                        #raise Exception(key + ' cannot be edited. (Tried to change from ' + str(current_value) + ' to ' + str(new_value) + '.)')
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
                        try:
                            new_fk_obj, status = cls.create_or_find(new_fk_json_obj_entry, session, parent_obj=self)
                            if make_changes and allow_updates:
                                #If we find an object, and we allow updates, then we update it.
                                updated, sub_warnings = new_fk_obj.update(new_fk_json_obj_entry, session, make_changes=True)
                                warnings.extend(sub_warnings)
                                if updated:
                                    anything_changed = True
                            else:
                                #If we find an object, and we don't allow updates, and it differs from the object we've been given, exception
                                should_be_updated, sub_warnings = new_fk_obj.update(new_fk_json_obj_entry, session, make_changes=False)
                                warnings.extend(sub_warnings)
                                if should_be_updated:
                                    warnings.append('Update not allowed, but fk differs.')
                                    #raise Exception('Update not allowed, but fk differs.')

                            if new_fk_obj.unique_key() in keys_not_seen:
                                #We already have this object, and we've done our update so we're all set. Just a little bit of bookkeeping
                                keys_not_seen.remove(new_fk_obj.unique_key())
                            elif new_fk_obj.unique_key() in key_to_current_value:
                                print new_fk_json_obj
                                #We already have this object AND we've already seen it before, so we've been given duplicates - not allowed.
                                raise Exception('Duplicate foreign key ' + key)
                            else:
                                if make_changes:
                                    #We haven't seen this object, so add it.
                                    current_fk_value.append(new_fk_obj)
                                anything_changed = True
                        except:
                            print traceback.print_exc()

                    for key in keys_not_seen:
                        #We didn't see these keys, so they need to be deleted.
                        if make_changes:
                            current_fk_value.remove(key_to_current_value[key])
                        anything_changed = True

                else:
                    #This foreign key is just a single object
                    new_fk_obj, status = cls.create_or_find(new_fk_json_obj, session, parent_obj=self)
                    if make_changes and allow_updates and new_fk_obj is not None:
                        #If we find an object, and we allow updates, then we update it.
                        new_fk_obj.update(new_fk_json_obj, session, make_changes=True)
                    elif new_fk_obj is not None:
                        #If we find an object, and we don't allow updates, and it differs from the object we've been given, exception
                        should_be_updated, sub_warnings = new_fk_obj.update(new_fk_json_obj, session, make_changes=False)
                        warnings.extend(sub_warnings)
                        if should_be_updated:
                            warnings.append('Update not allowed, but fk differs.')
                            #raise Exception('Update not allowed, but fk differs.')

                    if current_fk_value is None and new_fk_obj is None:
                        pass
                    elif (current_fk_value is None and new_fk_obj is not None) or (current_fk_value is not None and new_fk_obj is None) or new_fk_obj.unique_key() != current_fk_value.unique_key():
                        #Change the foreign key object
                        if make_changes:
                            setattr(self, key, new_fk_obj)
                        anything_changed = True

        return anything_changed, warnings

    def __init__(self, obj_json, session):
        self.id = str(uuid.uuid4())
        self.name = self.__create_name__(obj_json)
        self.link = self.__create_link__(obj_json)
        self.update(obj_json, session, make_changes=True)

    @classmethod
    def __create_link__(cls, obj_json):
        return '/' + cls.__name__.lower() + '/' + cls.__create_file_name__(obj_json)

    @classmethod
    def __create_name__(cls, obj_json):
        return obj_json['name']

    @classmethod
    def __create_file_name__(cls, obj_json):
        return create_format_name(cls.__create_name__(obj_json))


class ToJsonMixin(object):

    def __to_mini_json__(self):
        return self.id, self.name

    def __to_small_json__(self):
        obj_json = dict()
        for key in {'id', 'name', 'link'}:
            obj_json[key] = getattr(self, key)
        return obj_json

    def __to_medium_json__(self):
        obj_json = dict()
        for key in {'id', 'name', 'link', 'description'}:
            obj_json[key] = getattr(self, key)
        return obj_json

    def __to_large_json__(self):
        obj_json = {}
        for key in self.__eq_values__:
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
                obj_json[key] = [x.to_json('small') for x in fk_obj]
            else:
                obj_json[key] = fk_obj.to_json('small')
        return obj_json

    def to_json(self, size='small'):
        if size == 'mini':
            return self.__to_mini_json__()
        elif size == 'small':
            return self.__to_small_json__()
        elif size == 'medium':
            return self.__to_medium_json__()
        elif size == 'large':
            return self.__to_large_json__()
        else:
            raise Exception('Invalid size.')

    def unique_key(self):
        return self.name
