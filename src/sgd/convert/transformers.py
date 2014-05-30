from abc import abstractmethod, ABCMeta
import sys
import traceback

from src.sgd.model.nex import UpdateByJsonMixin
from math import ceil

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

    def __init__(self, cls):
        self.cls = cls

    def convert(self, obj_json):
        if obj_json is None:
            return None
        else:
            return self.cls(obj_json)

    def finished(self):
        return None

class Obj2Json(TransformerInterface):

    def convert(self, obj):
        return obj.to_json()

    def finished(self):
        return None

class Obj2NexDB(TransformerInterface):

    def __init__(self, session_maker, current_obj_query, name=None, commit_interval=None, commit=False, delete_untouched=False):
        self.session = session_maker()
        self.current_obj_query = current_obj_query
        self.name = name
        self.commit_interval = commit_interval
        self.commit = commit
        self.delete_untouched = delete_untouched
        self.key_to_current_obj_json = dict([(x.unique_key(), UpdateByJsonMixin.to_json(x)) for x in make_db_starter(current_obj_query(self.session), 20000)()])
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
            if self.commit_interval is not None and (self.added_count + self.updated_count + self.deleted_count) % self.commit_interval == 0:
                self.session.commit()

            if newly_created_obj is None:
                self.none_count += 1
                return 'None'
            key = newly_created_obj.unique_key()
            if key not in self.keys_already_seen:
                self.keys_already_seen.add(key)
                current_obj_json = None if key not in self.key_to_current_obj_json else self.key_to_current_obj_json[key]
                newly_created_obj_json = UpdateByJsonMixin.to_json(newly_created_obj)
                if current_obj_json is None:
                    self.session.add(newly_created_obj)
                    self.added_count += 1
                    return 'Added'
                elif newly_created_obj.compare(current_obj_json):
                    current_obj = self.current_obj_query(self.session).filter_by(id=current_obj_json['id']).first()
                    if current_obj is not None:
                        current_obj.update(newly_created_obj_json)
                        self.updated_count += 1
                        return 'Updated'
                    else:
                        self.error_count += 1
                        return 'Error'
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

    def finished(self):
        if self.delete_untouched:
            keys_to_delete = set(self.key_to_current_obj_json.keys()).difference(self.keys_already_seen)
            ids_to_delete = [self.key_to_current_obj_json[key]['id'] for key in keys_to_delete]

            for untouched_id in ids_to_delete:
                current_obj = self.current_obj_query(self.session).filter_by(id=untouched_id).first()
                if current_obj is not None:
                    self.session.delete(current_obj)
                    self.deleted_count += 1
                else:
                    self.error_count += 1

        message = {'Added': self.added_count, 'Updated': self.updated_count, 'Deleted': self.deleted_count,
                   'No Change': self.no_change_count, 'Duplicate': self.duplicate_count, 'Error': self.error_count,
                   'None': self.none_count}
        if self.commit_interval is not None or self.commit:
            self.session.commit()
        else:
            message['Warning'] = 'Changes not committed!'
        self.session.close()
        return message if self.name is None else self.name + ': ' + str(message)

