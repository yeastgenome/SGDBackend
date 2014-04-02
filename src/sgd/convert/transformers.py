import json
from abc import abstractmethod, ABCMeta
import sys
import traceback

__author__ = 'kpaskov'

# ------------------------------------------ Transformers ------------------------------------------

class TransformerInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def convert(self, element):
        pass

    @abstractmethod
    def finished(self):
        pass

class Json2Obj(TransformerInterface):

    def __init__(self):
        from src.sgd.model.nex.bioentity import Locus, Transcript, Protein, Complex
        from src.sgd.model.nex.bioconcept import Phenotype, Go, ECNumber
        from src.sgd.model.nex.bioitem import Allele, Domain, Chemical, Orphanbioitem
        self.class_type_to_cls = {'LOCUS': Locus, 'TRANSCRIPT': Transcript, 'PROTEIN':Protein, 'COMPLEX': Complex,
                                  'PHENOTYPE': Phenotype, 'GO': Go, 'ECNUMBER': ECNumber,
                                  'ALLELE': Allele, 'DOMAIN': Domain, 'CHEMICAL': Chemical, 'ORPHAN': Orphanbioitem}

    def convert(self, obj_json):
        class_type = obj_json['class_type']
        if class_type in self.class_type_to_cls:
            return self.class_type_to_cls[class_type].from_json(obj_json)

    def finished(self, delete_untouched=False, commit=False):
        return None

class Obj2Json(TransformerInterface):

    def convert(self, obj):
        return obj.to_json()

class Obj2NexDB(TransformerInterface):

    def __init__(self, session_maker, current_obj_query, name=None):
        self.session = session_maker()
        self.name = name
        current_objs = current_obj_query(self.session).all()
        self.key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        self.keys_already_seen = set()
        self.none_count = 0
        self.added_count = 0
        self.updated_count = 0
        self.no_change_count = 0
        self.duplicate_count = 0
        self.error_count = 0
        self.deleted_count = 0

    def convert(self, newly_created_obj):
        try:
            if newly_created_obj is None:
                self.none_count += 1
                return 'None'
            key = newly_created_obj.unique_key()
            if key not in self.keys_already_seen:
                self.keys_already_seen.add(key)
                current_obj = None if key not in self.key_to_current_obj else self.key_to_current_obj[key]
                newly_created_obj_json = newly_created_obj.to_json()
                if current_obj is None:
                    self.session.add(newly_created_obj)
                    self.added_count += 1
                    return 'Added'
                else:
                    updated = current_obj.update(newly_created_obj_json)
                    if updated:
                        self.updated_count += 1
                        return 'Updated'
                    else:
                        self.no_change_count += 1
                        return 'No Change'
            else:
                self.duplicate_count += 1
                return 'Duplicate'
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.error_count += 1
            return 'Error'

    def finished(self, delete_untouched=False, commit=False):
        if delete_untouched:
            keys_to_delete = set(self.key_to_current_obj.keys()).difference(self.keys_already_seen)
            for untouched_key in keys_to_delete:
                self.session.delete(self.key_to_current_obj[untouched_key])
            self.deleted_count = len(keys_to_delete)

        message = {'Added': self.added_count, 'Updated': self.updated_count, 'Deleted': self.deleted_count,
                   'No Change': self.no_change_count, 'Duplicate': self.duplicate_count, 'Error': self.error_count,
                   'None': self.none_count}
        if commit:
            self.session.commit()
        else:
            message['Warning'] = 'Changes not committed!'
        self.session.close()
        return message if self.name is None else self.name + ': ' + str(message)

