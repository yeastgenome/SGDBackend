import logging
import sys

from mpmath import ceil
from sqlalchemy.orm import joinedload

from src.sgd.convert import OutputCreator, create_format_name, create_or_update, break_up_file
from src.sgd.convert.transformers import TransformerInterface, make_db_starter


__author__ = 'kpaskov'

# --------------------- Convert Evidence ---------------------
go_fixes = {'GO:0007243': 'GO:0035556'}

# --------------------- Convert Interaction Evidence ---------------------
def make_go_evidence_starter(bud_session):
    from src.sgd.model.bud.interaction import Interaction as OldInteraction
    return make_db_starter(bud_session.query(OldInteraction).filter_by(interaction_type=interaction_type), 1000)

class BudObj2InteractionEvidenceObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Experiment, Source
        from src.sgd.model.nex.reference import Reference
        from src.sgd.model.nex.bioentity import Locus
        from src.sgd.model.nex.bioconcept import Phenotype

        #Grab cached dictionaries
        self.key_to_experiment = dict([(x.unique_key(), x) for x in self.session.query(Experiment).all()])
        self.key_to_phenotype = dict([(x.unique_key(), x) for x in self.session.query(Phenotype).all()])
        self.id_to_bioents = dict([(x.id, x) for x in self.session.query(Locus).all()])
        self.id_to_reference = dict([(x.id, x) for x in self.session.query(Reference).all()])
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.nex.evidence import Geninteractionevidence, Physinteractionevidence
        from src.sgd.model.nex.bioconcept import create_phenotype_format_name
        reference_ids = bud_obj.reference_ids
        if len(reference_ids) != 1:
            print 'Too many references'
            return None
        reference_id = reference_ids[0]
        reference = None if reference_id not in self.id_to_reference else self.id_to_reference[reference_id]

        note = bud_obj.interaction_references[0].note

        if bud_obj.interaction_features[0].feature_id < bud_obj.interaction_features[1].feature_id:
            bioent1_id = bud_obj.interaction_features[0].feature_id
            bioent2_id = bud_obj.interaction_features[1].feature_id
            bait_hit = bud_obj.interaction_features[0].action + '-' + bud_obj.interaction_features[1].action
        else:
            bioent1_id = bud_obj.interaction_features[1].feature_id
            bioent2_id = bud_obj.interaction_features[0].feature_id
            bait_hit = bud_obj.interaction_features[1].action + '-' + bud_obj.interaction_features[0].action

        bioentity1 = None if bioent1_id not in self.id_to_bioents else self.id_to_bioents[bioent1_id]
        bioentity2 = None if bioent2_id not in self.id_to_bioents else self.id_to_bioents[bioent2_id]

        experiment_key = create_format_name(bud_obj.experiment_type)
        experiment = None if experiment_key not in self.key_to_experiment else self.key_to_experiment[experiment_key]

        source_key = bud_obj.source
        source = None if source_key not in self.key_to_source else self.key_to_source[source_key]

        if bud_obj.interaction_type == 'genetic interactions':
            mutant_type = None
            phenotype = None
            phenotypes = bud_obj.interaction_phenotypes
            if len(phenotypes) == 1:
                phenotype_key = (create_phenotype_format_name(phenotypes[0].observable, phenotypes[0].qualifier), 'PHENOTYPE')
                if phenotype_key in self.key_to_phenotype:
                    phenotype = None if phenotype_key is None else self.key_to_phenotype[phenotype_key]
                    mutant_type = phenotypes[0].mutant_type
                else:
                    print 'Phenotype not found: ' + str(phenotype_key)
            elif len(phenotypes) > 1:
                print 'Too many phenotypes'

            return Geninteractionevidence(source, reference, experiment,
                                                                bioentity1, bioentity2, phenotype, mutant_type,
                                                                bud_obj.annotation_type, bait_hit, note,
                                                                bud_obj.date_created, bud_obj.created_by)
        elif bud_obj.interaction_type == 'physical interactions':
            return Physinteractionevidence(source, reference, experiment,
                                                                bioentity1, bioentity2,
                                                                bud_obj.modification, bud_obj.annotation_type, bait_hit, note,
                                                                bud_obj.date_created, bud_obj.created_by)
        return None

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None