class Evidence2NexDB(TransformerInterface):

    def __init__(self, session_maker, current_obj_query, name=None, commit_interval=None, commit=False, delete_untouched=False):
        self.session = session_maker()
        self.current_obj_query = current_obj_query
        self.name = name
        self.commit_interval = commit_interval
        self.commit = commit
        self.delete_untouched = delete_untouched
        self.key_to_current_json = dict([(x.unique_key(), (x.json, x.id)) for x in make_db_starter(current_obj_query(self.session), 20000)()])
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
            if self.commit_interval is not None and (self.added_count + self.updated_count + self.deleted_count) % self.commit_interval == 0:
                self.session.commit()

            if newly_created_obj is None:
                self.none_count += 1
                return 'None'
            key = newly_created_obj.unique_key()
            if key not in self.keys_already_seen:
                self.keys_already_seen.add(key)
                current_json = None if key not in self.key_to_current_json else self.key_to_current_json[key][0]
                newly_created_json = newly_created_obj.json
                if key not in self.key_to_current_json:
                    self.session.add(newly_created_obj)
                    self.added_count += 1
                    return 'Added'
                elif current_json == newly_created_json:
                    self.no_change_count += 1
                    return 'No Change'
                else:
                    newly_created_obj_json = UpdateByJsonMixin.to_json(newly_created_obj)
                    current_obj = self.current_obj_query(self.session).filter_by(id=self.key_to_current_json[key][1]).first()
                    current_obj.update(newly_created_obj_json)
                    current_obj.json = newly_created_json
                    self.updated_count += 1
                    return 'Updated'
            else:
                self.duplicate_count += 1
                return 'Duplicate'
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.error_count += 1
            return 'Error'

    def finished(self):
        if self.delete_untouched:
            keys_to_delete = set(self.key_to_current_json.keys()).difference(self.keys_already_seen)
            ids_to_delete = [self.key_to_current_json[key][1] for key in keys_to_delete]

            for untouched_id in ids_to_delete:
                current_obj = self.current_obj_query(self.session).filter_by(id=untouched_id).first()
                self.session.delete(current_obj)
            self.deleted_count = len(keys_to_delete)

        message = {'Added': self.added_count, 'Updated': self.updated_count, 'Deleted': self.deleted_count,
                   'No Change': self.no_change_count, 'Duplicate': self.duplicate_count, 'Error': self.error_count,
                   'None': self.none_count}
        if self.commit_interval is not None or self.commit:
            self.session.commit()
        else:
            message['Warning'] = 'Changes not committed!'
        self.session.close()
        return message if self.name is None else self.name + ': ' + str(message)

class BigObj2NexDB(TransformerInterface):

    def __init__(self, session_maker, current_obj_query, name=None, commit_interval=None, commit=False, delete_untouched=False):
        self.session = session_maker()
        self.current_obj_query = current_obj_query
        self.name = name
        self.commit_interval = commit_interval
        self.commit = commit
        self.delete_untouched = delete_untouched
        self.key_to_current_id = dict([(x.unique_key(), x.id) for x in make_db_starter(current_obj_query(self.session), 20000)()])
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
            if self.commit_interval is not None and (self.added_count + self.updated_count + self.deleted_count) % self.commit_interval == 0:
                self.session.commit()

            if newly_created_obj is None:
                self.none_count += 1
                return 'None'
            key = newly_created_obj.unique_key()
            if key not in self.keys_already_seen:
                self.keys_already_seen.add(key)
                current_id = None if key not in self.key_to_current_id else self.key_to_current_id[key]
                if current_id is None:
                    self.session.add(newly_created_obj)
                    self.added_count += 1
                    return 'Added'
                else:
                    current_obj = self.current_obj_query(self.session).filter_by(id=current_id).first()
                    current_obj_json = UpdateByJsonMixin.to_json(current_obj)
                    if newly_created_obj.compare(current_obj_json):
                        current_obj.update(current_obj_json)
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

    def finished(self):
        if self.delete_untouched:
            keys_to_delete = set(self.key_to_current_id.keys()).difference(self.keys_already_seen)
            ids_to_delete = [self.key_to_current_id[key] for key in keys_to_delete]

            for untouched_id in ids_to_delete:
                current_obj = self.current_obj_query(self.session).filter_by(id=untouched_id).first()
                self.session.delete(current_obj)
            self.deleted_count = len(keys_to_delete)

        message = {'Added': self.added_count, 'Updated': self.updated_count, 'Deleted': self.deleted_count,
                   'No Change': self.no_change_count, 'Duplicate': self.duplicate_count, 'Error': self.error_count,
                   'None': self.none_count}
        if self.commit_interval is not None or self.commit:
            self.session.commit()
        else:
            message['Warning'] = 'Changes not committed!'
        self.session.close()
        return message if self.name is None else self.name + ': ' + str(message)

