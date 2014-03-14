from mpmath import ceil
from sqlalchemy.orm import joinedload

from src.sgd.model.nex.evelements import Strain
from src.sgd.model.nex.evidence import GenomicDNAsequenceevidence, Sequenceevidence, SequenceLabel
from src.sgd.model.nex.bioentity import Protein
from src.sgd.model.nex.sequence import Contig
from src.sgd.backend.nex import DBSession, create_simple_table, get_obj, query_limit
from src.sgd.backend.nex.obj_to_json import sequence_to_json, minimize_json, \
    evidence_to_json, sequence_label_to_json
from src.sgd.model.nex.bioentity import Bioentity


__author__ = 'kpaskov'

# -------------------------------Overview---------------------------------------
def make_overview(locus_id):
    return []

# -------------------------------Contig---------------------------------------
def make_contig(contig_id):
    contig = DBSession.query(Contig).filter(Contig.id == contig_id).first()
    return sequence_to_json(contig)
    
# -------------------------------Details---------------------------------------
def get_sequence_evidence(locus_id=None, contig_id=None):
    query = DBSession.query(Sequenceevidence).options(joinedload('sequence'))
    if contig_id is not None:
        query = DBSession.query(GenomicDNAsequenceevidence).filter(GenomicDNAsequenceevidence.contig_id == contig_id)
    if locus_id is not None:
        query = query.filter(Sequenceevidence.bioentity_id == locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def get_sequence_neighbors(evidence):
    if evidence.contig_id is None:
        return []
    else:
        return DBSession.query(GenomicDNAsequenceevidence).filter(
                                                    GenomicDNAsequenceevidence.contig_id == evidence.contig_id).filter(
                                                    GenomicDNAsequenceevidence.start >= evidence.start - 5000).filter(
                                                    GenomicDNAsequenceevidence.start <= evidence.start + 5000).filter(
                                                    GenomicDNAsequenceevidence.id != evidence.id).all()

def get_sequence_labels(evidence_ids):
    sequence_labels = []
    num_chunks = ceil(1.0*len(evidence_ids)/500)
    for i in range(num_chunks):
        this_chunk = evidence_ids[i*500:(i+1)*500]
        sequence_labels.extend(DBSession.query(SequenceLabel).filter(SequenceLabel.evidence_id.in_(this_chunk)).all())
    return sequence_labels

def make_details(locus_id=None, contig_id=None):
    if locus_id is None and contig_id is None:
        return {'Error': 'No locus_id or contig_id given.'}

    seqevidences = get_sequence_evidence(locus_id=locus_id, contig_id=contig_id)

    if seqevidences is None:
        return {'Error': 'Too much data to display.'}

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

        id_to_contig = dict([(x.id, x) for x in DBSession.query(Contig).filter(Contig.id.in_([x.contig_id for x in dna_seqevidences])).all()])


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