def create_evidence(old_go_feature, gofeat_id_to_gorefs, goref_id_to_dbxrefs, id_to_bioentity, sgdid_to_bioentity, id_to_reference, key_to_source, 
                    key_to_bioconcept, key_to_bioitem, key_to_gpad_info):
    from src.sgd.model.nex.evidence import Goevidence as NewGoevidence, Bioconceptcondition, Bioentitycondition, Bioitemcondition
    evidences = []

    go_id = 'GO:' + str(old_go_feature.go.go_go_id).zfill(7)
    if go_id in go_fixes:
        go_id = go_fixes[go_id]
    go_key = (go_id, 'GO')
    go = None if go_key not in key_to_bioconcept else key_to_bioconcept[go_key]

    if go is None:
        print 'Go term not found: ' + str(go_key)
        return None
        
    bioent_id = old_go_feature.feature_id
    bioent = None if bioent_id not in id_to_bioentity else id_to_bioentity[bioent_id]
    if bioent is None:
        print 'Bioentity not found: ' + str(bioent_id)
        return None
        
    source = key_to_source[old_go_feature.source]
            
    old_go_refs = [] if old_go_feature.id not in gofeat_id_to_gorefs else gofeat_id_to_gorefs[old_go_feature.id]
    for old_go_ref in old_go_refs:        
        reference_id = old_go_ref.reference_id
        reference = None if reference_id not in id_to_reference else id_to_reference[reference_id]
    
        qualifier = None
        if old_go_ref.go_qualifier is not None:
            qualifier = old_go_ref.qualifier.replace('_', ' ')
        else:
            aspect = go.go_aspect
            if aspect == 'biological process':
                qualifier = 'involved in'
            elif aspect == 'molecular function':
                qualifier = 'enables'
            elif aspect == 'cellular component':
                qualifier = 'part of'
        conditions = []
            
        old_dbxrefs = [] if old_go_ref.id not in goref_id_to_dbxrefs else goref_id_to_dbxrefs[old_go_ref.id]
        for dbxrefref in old_dbxrefs:
            dbxref = dbxrefref.dbxref
            dbxref_type = dbxref.dbxref_type
            if dbxref_type == 'GOID':
                go_key = ('GO:' + str(int(dbxref.dbxref_id)).zfill(7), 'GO')
                cond_go = None if go_key not in key_to_bioconcept else key_to_bioconcept[go_key]
                if cond_go is not None:
                    conditions.append(Bioconceptcondition(None, dbxrefref.support_type, cond_go))
                else:
                    print 'Could not find bioconcept: ' + str(go_key)
            elif dbxref_type == 'EC number':
                ec_key = (dbxref.dbxref_id, 'EC_NUMBER')
                ec = None if ec_key not in key_to_bioconcept else key_to_bioconcept[ec_key]
                if ec is not None:
                    conditions.append(Bioconceptcondition(None, dbxrefref.support_type, ec))
                else:
                    print 'Could not find bioconcept: ' + str(ec_key)
                
            elif dbxref_type == 'DBID Primary':
                sgdid = dbxref.dbxref_id
                cond_bioent = None if sgdid not in sgdid_to_bioentity else sgdid_to_bioentity[sgdid]
                if cond_bioent is not None:
                    conditions.append(Bioentitycondition(None, dbxrefref.support_type, cond_bioent))
                else:
                    print 'Could not find bioentity: ' + str(sgdid)
            elif dbxref_type == 'PANTHER' or dbxref_type == 'Prosite':
                domain_key = (dbxref.dbxref_id, 'DOMAIN')
                cond_domain = None if domain_key not in key_to_bioitem else key_to_bioitem[domain_key]
                if cond_domain is not None:
                    conditions.append(Bioitemcondition(None, dbxrefref.support_type, cond_domain))
                else:
                    print 'Could not find bioconcept: ' + str(go_key)
            else:
                bioitem_key = (dbxref.dbxref_id, 'ORPHAN')
                bioitem = None if bioitem_key not in key_to_bioitem else key_to_bioitem[bioitem_key]
                if bioitem is not None:
                    conditions.append(Bioitemcondition(None, dbxrefref.support_type, bioitem))
                else:
                    print 'Could not find bioitem: ' + str(bioitem_key)
                            
        test_evidence = NewGoevidence(source, reference, None, bioent, go,
                                old_go_feature.go_evidence, old_go_feature.annotation_type, qualifier, [],
                                old_go_ref.date_created, old_go_ref.created_by)
        experiment_id = None
        if test_evidence.unique_key() in key_to_gpad_info:
            info = key_to_gpad_info[test_evidence.unique_key()]
            experiment_id = info[0]
            conditions.extend(info[1])

        new_evidence = NewGoevidence(source, reference, None, bioent, go,
                                old_go_feature.go_evidence, old_go_feature.annotation_type, qualifier, conditions,
                                old_go_ref.date_created, old_go_ref.created_by)
        new_evidence.experiment_id = experiment_id

        evidences.append(new_evidence)
    return evidences