class Json2CorePerfDB(TransformerInterface):

    def __init__(self, session_maker, cls, name=None, commit_interval=None, commit=False, delete_untouched=False):
        self.session = session_maker()
        self.cls = cls
        self.name = name
        self.commit_interval = commit_interval
        self.commit = commit
        self.delete_untouched = delete_untouched
        self.id_to_current_obj = dict([(x.id, x) for x in self.session.query(cls).all()])
        self.ids_already_seen = set()
        self.none_count = 0
        self.added_count = 0
        self.updated_count = 0
        self.no_change_count = 0
        self.duplicate_count = 0
        self.error_count = 0
        self.deleted_count = 0

    def convert(self, newly_created_obj_json):
        if newly_created_obj_json is None:
            self.none_count += 1
            return 'None'
        try:
            if self.commit_interval is not None and (self.added_count + self.updated_count + self.deleted_count) % self.commit_interval == 0:
                self.session.commit()

            identifier = newly_created_obj_json['id']
            if identifier not in self.ids_already_seen:
                self.ids_already_seen.add(identifier)
                current_obj = None if identifier not in self.id_to_current_obj else self.id_to_current_obj[identifier]
                if current_obj is None:
                    self.session.add(self.cls(newly_created_obj_json))
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

    def finished(self):
        if self.delete_untouched:
            ids_to_delete = set(self.id_to_current_obj.keys()).difference(self.ids_already_seen)
            for untouched_id in ids_to_delete:
                self.session.delete(self.id_to_current_obj[untouched_id])
            self.deleted_count = len(ids_to_delete)

        message = {'Added': self.added_count, 'Updated': self.updated_count, 'Deleted': self.deleted_count,
                   'No Change': self.no_change_count, 'Duplicate': self.duplicate_count, 'Error': self.error_count,
                   'None': self.none_count}
        if self.commit_interval is not None or self.commit:
            self.session.commit()
        else:
            message['Warning'] = 'Changes not committed!'
        self.session.close()
        return message if self.name is None else self.name + ': ' + str(message)

class Json2DisambigPerfDB(TransformerInterface):

    def __init__(self, session_maker, commit_interval=None, commit=False):
        from src.sgd.model.perf.core import Disambig
        self.name = 'convert.from_backend.disambig'
        self.session = session_maker()
        self.commit_interval = commit_interval
        self.commit = commit
        self.id_to_current_obj = dict([((x.class_type, x.subclass_type, x.disambig_key), x.obj_id) for x in self.session.query(Disambig).all()])
        self.already_seen = set()
        self.none_count = 0
        self.added_count = 0
        self.updated_count = 0
        self.no_change_count = 0
        self.duplicate_count = 0
        self.error_count = 0
        self.deleted_count = 0

    def convert(self, newly_created_obj_json):
        from src.sgd.model.perf.core import Disambig
        if newly_created_obj_json is None:
            self.none_count += 1
            return 'None'
        try:
            if self.commit_interval is not None and (self.added_count + self.updated_count + self.deleted_count) % self.commit_interval == 0:
                self.session.commit()

            key = (newly_created_obj_json['class_type'], newly_created_obj_json['subclass_type'], newly_created_obj_json['disambig_key'])
            identifier = newly_created_obj_json['identifier']
            if key in self.id_to_current_obj:
                if identifier == self.id_to_current_obj[key]:
                    self.no_change_count += 1
                    self.already_seen.add(key)
                    return 'No Change'
                else:
                    to_update = self.session.query(Disambig).filter_by(class_type=key[0], subclass_type=key[1], disambig_key=key[2]).first()
                    to_update.obj_id = identifier
                    self.updated_count += 1
                    self.already_seen.add(key)
                    return 'Updated'
            else:
                self.session.add(Disambig(newly_created_obj_json))
                self.added_count += 1
                return 'Added'
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.error_count += 1
            return 'Error'

    def finished(self):
        from src.sgd.model.perf.core import Disambig
        for untouched_key in self.already_seen:
            to_delete = self.session.query(Disambig).filter_by(class_type=untouched_key[0], subclass_type=untouched_key[1], disambig_key=untouched_key[2]).first()
            self.session.delete(to_delete)
        self.deleted_count = len(self.id_to_current_obj)

        message = {'Added': self.added_count, 'Updated': self.updated_count, 'Deleted': self.deleted_count,
                   'No Change': self.no_change_count, 'Duplicate': self.duplicate_count, 'Error': self.error_count,
                   'None': self.none_count}
        if self.commit_interval is not None or self.commit:
            self.session.commit()
        else:
            message['Warning'] = 'Changes not committed!'
        self.session.close()
        return message if self.name is None else self.name + ': ' + str(message)

