from math import ceil

from src.sgd.backend.nex import DBSession, query_limit
from src.sgd.backend.nex.query_tools import get_all_bioconcept_children, get_relations
from src.sgd.model.nex.bioconcept import Bioconceptrelation, Phenotype
from src.sgd.model.nex.misc import Experiment, Experimentrelation
from src.sgd.model.nex.evidence import Phenotypeevidence, Chemicalcondition

__author__ = 'kpaskov'

# -------------------------------Overview---------------------------------------
def get_experiment_ancestry(experiment_id, child_experiment_id_to_parent_id):
    ancestry = [experiment_id]
    last_entry = experiment_id
    while last_entry in child_experiment_id_to_parent_id:
        last_entry = child_experiment_id_to_parent_id[last_entry]
        ancestry.append(last_entry)
    return ancestry

def make_overview(locus_id=None, phenotype_id=None):
    qualifiers = None
    phenoevidences = []
    if phenotype_id is not None and DBSession.query(Phenotype).filter_by(id=phenotype_id).first().is_core:
        qualifiers = [x.child.to_json() for x in get_relations(Bioconceptrelation, 'PHENOTYPE', parent_ids=[phenotype_id]) if not x.child.is_core]
        for child in qualifiers:
            more_evidences = get_phenotype_evidence(locus_id=locus_id, phenotype_id=child['id'], chemical_id=None, reference_id=None, with_children=None)
            if more_evidences is not None:
                phenoevidences.extend(more_evidences)

    more_evidences = get_phenotype_evidence(locus_id=locus_id, phenotype_id=phenotype_id, chemical_id=None, reference_id=None, with_children=None)
    if more_evidences is not None:
        phenoevidences.extend(more_evidences)

    child_experiment_id_to_parent_id = dict([(x.child_id, x.parent_id) for x in DBSession.query(Experimentrelation).all()])

    mutant_type_set = set()
    classical_mutant_to_phenotypes = {}
    large_scale_mutant_to_phenotypes = {}

    strain_to_phenotypes = {}

    for phenoevidence in phenoevidences:
        experiment_ancestry = get_experiment_ancestry(phenoevidence.experiment_id, child_experiment_id_to_parent_id)
        experiment = DBSession.query(Experiment).filter_by(id=experiment_ancestry[0 if len(experiment_ancestry) < 3 else len(experiment_ancestry)-3]).first()
        mutant_type = phenoevidence.mutant_type
        strain = phenoevidence.strain
        if experiment.display_name == 'classical genetics':
            if mutant_type in classical_mutant_to_phenotypes:
                classical_mutant_to_phenotypes[mutant_type].add(phenoevidence.id)
            else:
                classical_mutant_to_phenotypes[mutant_type] = {phenoevidence.id}
        elif experiment.display_name == 'large-scale survey':
            if mutant_type in large_scale_mutant_to_phenotypes:
                large_scale_mutant_to_phenotypes[mutant_type].add(phenoevidence.id)
            else:
                large_scale_mutant_to_phenotypes[mutant_type] = {phenoevidence.id}
        mutant_type_set.add(mutant_type)

        if strain is not None:
            if strain.display_name in strain_to_phenotypes:
                strain_to_phenotypes[strain.display_name].add(phenoevidence.id)
            else:
                strain_to_phenotypes[strain.display_name] = {phenoevidence.id}

    mutant_list = list(mutant_type_set)
    mutant_to_count = dict([(x, (0 if x not in classical_mutant_to_phenotypes else len(classical_mutant_to_phenotypes[x]),
                                 0 if x not in large_scale_mutant_to_phenotypes else len(large_scale_mutant_to_phenotypes[x]))) for x in mutant_list])

    strain_to_count = dict([(x, len(y)) for x, y in strain_to_phenotypes.iteritems()])
    strain_list = sorted(strain_to_count.keys(), key=lambda x: strain_to_count[x], reverse=True)


    overview = {'experiment_types': ['classical genetics', 'large-scale survey'], 'mutant_to_count': mutant_to_count, 'mutant_types': mutant_list, 'strain_to_count':strain_to_count, 'strain_list': strain_list}
    if qualifiers is not None:
        overview['qualifiers'] = qualifiers
    return overview

