'''
Created on Feb 27, 2013

@author: kpaskov
'''
import model_new_schema
import model_old_schema

new_evidence = {}
name_allele = {}
name_chemical = {}
new_phenoevidence_chemical = {}

class OutputCreator():
    num_added = 0
    num_changed = 0
    def added(self, message):
        self.num_added = self.num_added+1
        if self.num_added%1000==0:
            print str(self.num_added) + ' ' + message + 's added.'
    
    def changed(self, message):
        self.num_changed = self.num_changed+1
        if self.num_changed%1000==0:
            print str(self.num_changed) + ' ' + message + 's changed.'
    
    def finished(self, message):
        print 'In total ' + str(self.num_added) + ' ' + message + 's added.'
        print 'In total ' + str(self.num_changed) + ' ' + message + 's changed.'
        self.num_added = 0
        self.num_changed = 0
        
    def cached(self, message):
        print 'Cache finished for ' + message + '.'
    
def check_value(new_obj, old_obj, field_name):
    new_obj_value = getattr(new_obj, field_name)
    old_obj_value = getattr(old_obj, field_name)
    if new_obj_value != old_obj_value:
        setattr(new_obj, field_name, old_obj_value)
        return False
    return True

def check_values(new_obj, old_obj, field_names):
    match = True
    for field_name in field_names:
        match = check_value(new_obj, old_obj, field_name) and match
    return match


def update_phenoevidence(p):
    from model_new_schema.evidence import Allele as NewAllele, PhenoevidenceChemical as NewPhenoevidenceChemical
    from model_new_schema.chemical import Chemical as NewChemical
    
    if not p.id in new_evidence:
        return
    
    new_biocon_ev = new_evidence[p.id]

    #Pull information from expt_props
    expt_prop_info = {'chemical':[], 'allele':None, 'allele_desc':None, 'reporter':None, 'reporter_desc':None, 'strain':None, 'strain_details':None,
                      'budding_index':None, 'glutathione_excretion':None, 'z_score':None, 'relative_fitness_score':None, 'chitin_level':None, 
                      'condition':[], 'details':[]}
    if p.experiment is not None:
        for prop in p.experiment_properties:
            if prop.type == 'Chemical_pending' or prop.type == 'chebi_ontology':
                expt_prop_info['chemical'].append((prop.value, prop.description))
            elif prop.type == 'Allele':
                expt_prop_info['allele'] = prop.value
                expt_prop_info['allele_desc'] = prop.description
            elif prop.type == 'Reporter':
                expt_prop_info['reporter'] = prop.value
                expt_prop_info['reporter_desc'] = prop.description
            elif prop.type == 'strain_background':
                expt_prop_info['strain'] = prop.value
                expt_prop_info['strain_details'] = prop.description
            elif prop.type == 'Numerical_value' and prop.description == 'relative budding index compared to control':
                expt_prop_info['budding_index'] = prop.value
            elif prop.type == 'Numerical_value' and prop.description == 'Fold elevation of glutathione excretion':
                expt_prop_info['glutathione_excretion'] = prop.value
            elif prop.type == 'Numerical_value' and prop.description == 'Fitness defect score (Z-score)':
                expt_prop_info['z_score'] = prop.value
            elif prop.type == 'Numerical_value' and prop.description == 'Relative fitness score':
                expt_prop_info['relative_fitness_score'] = prop.value
            elif prop.type == 'Numerical_value' and prop.description == 'Chitin level (nmole GlcNAc/mg dry weight)':
                expt_prop_info['chitin_level'] = prop.value
            elif prop.type == 'Condition':
                expt_prop_info['condition'].append((prop.value, prop.description))
            elif prop.type == 'Details':
                expt_prop_info['details'].append((prop.value, prop.description))
                
    allele = None
    allele_name = expt_prop_info['allele']
    if allele_name is not None:
        if allele_name in name_allele:
            allele = name_allele[allele_name]
        else:
            allele = NewAllele(allele_name, expt_prop_info['allele_desc'])
            name_allele[allele_name] = allele
        new_biocon_ev.mutant_allele = allele
            
    for chem_info in expt_prop_info['chemical']:
        chemical_name = chem_info[0]
        chemical_amt = chem_info[1]
        if chemical_name in name_chemical:
            chemical = name_chemical[chemical_name]
        else:
            chemical = NewChemical(chemical_name)
            name_chemical[chemical_name] = chemical
        already_has = False
        for phenoev_chemical in new_biocon_ev.phenoev_chemicals:
            if phenoev_chemical.chemical == chemical:
                already_has = True
        if not already_has:
            new_biocon_ev.phenoev_chemicals.append(NewPhenoevidenceChemical(new_biocon_ev, chemical, chemical_amt))
            

    new_biocon_ev.reporter = expt_prop_info['reporter']
    new_biocon_ev.reporter_desc = expt_prop_info['reporter_desc']
    new_biocon_ev.strain_id = expt_prop_info['strain']
    new_biocon_ev.strain_details = expt_prop_info['strain_details']
    new_biocon_ev.budding_index = expt_prop_info['budding_index']
    new_biocon_ev.glutathione_excretion = expt_prop_info['glutathione_excretion']
    new_biocon_ev.z_score = expt_prop_info['z_score']
    new_biocon_ev.relative_fitness_score = expt_prop_info['relative_fitness_score']
    new_biocon_ev.chitin_level = expt_prop_info['chitin_level']
        
    description_pieces = []
    if p.experiment is not None and p.experiment_comment is not None:
        description_pieces.append('Experiment: ' + p.experiment_comment)
            
    if len(expt_prop_info['condition']) > 0:
        conditions = []
        for (a, b) in expt_prop_info['condition']:
            if b is None:
                conditions.append(a)
            else:
                conditions.append(a + '- ' + b)
        condition_info = ', '.join(conditions)
        description_pieces.append('Condition: ' + condition_info)
            
    if len(expt_prop_info['details']) > 0:
        details = []
        for (a, b) in expt_prop_info['details']:
            if b is None:
                details.append(a)
            else:
                details.append(a + '- ' + b)
        detail_info = ', '.join(details)
        description_pieces.append('Details: ' + detail_info)
            
    new_biocon_ev.description = '; '.join(description_pieces)
    return new_biocon_ev
           
             