def create_evidence_from_gpad(gpad, uniprot_id_to_bioentity, pubmed_id_to_reference, key_to_source, eco_id_to_experiment, key_to_bioconcept,
                              chebi_id_to_chemical, sgdid_to_bioentity):
    from src.sgd.model.nex.evidence import Goevidence as NewGoevidence, Bioconceptcondition, Bioentitycondition, Chemicalcondition

    if len(gpad) == 1:
        return None
    #db = gpad[0]
    db_object_id = gpad[1]
    qualifier = gpad[2].replace('_', ' ')
    go_id = 'GO:' + str(int(gpad[3][3:])).zfill(7)
    pubmed_id = gpad[4]
    eco_evidence_id = gpad[5]
    #with_field = gpad[6]
    #interacting_taxon_id = gpad[7]
    #date = gpad[8]
    assigned_by = gpad[9]
    annotation_extension = gpad[10].strip()
    annotation_properties = gpad[11].split('|')

    if assigned_by != 'SGD':
        return None

    if go_id in go_fixes:
        go_id = go_fixes[go_id]
    go_key = (go_id, 'GO')
    go = None if go_key not in key_to_bioconcept else key_to_bioconcept[go_key]
    if go is None:
        print 'GO term not found: ' + str(go_key)
        return None

    bioent = None if db_object_id not in uniprot_id_to_bioentity else uniprot_id_to_bioentity[db_object_id]
    if bioent is None:
        print 'Bioentity not found: ' + str(db_object_id)
        return None

    if pubmed_id.startswith('PMID:'):
        reference = None if pubmed_id[5:] not in pubmed_id_to_reference else pubmed_id_to_reference[pubmed_id[5:]]
    else:
        return None
    if reference is None:
        print 'Reference not found: ' + pubmed_id[5:]
        return None

    experiment = None if eco_evidence_id not in eco_id_to_experiment else eco_id_to_experiment[eco_evidence_id]
    if experiment is None:
        print 'Experiment not found: ' + str(eco_evidence_id)

    source = key_to_source[assigned_by]
    date_created = None
    go_evidence = None
    created_by = None
    annotation_type = None
    for annotation_prop in annotation_properties:
        pieces = annotation_prop.split('=')
        if pieces[0] == 'go_evidence':
            go_evidence = pieces[1]
        elif pieces[0] == 'curator_name':
            created_by = pieces[1]

    exts = set()
    for x in annotation_extension.split(','):
        for y in x.split('|'):
            if '(' in y:
                exts.add(y)
    conditions = []
    for annotation_ext in exts:
        pieces = annotation_ext.split('(')
        role = pieces[0].replace('_', ' ')
        value = pieces[1][:-1]
        if value.startswith('GO:'):
            go_key = ('GO:' + str(int(value[3:])).zfill(7), 'GO')
            cond_go = None if go_key not in key_to_bioconcept else key_to_bioconcept[go_key]
            if cond_go is not None:
                conditions.append(Bioconceptcondition(None, role, cond_go))
            else:
                print 'Could not find bioconcept: ' + str(go_key)


        elif value.startswith('CHEBI:'):
            chebi_id = value
            chemical = None if chebi_id not in chebi_id_to_chemical else chebi_id_to_chemical[chebi_id]
            if chemical is not None:
                conditions.append(Chemicalcondition(None, role, chemical, None))
            else:
                print 'Could not find chemical: ' + str(chebi_id)

        elif value.startswith('SGD:'):
            sgdid = value[4:]
            cond_bioent = None if sgdid not in sgdid_to_bioentity else sgdid_to_bioentity[sgdid]
            if cond_bioent is not None:
                conditions.append(Bioentitycondition(None, role, cond_bioent))
            else:
                print 'Could not find bioentity: ' + str(sgdid)

        elif value.startswith('UniProtKB:'):
            uniprotid = value[10:]
            cond_bioent = None if uniprotid not in uniprot_id_to_bioentity else uniprot_id_to_bioentity[uniprotid]
            if cond_bioent is not None:
                conditions.append(Bioentitycondition(None, role, cond_bioent))
            else:
                print 'Could not find bioentity: ' + str(uniprotid)

        else:
            print 'Annotation not handled: ' + str((role, value))

    new_evidence = NewGoevidence(source, reference, experiment, bioent, go,
                                go_evidence, annotation_type, qualifier, [],
                                date_created, created_by)
    return new_evidence.unique_key(), (new_evidence.experiment_id, conditions)

