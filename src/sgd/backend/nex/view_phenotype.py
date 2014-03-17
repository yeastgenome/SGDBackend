from math import ceil

from src.sgd.backend.nex import create_simple_table, DBSession, query_limit
from src.sgd.backend.nex.query_tools import get_all_bioconcept_children, get_relations, \
    get_conditions, get_biofacts
from src.sgd.model.nex import create_format_name
from src.sgd.model.nex.bioconcept import Bioconcept, Bioconceptrelation
from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.model.nex.condition import Chemicalcondition
from src.sgd.model.nex.evelements import Strain, Experiment, Experimentrelation
from src.sgd.model.nex.evidence import Phenotypeevidence
from src.sgd.backend.nex.obj_to_json import condition_to_json, minimize_json, \
    evidence_to_json
from src.sgd.backend.nex.cache import get_obj, get_objs


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
    if phenotype_id is not None and get_obj(Bioconcept, phenotype_id)['is_core']:
        child_ids = [x.child_id for x in get_relations(Bioconceptrelation, 'PHENOTYPE', parent_ids=[phenotype_id]) if not get_obj(Bioconcept, x.child_id)['is_core']]
        for child_id in child_ids:
            more_evidences = get_phenotype_evidence(locus_id=locus_id, phenotype_id=child_id, chemical_id=None, reference_id=None, with_children=None)
            if more_evidences is not None:
                phenoevidences.extend(more_evidences)

        qualifiers = [get_obj(Bioconcept, x.child_id) for x in get_relations(Bioconceptrelation, 'PHENOTYPE', parent_ids=[phenotype_id]) if not get_obj(Bioconcept, x.child_id)['is_core']]


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
        experiment = get_obj(Experiment, experiment_ancestry[0 if len(experiment_ancestry) < 3 else len(experiment_ancestry)-3])
        mutant_type = phenoevidence.mutant_type
        strain = phenoevidence.strain_id
        if experiment['display_name'] == 'classical genetics':
            if mutant_type in classical_mutant_to_phenotypes:
                classical_mutant_to_phenotypes[mutant_type].add(phenoevidence.id)
            else:
                classical_mutant_to_phenotypes[mutant_type] = {phenoevidence.id}
        elif experiment['display_name'] == 'large-scale survey':
            if mutant_type in large_scale_mutant_to_phenotypes:
                large_scale_mutant_to_phenotypes[mutant_type].add(phenoevidence.id)
            else:
                large_scale_mutant_to_phenotypes[mutant_type] = {phenoevidence.id}
        mutant_type_set.add(mutant_type)

        if strain is not None:
            if strain in strain_to_phenotypes:
                strain_to_phenotypes[strain].add(phenoevidence.id)
            else:
                strain_to_phenotypes[strain] = {phenoevidence.id}

    mutant_list = list(mutant_type_set)
    mutant_to_count = dict([(x, (0 if x not in classical_mutant_to_phenotypes else len(classical_mutant_to_phenotypes[x]),
                                 0 if x not in large_scale_mutant_to_phenotypes else len(large_scale_mutant_to_phenotypes[x]))) for x in mutant_list])

    strain_to_count = dict([(get_obj(Strain, x)['display_name'], len(y)) for x, y in strain_to_phenotypes.iteritems()])
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
        chemical_evidence_ids = set([x.evidence_id for x in DBSession.query(Chemicalcondition).filter_by(chemical_id=chemical_id).all()])

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
    child_ids = [x.child_id for x in get_relations(Bioconceptrelation, 'PHENOTYPE', parent_ids=[phenotype_id]) if not get_obj(Bioconcept, x.child_id)['is_core']]
    for child_id in child_ids:
        more_evidences = get_phenotype_evidence(locus_id=locus_id, phenotype_id=child_id, chemical_id=chemical_id, reference_id=reference_id, with_children=with_children)
        if more_evidences is None or len(phenoevidences) + len(more_evidences) > query_limit:
            return None
        phenoevidences.extend(more_evidences)
    return phenoevidences