"""
---------------------Convert GO------------------------------
"""
def create_go_id(old_go_id):
    return old_go_id+87636

def create_goevidence_id(old_evidence_id):
    return old_evidence_id+1322521  
                 
def create_go(old_go):
    from model_new_schema.bioconcept import Go as NewGo
    new_go = NewGo(old_go.go_go_id, old_go.go_term, old_go.go_aspect, old_go.go_definition, 
                   biocon_id=create_go_id(old_go.id), date_created=old_go.date_created, created_by=old_go.created_by)
    return new_go

def create_go_bioent_biocon(old_go_feature):
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon
    bioent_id = old_go_feature.feature_id
    biocon_id = create_go_id(old_go_feature.go_id)
        
    bioent = id_to_bioent[bioent_id]
    biocon = id_to_biocon[biocon_id]
    return NewBioentBiocon(bioent_id, biocon_id, bioent.official_name + '---' + biocon.official_name, biocon.biocon_type)

def create_goevidence(old_go_feature, go_ref):
    from model_new_schema.evidence import Goevidence as NewGoevidence
    evidence_id = create_goevidence_id(go_ref.id)
    qualifier = None
    if go_ref.go_qualifier is not None:
        qualifier = go_ref.qualifier
    return NewGoevidence(old_go_feature.reference_id, old_go_feature.go_evidence, old_go_feature.annotation_type, old_go_feature.source,
                                qualifier, old_go_feature.date_last_reviewed, 
                                evidence_id=evidence_id, date_created=go_ref.date_created, created_by=go_ref.created_by)

def create_go_bioent_biocon_evidence(old_go_feature, go_ref):
    from model_new_schema.bioconcept import BioentBioconEvidence as NewBioentBioconEvidence
    bioent_id = old_go_feature.feature_id
    biocon_id = create_go_id(old_go_feature.go_id)
    evidence_id = create_goevidence_id(go_ref.id)
    bioent_biocon_id = tuple_to_bioent_biocon[(bioent_id, biocon_id)].id
    return NewBioentBioconEvidence(bioent_biocon_id, evidence_id)


