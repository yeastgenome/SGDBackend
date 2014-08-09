from sqlalchemy.sql.expression import func
from sqlalchemy.orm import joinedload

from src.sgd.convert import is_number
from src.sgd.convert.transformers import make_db_starter
from src.sgd.model.nex.bioentity import Locus, Complex
from src.sgd.model.nex.bioconcept import Bioconcept, Go, Observable
from src.sgd.model.nex.bioitem import Bioitem, Domain, Dataset, Datasetcolumn
from src.sgd.model.nex.evidence import Geninteractionevidence, Physinteractionevidence, Regulationevidence, Goevidence, \
    Phenotypeevidence, Literatureevidence, Domainevidence, Bioentitydata, Expressionevidence
from src.sgd.model.nex.auxiliary import Bioconceptinteraction, Bioiteminteraction
import math
import datetime
import operator
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
def make_bioentity_geninteraction_starter(nex_session_maker):
    def bioentity_interaction_starter():
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])

        #Geninteraction
        bioentity_pair_to_evidence_count = {}
        for evidence in nex_session.query(Geninteractionevidence).all():
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

        nex_session.close()
    return bioentity_interaction_starter

def make_bioentity_physinteraction_starter(nex_session_maker):
    def bioentity_interaction_starter():
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])

        #Physinteraction
        bioentity_pair_to_evidence_count = {}
        for evidence in nex_session.query(Physinteractionevidence).all():
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

        nex_session.close()
    return bioentity_interaction_starter

def make_bioentity_regulation_interaction_starter(nex_session_maker):
    def bioentity_interaction_starter():
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        #Regulation
        bioentity_pair_to_evidence_count = {}
        for evidence in nex_session.query(Regulationevidence).all():
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

        nex_session.close()
    return bioentity_interaction_starter

def make_bioentity_expression_interaction_starter(nex_session_maker):
    def bioentity_interaction_starter():
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        dataset_id_to_evidence_ids = dict()
        for evidence in nex_session.query(Expressionevidence).options(joinedload(Expressionevidence.datasetcolumn)).all():
            dataset_id = evidence.datasetcolumn.dataset_id
            if dataset_id in dataset_id_to_evidence_ids:
                dataset_id_to_evidence_ids[dataset_id].append(evidence.id)
            else:
                dataset_id_to_evidence_ids[dataset_id] = [evidence.id]

        bioent_id_to_index = dict()
        for bioent_id in id_to_bioentity.keys():
            bioent_id_to_index[bioent_id] = len(bioent_id_to_index)

        bioent_count = len(bioent_id_to_index)

        magnitudes = [0]*bioent_count
        ns = [0]*bioent_count
        pair_dot_products = [([0]*bioent_count) for _ in range(bioent_count)]
        print 'Empty arrays created.'

        count = 0
        for evidence_ids in dataset_id_to_evidence_ids.values():
            if len(evidence_ids) > 1:
                start = datetime.datetime.now()

                evidence_id_to_index = dict()
                for evidence_id in evidence_ids:
                    evidence_id_to_index[evidence_id] = len(evidence_id_to_index)

                means = [0]*bioent_count
                data = [([0]*bioent_count) for _ in range(len(evidence_ids))]
                for x in nex_session.query(Bioentitydata).filter(Bioentitydata.evidence_id.in_(evidence_ids)).all():
                    value = 2**float(x.value)
                    bioentity_index = bioent_id_to_index[x.locus_id]
                    evidence_index = evidence_id_to_index[x.evidence_id]
                    data[evidence_index][bioentity_index] = value
                    means[bioentity_index] += value

                    ns[bioentity_index] += 1

                means = [means[x]/len(evidence_ids) for x in range(0, bioent_count)]
                print len(evidence_ids)

                for data_row in data:
                    data_row = map(operator.sub, data_row, means)

                    for bioentity1_index, value1 in enumerate(data_row):
                        #Update magnitudes
                        magnitudes[bioentity1_index] += value1**2

                        #Update pair dot products
                        for bioentity2_index, value2 in enumerate(data_row):
                            if bioentity1_index < bioentity2_index:
                                pair_dot_products[bioentity1_index][bioentity2_index] += value1*value2

            count += 1
            print count, (datetime.datetime.now() - start)

        magnitudes = [math.sqrt(x) for x in magnitudes]

        for bioentity1_id, bioentity1_index in bioent_id_to_index.iteritems():
            for bioentity2_id, bioentity2_index in bioent_id_to_index.iteritems():
                if bioentity1_index < bioentity2_index and magnitudes[bioentity1_index] > 0 and magnitudes[bioentity2_index] > 0:
                    r = pair_dot_products[bioentity1_index][bioentity2_index]/(magnitudes[bioentity1_index]*magnitudes[bioentity2_index])
                    n = min(ns[bioentity1_index], ns[bioentity2_index])
                    score = r*math.sqrt((n-2)/(1-r*r))

                    if score >= 20 or score <= -20:
                        bioentity = id_to_bioentity[bioentity1_id]
                        interactor = id_to_bioentity[bioentity2_id]

                        if score < 0:
                            yield {'interaction_type': 'EXPRESSION', 'coeff': -score, 'bioentity': bioentity, 'interactor': interactor, 'direction': 'negative'}
                            yield {'interaction_type': 'EXPRESSION', 'coeff': -score, 'bioentity': interactor, 'interactor': bioentity, 'direction': 'negative'}
                        else:
                            yield {'interaction_type': 'EXPRESSION', 'coeff': score, 'bioentity': bioentity, 'interactor': interactor, 'direction': 'positive'}
                            yield {'interaction_type': 'EXPRESSION', 'coeff': score, 'bioentity': interactor, 'interactor': bioentity, 'direction': 'positive'}

        nex_session.close()
    return bioentity_interaction_starter

def dot_product(x, y):
    return sum(p*q for p,q in zip(x, y))

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
        for row in nex_session.query(Goevidence.locus_id, Goevidence.go_id, func.count(Goevidence.id)).filter(Goevidence.annotation_type != 'computational').group_by(Goevidence.locus_id, Goevidence.go_id).all():
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