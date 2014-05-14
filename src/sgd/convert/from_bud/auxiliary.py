from sqlalchemy.sql.expression import func

from src.sgd.convert import is_number
from src.sgd.convert.transformers import make_db_starter
from src.sgd.model.nex.bioentity import Locus, Complex
from src.sgd.model.nex.bioconcept import Bioconcept, Go
from src.sgd.model.nex.bioitem import Bioitem
from src.sgd.model.nex.evidence import Geninteractionevidence, Physinteractionevidence, Regulationevidence, Goevidence, \
    Phenotypeevidence, Literatureevidence, Domainevidence
import math

__author__ = 'kpaskov'
    
# --------------------- Convert Disambigs ---------------------
def make_disambig_starter(nex_session_maker, cls, fields, class_type, subclass_type):
    def disambig_starter():
        nex_session = nex_session_maker()

        for obj in make_db_starter(nex_session.query(cls), 1000)():
            for field in fields:
                field_value = getattr(obj, field)
                if field == 'doi':
                    field_value = None if field_value is None else 'doi:' + field_value.lower()
                if field_value is not None and (field == 'id' or field == 'pubmed_id' or not is_number(field_value)):
                    yield {'disambig_key': str(field_value),
                           'class_type': class_type,
                           'subclass_type': subclass_type,
                           'identifier': obj.id}

        nex_session.close()
    return disambig_starter

# --------------------- Convert Bioentityinteractions ---------------------
def make_bioentity_interaction_starter(nex_session_maker):
    def bioentity_interaction_starter():
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])

        #Geninteraction
        bioentity_pair_to_evidence_count = {}
        for evidence in make_db_starter(nex_session.query(Geninteractionevidence), 1000)():
            bioentity_pair = (evidence.locus1_id, evidence.locus2_id)
            if bioentity_pair in bioentity_pair_to_evidence_count:
                bioentity_pair_to_evidence_count[bioentity_pair] += 1
            else:
                bioentity_pair_to_evidence_count[bioentity_pair] = 1

        for bioentity_pair, evidence_count in bioentity_pair_to_evidence_count.iteritems():
            bioentity1_id, bioentity2_id = bioentity_pair
            bioentity1 = id_to_bioentity[bioentity1_id]
            bioentity2 = id_to_bioentity[bioentity2_id]
            yield {'interaction_type': 'GENINTERACTION', 'evidence_count': evidence_count, 'bioentity': bioentity1, 'interactor': bioentity2, 'direction': 'undirected'}
            yield {'interaction_type': 'GENINTERACTION', 'evidence_count': evidence_count, 'bioentity': bioentity2, 'interactor': bioentity1, 'direction': 'undirected'}

        #Physinteraction
        bioentity_pair_to_evidence_count = {}
        for evidence in make_db_starter(nex_session.query(Physinteractionevidence), 1000)():
            bioentity_pair = (evidence.locus1_id, evidence.locus2_id)
            if bioentity_pair in bioentity_pair_to_evidence_count:
                bioentity_pair_to_evidence_count[bioentity_pair] += 1
            else:
                bioentity_pair_to_evidence_count[bioentity_pair] = 1

        for bioentity_pair, evidence_count in bioentity_pair_to_evidence_count.iteritems():
            bioentity1_id, bioentity2_id = bioentity_pair
            bioentity1 = id_to_bioentity[bioentity1_id]
            bioentity2 = id_to_bioentity[bioentity2_id]
            yield {'interaction_type': 'PHYSINTERACTION', 'evidence_count': evidence_count, 'bioentity': bioentity1, 'interactor': bioentity2, 'direction': 'undirected'}
            yield {'interaction_type': 'PHYSINTERACTION', 'evidence_count': evidence_count, 'bioentity': bioentity2, 'interactor': bioentity1, 'direction': 'undirected'}

        #Regulation
        bioentity_pair_to_evidence_count = {}
        for evidence in make_db_starter(nex_session.query(Regulationevidence), 1000)():
            bioentity_pair = (evidence.locus1_id, evidence.locus2_id)
            if bioentity_pair in bioentity_pair_to_evidence_count:
                bioentity_pair_to_evidence_count[bioentity_pair] += 1
            else:
                bioentity_pair_to_evidence_count[bioentity_pair] = 1

        for bioentity_pair, evidence_count in bioentity_pair_to_evidence_count.iteritems():
            bioentity1_id, bioentity2_id = bioentity_pair
            bioentity1 = id_to_bioentity[bioentity1_id]
            bioentity2 = id_to_bioentity[bioentity2_id]
            yield {'interaction_type': 'REGULATION', 'evidence_count': evidence_count, 'bioentity': bioentity1, 'interactor': bioentity2, 'direction': 'forward'}
            yield {'interaction_type': 'REGULATION', 'evidence_count': evidence_count, 'bioentity': bioentity2, 'interactor': bioentity1, 'direction': 'backward'}

        #Expression

        nex_session.close()
    return bioentity_interaction_starter