# -------------------------------Details---------------------------------------
def get_phenotype_evidence(locus_id, phenotype_id, chemical_id, reference_id, with_children):
    query = DBSession.query(Phenotypeevidence)
    if locus_id is not None:
        query = query.filter_by(bioentity_id=locus_id)
    if reference_id is not None:
        query = query.filter_by(reference_id=reference_id)
    if chemical_id is not None:
        chemical_evidence_ids = set([x.evidence_id for x in DBSession.query(Chemicalcondition).filter_by(bioitem_id=chemical_id).all()])

        if phenotype_id is not None:
            if with_children:
                child_ids = list(get_all_bioconcept_children(phenotype_id))
                num_chunks = int(ceil(1.0*len(child_ids)/500))
                evidences = []
                for i in range(num_chunks):
                    subquery = query.filter(Phenotypeevidence.bioconcept_id.in_(child_ids[i*500:(i+1)*500]))
                    evidences.extend([x for x in subquery.all() if x.id in chemical_evidence_ids])
                    if len(evidences) > query_limit:
                        return None
                return evidences
            else:
                query = query.filter_by(bioconcept_id=phenotype_id)
                if query.count() > query_limit:
                    return None
                return [x for x in query.all() if x.id in chemical_evidence_ids]
        else:
            chemical_evidence_ids = list(chemical_evidence_ids)
            num_chunks = int(ceil(1.0*len(chemical_evidence_ids)/500))
            evidences = []
            for i in range(num_chunks):
                subquery = query.filter(Phenotypeevidence.id.in_(chemical_evidence_ids[i*500:(i+1)*500]))
                if len(evidences) + subquery.count() > query_limit:
                    return None
                evidences.extend(subquery.all())
            return evidences
    else:
        if phenotype_id is not None:
            if with_children:
                child_ids = list(get_all_bioconcept_children(phenotype_id))
                num_chunks = int(ceil(1.0*len(child_ids)/500))
                evidences = []
                for i in range(num_chunks):
                    subquery = query.filter(Phenotypeevidence.bioconcept_id.in_(child_ids[i*500:(i+1)*500]))
                    if len(evidences) + subquery.count() > query_limit:
                        return None
                    evidences.extend([x for x in subquery.all()])
                return evidences
            else:
                query = query.filter_by(bioconcept_id=phenotype_id)

    if query.count() > query_limit:
        return None
    return query.all()

def get_phenotype_evidence_for_observable(locus_id, phenotype_id, chemical_id, reference_id, with_children):
    phenoevidences = []
    child_ids = [x.child_id for x in get_relations(Bioconceptrelation, 'PHENOTYPE', parent_ids=[phenotype_id]) if not x.child.is_core]
    for child_id in child_ids:
        more_evidences = get_phenotype_evidence(locus_id=locus_id, phenotype_id=child_id, chemical_id=chemical_id, reference_id=reference_id, with_children=with_children)
        if more_evidences is None or len(phenoevidences) + len(more_evidences) > query_limit:
            return None
        phenoevidences.extend(more_evidences)
    return phenoevidences

def make_details(locus_id=None, phenotype_id=None, chemical_id=None, reference_id=None, with_children=False):
    if locus_id is None and phenotype_id is None and chemical_id is None and reference_id is None:
        return {'Error': 'No locus_id or phenotype_id or chemical_id or reference_id given.'}

    if phenotype_id is not None and DBSession.query(Phenotype).filter_by(id=phenotype_id).first().is_core and not with_children:
        phenoevidences = get_phenotype_evidence_for_observable(locus_id=locus_id, phenotype_id=phenotype_id, chemical_id=chemical_id, reference_id=reference_id, with_children=with_children)
    else:
        phenoevidences = get_phenotype_evidence(locus_id=locus_id, phenotype_id=phenotype_id, chemical_id=chemical_id, reference_id=reference_id, with_children=with_children)

    if phenoevidences is None:
        return {'Error': 'Too much data to display.'}

    return [x.to_json() for x in phenoevidences]

# -------------------------------Ontology---------------------------------------
def make_ontology():
    relations = get_relations(Bioconceptrelation, 'PHENOTYPE')
    id_to_phenotype = dict([(x.id, x.to_json()) for x in DBSession.query(Phenotype).all() if x.is_core])
    child_to_parent = dict([(x.child_id, x.parent_id) for x in relations if x.parent_id in id_to_phenotype and x.child_id in id_to_phenotype])

    return {'elements': sorted(id_to_phenotype.values(), key=lambda x: x['display_name']), 'child_to_parent': child_to_parent}

