'''
Created on Feb 27, 2013

@author: kpaskov
'''

new_evidence = {}
name_allele = {}
new_bioents = {}
new_biocons = {}
new_bioent_biocons = {}
evidence_reference = {}

def phenoevidence_to_bioconcept(p):
    from model_new_schema.evidence import Allele as NewAllele, Phenoevidence as NewPhenoevidence, Chemevidence as NewChemevidence
    from model_new_schema.bioconcept import Chemical as NewChemical, Phenotype as NewPhenotype
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon
    
    new_biocon_ev = new_evidence[p.id]
    
    #Pull information from expt_props
    expt_prop_info = {}
    for prop in p.experiment_properties:
        if prop.type == 'Chemical_pending' or prop.type == 'chebi_ontology':
            expt_prop_info['chemical'] = prop.value
            expt_prop_info['chemical_amt'] = prop.description
        elif prop.type == 'Allele':
            expt_prop_info['allele'] = prop.value
            expt_prop_info['allele_description'] = prop.description
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
            expt_prop_info['condition'] = prop.value
            expt_prop_info['condition_desc'] = prop.description
        elif prop.type == 'Details':
            expt_prop_info['details'] = prop.value
            expt_prop_info['details_desc'] = prop.description
                
    allele_id = None
    allele_name = expt_prop_info['allele']
    if allele_name is not None:
        allele = name_allele[allele_name]
        if allele is None:
            allele = NewAllele(allele_name, expt_prop_info['allele_description'])
        allele_id = allele.id
            
    if new_biocon_ev is None:
        if p.observable == 'resistance to chemicals':
            new_biocon_ev = NewChemevidence(p.experiment_type, evidence_reference[p.id], expt_prop_info['strain'], p.mutant_type, allele_id,
                                            p.source, p.experiment_comment, p.qualifier, 'resistance',
                                            evidence_id=p.id, date_created=p.date_created, created_by=p.created_by)      
        elif p.observable == 'chemical compound accumulation':
            new_biocon_ev = NewChemevidence(p.experiment_type, evidence_reference[p.id], expt_prop_info['strain'], p.mutant_type, allele_id,
                                            p.source, p.experiment_comment, p.qualifier, 'accumulation',
                                            evidence_id=p.id, date_created=p.date_created, created_by=p.created_by)    
        elif p.observable == 'chemical compound excretion':
            new_biocon_ev = NewChemevidence(p.experiment_type, evidence_reference[p.id], expt_prop_info['strain'], p.mutant_type, allele_id,
                                            p.source, p.experiment_comment, p.qualifier, 'excretion',
                                            evidence_id=p.id, date_created=p.date_created, created_by=p.created_by)
    
        ##Should these be biocons or biorels? If biocons, what is the bioconcept? If biorels, should they be associated with the protein or the gene?
