'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.evidence import Sequenceevidence, Proteinsequenceevidence
from mpmath import sqrt, ceil
from sgdbackend_query import get_sequence_evidence, get_sequence_labels, get_sequence_neighbors, get_contigs, get_contig
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_bioent, id_to_strain
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
    seqevidences = get_sequence_evidence(Sequenceevidence, locus_id=locus_id, contig_id=contig_id)
    if seqevidences is None:
        return {'Error': 'Too much data to display.'}
    
    id_to_labels = {}
    for sequence_label in get_sequence_labels([x.id for x in seqevidences]):
        evidence_id = sequence_label.evidence_id
        if evidence_id in id_to_labels:
            id_to_labels[evidence_id].append(sequence_label)
        else:
            id_to_labels[evidence_id] = [sequence_label]

    id_to_neighbors = {}
    id_to_contig = {}
    if locus_id is not None and contig_id is None:
        for seqevidence in seqevidences:
            id_to_neighbors[seqevidence.id] = [{'start': x.start, 'end': x.end, 'display_name': id_to_bioent[x.bioentity_id]['display_name'], 'strand': x.strand} for x in get_sequence_neighbors(seqevidence)]

        id_to_contig = dict([(x.id, x) for x in get_contigs(seqevidences)])


    
    return create_simple_table(sorted(seqevidences, key=lambda x: id_to_strain[x.strain_id]['display_name'] if id_to_strain[x.strain_id]['display_name'] != 'S288C' else 'AAA'), make_evidence_row,
                               id_to_labels=id_to_labels,
                               id_to_neighbors=id_to_neighbors,
                               id_to_contig=id_to_contig)

def make_evidence_row(seqevidence, id_to_labels, id_to_neighbors, id_to_contig):
    bioentity_id = seqevidence.bioentity_id

    obj_json = evidence_to_json(seqevidence).copy()
    obj_json['strain']['description'] = id_to_strain[seqevidence.strain_id]['description']
    obj_json['strain']['is_alternative_reference'] = id_to_strain[seqevidence.strain_id]['is_alternative_reference']
    obj_json['bioentity'] = id_to_bioent[bioentity_id]
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

'''
-------------------------------Protein Details---------------------------------------
'''

def make_protein_details(locus_id):
    seqevidences = get_sequence_evidence(Proteinsequenceevidence, locus_id + 200000)
    if seqevidences is None:
        return {'Error': 'Too much data to display.'}

    return create_simple_table(sorted(seqevidences, key=lambda x: id_to_strain[x.strain_id]['display_name'] if id_to_strain[x.strain_id]['display_name'] != 'S288C' else 'AAA'), make_protein_evidence_row)

def make_protein_evidence_row(seqevidence):
    bioentity_id = seqevidence.bioentity_id

    obj_json = evidence_to_json(seqevidence).copy()
    obj_json['strain']['description'] = id_to_strain[seqevidence.strain_id]['description']
    obj_json['strain']['format_name'] = id_to_strain[seqevidence.strain_id]['format_name']
    obj_json['bioentity'] = minimize_json(id_to_bioent[bioentity_id], include_format_name=True)
    obj_json['sequence'] = sequence_to_json(seqevidence.sequence)
    return obj_json