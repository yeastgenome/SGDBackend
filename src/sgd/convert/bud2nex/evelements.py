import logging
import sys

from sqlalchemy.orm import joinedload

from src.sgd.convert import OutputCreator, create_or_update, create_format_name
from src.sgd.convert.transformers import TransformerInterface, make_multi_starter, make_db_starter, make_file_starter, \
    make_obo_file_starter


__author__ = 'kpaskov'

#Recorded times: 
#Maitenance (cherry-vm08): 0:01, 
#First Load (sgd-ng1): :09, :10
#1.23.14 Maitenance (sgd-dev): :06

# --------------------- Convert Experiment ---------------------
def make_experiment_starter(bud_session):
    from src.sgd.model.bud.cv import CVTerm
    return make_multi_starter([make_obo_file_starter('src/sgd/convert/data/eco.obo'),
                               make_db_starter(bud_session.query(CVTerm).filter(CVTerm.cv_no==7), 1000),
                               make_file_starter('src/sgd/convert/data/yeastmine_regulation.tsv', row_f=lambda x: (x[4], x[5], x[12])),
                               make_file_starter('src/sgd/convert/data/yetfasco_data.txt', delimeter=';', row_f=lambda x: (x[9][1:-1], None, 'YeTFaSCo')),
                               make_file_starter('src/sgd/convert/data/phosphosites.txt', delimeter=';', row_f=lambda x: [(y, None, 'PhosphoGRID') for y in ([] if len(x) <= 3 else x[3].split('|'))])])

class BudObj2ExperimentObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Source
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.bud.cv import CVTerm
        from src.sgd.model.nex.misc import Experiment

        if isinstance(bud_obj, CVTerm):
            return Experiment(bud_obj.name, self.key_to_source['SGD'], bud_obj.definition, None,
                                       bud_obj.date_created, bud_obj.created_by)
        elif isinstance(bud_obj, tuple):
            display_name, eco_id, source_key = bud_obj
            if display_name is None:
                display_name = eco_id
            source = None if source_key.strip() not in self.key_to_source else self.key_to_source[source_key.strip()]
            return Experiment(display_name, source, None, eco_id, None, None)
        elif isinstance(bud_obj, dict):
            return Experiment(bud_obj['name'], self.key_to_source['ECO'], None if 'def' not in bud_obj else bud_obj['def'], bud_obj['id'], None, None)

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None

# --------------------- Convert Experiment Alias ---------------------
def create_experiment_alias(old_cv_term, key_to_experiment, key_to_source):
    from src.sgd.model.nex.evelements import Experimentalias as NewExperimentalias

    experiment_key = create_format_name(old_cv_term.name)
    if experiment_key not in key_to_experiment:
        print 'Experiment does not exist.'
        return []
    experiment = key_to_experiment[experiment_key]
    source = key_to_source['SGD']

    new_altids = [NewExperimentalias(dbxref.dbxref_id, source, 'APOID', experiment,
                                   dbxref.date_created, dbxref.created_by)
                  for dbxref in old_cv_term.dbxrefs]
    return new_altids

def convert_experiment_alias(old_session_maker, new_session_maker):
    from src.sgd.model.nex.evelements import Experiment as NewExperiment, Source as NewSource, Experimentalias as NewExperimentalias
    from src.sgd.model.bud.cv import CVTerm as OldCVTerm

    old_session = None
    new_session = None
    log = logging.getLogger('convert.evelements.experiment_alias')
    output_creator = OutputCreator(log)

    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewExperimentalias).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        #Values to check
        values_to_check = ['source_id', 'category']

        untouched_obj_ids = set(id_to_current_obj.keys())

        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(NewExperiment).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])

        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==7).options(
                                                    joinedload('cv_dbxrefs'),
                                                    joinedload('cv_dbxrefs.dbxref')).all()

        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_experiment_alias(old_obj, key_to_experiment, key_to_source)

            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)

        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()

# --------------------- Convert Experiment Relation ---------------------
def create_experiment_relation(old_cv_term, key_to_experiment, key_to_source):
    from src.sgd.model.nex.evelements import Experimentrelation as NewExperimentrelation

    source = key_to_source['SGD']

    child_key = create_format_name(old_cv_term.name)
    if child_key not in key_to_experiment:
        print 'Experiment does not exist.'
        return []
    child = key_to_experiment[child_key]

    new_rels = []
    for parent_rel in old_cv_term.parent_rels:
        parent_key = create_format_name(parent_rel.parent.name)
        if parent_key not in key_to_experiment:
            print 'Experiment does not exist.'
        else:
            parent = key_to_experiment[parent_key]
            new_rels.append(NewExperimentrelation(source, None, parent, child,
                                                 parent_rel.date_created, parent_rel.created_by))

    return new_rels