id_to_bioent = {}
id_to_biocon = {}
id_to_evidence = {}
tuple_to_bioent_biocon = {}
tuple_to_bioent_biocon_evidence = {}
 
def cache_bioent(session):
    from model_new_schema.bioentity import Bioentity as NewBioentity
    new_entries = dict([(bioent.id, bioent) for bioent in model_new_schema.model.get(NewBioentity, session=session)])
    id_to_bioent.update(new_entries)

def cache_biocon(session, biocon_type):
    from model_new_schema.bioconcept import Bioconcept as NewBiocon
    if biocon_type is None:
        new_entries = dict([(biocon.id, biocon) for biocon in model_new_schema.model.get(NewBiocon, session=session)])
    else:
        new_entries = dict([(biocon.id, biocon) for biocon in model_new_schema.model.get(NewBiocon, biocon_type=biocon_type, session=session)])
    id_to_biocon.update(new_entries)
    
def cache_bioent_biocon(session, biocon_type):
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon
    key_extractor = lambda x: (x.bioent_id, x.biocon_id)
    if biocon_type is None:
        new_entries = dict([(key_extractor(bioent_biocon), bioent_biocon) for bioent_biocon in model_new_schema.model.get(NewBioentBiocon, session=session)])
    else:
        new_entries = dict([(key_extractor(bioent_biocon), bioent_biocon) for bioent_biocon in model_new_schema.model.get(NewBioentBiocon, biocon_type=biocon_type, session=session)])
    tuple_to_bioent_biocon.update(new_entries)
    
def cache_evidence(session, evidence_type):
    from model_new_schema.evidence import Evidence as NewEvidence
    if evidence_type is None:
        new_entries = dict([(goevidence.id, goevidence) for goevidence in model_new_schema.model.get(NewEvidence, session=session)])
    else:
        new_entries = dict([(goevidence.id, goevidence) for goevidence in model_new_schema.model.get(NewEvidence, evidence_type=evidence_type, session=session)])
    id_to_evidence.update(new_entries)

def cache_bioent_biocon_evidence(session):
    from model_new_schema.bioconcept import BioentBioconEvidence as NewBioentBioconEvidence
    key_extractor = lambda x: (x.bioent_biocon_id, x.evidence_id)
    new_entries = dict([(key_extractor(bb_ev), bb_ev) for bb_ev in model_new_schema.model.get(NewBioentBioconEvidence, session=session)])
    tuple_to_bioent_biocon_evidence.update(new_entries)
   
def check_biocon(new_biocon, current_biocon):
    match = check_values(new_biocon, current_biocon, 
                         ['official_name', 'biocon_type', 'date_created', 'created_by'])
    return match

def check_evidence(new_evidence, current_evidence):
    match = check_values(new_evidence, current_evidence, 
                         ['experiment_type', 'reference_id', 'evidence_type', 'strain_id', 'date_created', 'created_by'])
    return match
        
def add_or_check_go_term(new_go, session, output_creator):
    key = new_go.id
    if key in id_to_biocon:
        current_go = id_to_biocon[key]
        match = check_biocon(new_go, current_go) and check_values(new_go, current_go, 
                         ['go_go_id', 'go_term', 'go_aspect', 'go_definition'])
        if not match:
            output_creator.changed('go_term')
    else:
        model_new_schema.model.add(new_go, session=session)
        id_to_biocon[key] = new_go
        output_creator.added('go_term')
        
def add_or_check_bioent_biocon(new_bioent_biocon, session, output_creator):
    key = (new_bioent_biocon.bioent_id, new_bioent_biocon.biocon_id)
    if key in tuple_to_bioent_biocon:
        current_bioent_biocon = tuple_to_bioent_biocon[key]
        match = check_values(new_bioent_biocon, current_bioent_biocon, 
                         ['id', 'bioent_id', 'biocon_id', 'official_name', 'biocon_type'])
        if not match:
            output_creator.changed('bioent_biocon')
    else:
        model_new_schema.model.add(new_bioent_biocon, session=session)
        tuple_to_bioent_biocon[key] = new_bioent_biocon
        output_creator.added('bioent_biocon')
        
