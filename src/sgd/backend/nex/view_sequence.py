from src.sgd.model.nex.evidence import GenomicDNAsequenceevidence, Sequenceevidence, Bindingevidence
from src.sgd.model.nex.bioentity import Protein
from src.sgd.model.nex.sequence import Contig
from src.sgd.backend.nex import DBSession, query_limit

__author__ = 'kpaskov'

# -------------------------------Overview---------------------------------------
def make_overview(locus_id):
    return []

# -------------------------------Contig---------------------------------------
def make_contig(contig_id):
    contig = DBSession.query(Contig).filter(Contig.id == contig_id).first()
    return contig.to_full_json()
    
# -------------------------------Details---------------------------------------
def get_sequence_evidence(locus_id=None, contig_id=None):
    query = DBSession.query(Sequenceevidence)
    if contig_id is not None:
        query = DBSession.query(GenomicDNAsequenceevidence).filter(GenomicDNAsequenceevidence.contig_id == contig_id)
    if locus_id is not None:
        query = query.filter(Sequenceevidence.bioentity_id == locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None, contig_id=None):
    if locus_id is None and contig_id is None:
        return {'Error': 'No locus_id or contig_id given.'}

    seqevidences = get_sequence_evidence(locus_id=locus_id, contig_id=contig_id)

    if seqevidences is None:
        return {'Error': 'Too much data to display.'}

    dna_seqevidences = [x for x in seqevidences if x.class_type == 'GENDNASEQUENCE']
    protein_seqevidences = [x for x in seqevidences if x.class_type == 'PROTEINSEQUENCE']
    coding_seqevidences = [x for x in seqevidences if x.class_type == 'CODDNASEQUENCE']

    tables = {}
    tables['genomic_dna'] = sorted([x.to_json() for x in dna_seqevidences], key=lambda x: x['strain']['display_name'] if x['strain']['display_name'] != 'S288C' else 'AAA')

    protein_ids = [x.id for x in DBSession.query(Protein).filter(Protein.locus_id == locus_id).all()]
    for protein_id in protein_ids:
        protein_seqevidences.extend([x for x in get_sequence_evidence(locus_id=protein_id) if x.class_type == 'PROTEINSEQUENCE'])

    tables['protein'] = sorted([x.to_json() for x in protein_seqevidences], key=lambda x: x['strain']['display_name'] if x['strain']['display_name'] != 'S288C' else 'AAA')
    tables['coding_dna'] = sorted([x.to_json() for x in coding_seqevidences], key=lambda x: x['strain']['display_name'] if x['strain']['display_name'] != 'S288C' else 'AAA')

    return tables

# -------------------------------Details---------------------------------------
def get_binding_evidence(locus_id):
    query = DBSession.query(Bindingevidence)
    if locus_id is not None:
        query = query.filter_by(bioentity_id=locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_binding_details(locus_id=None):
    if locus_id is None:
        return {'Error': 'No locus_id given.'}

    binding_site_evidences = get_binding_evidence(locus_id=locus_id)

    if binding_site_evidences is None:
        return {'Error': 'Too much data to display.'}

    return [x.to_json() for x in binding_site_evidences]