def convert_evidence(old_session_maker, new_session_maker, chunk_size):
    from src.sgd.model.nex.evidence import Condition, Goevidence as NewGoevidence
    from src.sgd.model.nex.misc import Source as NewSource, Experiment as NewExperiment
    from src.sgd.model.nex.reference import Reference as NewReference
    from src.sgd.model.nex.bioentity import Bioentity as NewBioentity
    from src.sgd.model.nex.bioconcept import Bioconcept as NewBioconcept
    from src.sgd.model.nex.bioitem import Bioitem as NewBioitem, Chemical as NewChemical
    from src.sgd.model.bud.go import GoFeature as OldGoFeature, GoRef as OldGoRef, GorefDbxref as OldGorefDbxref

    new_session = None
    old_session = None
    log = logging.getLogger('convert.go.evidence')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()      
                  
        #Values to check
        values_to_check = ['experiment_id', 'reference_id', 'strain_id', 'source_id',
                       'go_evidence', 'annotation_type', 'qualifier',
                       'bioentity_id', 'bioconcept_id', 'conditions_key']
        
        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        key_to_bioconcept = dict([(x.unique_key(), x) for x in new_session.query(NewBioconcept).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        key_to_bioitem = dict([(x.unique_key(), x) for x in new_session.query(NewBioitem).all()])
        sgdid_to_bioentity = dict([(x.sgdid, x) for x in id_to_bioentity.values()])
        chebi_id_to_chemical = dict([(x.chebi_id, x) for x in new_session.query(NewChemical).all()])

        uniprot_id_to_bioentity = dict([(x.uniprotid, x) for x in new_session.query(NewBioentity).all()])
        pubmed_id_to_reference = dict([(str(x.pubmed_id), x) for x in new_session.query(NewReference).all()])
        eco_id_to_experiment = dict([(x.eco_id, x) for x in new_session.query(NewExperiment).all()])
        
        gofeat_id_to_gorefs = dict()
        goref_id_to_dbxrefs = dict()
        old_gorefs = old_session.query(OldGoRef).options(joinedload('go_qualifier')).all()
        for old_goref in old_gorefs:
            if old_goref.go_annotation_id in gofeat_id_to_gorefs:
                gofeat_id_to_gorefs[old_goref.go_annotation_id].append(old_goref)
            else:
                gofeat_id_to_gorefs[old_goref.go_annotation_id] = [old_goref]

        old_gorefdbxrefs = old_session.query(OldGorefDbxref).options(joinedload('dbxref')).all()
        for old_gorefdbxref in old_gorefdbxrefs:
            if old_gorefdbxref.goref_id in goref_id_to_dbxrefs:
                goref_id_to_dbxrefs[old_gorefdbxref.goref_id].append(old_gorefdbxref)
            else:
                goref_id_to_dbxrefs[old_gorefdbxref.goref_id] = [old_gorefdbxref]
            
        key_to_gpad_info = {}    
        for x in break_up_file('src/sgd/convert/data/gp_association.559292_sgd'):
            new_data = create_evidence_from_gpad(x, uniprot_id_to_bioentity, pubmed_id_to_reference, key_to_source, eco_id_to_experiment, key_to_bioconcept, 
                              chebi_id_to_chemical, sgdid_to_bioentity)
            if new_data is not None:
                key, info = new_data
                key_to_gpad_info[key] = info
                
        min_bioent_id = 0
        max_bioent_id = 10000
        num_chunks = ceil(1.0*(max_bioent_id-min_bioent_id)/chunk_size)
        for i in range(0, num_chunks):
            min_id = min_bioent_id + i*chunk_size
            max_id = min_bioent_id + (i+1)*chunk_size
            
            #Grab all current objects and old objects
            if i < num_chunks-1:
                current_objs = new_session.query(NewGoevidence).filter(NewGoevidence.bioentity_id >= min_id).filter(NewGoevidence.bioentity_id < max_id).all()

                old_objs = old_session.query(OldGoFeature).filter(
                                OldGoFeature.feature_id >= min_id).filter(
                                OldGoFeature.feature_id < max_id).all()
                                    
            else:
                current_objs = new_session.query(NewGoevidence).filter(NewGoevidence.bioentity_id >= min_id).all()

                old_objs = old_session.query(OldGoFeature).filter(OldGoFeature.feature_id >= min_id).all()

            evidence_ids = [x.id for x in current_objs]
            condition_num_chunks = ceil(1.0*len(evidence_ids)/500)
            condition_current_objs = []
            for j in range(0, condition_num_chunks):
                condition_current_objs.extend(new_session.query(Condition).filter(Condition.evidence_id.in_(evidence_ids[j*500:(j+1)*500])).all())

            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
            
            untouched_obj_ids = set(id_to_current_obj.keys())

            already_seen_obj = set()

            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_evidence(old_obj, gofeat_id_to_gorefs, goref_id_to_dbxrefs,
                                                     id_to_bioentity, sgdid_to_bioentity, id_to_reference, key_to_source, key_to_bioconcept, key_to_bioitem,
                                                     key_to_gpad_info)
                    
                #Edit or add new objects
                if newly_created_objs is not None:
                    for newly_created_obj in newly_created_objs:
                        obj_key = newly_created_obj.unique_key()
                        if obj_key not in already_seen_obj:
                            obj_id = newly_created_obj.id
                            current_obj_by_id = None if obj_id not in id_to_current_obj else id_to_current_obj[obj_id]
                            current_obj_by_key = None if obj_key not in key_to_current_obj else key_to_current_obj[obj_key]
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                            if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_id.id)
                            if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_key.id)
                            already_seen_obj.add(obj_key)
                        else:
                            print 'Duplicate evidence: ' + str(obj_key)
                            
            #Delete untouched objs
            for untouched_obj_id  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj_id])
                output_creator.removed()
    
            #Commit
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()

