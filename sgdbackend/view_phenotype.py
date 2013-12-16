'''
Created on Mar 15, 2013

@author: kpaskov
'''
from model_new_schema.bioconcept import Bioconceptrelation
from model_new_schema.evidence import Phenotypeevidence
from sgdbackend_query import get_evidence, get_conditions
from sgdbackend_query.query_auxiliary import get_biofacts
from sgdbackend_query.query_evelements import get_experiment_graph
from sgdbackend_query.query_misc import get_relations
from sgdbackend_utils import create_simple_table
from sgdbackend_utils.cache import id_to_biocon, id_to_bioent, id_to_experiment, id_to_strain
from sgdbackend_utils.obj_to_json import condition_to_json, minimize_json, \
    evidence_to_json

# -------------------------------Overview---------------------------------------
def get_experiment_ancestry(experiment_id, child_experiment_id_to_parent_id):
    ancestry = [experiment_id]
    last_entry = experiment_id
    while last_entry in child_experiment_id_to_parent_id:
        last_entry = child_experiment_id_to_parent_id[last_entry]
        ancestry.append(last_entry)
    return ancestry


def make_overview(bioentity_id):
    phenoevidences = get_evidence(Phenotypeevidence, bioent_id=bioentity_id)
    child_experiment_id_to_parent_id = get_experiment_graph()

    mutant_type_set = set()
    classical_mutant_to_phenotypes = {}
    large_scale_mutant_to_phenotypes = {}

    strain_to_phenotypes = {}

    for phenoevidence in phenoevidences:
        experiment_ancestry = get_experiment_ancestry(phenoevidence.experiment_id, child_experiment_id_to_parent_id)
        experiment = id_to_experiment[experiment_ancestry[0 if len(experiment_ancestry) < 3 else len(experiment_ancestry)-3]]
        mutant_type = phenoevidence.mutant_type
        phenotype = phenoevidence.bioconcept_id
        strain = phenoevidence.strain_id
        if experiment['display_name'] == 'classical genetics':
            if mutant_type in classical_mutant_to_phenotypes:
                classical_mutant_to_phenotypes[mutant_type].add(phenotype)
            else:
                classical_mutant_to_phenotypes[mutant_type] = set([phenotype])
        elif experiment['display_name'] == 'large-scale survey':
            if mutant_type in large_scale_mutant_to_phenotypes:
                large_scale_mutant_to_phenotypes[mutant_type].add(phenotype)
            else:
                large_scale_mutant_to_phenotypes[mutant_type] = set([phenotype])
        mutant_type_set.add(mutant_type)

        if strain is not None:
            if strain in strain_to_phenotypes:
                strain_to_phenotypes[strain].add(phenotype)
            else:
                strain_to_phenotypes[strain] = set([phenotype])

    mutant_list = list(mutant_type_set)
    mutant_to_count = dict([(x, (0 if x not in classical_mutant_to_phenotypes else len(classical_mutant_to_phenotypes[x]),
                                 0 if x not in large_scale_mutant_to_phenotypes else len(large_scale_mutant_to_phenotypes[x]))) for x in mutant_list])

    strain_to_count = dict([(id_to_strain[x]['display_name'], len(y)) for x, y in strain_to_phenotypes.iteritems()])
    strain_list = sorted(strain_to_count.keys(), key=lambda x: strain_to_count[x], reverse=True)


    return {'experiment_types': ['classical genetics', 'large-scale survey'], 'mutant_to_count': mutant_to_count, 'mutant_types': mutant_list, 'strain_to_count':strain_to_count, 'strain_list': strain_list}

# -------------------------------Details---------------------------------------
    
def make_details(locus_id=None, phenotype_id=None, chemical_id=None, with_children=False):
    phenoevidences = []
    if phenotype_id is not None and id_to_biocon[phenotype_id]['is_core'] and not with_children:
        child_ids = [x.child_id for x in get_relations(Bioconceptrelation, 'PHENOTYPE', parent_ids=[phenotype_id]) if not id_to_biocon[x.child_id]['is_core']]
        for child_id in child_ids:
            phenoevidences.extend(get_evidence(Phenotypeevidence, bioent_id=locus_id, biocon_id=child_id, chemical_id=chemical_id, with_children=with_children))

    phenoevidences.extend(get_evidence(Phenotypeevidence, bioent_id=locus_id, biocon_id=phenotype_id, chemical_id=chemical_id, with_children=with_children))
    
    id_to_conditions = {}
    for condition in get_conditions([x.id for x in phenoevidences]):
        evidence_id = condition.evidence_id
        if evidence_id in id_to_conditions:
            id_to_conditions[evidence_id].append(condition)
        else:
            id_to_conditions[evidence_id] = [condition]
            
    tables = create_simple_table(phenoevidences, make_evidence_row, id_to_conditions=id_to_conditions)
    return tables  