def make_details(locus_id=None, phenotype_id=None, chemical_id=None, reference_id=None, with_children=False):
    if locus_id is None and phenotype_id is None and chemical_id is None and reference_id is None:
        return {'Error': 'No locus_id or phenotype_id or chemical_id or reference_id given.'}

    if phenotype_id is not None and get_obj(Bioconcept, phenotype_id)['is_core'] and not with_children:
        phenoevidences = get_phenotype_evidence_for_observable(locus_id=locus_id, phenotype_id=phenotype_id, chemical_id=chemical_id, reference_id=reference_id, with_children=with_children)
    else:
        phenoevidences = get_phenotype_evidence(locus_id=locus_id, phenotype_id=phenotype_id, chemical_id=chemical_id, reference_id=reference_id, with_children=with_children)

    if phenoevidences is None:
        return {'Error': 'Too much data to display.'}

    id_to_conditions = {}
    for condition in get_conditions([x.id for x in phenoevidences]):
        evidence_id = condition.evidence_id
        if evidence_id in id_to_conditions:
            id_to_conditions[evidence_id].append(condition)
        else:
            id_to_conditions[evidence_id] = [condition]

    child_experiment_id_to_parent_id = dict([(x.child_id, x.parent_id) for x in DBSession.query(Experimentrelation).all()])
            
    tables = create_simple_table(phenoevidences, make_evidence_row, id_to_conditions=id_to_conditions, child_experiment_id_to_parent_id=child_experiment_id_to_parent_id)
    return tables  

def make_evidence_row(phenoevidence, id_to_conditions, child_experiment_id_to_parent_id):
    bioentity_id = phenoevidence.bioentity_id
    bioconcept_id = phenoevidence.bioconcept_id
    conditions = [] if phenoevidence.id not in id_to_conditions else [condition_to_json(x) for x in id_to_conditions[phenoevidence.id]]
    condition_entries = []
    allele = None
    reporter = None
    chemical = None
    for condition in conditions:
        if 'chemical' in condition:
            chemical = condition['chemical'].copy()
            chemical['amount'] = condition['amount']
            chemical['note'] = condition['note']
        elif 'role' in condition and condition['role'] == 'Allele':
            allele = condition['obj'].copy()
            allele['note'] = condition['note']
        elif 'role' in condition and condition['role'] == 'Reporter':
            reporter = condition['obj'].copy()
            reporter['note'] = condition['note']
        elif isinstance(condition, basestring):
            condition_entries.append(condition)
        else:
            print condition

    experiment_ancestry = get_experiment_ancestry(phenoevidence.experiment_id, child_experiment_id_to_parent_id)
    experiment_ancestor = get_obj(Experiment, experiment_ancestry[0 if len(experiment_ancestry) < 3 else len(experiment_ancestry)-3])
        
    obj_json = evidence_to_json(phenoevidence).copy()
    obj_json['bioentity'] = minimize_json(get_obj(Bioentity, bioentity_id), include_format_name=True)
    obj_json['bioconcept'] = get_obj(Bioconcept, bioconcept_id)
    obj_json['mutant_type'] = phenoevidence.mutant_type
    obj_json['experiment_type_category'] = experiment_ancestor['display_name']
    obj_json['allele'] = allele
    obj_json['reporter'] = reporter
    obj_json['chemical'] = chemical
    obj_json['condition'] = condition_entries

    if obj_json['strain'] is not None:
        obj_json['strain']['details'] = phenoevidence.strain_details
    if obj_json['experiment'] is not None:
        obj_json['experiment']['details'] = phenoevidence.experiment_details

    obj_json['note'] = obj_json['note']
    return obj_json

# -------------------------------Ontology Graph---------------------------------------
def create_node(biocon, is_focus):
    if is_focus:
        sub_type = 'FOCUS'
    else:
        sub_type = biocon['ancestor_type']
    return {'data':{'id':'Node' + str(biocon['id']), 'name':biocon['display_name'] + ('' if biocon['format_name'] == 'ypo' else ' (' + str(biocon['count']) + ')'), 'link': biocon['link'],
                    'sub_type':sub_type}}

def create_ontology_edge(interaction_id, biocon1_id, biocon2_id):
    return {'data':{'target': 'Node' + str(biocon1_id), 'source': 'Node' + str(biocon2_id)}} 

