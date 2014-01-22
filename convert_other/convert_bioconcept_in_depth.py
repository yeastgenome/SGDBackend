'''
Created on Oct 25, 2013

@author: kpaskov
'''
from sqlalchemy import or_
from convert_other.convert_auxiliary import convert_disambigs, \
    convert_biocon_count, convert_biofact
from convert_utils import create_or_update, create_format_name
from convert_utils.output_manager import OutputCreator
from sqlalchemy.orm import joinedload
import logging
import sys


"""
--------------------- Convert ECNumber Relation ---------------------
"""

def create_ecnumber_relation(ecnumber, key_to_ecnumber, key_to_source):
    from model_new_schema.bioconcept import Bioconceptrelation as NewBioconceptrelation
    
    source = key_to_source['IUBMB']
    
    format_name = ecnumber.format_name
    pieces = format_name.split('.')
    i = 1
    done = False
    while not done:
        if pieces[-i] != '-':
            pieces[-i] = '-'
            done = True
        i = i+1
    parent_format_name = ('.'.join(pieces), 'EC_NUMBER')
    parent = None if parent_format_name not in key_to_ecnumber else key_to_ecnumber[parent_format_name]
    if parent is None:
        print parent_format_name
        return []
    return [NewBioconceptrelation(source, None, parent, ecnumber, 'EC_NUMBER', None, None)]