def add_or_check_goevidence(new_goevidence, session, output_creator):
    key = new_goevidence.id
    if key in id_to_evidence:
        current_goevidence = id_to_evidence[key]
        match = check_biocon(new_goevidence, current_goevidence) and check_values(new_goevidence, current_goevidence, 
                         ['go_evidence', 'annotation_type', 'source', 'source', 'qualifier'])
        if not match:
            output_creator.changed('goevidence')
    else:
        model_new_schema.model.add(new_goevidence, session=session)
        id_to_evidence[key] = new_goevidence
        output_creator.added('goevidence')
        
def add_or_check_bioent_biocon_evidence(new_bioent_biocon_evidence, session, output_creator):
    key = (new_bioent_biocon_evidence.bioent_biocon_id, new_bioent_biocon_evidence.evidence_id)
    if key in tuple_to_bioent_biocon_evidence:
        current_bioent_biocon_evidence = tuple_to_bioent_biocon_evidence[key]
        match = check_values(new_bioent_biocon_evidence, current_bioent_biocon_evidence, 
                         ['id', 'bioent_biocon_id', 'evidence_id', 'source', 'qualifier'])
        if not match:
            output_creator.changed('bioent_biocon_evidence')
    else:
        model_new_schema.model.add(new_bioent_biocon_evidence, session=session)
        tuple_to_bioent_biocon[key] = new_bioent_biocon_evidence
        output_creator.added('bioent_biocon_evidence')

def go_to_bioconcept(old_model, session):
    from model_old_schema.go import Go as OldGo, GoFeature as OldGoFeature
    from model_old_schema.config import DBUSER as OLD_DBUSER
    
    output_creator = OutputCreator()

    #Cache bioents
    cache_bioent(session)
    output_creator.cached('bioent')
     
    #Cache go_biocons
    cache_biocon(session, 'GO')
    output_creator.cached('biocon')

    #Create new go_biocons if they don't exist, or update the database if they do.
    gos = old_model.execute(model_old_schema.model.get(OldGo), OLD_DBUSER)
    for old_go in gos:
        new_go = create_go(old_go)
        add_or_check_go_term(new_go, session, output_creator)
    output_creator.finished('go_term')

    #Cache bioent_biocons
    cache_bioent_biocon(session, 'GO')
    output_creator.cached('bioent_biocon')
    
    #Create new bioent_biocons if they don't exist, or update the database if they do.
    old_go_features = old_model.execute(model_old_schema.model.get(OldGoFeature), OLD_DBUSER)
    for old_go_feature in old_go_features:
        new_bioent_biocon = create_go_bioent_biocon(old_go_feature)
        add_or_check_bioent_biocon(new_bioent_biocon, session, output_creator)
    output_creator.finished('bioent_biocon')
    
    #Cache goevidences
    cache_evidence(session, 'GO_EVIDENCE')
    output_creator.cached('goevidence')
    
    #Create new goevidences if they don't exist, or update the database if they do.
    for old_go_feature in old_go_features:
        for go_ref in old_go_feature.go_refs:
            new_goevidence = create_goevidence(old_go_feature, go_ref)
            add_or_check_goevidence(new_goevidence, session, output_creator)
    output_creator.finished('goevidence')
        
    #Cache bioent_biocon_evidences
    cache_bioent_biocon_evidence(session)
    output_creator.cached('bioent_biocon_evidences')
    
    #Create new bioent_biocon_evidences if they don't exist, or update the database if they do.
    for old_go_feature in old_go_features: 
        for go_ref in old_go_feature.go_refs:
            new_bioent_biocon_evidence = create_go_bioent_biocon_evidence(old_go_feature, go_ref)
            add_or_check_bioent_biocon_evidence(new_bioent_biocon_evidence, session, output_creator)
    output_creator.finished('bioent_biocon_evidences')
        
        
        
            
            
            
            
            