def average(x):
    assert len(x) > 0
    return float(sum(x)) / len(x)

def pearson_def(x, y):
    assert len(x) == len(y)
    n = len(x)
    assert n > 0
    avg_x = average(x)
    avg_y = average(y)
    diffprod = 0
    xdiff2 = 0
    ydiff2 = 0
    for idx in range(n):
        xdiff = x[idx] - avg_x
        ydiff = y[idx] - avg_y
        diffprod += xdiff * ydiff
        xdiff2 += xdiff * xdiff
        ydiff2 += ydiff * ydiff

    return diffprod / math.sqrt(xdiff2 * ydiff2)

# --------------------- Convert Bioconceptinteractions ---------------------
def make_bioconcept_interaction_starter(nex_session_maker):
    def bioconcept_interaction_starter():
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        id_to_bioconcept = dict([(x.id, x) for x in nex_session.query(Bioconcept).all()])

        bad_interactors = set([x.id for x in nex_session.query(Bioconcept).filter(Bioconcept.format_name.in_({'vegetative_growth',
                                                                                                                'haploinsufficient',
                                                                                                                'viable',
                                                                                                                'heat_sensitivity',
                                                                                                                'toxin_resistance',
                                                                                                                'chronological_lifespan',
                                                                                                                'competitive_fitness',
                                                                                                                'desiccation_resistance',
                                                                                                                'resistance_to_cycloheximide',
                                                                                                                'resistance_to_methyl_methanesulfonate',
                                                                                                                'resistance_to_sirolimus',
                                                                                                                'vacuolar_morphology',
                                                                                                                'inviable'})).all()])

        #Complex
        id_to_complex = dict([(x.id, x) for x in nex_session.query(Complex).all()])
        complex_to_gene_ids = dict([(x.id, set([y.locus_id for y in x.complex_evidences])) for x in id_to_complex.values()])
        for go in nex_session.query(Go).all():
            gene_ids = set([x.locus_id for x in go.go_evidences])
            for complex_id, complex_gene_ids in complex_to_gene_ids.iteritems():
                overlap = len(gene_ids & complex_gene_ids)
                if overlap > 1:
                    yield {'interaction_type': 'GO', 'evidence_count': overlap, 'bioentity': id_to_complex[complex_id], 'interactor': go}

        #Go
        for row in nex_session.query(Goevidence.locus_id, Goevidence.go_id, func.count(Goevidence.id)).group_by(Goevidence.locus_id, Goevidence.go_id).all():
            go = id_to_bioconcept[row[1]]
            locus = id_to_bioentity[row[0]]
            if go.go_aspect == 'biological process' and go.id not in bad_interactors:
                yield {'interaction_type': 'GO', 'evidence_count': row[2], 'bioentity': locus, 'interactor': go}

        #Phenotype
        for row in nex_session.query(Phenotypeevidence.locus_id, Phenotypeevidence.phenotype_id, func.count(Phenotypeevidence.id)).group_by(Phenotypeevidence.locus_id, Phenotypeevidence.phenotype_id).all():
            observable = id_to_bioconcept[row[1]].observable
            locus = id_to_bioentity[row[0]]
            if observable.id not in bad_interactors:
                yield {'interaction_type': 'PHENOTYPE', 'evidence_count': row[2], 'bioentity': locus, 'interactor': observable}

        nex_session.close()
    return bioconcept_interaction_starter

# --------------------- Convert Bioiteminteraction ---------------------
def make_bioitem_interaction_starter(nex_session_maker):
    def bioitem_interaction_starter():
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        id_to_bioitem = dict([(x.id, x) for x in nex_session.query(Bioitem).all()])

        bad_interactors = set([x.id for x in nex_session.query(Bioitem).filter(Bioitem.format_name.in_({'seg', 'coil', 'predicted_signal_peptide', 'predicted_transmembrane_domain'})).all()])

        #Domain
        for row in nex_session.query(Domainevidence.locus_id, Domainevidence.domain_id, func.count(Domainevidence.id)).group_by(Domainevidence.locus_id, Domainevidence.domain_id).all():
            domain = id_to_bioitem[row[1]]
            locus = id_to_bioentity[row[0]]
            if domain.id not in bad_interactors:
                yield {'interaction_type': 'DOMAIN', 'evidence_count': row[2], 'bioentity': locus, 'interactor': domain}

        nex_session.close()
    return bioitem_interaction_starter

# --------------------- Convert Reference Interactions ---------------------
def make_reference_interaction_starter(nex_session_maker):
    def reference_interaction_starter():
        nex_session = nex_session_maker()

        for evidence in nex_session.query(Literatureevidence).filter(Literatureevidence.topic == 'Primary Literature').all():
            yield {'interaction_type': 'PRIMARY', 'evidence_count': 1, 'bioentity': evidence.locus, 'interactor': evidence.reference}

        nex_session.close()
    return reference_interaction_starter