def convert_ecnumber_relation(new_session_maker):
    from model_new_schema.evelements import Source
    from model_new_schema.bioconcept import Bioconceptrelation, ECNumber
    
    log = logging.getLogger('convert.bioconcept.ecnumber_relations')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(Bioconceptrelation).filter(Bioconceptrelation.bioconrel_class_type == 'EC_NUMBER').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['parent_id', 'child_id']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab cached dictionaries
        key_to_ecnumber = dict([(x.unique_key(), x) for x in new_session.query(ECNumber).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        
        for old_obj in key_to_ecnumber.values():
            #Convert old objects into new ones
            newly_created_objs = create_ecnumber_relation(old_obj, key_to_ecnumber, key_to_source)
                
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
        
    log.info('complete')
    
# --------------------- Convert GO Relation ---------------------

def get_go_format_name(go_id):
    if go_id == 8150:
        return 'biological_process'
    elif go_id == 5575:
        return 'cellular_component'
    elif go_id == 3674:
        return 'molecular_function'
    return 'GO:' + str(go_id)


def create_go_relation(gopath, key_to_go, key_to_source):
    from model_new_schema.bioconcept import Bioconceptrelation as NewBioconceptrelation
    
    source = key_to_source['SGD']
    
    parent_key = (get_go_format_name(gopath.ancestor.go_go_id), 'GO')
    child_key = (get_go_format_name(gopath.child.go_go_id), 'GO')
    
    parent = None
    child = None
    if parent_key in key_to_go:
        parent = key_to_go[parent_key]
    if child_key in key_to_go:
        child = key_to_go[child_key]
    
    if parent is not None and child is not None:
        return [NewBioconceptrelation(source, gopath.relationship_type, parent, child, 'GO', None, None)]
    else:
        return []

def convert_go_relation(old_session_maker, new_session_maker):
    from model_new_schema.evelements import Source
    from model_new_schema.bioconcept import Bioconceptrelation, Go
    from model_old_schema.go import GoPath
    
    log = logging.getLogger('convert.bioconcept.go_relation')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(Bioconceptrelation).filter(Bioconceptrelation.bioconrel_class_type == 'GO').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['parent_id', 'child_id']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab cached dictionaries
        key_to_go = dict([(x.unique_key(), x) for x in new_session.query(Go).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])

        already_seen = set()
        
        old_session = old_session_maker()
        old_objs = old_session.query(GoPath).filter(GoPath.generation == 1).options(joinedload('child'), joinedload('ancestor')).all()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_go_relation(old_obj, key_to_go, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                if newly_created_obj.unique_key() not in already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                    already_seen.add(newly_created_obj.unique_key())
                        
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
        
    log.info('complete')
    
# --------------------- Convert Phenotype Relation ---------------------

def create_phenotype_relation(cvtermrel, key_to_phenotype, key_to_source):
    from model_new_schema.bioconcept import Bioconceptrelation as NewBioconceptrelation
    
    source = key_to_source['SGD']
    
    parent_key = (create_format_name(cvtermrel.parent.name), 'PHENOTYPE')
    child_key = (create_format_name(cvtermrel.child.name), 'PHENOTYPE')
    
    if parent_key == ('observable', 'PHENOTYPE'):
        parent_key = ('ypo', 'PHENOTYPE')
    
    parent = None
    child = None
    if parent_key in key_to_phenotype:
        parent = key_to_phenotype[parent_key]
    if child_key in key_to_phenotype:
        child = key_to_phenotype[child_key]
    
    if parent is not None and child is not None:
        return [NewBioconceptrelation(source, cvtermrel.relationship_type, parent, child, 'PHENOTYPE', cvtermrel.date_created, cvtermrel.created_by)]
    else:
        return []
    
def create_phenotype_relation_from_phenotype(phenotype, key_to_phenotype, key_to_source):
    from model_new_schema.bioconcept import Bioconceptrelation as NewBioconceptrelation
    
    source = key_to_source['SGD']
    
    if phenotype.qualifier is not None:
        parent_key = (create_format_name(phenotype.observable), 'PHENOTYPE')
        if parent_key in key_to_phenotype:
            parent = key_to_phenotype[parent_key]
            return [NewBioconceptrelation(source, 'is a', parent, phenotype, 'PHENOTYPE', None, None)]
    return []

def create_chemical_phenotype_relation(old_phenotype, key_to_phenotype, key_to_source):
    from model_new_schema.bioconcept import Bioconceptrelation as NewBioconceptrelation, create_phenotype_format_name

    new_relations = []
    for phenotype_feature in old_phenotype.phenotype_features:
        if len(phenotype_feature.experiment.chemicals) != 1:
            print 'Chemical problem ' + str(phenotype_feature.experiment.chemicals)

        source = key_to_source['SGD']

        chemical = phenotype_feature.experiment.chemicals[0][0]
        old_observable = old_phenotype.observable
        if old_observable == 'resistance to chemicals':
            new_observable = old_phenotype.observable.replace('chemicals', chemical)
        else:
            new_observable = old_phenotype.observable.replace('chemical compound', chemical)
        qualifier = old_phenotype.qualifier

        grandparent_key = (create_format_name(old_observable), 'PHENOTYPE')
        parent_key = (create_format_name(new_observable), 'PHENOTYPE')
        child_key = (create_phenotype_format_name(new_observable, qualifier), 'PHENOTYPE')

        grandparent = key_to_phenotype[grandparent_key]
        parent = key_to_phenotype[parent_key]
        child = key_to_phenotype[child_key]

        new_relations.append(NewBioconceptrelation(source, 'is a', grandparent, parent, 'PHENOTYPE', parent.date_created, parent.created_by))
        new_relations.append(NewBioconceptrelation(source, 'is a', parent, child, 'PHENOTYPE', child.date_created, child.created_by))
    return new_relations

def convert_phenotype_relation(old_session_maker, new_session_maker):
    from model_new_schema.evelements import Source
    from model_new_schema.bioconcept import Bioconceptrelation, Phenotype
    from model_old_schema.cv import CVTermRel
    from model_old_schema.phenotype import Phenotype as OldPhenotype
    
    log = logging.getLogger('convert.bioconcept.phenotype_relations')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(Bioconceptrelation).filter(Bioconceptrelation.bioconrel_class_type == 'PHENOTYPE').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['parent_id', 'child_id']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab cached dictionaries
        key_to_phenotype = dict([(x.unique_key(), x) for x in new_session.query(Phenotype).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
        
        old_session = old_session_maker()
        old_objs = old_session.query(CVTermRel).options(joinedload('child'), joinedload('parent')).all()
        already_seen = set()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_phenotype_relation(old_obj, key_to_phenotype, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                
                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)
                already_seen.add(newly_created_obj.unique_key())
                    
        for old_obj in key_to_phenotype.values():
            #Convert old objects into new ones
            newly_created_objs = create_phenotype_relation_from_phenotype(old_obj, key_to_phenotype, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                
                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)
                already_seen.add(newly_created_obj.unique_key())

        old_chem_phenotypes = old_session.query(OldPhenotype).filter(or_(OldPhenotype.observable == 'chemical compound accumulation',
                                                                           OldPhenotype.observable == 'chemical compound excretion',
                                                                           OldPhenotype.observable == 'resistance to chemicals')).options(
                                        joinedload('phenotype_features'), joinedload('phenotype_features.experiment'))

        for old_obj in old_chem_phenotypes:
            #Convert old objects into new ones
            newly_created_objs = create_chemical_phenotype_relation(old_obj, key_to_phenotype, key_to_source)

            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                if newly_created_obj.unique_key() not in already_seen:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                    already_seen.add(newly_created_obj.unique_key())

                        
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
        
    log.info('complete')
    
# --------------------- Convert Phenotype Alias ---------------------

def create_phenotype_alias(cvtermsynonym, key_to_phenotype, key_to_source, id_to_cvterm):
    from model_new_schema.bioconcept import Bioconceptalias as NewBioconceptalias
    
    source = key_to_source['SGD']
    
    phenotype_key = (create_format_name(id_to_cvterm[cvtermsynonym.cvterm_id].name), 'PHENOTYPE')
        
    phenotype = None
    if phenotype_key in key_to_phenotype:
        phenotype = key_to_phenotype[phenotype_key]
    
    if phenotype is not None:
        return [NewBioconceptalias(cvtermsynonym.synonym, source, None, phenotype, cvtermsynonym.date_created, cvtermsynonym.created_by)]
    else:
        return []
    
def create_phenotype_alias_from_dbxref(cvterm_dbxref, key_to_phenotype, key_to_source, id_to_cvterm):
    from model_new_schema.bioconcept import Bioconceptalias as NewBioconceptalias
    
    source = key_to_source['SGD']
    
    phenotype_key = (create_format_name(id_to_cvterm[cvterm_dbxref.cvterm_id].name), 'PHENOTYPE')
        
    phenotype = None
    if phenotype_key in key_to_phenotype:
        phenotype = key_to_phenotype[phenotype_key]
    
    if phenotype is not None:
        return [NewBioconceptalias(cvterm_dbxref.dbxref.dbxref_id, source, cvterm_dbxref.dbxref.dbxref_type, phenotype, cvterm_dbxref.dbxref.date_created, cvterm_dbxref.dbxref.created_by)]
    else:
        return []

def convert_phenotype_alias(old_session_maker, new_session_maker):
    from model_new_schema.evelements import Source
    from model_new_schema.bioconcept import Bioconceptalias, Phenotype
    from model_old_schema.cv import CVTermSynonym, CVTermDbxref, CVTerm
    
    log = logging.getLogger('convert.bioconcept.phenotype_alias')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(Bioconceptalias).filter(Bioconceptalias.subclass_type == 'PHENOTYPE').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['category', 'source_id']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab cached dictionaries
        key_to_phenotype = dict([(x.unique_key(), x) for x in new_session.query(Phenotype).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])
 
        old_session = old_session_maker()       
        id_to_cvterm = dict([(x.id, x) for x in old_session.query(CVTerm).filter(CVTerm.cv_no == 6).all()])
        
        old_objs = old_session.query(CVTermSynonym).filter(CVTermSynonym.cvterm_id.in_(id_to_cvterm.keys())).all()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_phenotype_alias(old_obj, key_to_phenotype, key_to_source, id_to_cvterm)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                
                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)
         
        #From cvterm_dbxrefs           
        old_objs = old_session.query(CVTermDbxref).options(joinedload('dbxref')).filter(CVTermDbxref.cvterm_id.in_(id_to_cvterm.keys())).all()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_phenotype_alias_from_dbxref(old_obj, key_to_phenotype, key_to_source, id_to_cvterm)
                
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
        
    log.info('complete')
    
# ---------------------Convert------------------------------

def convert(old_session_maker, new_session_maker):  
    #convert_ecnumber_relation(new_session_maker)
    
    from model_new_schema.bioconcept import Phenotype
    from model_new_schema.evidence import Phenotypeevidence
    convert_phenotype_relation(old_session_maker, new_session_maker)
    #convert_phenotype_alias(old_session_maker, new_session_maker)
    #convert_biofact(new_session_maker, Phenotypeevidence, Phenotype, 'PHENOTYPE', 'convert.phenotype.biofact', 10000)
    convert_biocon_count(new_session_maker, 'PHENOTYPE', 'convert.phenotype.biocon_count')
    convert_disambigs(new_session_maker, Phenotype, ['id', 'format_name'], 'BIOCONCEPT', 'PHENOTYPE', 'convert.phenotype.disambigs', 2000)
 
    #from model_new_schema.bioconcept import Go
    #from model_new_schema.evidence import Goevidence
    #convert_biofact(new_session_maker, Goevidence, Go, 'GO', 'convert.go.biofact', 10000)
    #convert_go_relation(old_session_maker, new_session_maker)
    #convert_biocon_count(new_session_maker, 'GO', 'convert.go.biocon_count')
    #convert_disambigs(new_session_maker, Go, ['id', 'format_name'], 'BIOCONCEPT', 'GO', 'convert.go.disambigs', 2000)
