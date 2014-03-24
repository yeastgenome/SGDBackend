from src.sgd.model.nex.evidence import DNAsequenceevidence, Proteinsequenceevidence, Bindingevidence
from src.sgd.model.nex.bioentity import Protein
from src.sgd.model.nex.bioitem import Contig
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
def get_dnasequence_evidence(locus_id=None, contig_id=None):
    query = DBSession.query(DNAsequenceevidence)
    if contig_id is not None:
        query = DBSession.query(DNAsequenceevidence).filter_by(contig_id=contig_id)
    if locus_id is not None:
        query = query.filter_by(bioentity_id=locus_id)

    if query.count() > query_limit:
        return None
    return query.all()

def get_proteinsequence_evidence(protein_id=None):
    query = DBSession.query(Proteinsequenceevidence)
    if protein_id is not None:
        query = query.filter_by(bioentity_id=protein_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None, contig_id=None):
    if locus_id is None and contig_id is None:
        return {'Error': 'No locus_id or contig_id given.'}

    dnaseqevidences = get_dnasequence_evidence(locus_id=locus_id, contig_id=contig_id)
    proteinseqevidences = []

    protein_ids = [] if locus_id is None else [x.id for x in DBSession.query(Protein).filter(Protein.locus_id == locus_id).all()]
    for protein_id in protein_ids:
        proteinseqevidences.extend(get_proteinsequence_evidence(protein_id=protein_id))

    if dnaseqevidences is None or proteinseqevidences is None:
        return {'Error': 'Too much data to display.'}

    genomic_dnaseqevidences = [x for x in dnaseqevidences if x.dna_type == 'GENOMIC']
    coding_dnaseqevidences = [x for x in dnaseqevidences if x.dna_type == 'CODING']

    tables = {}
    tables['genomic_dna'] = sorted([x.to_json() for x in genomic_dnaseqevidences], key=lambda x: x['strain']['display_name'] if x['strain']['display_name'] != 'S288C' else 'AAA')
    tables['coding_dna'] = sorted([x.to_json() for x in coding_dnaseqevidences], key=lambda x: x['strain']['display_name'] if x['strain']['display_name'] != 'S288C' else 'AAA')
    tables['protein'] = sorted([x.to_json() for x in proteinseqevidences], key=lambda x: x['strain']['display_name'] if x['strain']['display_name'] != 'S288C' else 'AAA')

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