def make_ontology_graph(phenotype_id):
    all_children = None
    children = get_relations(Bioconceptrelation, 'PHENOTYPE', parent_ids=[phenotype_id])
    parents = get_relations(Bioconceptrelation, 'PHENOTYPE', child_ids=[phenotype_id])
    if len(parents) > 0:
        grandparents = get_relations(Bioconceptrelation, 'PHENOTYPE', child_ids=[parent.parent_id for parent in parents])
        great_grandparents = get_relations(Bioconceptrelation, 'PHENOTYPE', child_ids=[parent.parent_id for parent in grandparents])
        great_great_grandparents = get_relations(Bioconceptrelation, 'PHENOTYPE', child_ids=[parent.parent_id for parent in great_grandparents])
        nodes = []
        nodes.append(create_node(get_obj(Bioconcept, phenotype_id), True))
        
        child_ids = set([x.child_id for x in children])
        parent_ids = set([x.parent_id for x in parents])
        parent_ids.update([x.parent_id for x in grandparents])
        parent_ids.update([x.parent_id for x in great_grandparents])
        parent_ids.update([x.parent_id for x in great_great_grandparents])
        
        child_id_to_child = get_objs(Bioconcept, child_ids)
        parent_id_to_parent = get_objs(Bioconcept, parent_ids)
        viable_ids = set([k for k, v in child_id_to_child.iteritems() if v['is_core']])

        #If there are too many children, hide some.
        all_children = []
        hidden_children_count = 0
        if len(viable_ids) > 8:
            all_children = sorted(get_objs(Bioconcept, viable_ids).values(), key=lambda x: x['display_name'])
            hidden_children_count = len(viable_ids)-7
            viable_ids = set(list(viable_ids)[:7])

        viable_ids.update([k for k, v in parent_id_to_parent.iteritems() if v['is_core']])
        viable_ids.add(phenotype_id)
        
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])
        nodes.extend([create_node(v, False) for k, v in parent_id_to_parent.iteritems() if k in viable_ids])
        
        edges = []
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in children if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in parents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in great_grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in great_great_grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])

        if hidden_children_count > 0:
            nodes.insert(0, {'data':{'id':'NodeMoreChildren', 'name':str(hidden_children_count) + ' more children', 'link': None, 'sub_type':get_obj(Bioconcept, phenotype_id)['ancestor_type']}})
            edges.insert(0, {'data':{'target': 'NodeMoreChildren', 'source': 'Node' + str(phenotype_id)}})

    else:
        grandchildren = get_relations(Bioconceptrelation, 'PHENOTYPE', parent_ids=[x.child_id for x in children])  
        
        child_ids = set([x.child_id for x in children])
        child_ids.update([x.child_id for x in grandchildren])  
        
        child_id_to_child = get_objs(Bioconcept, child_ids)
        viable_ids = set([k for k, v in child_id_to_child.iteritems() if v['is_core']])
        viable_ids.add(phenotype_id)
        
        nodes = []
        nodes.append(create_node(get_obj(Bioconcept, phenotype_id), True))
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])
        
        edges = []
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in children if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_ontology_edge(x.id, x.child_id, x.parent_id) for x in grandchildren if x.child_id in viable_ids and x.parent_id in viable_ids])
    
    return {'nodes': list(nodes), 'edges': edges, 'all_children': all_children}

# -------------------------------Ontology---------------------------------------
def make_ontology():
    relations = get_relations(Bioconceptrelation, 'PHENOTYPE')
    id_to_phenotype = get_objs(Bioconcept, [x.parent_id for x in relations])
    id_to_phenotype.update(get_objs(Bioconcept, [x.child_id for x in relations]))
    id_to_phenotype = dict([(k, v) for k, v in id_to_phenotype.iteritems() if v['is_core']])
    child_to_parent = dict([(x.child_id, x.parent_id) for x in relations if x.parent_id in id_to_phenotype and x.child_id in id_to_phenotype])

    return {'elements': sorted(id_to_phenotype.values(), key=lambda x: x['display_name']), 'child_to_parent': child_to_parent}

# -------------------------------Graph-----------------------------------------
def create_bioent_node(bioent, is_focus, gene_count):
    sub_type = None
    if is_focus:
        sub_type = 'FOCUS'
    return {'data':{'id':'BioentNode' + str(bioent['id']), 'name':bioent['display_name'], 'link': bioent['link'],
                    'sub_type':sub_type, 'type': 'BIOENTITY', 'gene_count':gene_count}}

def create_biocon_node(biocon_id, biocon_type, gene_count):
    if biocon_type == 'PHENOTYPE':
        return {'data':{'id':'BioconNode' + biocon_id, 'name':biocon_id, 'link': '/observable/' + create_format_name(biocon_id) + '/overview',
                    'sub_type':None, 'type': 'BIOCONCEPT', 'gene_count':gene_count}}
    else:
        biocon = get_obj(Bioconcept, biocon_id)
        return {'data':{'id':'BioconNode' + str(biocon['id']), 'name':biocon['display_name'], 'link': biocon['link'],
                    'sub_type':None if not 'go_aspect' in biocon else biocon['go_aspect'], 'type': 'BIOCONCEPT', 'gene_count':gene_count}}

