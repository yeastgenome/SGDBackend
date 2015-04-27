from sqlalchemy.orm import joinedload
from src.sgd.model.nex.evidence import DNAsequenceevidence, Proteinsequenceevidence, Bindingevidence, Alignmentevidence
from src.sgd.model.nex.bioitem import Contig
from src.sgd.model.nex.bioentity import Locus
from src.sgd.backend.nex import DBSession, query_limit
from src.sgd.backend import calculate_variant_data
import json

__author__ = 'kpaskov'

# -------------------------------Overview---------------------------------------
def make_overview(locus_id):
    return []

# -------------------------------Contig---------------------------------------
def make_contig(contig_id):
    contig = DBSession.query(Contig).filter(Contig.id == contig_id).first()
    return contig.to_json()
    
# -------------------------------Details---------------------------------------
def get_dnasequence_evidence(locus_id=None, contig_id=None):
    query = DBSession.query(DNAsequenceevidence).options(joinedload('locus'), joinedload('strain'), joinedload('contig'))
    if contig_id is not None:
        query = query.filter_by(contig_id=contig_id)
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)
    if query.count() > query_limit:
        return None

    return query.all()

def get_alignment_evidence(locus_id=None):
    query = DBSession.query(Alignmentevidence).options(joinedload('locus'), joinedload('strain'))
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)
    if query.count() > query_limit:
        return None

    return query.all()

def get_proteinsequence_evidence(locus_id=None):
    query = DBSession.query(Proteinsequenceevidence).options(joinedload('locus'), joinedload('strain'))
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None, contig_id=None):
    if locus_id is None and contig_id is None:
        return {'Error': 'No locus_id or contig_id given.'}

    dnaseqevidences = get_dnasequence_evidence(locus_id=locus_id, contig_id=contig_id)

    if locus_id is not None:
        proteinseqevidences = get_proteinsequence_evidence(locus_id=locus_id)
    else:
        proteinseqevidences = []

    if dnaseqevidences is None or proteinseqevidences is None:
        return {'Error': 'Too much data to display.'}

    genomic_dnaseqevidences = [x for x in dnaseqevidences if x.dna_type == 'GENOMIC']
    coding_dnaseqevidences = [x for x in dnaseqevidences if x.dna_type == 'CODING']
    kb_dnaseqevidences = [x for x in dnaseqevidences if x.dna_type == '1KB']

    tables = {}
    tables['genomic_dna'] = [x.to_json() for x in sorted(genomic_dnaseqevidences, key=lambda x: x.strain.display_name if x.strain.display_name != 'S288C' else '1') if x.locus.bioent_status == 'Active' or x.locus_id == locus_id]
    tables['coding_dna'] = [x.to_json() for x in sorted(coding_dnaseqevidences, key=lambda x: x.strain.display_name if x.strain.display_name != 'S288C' else '1') if x.locus.bioent_status == 'Active' or x.locus_id == locus_id]
    tables['protein'] = [x.to_json() for x in sorted(proteinseqevidences, key=lambda x: x.strain.display_name if x.strain.display_name != 'S288C' else '1') if x.locus.bioent_status == 'Active' or x.locus_id == locus_id]
    tables['1kb'] = [x.to_json() for x in sorted(kb_dnaseqevidences, key=lambda x: x.strain.display_name if x.strain.display_name != 'S288C' else '1') if x.locus.bioent_status == 'Active' or x.locus_id == locus_id]

    return tables

def make_neighbor_details(locus_id=None):
    if locus_id is None:
        return {'Error': 'No locus_id given.'}

    dnaseqevidences = get_dnasequence_evidence(locus_id=locus_id, contig_id=None)

    if dnaseqevidences is None:
        return {'Error': 'Too much data to display.'}

    neighbors = {}
    genomic_dnaseqevidences = [x for x in dnaseqevidences if x.dna_type == 'GENOMIC']
    for evidence in genomic_dnaseqevidences:
        midpoint = int(round((evidence.start + (evidence.end-evidence.start)/2)/1000))*1000
        start = max(1, midpoint - 5000)
        end = min(len(evidence.contig.residues), start + 10000)
        neighbor_evidences = DBSession.query(DNAsequenceevidence).filter_by(dna_type='GENOMIC').filter_by(contig_id=evidence.contig_id).filter(DNAsequenceevidence.end >= start).filter(DNAsequenceevidence.start <= end).options(joinedload('locus'), joinedload('strain')).all()
        neighbors[evidence.strain.format_name] = {'neighbors': [x.to_json() for x in sorted(neighbor_evidences, key=lambda x: x.start if x.strand == '+' else x.end) if x.locus.bioent_status == 'Active' or x.locus_id == locus_id], 'start': start, 'end': end}

    return neighbors

