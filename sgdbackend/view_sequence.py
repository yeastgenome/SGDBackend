'''
Created on Mar 15, 2013

@author: kpaskov
'''
from go_enrichment import query_batter
from model_new_schema.bioconcept import Bioconceptrelation
from model_new_schema.evidence import Sequenceevidence
from mpmath import sqrt, ceil
from sgdbackend_query import get_sequence_evidence, get_sequence_labels, get_sequence_neighbors, get_contigs
from sgdbackend_query.query_misc import get_relations
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_biocon, id_to_bioent, id_to_strain
from sgdbackend_utils.obj_to_json import sequence_to_json, minimize_json, \
    evidence_to_json, sequence_label_to_json


'''
-------------------------------Overview---------------------------------------
'''  

def make_overview(bioent_id):
    return []

    
'''
-------------------------------Details---------------------------------------
'''

def make_details(locus_id):
    seqevidences = get_sequence_evidence(locus_id)
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
    obj_json['bioentity'] = minimize_json(id_to_bioent[bioentity_id], include_format_name=True)
    obj_json['sequence'] = sequence_to_json(seqevidence.sequence)
    obj_json['sequence_labels'] = [] if seqevidence.id not in id_to_labels else sorted([sequence_label_to_json(x) for x in id_to_labels[seqevidence.id]], key=lambda x: x['relative_start'])
    obj_json['neighbors'] = [] if seqevidence.id not in id_to_neighbors else id_to_neighbors[seqevidence.id]
    obj_json['start'] = seqevidence.start
    obj_json['end'] = seqevidence.end
    obj_json['strand'] = seqevidence.strand

    if seqevidence.contig_id is not None:
        contig = id_to_contig[seqevidence.contig_id]
        obj_json['contig'] = {'display_name': contig.display_name, 'format_name': contig.format_name}
    return obj_json

'''
-------------------------------Protein Details---------------------------------------
'''

def make_details(locus_id):
    seqevidences = get_sequence_evidence(locus_id)
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
    obj_json['strain']['format_name'] = id_to_strain[seqevidence.strain_id]['format_name']
    obj_json['bioentity'] = minimize_json(id_to_bioent[bioentity_id], include_format_name=True)
    obj_json['sequence'] = sequence_to_json(seqevidence.sequence)
    obj_json['sequence_labels'] = [] if seqevidence.id not in id_to_labels else sorted([sequence_label_to_json(x) for x in id_to_labels[seqevidence.id]], key=lambda x: x['relative_start'])
    obj_json['neighbors'] = [] if seqevidence.id not in id_to_neighbors else id_to_neighbors[seqevidence.id]
    obj_json['start'] = seqevidence.start
    obj_json['end'] = seqevidence.end
    obj_json['strand'] = seqevidence.strand

    if seqevidence.contig_id is not None:
        contig = id_to_contig[seqevidence.contig_id]
        obj_json['contig'] = {'display_name': contig.display_name, 'format_name': contig.format_name}
    return obj_json