class Json2DataPerfDB(TransformerInterface):

    def __init__(self, session_maker, cls, class_type, obj_ids, name=None, commit_interval=None, commit=False):
        self.session = session_maker()
        self.cls = cls
        self.name = name
        self.commit_interval = commit_interval
        self.commit = commit

        self.id_to_obj = dict([(x.obj_id, x) for x in self.session.query(cls).filter_by(class_type=class_type).all()])
        current_ids = set(self.id_to_obj.keys())
        obj_ids = set(obj_ids)
        to_be_added = obj_ids - current_ids
        to_be_deleted = list(current_ids - obj_ids)

        for obj_id in to_be_added:
            new_obj = self.cls(obj_id, class_type, None)
            self.session.add(new_obj)
            self.id_to_obj[obj_id] = new_obj
        for obj_id in to_be_deleted:
            self.session.delete(self.id_to_obj[obj_id])
            del self.id_to_obj[obj_id]

        if self.commit_interval is not None or self.commit:
            self.session.commit()

        self.none_count = 0
        self.added_count = len(to_be_added)
        self.updated_count = 0
        self.no_change_count = 0
        self.duplicate_count = 0
        self.error_count = 0
        self.deleted_count = len(to_be_deleted)

    def convert(self, newly_created_obj_json):
        try:
            if self.commit_interval is not None and (self.added_count + self.updated_count + self.deleted_count) % self.commit_interval == 0:
                self.session.commit()

            obj_id, json_str = newly_created_obj_json

            self.id_to_obj[obj_id].json = json_str
            self.updated_count += 1
            return 'Updated'

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.error_count += 1
            return 'Error'

    def finished(self):
        message = {'Added': self.added_count, 'Updated': self.updated_count, 'Deleted': self.deleted_count,
                   'No Change': self.no_change_count, 'Duplicate': self.duplicate_count, 'Error': self.error_count,
                   'None': self.none_count}
        if self.commit_interval is not None or self.commit:
            self.session.commit()
        else:
            message['Warning'] = 'Changes not committed!'
        self.session.close()
        return message if self.name is None else self.name + ': ' + str(message)

class NullTransformer(TransformerInterface):

    def convert(self, x):
        return x

    def finished(self):
        return None

class OutputTransformer(TransformerInterface):

    def __init__(self, chunk_size):
        self.chunk_size = chunk_size
        self.output = {}
        self.count = 0

    def convert(self, x):
        self.count += 1
        if x in self.output:
            self.output[x] = self.output[x] + 1
        else:
            self.output[x] = 1

        if self.chunk_size is not None and self.count % self.chunk_size == 0:
            print self.output
        return x

    def finished(self):
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
        f = open(filename, 'U')
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
            objs = getattr(backend, method)(chunk_size, offset)
            if len(objs) == 0:
                break

            for obj in objs:
                yield obj
            offset += chunk_size
    return backend_starter

