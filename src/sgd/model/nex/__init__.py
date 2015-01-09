'''
This package contains the complete nex model. The model is defined as a group of SQLAlchemy classes which are meant
to be used to query the nex database schema. The schema is contained in the two sql files nex_schema.sql and
nex_triggers.sql. This model is used by both the covert and backend packages, but can also be used independently.

This file contains core methods and base classes for the nex model.
'''

__author__ = 'kpaskov'

import datetime

'''
All classes in this model inherit from the base class provided by the following variable. In order to use this model,
you must initialize the Base variable before importing any class in this model. For example..

    class Base(object):
        __table_args__ = {'schema': schema, 'extend_existing':True}

    nex.Base = declarative_base(cls=Base)
    engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), pool_recycle=3600)
'''

Base = None


def create_format_name(display_name):
    '''
    Given a string (display_name), cleans it up to create a format name (usable in urls and filenames) by replacing
    spaces and slashes.
    :param display_name: any string
    :return: a cleaned up string that can be used for urls and filenames.
    '''
    format_name = display_name.replace(' ', '_')
    format_name = format_name.replace('/', '-')
    return format_name

# All locus types in the nex database. This variable is used throughout the nex model.
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

class UpdateByJsonMixin(object):
    '''
    Many classes in the nex model inherit from this class. The update and compare methods are used by the convert
    package to transfer data from the bud schema to the nex schema. The to_json method is used by the backend package
    to define the json output for this object. These methods rely on the __eq_values__ and __eq_fks__
    fields which are expected to be defined. __eq_values__ is a list of strings representing the fields of the
    object that are eligible to be updated. This list does NOT include fields whose values are other objects, defined
    by foreign key relationships in the schema. __eq_fks__ is a list of strings representing these foreign key
    fields which are eligible to be updated.
    '''
    def update(self, json_obj):
        '''
        Given a piece of json containing updated information, update all fields for this object.
        :param json_obj: A json object containing updated information
        :return: True if one or more fields were updated.
        '''

        anything_changed = False

        # Update non-foreign key fields represented in __eq_values__. For example, this for-loop might update the
        # object's name or its url.

        for key in self.__eq_values__:
            current_value = getattr(self, key)
            new_value = None if key not in json_obj else json_obj[key]

            # Handle dates. (This could perhaps be done more elegantly, but I often run into trouble with dates being
            # stored as strings in the bud schema, and this code transforms those strings into datetime objects.)
            if isinstance(new_value, str) and (key == 'seq_version' or key == 'coord_version' or key == 'date_of_run' or key == 'expiration_date' or key == 'reservation_date'):
                new_value = None if new_value is None else datetime.datetime.strptime(new_value, "%Y-%m-%d")

            # This method skips id, date_created, created_by, and json fields. These core attributes should never
            # be updated - this would break key assumptions in the schema.
            if key == 'id' or key == 'date_created' or key == 'created_by' or key == 'json':
                pass
            elif new_value != current_value:
                setattr(self, key, new_value)
                anything_changed = True

        # Update foreign key fields represented in __eq_fks__. For example, this for-loop might update an object's
        # foreign key relationship to the source table.
        for key in self.__eq_fks__:
            current_value = getattr(self, key + '_id')
            new_value = None if (key not in json_obj or json_obj[key] is None) else json_obj[key]['id']

            if new_value != current_value:
                setattr(self, key + '_id', new_value)
                anything_changed = True

        return anything_changed

    def compare(self, json_obj):
        '''
        This method is very similar to the update method. However, rather than actually updating this object according
        to the information in json_obj, it only checks if this object will require updating.
        :param json_obj: A json object containing updated information.
        :return: False if the information stored in json_obj is the same as the information stored in this object, and
        True if the object differs from json_obj in one or more fields.
        '''
        anything_changed = False

        #Compare non-foreign key fields represented in __eq_values__. For example, this for-loop might compare the
        # object's name to the name given in the json_obj.
        for key in self.__eq_values__:
            current_value = getattr(self, key)
            new_value = json_obj[key]

            #Handle dates.
            if isinstance(new_value, str) and (key == 'seq_version' or key == 'coord_version' or key == 'date_of_run' or key == 'expiration_date' or key == 'reservation_date'):
                new_value = None if new_value is None else datetime.datetime.strptime(new_value, "%Y-%m-%d")

            # The id, date_created, created_by, and json fields are not checked for equality. These fields cannot be
            # updated.
            if key == 'id' or key == 'date_created' or key == 'created_by' or key == 'json':
                pass
            elif new_value != current_value:
                anything_changed = True

        # Compare foreign key fields represented in __eq_fks__. For example, this for-loop might compare an object's
        # foreign key relationship to the source table to the source given in the json_obj.
        for key in self.__eq_fks__:
            current_value = getattr(self, key + '_id')
            new_value = None if (key not in json_obj or json_obj[key] is None) else json_obj[key]['id']

            if new_value != current_value:
                anything_changed = True

        return anything_changed

    def to_min_json(self, include_description=False):
        '''
        This method constructs a bare minimum json representation of the object. It is often used in the to_json
        method to represent foreign key relationships.
        :param include_description: True if the resulting json object should contain the object's description
        :return: A minimum json representation of the object.
        '''
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
        '''
        This method constructs a full json representation of the object using the fields listed in __eq_values__ and
        __eq_fks__. For each foreign key relationship in __eq_fks__, it stores in the to_min_json representation of the
        foreign key object in the json representation.
        :return:
        '''
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
        '''
        Given a piece of json, create an object with the given values and foreign key relationships.
        :param obj_json: A json representation of the object
        :return:
        '''
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