def create_edge(bioent_id, biocon_id):
    return {'data':{'target': 'BioentNode' + str(bioent_id), 'source': 'BioconNode' + str(biocon_id)}}

def biocon_id_conversion(bioconcept_id, biocon_type):
    if biocon_type == 'PHENOTYPE':
        return get_obj(Bioconcept, bioconcept_id)["observable"]
    else:
        return bioconcept_id

def make_graph(bioent_id, biocon_type, biocon_f=None, bioent_type='LOCUS'):

    #Get bioconcepts for gene
    bioconcept_ids = [x.bioconcept_id for x in get_biofacts(biocon_type, bioent_id=bioent_id)]

    biocon_id_to_bioent_ids = {}
    bioent_id_to_biocon_ids = {}

    if len(bioconcept_ids) > 0:
        all_relevant_biofacts = [x for x in get_biofacts(biocon_type, biocon_ids=bioconcept_ids, bioent_type=bioent_type) if biocon_f is None or biocon_f(x.bioconcept_id)]
    else:
        all_relevant_biofacts = []

    for biofact in all_relevant_biofacts:
        bioentity_id = biofact.bioentity_id
        bioconcept_id = biocon_id_conversion(biofact.bioconcept_id, biocon_type)

        if bioconcept_id in biocon_id_to_bioent_ids:
            biocon_id_to_bioent_ids[bioconcept_id].add(bioentity_id)
        else:
            biocon_id_to_bioent_ids[bioconcept_id] = {bioentity_id}

        if bioentity_id in bioent_id_to_biocon_ids:
            bioent_id_to_biocon_ids[bioentity_id].add(bioconcept_id)
        else:
            bioent_id_to_biocon_ids[bioentity_id] = {bioconcept_id}

    cutoff = 1
    node_count = len(bioent_id_to_biocon_ids) + len(biocon_id_to_bioent_ids)
    edge_count = len(all_relevant_biofacts)
    bioent_count = len(bioent_id_to_biocon_ids)
    bioent_ids_in_use = set([x for x, y in bioent_id_to_biocon_ids.iteritems() if len(y) >= cutoff])
    biocon_ids_in_use = set([x for x, y in biocon_id_to_bioent_ids.iteritems() if len(y & bioent_ids_in_use) > 1])
    biofacts_in_use = [x for x in all_relevant_biofacts]
    while node_count > 100 or edge_count > 250 or bioent_count > 50:
        cutoff = cutoff + 1
        bioent_ids_in_use = set([x for x, y in bioent_id_to_biocon_ids.iteritems() if len(y) >= cutoff])
        biocon_ids_in_use = set([x for x, y in biocon_id_to_bioent_ids.iteritems() if len(y & bioent_ids_in_use) > 1])
        biofacts_in_use = [x for x in all_relevant_biofacts if x.bioentity_id in bioent_ids_in_use and biocon_id_conversion(x.bioconcept_id, biocon_type) in biocon_ids_in_use]
        node_count = len(bioent_ids_in_use) + len(biocon_ids_in_use)
        edge_count = len(biofacts_in_use)
        bioent_count = len(bioent_ids_in_use)

    if len(bioent_ids_in_use) > 0:

        bioent_to_score = dict({(x, len(y&biocon_ids_in_use)) for x, y in bioent_id_to_biocon_ids.iteritems()})
        bioent_to_score[bioent_id] = 0

        nodes = [create_bioent_node(get_obj(Bioentity, x), x==bioent_id, len(bioent_id_to_biocon_ids[x] & biocon_ids_in_use)) for x in bioent_ids_in_use]
        nodes.extend([create_biocon_node(x, biocon_type, max(bioent_to_score[x] for x in biocon_id_to_bioent_ids[x])) for x in biocon_ids_in_use])

        edges = [create_edge(biofact.bioentity_id, biocon_id_conversion(biofact.bioconcept_id, biocon_type)) for biofact in biofacts_in_use]

        return {'nodes': nodes, 'edges': edges, 'max_cutoff': max(bioent_to_score.values()), 'min_cutoff':cutoff if len(bioent_ids_in_use) == 1 else min([bioent_to_score[x] for x in bioent_ids_in_use if x != bioent_id])}
    else:
        return {'nodes':[], 'edges':[], 'max_cutoff':0, 'min_cutoff':0}