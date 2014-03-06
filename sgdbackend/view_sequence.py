'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentity, Protein
from model_new_schema.evelements import Strain
from mpmath import sqrt, ceil
from sgdbackend import DBSession
from sgdbackend_query import get_sequence_evidence, get_sequence_labels, get_sequence_neighbors, get_contigs, get_contig
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import get_obj
from sgdbackend_utils.obj_to_json import sequence_to_json, minimize_json, \
    evidence_to_json, sequence_label_to_json


'''
-------------------------------Overview---------------------------------------
'''  

def make_overview(bioent_id):
    return []

'''
-------------------------------Contig---------------------------------------
'''
def make_contig(contig_id):
    contig = get_contig(contig_id)
    return sequence_to_json(contig)
    
'''
-------------------------------Details---------------------------------------
'''

def make_details(locus_id=None, contig_id=None):
    seqevidences = get_sequence_evidence(locus_id=locus_id, contig_id=contig_id)

    dna_seqevidences = [x for x in seqevidences if x.class_type == 'GENDNASEQUENCE']
    protein_seqevidences = [x for x in seqevidences if x.class_type == 'PROTEINSEQUENCE']
    coding_seqevidences = [x for x in seqevidences if x.class_type == 'CODDNASEQUENCE']
    
    id_to_labels = {}
    for sequence_label in get_sequence_labels([x.id for x in dna_seqevidences]):
        evidence_id = sequence_label.evidence_id
        if evidence_id in id_to_labels:
            id_to_labels[evidence_id].append(sequence_label)
        else:
            id_to_labels[evidence_id] = [sequence_label]

    id_to_neighbors = {}
    id_to_contig = {}
    if locus_id is not None and contig_id is None:
        for seqevidence in dna_seqevidences:
            id_to_neighbors[seqevidence.id] = [{'start': x.start, 'end': x.end, 'display_name': get_obj(Bioentity, x.bioentity_id)['display_name'], 'strand': x.strand} for x in get_sequence_neighbors(seqevidence)]

        id_to_contig = dict([(x.id, x) for x in get_contigs(dna_seqevidences)])


    tables = {}
    tables['genomic_dna'] = create_simple_table(sorted(dna_seqevidences, key=lambda x: get_obj(Strain, x.strain_id)['display_name'] if get_obj(Strain, x.strain_id)['display_name'] != 'S288C' else 'AAA'), make_dna_evidence_row,
                               id_to_labels=id_to_labels,
                               id_to_neighbors=id_to_neighbors,
                               id_to_contig=id_to_contig)

    protein_ids = [x.id for x in DBSession.query(Protein).filter(Protein.locus_id == locus_id).all()]
    for protein_id in protein_ids:
        protein_seqevidences.extend([x for x in get_sequence_evidence(locus_id=protein_id) if x.class_type == 'PROTEINSEQUENCE'])

    tables['protein'] = create_simple_table(sorted(protein_seqevidences, key=lambda x: get_obj(Strain, x.strain_id)['display_name'] if get_obj(Strain, x.strain_id)['display_name'] != 'S288C' else 'AAA'), make_sequence_evidence_row)
    tables['coding_dna'] = create_simple_table(sorted(coding_seqevidences, key=lambda x: get_obj(Strain, x.strain_id)['display_name'] if get_obj(Strain, x.strain_id)['display_name'] != 'S288C' else 'AAA'), make_sequence_evidence_row)

    return tables

def make_dna_evidence_row(seqevidence, id_to_labels, id_to_neighbors, id_to_contig):
    bioentity_id = seqevidence.bioentity_id

    obj_json = evidence_to_json(seqevidence).copy()
    obj_json['strain']['description'] = get_obj(Strain, seqevidence.strain_id)['description']
    obj_json['strain']['is_alternative_reference'] = get_obj(Strain, seqevidence.strain_id)['is_alternative_reference']
    obj_json['bioentity'] = get_obj(Bioentity, bioentity_id)
    obj_json['sequence'] = sequence_to_json(seqevidence.sequence)
    obj_json['sequence_labels'] = [] if seqevidence.id not in id_to_labels else sorted([sequence_label_to_json(x) for x in id_to_labels[seqevidence.id]], key=lambda x: x['relative_start'])
    obj_json['neighbors'] = [] if seqevidence.id not in id_to_neighbors else id_to_neighbors[seqevidence.id]
    obj_json['start'] = seqevidence.start
    obj_json['end'] = seqevidence.end
    obj_json['strand'] = seqevidence.strand

    if seqevidence.contig_id is not None and seqevidence.contig_id in id_to_contig:
        contig = id_to_contig[seqevidence.contig_id]
        obj_json['contig'] = sequence_to_json(contig)
    return obj_json

def make_sequence_evidence_row(seqevidence):
    bioentity_id = seqevidence.bioentity_id

    obj_json = evidence_to_json(seqevidence).copy()
    obj_json['strain']['description'] = get_obj(Strain, seqevidence.strain_id)['description']
    obj_json['strain']['format_name'] = get_obj(Strain, seqevidence.strain_id)['format_name']
    obj_json['bioentity'] = minimize_json(get_obj(Bioentity, bioentity_id), include_format_name=True)
    obj_json['sequence'] = sequence_to_json(seqevidence.sequence)
    return obj_json