def convert_experiment_relation(old_session_maker, new_session_maker):
    from src.sgd.model.nex.evelements import Experiment as NewExperiment, Experimentrelation as NewExperimentrelation, Source as NewSource
    from src.sgd.model.bud.cv import CVTerm as OldCVTerm

    old_session = None
    new_session = None
    log = logging.getLogger('convert.evelements.experiment_relation')
    output_creator = OutputCreator(log)

    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewExperimentrelation).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        #Values to check
        values_to_check = []

        untouched_obj_ids = set(id_to_current_obj.keys())

        #Grab cached dictionaries
        key_to_experiment = dict([(x.unique_key(), x) for x in new_session.query(NewExperiment).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])

        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldCVTerm).filter(OldCVTerm.cv_no==7).options(
                                                    joinedload('parent_rels'),
                                                    joinedload('parent_rels.parent')).all()

        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_experiment_relation(old_obj, key_to_experiment, key_to_source)

            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)

        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()

# --------------------- Convert Strain ---------------------
def make_strain_starter(bud_session):
    from src.sgd.model.bud.cv import CVTerm
    return make_multi_starter([make_db_starter(bud_session.query(CVTerm).filter(CVTerm.cv_no==10), 1000),
                               lambda: [
                                   ('AWRI1631', 'Haploid derivative of South African commercial wine strain N96.'),
                                   ('AWRI796', 'South African red wine strain.'),
                                   ('BY4741', 'S288C-derivative laboratory strain.'),
                                   ('BY4742', 'S288C-derivative laboratory strain.'),
                                   ('CBS7960', 'Brazilian bioethanol factory isolate.'),
                                   ('CLIB215', 'New Zealand bakery isolate.'),
                                   ('CLIB324', 'Vietnamese bakery isolate.'),
                                   ('CLIB382', 'Irish beer isolate.'),
                                   ('EC1118', 'Commercial wine strain.'),
                                   ('EC9-8', 'Haploid derivative of Israeli canyon isolate.'),
                                   ('FostersB', 'Commercial ale strain.'),
                                   ('FostersO', 'Commercial ale strain.'),
                                   ('JAY291', 'Haploid derivative of Brazilian industrial bioethanol strain PE-2.'),
                                   ('Kyokai7', 'Japanese sake yeast.'),
                                   ('LalvinQA23', 'Portuguese Vinho Verde white wine strain.'),
                                   ('M22', 'Italian vineyard isolate.'),
                                   ('PW5', 'Nigerian Raphia palm wine isolate.'),
                                   ('T7', 'Missouri oak tree exudate isolate.'),
                                   ('T73', 'Spanish red wine strain.'),
                                   ('UC5', 'Japanese sake yeast.'),
                                   ('VIN13', 'South African white wine strain.'),
                                   ('VL3', 'French white wine strain.'),
                                   ('Y10', 'Philippine coconut isolate.'),
                                   ('YJM269', 'Austrian Blauer Portugieser wine grape isolate.'),
                                   ('YJM789', 'Haploid derivative of opportunistic human pathogen.'),
                                   ('YPS163', 'Pennsylvania woodland isolate.'),
                                   ('ZTW1', 'Chinese corn mash bioethanol isolate.')
                               ]])

class BudObj2StrainObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Source
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.bud.cv import CVTerm
        from src.sgd.model.nex.misc import Strain

        if isinstance(bud_obj, CVTerm):
            return Strain(bud_obj.name, self.key_to_source['SGD'], bud_obj.definition, bud_obj.date_created, bud_obj.created_by)
        elif isinstance(bud_obj, tuple):
            display_name, description = bud_obj
            return Strain(display_name, self.key_to_source['SGD'], description, None, None)

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None

# --------------------- Convert Source ---------------------
def make_source_starter(bud_session):
    from src.sgd.model.bud.cv import Code
    return make_multi_starter([make_db_starter(bud_session.query(Code), 1000),
                               lambda: ['SGD', 'GO', 'PROSITE', 'Gene3D', 'SUPERFAMILY', 'TIGRFAMs', 'Pfam', 'PRINTS',
                                        'PIR superfamily', 'JASPAR', 'SMART', 'PANTHER', 'ProDom', 'DOI',
                                        'PubMedCentral', 'PubMed', '-', 'ECO', 'TMHMM', 'SignalP', 'PhosphoGRID',
                                        'GenBank/EMBL/DDBJ']])

ok_codes = {('ALIAS', 'ALIAS_TYPE'), ('DBXREF', 'SOURCE'), ('EXPERIMENT', 'SOURCE'), ('FEATURE', 'SOURCE'),
                ('GO_ANNOTATION', 'SOURCE'), ('HOMOLOG', 'SOURCE'), ('INTERACTION', 'SOURCE'), ('PHENOTYPE', 'SOURCE'),
                ('REFTYPE', 'SOURCE'), ('REFERENCE', 'SOURCE'), ('URL', 'SOURCE')}

class BudObj2SourceObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

    def convert(self, bud_obj):
        from src.sgd.model.bud.cv import Code
        from src.sgd.model.nex.misc import Source

        if isinstance(bud_obj, Code):
            if (bud_obj.tab_name, bud_obj.col_name) in ok_codes:
                return Source(bud_obj.code_value, bud_obj.description, bud_obj.date_created, bud_obj.created_by)
            else:
                return None
        elif isinstance(bud_obj, basestring):
            return Source(bud_obj, None, None, None)

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None