def make_evidence_row(phenoevidence, id_to_conditions):
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
        
    obj_json = evidence_to_json(phenoevidence).copy()
    obj_json['bioentity'] = minimize_json(id_to_bioent[bioentity_id], include_format_name=True)
    obj_json['bioconcept'] = id_to_biocon[bioconcept_id]
    obj_json['mutant_type'] = phenoevidence.mutant_type
    obj_json['allele'] = allele
    obj_json['reporter'] = reporter
    obj_json['chemical'] = chemical
    obj_json['condition'] = condition_entries

    obj_json['note'] = obj_json['note']
    return obj_json

# -------------------------------Ontology Graph---------------------------------------

def create_node(biocon, is_focus):
    if is_focus:
        sub_type = 'FOCUS'
    else:
        sub_type = biocon['ancestor_type']
    return {'data':{'id':'Node' + str(biocon['id']), 'name':biocon['display_name'] + ('' if biocon['format_name'] == 'ypo_ontology' else ' (' + str(biocon['count']) + ')'), 'link': biocon['link'],
                    'sub_type':sub_type}}

def create_edge(interaction_id, biocon1_id, biocon2_id):
    return {'data':{'target': 'Node' + str(biocon1_id), 'source': 'Node' + str(biocon2_id)}} 

def make_ontology_graph(phenotype_id):
    children = get_relations(Bioconceptrelation, 'PHENOTYPE', parent_ids=[phenotype_id])    
    parents = get_relations(Bioconceptrelation, 'PHENOTYPE', child_ids=[phenotype_id])
    if len(parents) > 0:
        grandparents = get_relations(Bioconceptrelation, 'PHENOTYPE', child_ids=[parent.parent_id for parent in parents])
        great_grandparents = get_relations(Bioconceptrelation, 'PHENOTYPE', child_ids=[parent.parent_id for parent in grandparents])
        great_great_grandparents = get_relations(Bioconceptrelation, 'PHENOTYPE', child_ids=[parent.parent_id for parent in great_grandparents])
        nodes = []
        nodes.append(create_node(id_to_biocon[phenotype_id], True))
        
        child_ids = set([x.child_id for x in children])
        parent_ids = set([x.parent_id for x in parents])
        parent_ids.update([x.parent_id for x in grandparents])
        parent_ids.update([x.parent_id for x in great_grandparents])
        parent_ids.update([x.parent_id for x in great_great_grandparents])
        
        child_id_to_child = dict([(x, id_to_biocon[x]) for x in child_ids])
        parent_id_to_parent = dict([(x, id_to_biocon[x]) for x in parent_ids])
        viable_ids = set([k for k, v in child_id_to_child.iteritems() if v['is_core']])
        viable_ids.update([k for k, v in parent_id_to_parent.iteritems() if v['is_core']])
        viable_ids.add(phenotype_id)
        
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])
        nodes.extend([create_node(v, False) for k, v in parent_id_to_parent.iteritems() if k in viable_ids])
        
        edges = []
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in children if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in parents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in great_grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in great_great_grandparents if x.child_id in viable_ids and x.parent_id in viable_ids])
    else:
        grandchildren = get_relations(Bioconceptrelation, 'PHENOTYPE', parent_ids=[x.child_id for x in children])  
        
        child_ids = set([x.child_id for x in children])
        child_ids.update([x.child_id for x in grandchildren])  
        
        child_id_to_child = dict([(x, id_to_biocon[x]) for x in child_ids])
        viable_ids = set([k for k, v in child_id_to_child.iteritems() if v['is_core']])
        viable_ids.add(phenotype_id)
        
        nodes = []
        nodes.append(create_node(id_to_biocon[phenotype_id], True))
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])
        
        edges = []
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in children if x.child_id in viable_ids and x.parent_id in viable_ids])
        edges.extend([create_edge(x.id, x.child_id, x.parent_id) for x in grandchildren if x.child_id in viable_ids and x.parent_id in viable_ids])
    
    return {'nodes': list(nodes), 'edges': edges}

# -------------------------------Ontology---------------------------------------

def make_ontology():
    relations = get_relations(Bioconceptrelation, 'PHENOTYPE')
    id_to_phenotype = dict([(x.parent_id, id_to_biocon[x.parent_id]) for x in relations])
    id_to_phenotype.update([(x.child_id, id_to_biocon[x.child_id]) for x in relations])
    id_to_phenotype = dict([(k, v) for k, v in id_to_phenotype.iteritems() if v['is_core']])
    child_to_parent = dict([(x.child_id, x.parent_id) for x in relations if x.parent_id in id_to_phenotype and x.child_id in id_to_phenotype])
        
    return {'elements': id_to_phenotype.values(), 'child_to_parent': child_to_parent}

