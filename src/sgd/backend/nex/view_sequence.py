from src.sgd.model.nex.evidence import DNAsequenceevidence, Proteinsequenceevidence, Bindingevidence
from src.sgd.model.nex.bioitem import Contig
from src.sgd.backend.nex import DBSession, query_limit

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
    query = DBSession.query(DNAsequenceevidence)
    if contig_id is not None:
        query = query.filter_by(contig_id=contig_id)
    if locus_id is not None:
        query = query.filter_by(locus_id=locus_id)

    if query.count() > query_limit:
        return None

    return query.all()

def get_proteinsequence_evidence(locus_id=None):
    query = DBSession.query(Proteinsequenceevidence)
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

    tables = {}
    tables['genomic_dna'] = sorted([x.to_json() for x in genomic_dnaseqevidences], key=lambda x: x['strain']['display_name'] if x['strain']['display_name'] != 'S288C' else 'AAA')
    tables['coding_dna'] = sorted([x.to_json() for x in coding_dnaseqevidences], key=lambda x: x['strain']['display_name'] if x['strain']['display_name'] != 'S288C' else 'AAA')
    tables['protein'] = sorted([x.to_json() for x in proteinseqevidences], key=lambda x: x['strain']['display_name'] if x['strain']['display_name'] != 'S288C' else 'AAA')

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
        neighbor_evidences = DBSession.query(DNAsequenceevidence).filter_by(contig_id=evidence.contig_id).filter(DNAsequenceevidence.start >= evidence.start - 5000).filter(DNAsequenceevidence.end <= evidence.end + 5000).all()
        neighbors[evidence.strain.format_name] = [x.to_json() for x in sorted(neighbor_evidences, key=lambda x: x.start)]

    return neighbors

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

    return [x.to_json() for x in binding_site_evidences]