# --------------------- Convert Paragraph ---------------------
def create_paragraph(gofeature, key_to_bioentity, key_to_source):
    from src.sgd.model.nex.paragraph import Paragraph

    format_name = create_format_name(gofeature.feature.name)
    bioentity_key = (format_name, 'LOCUS')

    bioentity = None if bioentity_key not in key_to_bioentity else key_to_bioentity[bioentity_key]
    source = key_to_source[gofeature.source]
    date_last_reviewed = gofeature.date_last_reviewed

    if bioentity is not None and source is not None:
        paragraph = Paragraph('GO', source, bioentity, str(date_last_reviewed), gofeature.date_created, gofeature.created_by)
        return [paragraph]
    else:
        return []

def convert_paragraph(old_session_maker, new_session_maker):
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.paragraph import Paragraph
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.go import GoFeature as OldGoFeature

    new_session = None
    old_session = None
    log = logging.getLogger('convert.go.paragraph')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()
        old_session = old_session_maker()

        #Values to check
        values_to_check = ['text', 'source_id', 'date_created', 'created_by', 'display_name']

        #Grab cached dictionaries
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])

        #Grab all current objects
        current_objs = new_session.query(Paragraph).filter(Paragraph.class_type == 'GO').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())

        already_seen = set()

        old_objs = old_session.query(OldGoFeature).all()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_paragraph(old_obj, key_to_bioentity, key_to_source)

            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    if unique_key not in already_seen:
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                        already_seen.add(unique_key)

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

# ---------------------Convert------------------------------
def convert(old_session_maker, new_session_maker):
    convert_evidence(old_session_maker, new_session_maker, 100)

    #convert_paragraph(old_session_maker, new_session_maker)
    
    #from src.sgd.model.nex.bioconcept import Go
    #from src.sgd.model.nex.evidence import Goevidence
    #get_bioent_ids_f = lambda x: [x.bioentity_id]
    #convert_bioentity_reference(new_session_maker, Goevidence, 'GO', 'convert.go.bioentity_reference', 10000, get_bioent_ids_f)

    #convert_biofact(new_session_maker, Goevidence, Go, 'GO', 'convert.go.biofact', 10000)