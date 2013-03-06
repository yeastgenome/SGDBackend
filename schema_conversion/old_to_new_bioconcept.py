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
                        

def convert_go_to_go(old_go):
    from model_new_schema.bioconcept import Go as NewGo
    new_go = NewGo(old_go.go_go_id, old_go.go_term, old_go.go_aspect, old_go.go_definition, 
                   biocon_id=old_go.id+87636, date_created=old_go.date_created, created_by=old_go.created_by)
    return new_go

def go_to_bioconcept(old_model, session):
    from model_old_schema.go import Go as OldGo, GoFeature as OldGoFeature
    from model_old_schema.config import DBUSER as OLD_DBUSER
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon, BioentBioconEvidence as NewBioentBioconEvidence
    from model_new_schema.evidence import Goevidence as NewGoevidence
    from model_new_schema.bioentity import Bioentity as NewBioentity
    gos = old_model.execute(model_old_schema.model.get(OldGo), OLD_DBUSER)
    
    id_to_go = {}
    for old_go in gos:
        new_go = convert_go_to_go(old_go)
        id_to_go[new_go.id] = new_go
    
    id_to_bioent = {}
    bioents = model_new_schema.model.get(NewBioentity, session=session)
    for bioent in bioents:
        id_to_bioent[bioent.id] = bioent

    bioent_biocons = {}
    old_go_features = old_model.execute(model_old_schema.model.get(OldGoFeature), OLD_DBUSER)
    i = 0
    for old_go_feature in old_go_features:
        bioent_id = old_go_feature.feature_id
        biocon_id = old_go_feature.go_id+87636
        bioent = id_to_bioent[bioent_id]
        biocon = id_to_go[biocon_id]
        
        if (bioent_id, biocon_id) in bioent_biocons:
            new_bioent_biocon = bioent_biocons[(bioent_id, biocon_id)]
        else:
            new_bioent_biocon = NewBioentBiocon(bioent, biocon)
            model_new_schema.model.add(new_bioent_biocon, session=session)
            bioent_biocons[(bioent_id, biocon_id)] = new_bioent_biocon
            
        for go_ref in old_go_feature.go_refs:
            qualifier = None
            if go_ref.go_qualifier is not None:
                qualifier = go_ref.qualifier
            new_evidence = NewGoevidence(go_ref.reference_id, old_go_feature.go_evidence, old_go_feature.annotation_type, old_go_feature.source,
                                      qualifier, old_go_feature.date_last_reviewed, 
                                      evidence_id=go_ref.id + 1322521, date_created=go_ref.date_created, created_by=go_ref.created_by)
            bioent_biocon_evidence = NewBioentBioconEvidence(new_bioent_biocon, new_evidence)
            model_new_schema.model.add(bioent_biocon_evidence, session=session)
        
        if i%1000==0:
            print i
        i=i+1
        
        
        
            
            
            
            
            