#        elif p.observable == 'protein activity':
#            new_biocon_ev = NewModevidence(p.experiment_type, evidence_reference[p.id], expt_prop_info['strain'], p.mutant_type, allele_id,
#                                            p.source, p.experiment_comment, p.qualifier, 'protein activity',
#                                            evidence_id=p.id, date_created=p.date_created, created_by=p.created_by)
#        elif p.observable == 'protein/peptide accumulation':
#            new_biocon_ev = NewModevidence(p.experiment_type, evidence_reference[p.id], expt_prop_info['strain'], p.mutant_type, allele_id,
#                                            p.source, p.experiment_comment, p.qualifier, 'protein accumulation',
#                                            evidence_id=p.id, date_created=p.date_created, created_by=p.created_by)
#        elif p.observable == 'protein/peptide distribution':
#            new_biocon_ev = NewModevidence(p.experiment_type, evidence_reference[p.id], expt_prop_info['strain'], p.mutant_type, allele_id,
#                                            p.source, p.experiment_comment, p.qualifier, 'protein distribution',
#                                            evidence_id=p.id, date_created=p.date_created, created_by=p.created_by)
#        elif p.observable == 'protein/peptide modification':
#            new_biocon_ev = NewModevidence(p.experiment_type, evidence_reference[p.id], expt_prop_info['strain'], p.mutant_type, allele_id,
#                                            p.source, p.experiment_comment, p.qualifier, 'protein modification',
#                                            evidence_id=p.id, date_created=p.date_created, created_by=p.created_by) 
#        elif p.observable == 'RNA accumulation':
#            new_biocon_ev = NewModevidence(p.experiment_type, evidence_reference[p.id], expt_prop_info['strain'], p.mutant_type, allele_id,
#                                            p.source, p.experiment_comment, p.qualifier, 'RNA accumulation',
#                                            evidence_id=p.id, date_created=p.date_created, created_by=p.created_by)      
#        elif p.observable == 'RNA localization':
#            new_biocon_ev = NewModevidence(p.experiment_type, evidence_reference[p.id], expt_prop_info['strain'], p.mutant_type, allele_id,
#                                            p.source, p.experiment_comment, p.qualifier, 'RNA localization',
#                                            evidence_id=p.id, date_created=p.date_created, created_by=p.created_by)   
        elif p.observable != 'protein activity' and p.observable != 'protein/peptide accumulation' and \
                    p.observable != 'protein/peptide distribution' and p.observable != 'protein/peptide modification' and \
                    p.observable != 'RNA accumulation' and p.observable != 'RNA localization':
            new_biocon_ev = NewPhenoevidence(p.experiment_type, evidence_reference[p.id], expt_prop_info['strain'], p.mutant_type, allele_id,
                                            p.source, p.experiment_comment, p.qualifier, 
                                            evidence_id=p.id, date_created=p.date_created, created_by=p.created_by)
             
             expt_prop_info['chemical'] = prop.value
            expt_prop_info['chemical_amt'] = prop.description
        
        elif prop.type == 'Reporter':
            expt_prop_info['reporter'] = prop.value
            expt_prop_info['reporter_desc'] = prop.description
        
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
            expt_prop_info['condition'] = prop.value
            expt_prop_info['condition_desc'] = prop.description
        elif prop.type == 'Details':
            expt_prop_info['details'] = prop.value
            expt_prop_info['details_desc'] = prop.description
            
    if new_biocon_ev is not None:
        new_biocon_ev.chemical = expt_prop_info['chemical']
        new_biocon_ev.chemical_amt = expt_prop_info['chemical_amt']
        new_biocon_ev.reporter_desc = expt_prop_info['reporter_desc']
        new_biocon_ev.budding_index = expt_prop_info['budding_index']
        new_biocon_ev.glutathione_excretion = expt_prop_info['glutathione_excretion']
        new_biocon_ev.z_score = expt_prop_info['z_score']
        new_biocon_ev.relative_fitness_score = expt_prop_info['relative_fitness_score']
        new_biocon_ev.chitin_level = expt_prop_info['chitin_level']
        new_biocon_ev.condition = expt_prop_info['condition']
        new_biocon_ev.condition_desc = expt_prop_info['condition_desc']
        new_biocon_ev.details = expt_prop_info['details']
        new_biocon_ev.details_desc = expt_prop_info['details_desc']
        
        
        bioent = new_bioents[p.feature_id]
        new_biocon = new_biocons[p.id]

        #Find or create bioconcept
        if new_biocon is None:
            if new_biocon_ev.evidence_type == 'CHEMICAL_EVIDENCE':
                new_biocon = NewChemical(expt_prop_info['chemical'], expt_prop_info['chemical_amt'], biocon_id=p.id, date_created=p.date_created, created_by=p.created_by)
            elif new_biocon_ev.evidence_type == 'PHENOTYPE_EVIDENCE':
                new_biocon = NewPhenotype(p.observable, biocon_id=p.id, date_created=p.date_created, created_by=p.created_by)
                
        #Find or create BioentBiocon
        bioent_biocon = new_bioent_biocons[(bioent.id, p.id)]
        if bioent_biocon is None:
            bioent_biocon = NewBioentBiocon(bioent, p.id)
        bioent_biocon.evidences.append(new_biocon_ev)
            
        return bioent_biocon
    else:
        return None
                        