class Obj2CorePerfDB(TransformerInterface):

    def __init__(self, session_maker, cls, name=None):
        self.session = session_maker()
        self.cls = cls
        self.name = name
        current_objs = self.session.query(cls).all()
        self.id_to_current_obj = dict([(x.id, x) for x in current_objs])
        self.ids_already_seen = set()
        self.none_count = 0
        self.added_count = 0
        self.updated_count = 0
        self.no_change_count = 0
        self.duplicate_count = 0
        self.error_count = 0
        self.deleted_count = 0

    def convert(self, newly_created_obj):
        if newly_created_obj is None:
            self.none_count += 1
            return 'None'
        try:
            identifier = newly_created_obj.id
            if identifier not in self.ids_already_seen:
                self.ids_already_seen.add(identifier)
                current_obj = None if identifier not in self.id_to_current_obj else self.id_to_current_obj[identifier]
                newly_created_obj_json = newly_created_obj.to_json()
                if current_obj is None:
                    self.session.add(self.cls.from_json(newly_created_obj_json))
                    self.added_count += 1
                    return 'Added'
                else:
                    updated = current_obj.update(newly_created_obj_json)
                    if updated:
                        self.updated_count += 1
                        return 'Updated'
                    else:
                        self.no_change_count += 1
                        return 'No Change'
            else:
                self.duplicate_count += 1
                return 'Duplicate'
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.error_count += 1
            return 'Error'

    def finished(self, delete_untouched=False, commit=False):
        if delete_untouched:
            ids_to_delete = set(self.id_to_current_obj.keys()).difference(self.ids_already_seen)
            for untouched_id in ids_to_delete:
                self.session.delete(self.id_to_current_obj[untouched_id])
            self.deleted_count = len(ids_to_delete)

        message = {'Added': self.added_count, 'Updated': self.updated_count, 'Deleted': self.deleted_count,
                   'No Change': self.no_change_count, 'Duplicate': self.duplicate_count, 'Error': self.error_count,
                   'None': self.none_count}
        if commit:
            self.session.commit()
        else:
            message['Warning'] = 'Changes not committed!'
        self.session.close()
        return message if self.name is None else self.name + ': ' + str(message)

class NullTransformer(TransformerInterface):

    def convert(self, x):
        return x

    def finished(self, delete_untouched=False, commit=False):
        return None

class OutputTransformer(TransformerInterface):

    def __init__(self, log, chunk_size):
        self.log = log
        self.chunk_size = chunk_size
        self.output = {}
        self.count = 0
        self.log.info('Start')

    def convert(self, x):
        self.count += 1
        if x in self.output:
            self.output[x] = self.output[x] + 1
        else:
            self.output[x] = 1

        if self.chunk_size is not None and self.count % self.chunk_size == 0:
            print self.output
            self.log.info(self.output)
        return x

    def finished(self, delete_untouched=False, commit=False):
        return self.output

# ------------------------------------------ Starters ------------------------------------------
#http://stackoverflow.com/questions/1145905/sqlalchemy-scan-huge-tables-using-orm
def make_db_starter(q, chunk_size):
    def db_starter():
        offset = 0
        while True:
            r = False
            for elem in q.limit(chunk_size).offset(offset):
               r = True
               yield elem
            offset += chunk_size
            if not r:
                break
    return db_starter

def make_mode_db_starter(q, chunk_size, modes):
    def mode_db_starter():
        for element in make_db_starter(q, chunk_size)():
            for mode in modes:
                yield (mode, element)
    return mode_db_starter

def make_multi_starter(starters):
    def multi_starter():
        for starter in starters:
            for elem in starter():
                yield elem
    return multi_starter

def make_file_starter(filename, delimeter='\t', offset=0, row_f=None):
    def file_starter():
        count = 0
        f = open(filename, 'r')
        for line in f:
            if count >= offset:
                pieces = line.split(delimeter)
                if row_f is None:
                    yield pieces
                else:
                    new_pieces = row_f(pieces)
                    if isinstance(new_pieces, list):
                        for element in new_pieces:
                            yield element
                    else:
                        yield new_pieces
            count += 1
        f.close()
    return file_starter

def make_obo_file_starter(filename):
    def obo_file_starter():
        f = open(filename, 'r')
        current_term = None
        for line in f:
            line = line.strip()
            if line == '[Term]':
                if current_term is not None:
                    yield current_term
                current_term = {}
            elif current_term is not None and ': ' in line:
                pieces = line.split(': ')
                if pieces[0] in current_term:
                    current_term[pieces[0]] = [current_term[pieces[0]], pieces[1]]
                else:
                    current_term[pieces[0]] = pieces[1]
        f.close()
    return obo_file_starter

def make_backend_starter(backend, method, chunk_size):
    def backend_starter():
        offset = 0
        while True:
            bioentities = json.loads(getattr(backend, method)(chunk_size, offset))
            if len(bioentities) == 0:
                break

            for bioentity in bioentities:
                yield bioentity
            offset += chunk_size
    return backend_starter

# ------------------------------------------ Conversion ------------------------------------------
def do_conversion(starter, converters, delete_untouched=False, commit=False):
    for element in starter():
        reduce(lambda x, y: y.convert(x), converters, element)

    for converter in converters:
        output = converter.finished(delete_untouched=delete_untouched, commit=commit)
        if output is not None:
            print output