def make_locus_data_backend_starter(backend, method, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield (obj_id, getattr(backend, method)(locus_identifier=obj_id, are_ids=True))
    return individual_backend_starter

def make_reference_data_backend_starter(backend, method, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield (obj_id, getattr(backend, method)(reference_identifier=obj_id, are_ids=True))
    return individual_backend_starter

def make_ecnumber_data_backend_starter(backend, method, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield (obj_id, getattr(backend, method)(ec_number_identifier=obj_id, are_ids=True))
    return individual_backend_starter

def make_domain_data_backend_starter(backend, method, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield (obj_id, getattr(backend, method)(domain_identifier=obj_id, are_ids=True))
    return individual_backend_starter

def make_go_data_backend_starter(backend, method, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield (obj_id, getattr(backend, method)(go_identifier=obj_id, are_ids=True))
    return individual_backend_starter

def make_phenotype_data_backend_starter(backend, method, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield (obj_id, getattr(backend, method)(phenotype_identifier=obj_id, are_ids=True))
    return individual_backend_starter

def make_observable_data_backend_starter(backend, method, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield (obj_id, getattr(backend, method)(observable_identifier=obj_id, are_ids=True))
    return individual_backend_starter

def make_chemical_data_backend_starter(backend, method, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield (obj_id, getattr(backend, method)(chemical_identifier=obj_id, are_ids=True))
    return individual_backend_starter

def make_contig_data_backend_starter(backend, method, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield (obj_id, getattr(backend, method)(contig_identifier=obj_id, are_ids=True))
    return individual_backend_starter

def make_individual_locus_backend_starter(backend, method, class_type, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield {'bioentity_id': obj_id,
                   'class_type': class_type,
                   'json': getattr(backend, method)(locus_identifier=obj_id, are_ids=True)}
    return individual_backend_starter

def make_individual_complex_backend_starter(backend, method, class_type, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield {'bioentity_id': obj_id,
                   'class_type': class_type,
                   'json': getattr(backend, method)(complex_identifier=obj_id, are_ids=True)}
    return individual_backend_starter

def make_individual_phenotype_backend_starter(backend, method, class_type, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield {'bioconcept_id': obj_id,
                   'class_type': class_type,
                   'json': getattr(backend, method)(phenotype_identifier=obj_id, are_ids=True)}
    return individual_backend_starter

def make_individual_observable_backend_starter(backend, method, class_type, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield {'bioconcept_id': obj_id,
                   'class_type': class_type,
                   'json': getattr(backend, method)(observable_identifier=obj_id, are_ids=True)}
    return individual_backend_starter

def make_individual_go_backend_starter(backend, method, class_type, obj_ids):
    def individual_backend_starter():
        for obj_id in obj_ids:
            yield {'bioconcept_id': obj_id,
                   'class_type': class_type,
                   'json': getattr(backend, method)(go_identifier=obj_id, are_ids=True)}
    return individual_backend_starter

def make_fasta_file_starter(filename):
    def fasta_file_starter():
        f = open(filename, 'r')
        on_sequence = False
        current_id = None
        current_sequence = []
        for line in f:
            line = line.replace("\r\n","").replace("\n", "")
            if not on_sequence and line == '##FASTA':
                on_sequence = True
            elif line.startswith('>'):
                if current_id is not None:
                    yield current_id, ''.join(current_sequence)
                current_id = line[1:]
                current_sequence = []
            elif on_sequence:
                current_sequence.append(line)

        if current_id is not None:
            yield current_id, ''.join(current_sequence)
        f.close()
    return fasta_file_starter

# ------------------------------------------ Conversion ------------------------------------------
def do_conversion(starter, converters):
    for element in starter():
        reduce(lambda x, y: y.convert(x), converters, element)

    for converter in converters:
        output = converter.finished()
        if output is not None:
            print output

