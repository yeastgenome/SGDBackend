'''
Created on Feb 4, 2013

@author: kpaskov
'''
from decimal import Decimal
from schema_conversion import cache, create_or_update_and_remove
from schema_conversion.output_manager import OutputCreator
from sqlalchemy.orm import joinedload

id_to_bioent = {}
dbxref_id_to_bioent = {}


"""
---------------------Create------------------------------
"""

def create_transcript_id(gene_id):
    return gene_id + 50000

def create_protein_id(gene_id):
    return gene_id + 100000

def create_gene(old_feature):
    from model_new_schema.bioentity import Gene as NewGene
    
    secondary_name = old_feature.gene_name
    if secondary_name is None:
        secondary_name = old_feature.name
    
    qualifier = None
    attribute = None
    short_description = None
    headline = None
    description = None
    genetic_position = None
    
    ann = old_feature.annotation
    if ann is not None:
        qualifier = ann.qualifier
        attribute = ann.attribute
        short_description = ann.name_description
        headline = ann.headline
        description = ann.description
        genetic_position = ann.genetic_position
        
    bioent_type = create_gene_type(old_feature.type)
    if bioent_type is not None:
        bioent = NewGene(old_feature.name, bioent_type, old_feature.dbxref_id, 
                          old_feature.source, old_feature.status, secondary_name, 
                          qualifier, attribute, short_description, headline, description, genetic_position,
                          bioent_id=old_feature.id, date_created=old_feature.date_created, created_by=old_feature.created_by)
        return bioent 
    return None


real_bioent_types = set(['ARS', 'CENTROMERE', 'GENE_CASSETTE', 'LONG_TERMINAL_REPEAT', 'MATING_LOCUS', 
                         'MULTIGENE_LOCUS', 'NCRNA', 'NOT_IN_SYSTEMATIC_SEQUENCE_OF_S288C', 'NOT_PHYSICALLY_MAPPED',
                         'ORF', 'PSEUDOGENE', 'RETROTRANSPOSON', 'RRNA', 'SNORNA', 'SNRNA', 'TELOMERE', 'TELOMERIC_REPEAT',
                         'TRANSPOSABLE_ELEMENT_GENE', 'TRNA', 'X_ELEMENT_COMBINATORIAL_REPEATS', 'X_ELEMENT_CORE_SEQUENCE',
                         "Y'_ELEMENT"])
def create_gene_type(old_feature_type):
    bioent_type = old_feature_type.upper()
    bioent_type = bioent_type.replace (" ", "_")
    if bioent_type in real_bioent_types:
        return bioent_type
    else:
        return None
    
def create_protein(old_protein_info):
    from model_new_schema.bioentity import Protein as NewProtein
    
    transcript_id = create_transcript_id(old_protein_info.feature_id)
    protein_id = create_protein_id(old_protein_info.feature_id)
    name = old_protein_info.feature.name + 'p'
    secondary_name = old_protein_info.feature.gene_name
    if secondary_name is None:
        secondary_name = name
    else:
        secondary_name = secondary_name + 'p'
    
    aliphatic_index = None
    atomic_comp_H = None
    atomic_comp_S = None
    atomic_comp_N = None
    atomic_comp_O = None
    atomic_comp_C = None
    half_life_yeast_in_vivo = None
    half_life_ecoli_in_vivo = None
    half_life_mammalian_reticulocytes_in_vitro = None
    extinction_coeff_no_cys_residues_as_half_cystines = None
    extinction_coeff_all_cys_residues_reduced = None
    extinction_coeff_all_cys_residues_appear_as_half_cystines = None
    extinction_coeff_all_cys_pairs_form_cystines = None
    instability_index = None
    molecules_per_cell = None
    
    for detail in old_protein_info.details:
        if detail.group == 'Aliphatic index':
            aliphatic_index = Decimal(detail.value)
        elif detail.group == 'Atomic composition':
            if detail.type == 'Hydrogen':
                atomic_comp_H = Decimal(detail.value)
            elif detail.type == 'Sulfur':
                atomic_comp_S = Decimal(detail.value)
            elif detail.type == 'Nitrogen':
                atomic_comp_N = Decimal(detail.value)
            elif detail.type == 'Oxygen':
                atomic_comp_O = Decimal(detail.value)
            elif detail.type == 'Carbon':
                atomic_comp_C = Decimal(detail.value)
        elif detail.group == 'Estimated half-life':
            if detail.type == 'yeast (in vivo)':
                half_life_yeast_in_vivo = detail.value
            elif detail.type == 'Escherichia coli (in vivo)':
                half_life_ecoli_in_vivo = detail.value
            elif detail.type == 'mammalian reticulocytes (in vitro)':
                half_life_mammalian_reticulocytes_in_vitro = detail.value
        elif detail.group == 'Extinction Coefficients at 280 nm':
            if detail.type == 'assuming NO Cys residues appear as half cystines':
                extinction_coeff_no_cys_residues_as_half_cystines = int(detail.value)
            elif detail.type == 'assuming all Cys residues are reduced':
                extinction_coeff_all_cys_residues_reduced = int(detail.value)
            elif detail.type == 'assuming ALL Cys residues appear as half cystines':
                extinction_coeff_all_cys_residues_appear_as_half_cystines = int(detail.value)
            elif detail.type == 'assuming all pairs of Cys residues form cystines':
                extinction_coeff_all_cys_pairs_form_cystines = int(detail.value)
        elif detail.group == 'Instability index':
            instability_index = Decimal(detail.value)
        elif detail.group == 'molecules/cell':
            molecules_per_cell = int(detail.value)
    
    protein = NewProtein(name, secondary_name, transcript_id, old_protein_info.molecular_weight, old_protein_info.pi, old_protein_info.cai, 
                         old_protein_info.length, old_protein_info.n_term_seq, old_protein_info.c_term_seq, old_protein_info.codon_bias, 
                         old_protein_info.fop_score, old_protein_info.gravy_score, old_protein_info.aromaticity_score, 
                         old_protein_info.ala, old_protein_info.arg, old_protein_info.asn, old_protein_info.asp, old_protein_info.cys, 
                         old_protein_info.gln, old_protein_info.glu, old_protein_info.gly, old_protein_info.his, old_protein_info.ile, 
                         old_protein_info.leu, old_protein_info.lys, old_protein_info.met, old_protein_info.phe, old_protein_info.pro, 
                         old_protein_info.thr, old_protein_info.ser, old_protein_info.trp, old_protein_info.tyr, old_protein_info.val, 
                         aliphatic_index, atomic_comp_H, atomic_comp_S, atomic_comp_N, atomic_comp_O, atomic_comp_C, 
                         half_life_yeast_in_vivo, half_life_ecoli_in_vivo, half_life_mammalian_reticulocytes_in_vitro, 
                         extinction_coeff_no_cys_residues_as_half_cystines, extinction_coeff_all_cys_residues_reduced, extinction_coeff_all_cys_residues_appear_as_half_cystines, extinction_coeff_all_cys_pairs_form_cystines, 
                         instability_index, molecules_per_cell, bioent_id=protein_id, created_by=old_protein_info.created_by, date_created=old_protein_info.date_created)
    return protein
    