def make_alignment_details(locus_id=None):
    if locus_id is None:
        return {'Error': 'No locus_id given.'}

    evidences = get_alignment_evidence(locus_id=locus_id)

    if evidences is None:
        return {'Error': 'Too much data to display.'}

    return [evidence.to_json() for evidence in evidences]

def switch_to_alignment_coord(ref_align_seq, indices):
    ref_index_to_alignment_index = dict()
    ref_indices = set([x-1 for x in indices])
    ref_coord = 0
    for i, residue in enumerate(ref_align_seq):
        if residue != '-':
            ref_coord += 1

        if ref_coord in ref_indices:
            ref_index_to_alignment_index[ref_coord] = i
    return [ref_index_to_alignment_index[ref_index]+1 for ref_index in ref_indices]


def make_alignment(locus_id=None):
    if locus_id is None:
        return {'Error': 'No locus_id given.'}

    evidences = get_alignment_evidence(locus_id=locus_id)

    if evidences is None:
        return {'Error': 'Too much data to display.'}

    try:
        locus = DBSession.query(Locus).filter_by(id=locus_id).first()
        obj_json = locus.to_min_json()

        dnasequenceevidence = DBSession.query(DNAsequenceevidence).filter_by(strain_id=1).filter_by(dna_type='GENOMIC').filter_by(locus_id=locus_id).first()
        if dnasequenceevidence is not None:
            obj_json['coordinates'] = {
                'start': dnasequenceevidence.start,
                'end': dnasequenceevidence.end,
            }
            obj_json['contig'] = dnasequenceevidence.contig.to_min_json()
            obj_json['strand'] = dnasequenceevidence.strand
            obj_json['introns'] = []
            obj_json['dna_length'] = len(dnasequenceevidence.residues)

        proteinsequenceevidence = DBSession.query(Proteinsequenceevidence).filter_by(strain_id=1).filter_by(locus_id=locus_id).first()
        if proteinsequenceevidence is not None:
            obj_json['protein_length'] = len(proteinsequenceevidence.residues)

        #Alignment data
        alignment_evidences = get_alignment_evidence(locus_id=locus_id)
        if evidences is None:
            return {'Error': 'Too much data to display.'}

        ordered_strains = ['S288C', 'X2180-1A', 'SEY6210', 'W303', 'JK9-3d', 'FL100', 'CEN.PK', 'D273-10B', 'Sigma1278b', 'RM11-1a', 'SK1', 'Y55']
        alignment_evidences.sort(key=lambda x: float('infinity') if x.strain.display_name not in ordered_strains else ordered_strains.index(x.strain.display_name))


        reference_aligment = [x for x in alignment_evidences if x.sequence_type == 'Genomic DNA' and x.strain_id == 1][0]
        if dnasequenceevidence is not None:
            for tag in dnasequenceevidence.tags:
                if tag.class_type == 'INTRON':
                    coords = switch_to_alignment_coord(reference_aligment.residues_with_gaps, [tag.relative_start, tag.relative_end])
                    obj_json['introns'].append({'start': coords[0], 'end': coords[1]})

        obj_json['aligned_dna_sequences'] = [{'strain_id': x.strain_id,
                                              'strain_display_name': x.strain.display_name,
                                              'strain_link': x.strain.link,
                                              'sequence': x.residues_with_gaps} for x in alignment_evidences if x.sequence_type == 'Genomic DNA']

        obj_json['aligned_protein_sequences'] = [{'strain_id': x.strain_id,
                                              'strain_display_name': x.strain.display_name,
                                              'strain_link': x.strain.link,
                                              'sequence': x.residues_with_gaps} for x in alignment_evidences if x.sequence_type == 'Protein']

        obj_json['variant_data_dna'] = calculate_variant_data('DNA', obj_json['aligned_dna_sequences'], obj_json['introns'])

        obj_json['variant_data_protein'] = calculate_variant_data('Protein', obj_json['aligned_protein_sequences'], obj_json['introns'])

    except:
        print locus_id
    return obj_json

# -------------------------------Details---------------------------------------
def get_binding_evidence(locus_id):
    query = DBSession.query(Bindingevidence)
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_binding_details(locus_id=None):
    if locus_id is None:
        return {'Error': 'No locus_id given.'}

    binding_site_evidences = get_binding_evidence(locus_id=locus_id)

    if binding_site_evidences is None:
        return {'Error': 'Too much data to display.'}

    return '[' + ', '.join([x.json for x in binding_site_evidences if x.json is not None]) + ']'