"""
---------------------Convert------------------------------
"""  

def convert_feature(old_session, new_session):
    
    from model_new_schema.bioentity import Gene as NewGene
    
    from model_old_schema.feature import Feature as OldFeature
    
    output_creator = OutputCreator('gene')

    #Cache genes
    key_maker = lambda x: x.id
    cache(NewGene, id_to_bioent, key_maker, new_session, output_creator)
    
    #Create new genes if they don't exist, or update the database if they do. 
    #Remove any genes that don't match features.
    old_feats = old_session.query(OldFeature).all()
    output_creator.pulled('feature', len(old_feats))
    
    values_to_check = ['official_name', 'bioent_type', 'dbxref_id', 'source', 'status', 'secondary_name', 'date_created', 'created_by',
                       'qualifier', 'attribute', 'name_description', 'headline', 'description', 'genetic_position', 'gene_type']
    create_or_update_and_remove(old_feats, id_to_bioent, create_gene, key_maker, values_to_check, new_session, output_creator)

def convert_protein(old_session, new_session):
    from model_new_schema.bioentity import Protein as NewProtein
    
    from model_old_schema.sequence import ProteinInfo as OldProteinInfo
    
    output_creator = OutputCreator('protein')
    
    #Cache proteins
    key_maker = lambda x: x.id
    cache(NewProtein, id_to_bioent, key_maker, new_session, output_creator)
    
    #Create new proteins if they don't exist, or update the database if they do.
    #Remove any proteins that don't match a protein_info.
    old_protein_infos = old_session.query(OldProteinInfo).options(joinedload('details'), joinedload('feature')).all()
    output_creator.pulled('protein_info', len(old_protein_infos))
    
    values_to_check = ['official_name', 'bioent_type', 'dbxref_id', 'source', 'status', 'secondary_name', 'date_created', 'created_by',
                       'transcript_id', 'molecular_weight', 'pi', 'cai', 'length', 'n_term_seq', 'c_term_seq', 'codon_bias', 'fop_score', 'gravy_score', 'aromaticity_score',
                       'ala', 'arg', 'asn', 'asp', 'cys', 'gln', 'glu', 'gly', 'his', 'ile', 'leu', 'lys', 'met', 'phe', 'pro', 'thr', 'ser', 'trp', 'tyr', 'val',
                       'aliphatic_index', 'atomic_comp_H', 'atomic_comp_N', 'atomic_comp_O', 'atomic_comp_C', 
                       'half_life_yeast_in_vivo', 'half_life_ecoli_in_vivo', 'half_life_mammalian_reticulocytes_in_vitro', 
                       'extinction_coeff_no_cys_residues_as_half_cystines', 'extinction_coeff_all_cys_residues_reduced', 'extinction_coeff_all_cys_residues_as_half_cystines', 'extinction_coeff_all_cys_pairs_form_cystines',
                       'instability_index', 'molecules_per_cell']
    create_or_update_and_remove(old_protein_infos, id_to_bioent, create_protein, key_maker, values_to_check, new_session, output_creator)




