'''
Created on Jun 17, 2013

@author: kpaskov
'''
from model_new_schema.bioentity import Bioentevidence
from model_new_schema.evidence import Evidence, EvidenceChemical
from model_new_schema.go import Goevidence
from model_new_schema.phenotype import Phenoevidence
from query import get_reference, get_bioent, get_biocon, get_experiment, \
    get_strain, get_chemical
from sgdbackend.models import DBSession
from sqlalchemy.orm import joinedload
 

'''
-------------------------------Graph---------------------------------------
'''  
    
schema = {'nodes': [ { 'name': "label", 'type': "string" }, 
                         {'name':'link', 'type':'string'}, 
                         {'name':'weight', 'type':'integer'},
                         {'name':'highlight', 'type':'boolean'},
                         {'name':'bio_type', 'type':'string'},
                         {'name':'sub_type', 'type':'string'}],
                'edges': [{'name':'weight', 'type':'integer'}]}
    
def create_node(obj, weight):
    obj_id = get_id(obj)
    subtype=None
    if hasattr(obj, 'subtype'):
        subtype = obj.subtype
    if hasattr(obj, 'weight'):
        weight = obj.weight
    return (obj_id, {'id':obj_id, 'label':obj.display_name, 'link':obj.link, 'weight':weight, 
            'highlight':False, 'bio_type':obj.type, 'sub_type':subtype})

def create_edge(source_obj, sink_obj, weight):
    target_id = get_id(source_obj)
    source_id = get_id(sink_obj)
    obj_id = target_id + '--' + source_id if target_id < source_id else source_id + '--' + target_id
    return (obj_id, { 'id': obj_id, 'target': target_id, 'source': source_id, 
            'weight':weight})
    
def create_graph(level_one_types, level_two_types, evidence_filter, l1_filter, l2_filter,
                 seed_refs=[], seed_bioents=[], seed_biocons=[], seed_expts=[],
                 seed_strains=[], seed_chems=[]):
            
    l1_refs_all = dict()
    l1_bioents_all = dict()
    l1_biocons_all = dict()
    l1_expts_all = dict()
    l1_strains_all = dict()
    l1_chems_all = dict()
    
    if 'REFERENCE' in level_one_types:
        l1_refs_all = get_related_references(seed_bioents, seed_biocons, seed_expts, seed_strains, seed_chems, evidence_filter)
    if 'BIOENTITY' in level_one_types:
        l1_bioents_all = get_related_bioents(seed_biocons, seed_refs, seed_expts, seed_strains, seed_chems, evidence_filter)
    if 'BIOCONCEPT' in level_one_types:
        l1_biocons_all = get_related_biocons(seed_bioents, seed_refs, seed_expts, seed_strains, seed_chems, evidence_filter)
    if 'EXPERIMENT' in level_one_types:
        l1_expts_all = get_related_experiments(seed_bioents, seed_biocons, seed_refs, seed_strains, seed_chems, evidence_filter)
    if 'STRAIN' in level_one_types:
        l1_strains_all = get_related_strains(seed_bioents, seed_biocons, seed_refs, seed_expts, seed_chems, evidence_filter)
    if 'CHEMICAL' in level_one_types:
        l1_chems_all = get_related_chemicals(seed_bioents, seed_biocons, seed_refs, seed_expts, seed_strains, evidence_filter)
        
    l1_refs = [k for k,v in l1_refs_all.iteritems() if l1_filter(k,v)]
    l1_bioents = [k for k,v in l1_bioents_all.iteritems() if l1_filter(k,v)]
    l1_biocons = [k for k,v in l1_biocons_all.iteritems() if l1_filter(k,v)]
    l1_expts = [k for k,v in l1_expts_all.iteritems() if l1_filter(k,v)]
    l1_strains = [k for k,v in l1_strains_all.iteritems() if l1_filter(k,v)]
    l1_chems = [k for k,v in l1_chems_all.iteritems() if l1_filter(k,v)]
        
    l2_refs_all = dict()
    l2_bioents_all = dict()
    l2_biocons_all = dict()
    l2_expts_all = dict()
    l2_strains_all = dict()
    l2_chems_all = dict()
    
    if 'REFERENCE' in level_two_types:
        l2_refs_all = get_related_references(l1_bioents, l1_biocons, l1_expts, l1_strains, l1_chems, evidence_filter)
    if 'BIOENTITY' in level_two_types:
        l2_bioents_all = get_related_bioents(l1_biocons, l1_refs, l1_expts, l1_strains, l1_chems, evidence_filter)
    if 'BIOCONCEPT' in level_two_types:
        l2_biocons_all = get_related_biocons(l1_bioents, l1_refs, l1_expts, l1_strains, l1_chems, evidence_filter)
    if 'EXPERIMENT' in level_two_types:
        l2_expts_all = get_related_experiments(l1_bioents, l1_biocons, l1_refs, l1_strains, l1_chems, evidence_filter)
    if 'STRAIN' in level_two_types:
        l2_strains_all = get_related_strains(l1_bioents, l1_biocons, l1_refs, l1_expts, l1_chems, evidence_filter)
    if 'CHEMICAL' in level_two_types:
        l2_chems_all = get_related_chemicals(l1_bioents, l1_biocons, l1_refs, l1_expts, l1_strains, evidence_filter)  
        
    l2_refs = [k for k,v in l2_refs_all.iteritems() if l2_filter(k,v)]
    l2_bioents = [k for k,v in l2_bioents_all.iteritems() if l2_filter(k,v)]
    l2_biocons = [k for k,v in l2_biocons_all.iteritems() if l2_filter(k,v)]
    l2_expts = [k for k,v in l2_expts_all.iteritems() if l2_filter(k,v)]
    l2_strains = [k for k,v in l2_strains_all.iteritems() if l2_filter(k,v)]
    l2_chems = [k for k,v in l2_chems_all.iteritems() if l2_filter(k,v)]
    
    nodes = dict()
    
    nodes.update([create_node(s, -1) for s in seed_refs])
    nodes.update([create_node(s, -1) for s in seed_bioents])
    nodes.update([create_node(s, -1) for s in seed_biocons])
    nodes.update([create_node(s, -1) for s in seed_expts])
    nodes.update([create_node(s, -1) for s in seed_strains])
    nodes.update([create_node(s, -1) for s in seed_chems])
    
    nodes.update([create_node(s, 1) for s in l1_refs])
    nodes.update([create_node(s, 1) for s in l1_bioents])
    nodes.update([create_node(s, 1) for s in l1_biocons])
    nodes.update([create_node(s, 1) for s in l1_expts])
    nodes.update([create_node(s, 1) for s in l1_strains])
    nodes.update([create_node(s, 1) for s in l1_chems])
    
    nodes.update([create_node(s, 1) for s in l2_refs])
    nodes.update([create_node(s, 1) for s in l2_bioents])
    nodes.update([create_node(s, 1) for s in l2_biocons])
    nodes.update([create_node(s, 1) for s in l2_expts])
    nodes.update([create_node(s, 1) for s in l2_strains])
    nodes.update([create_node(s, 1) for s in l2_chems])
    
    for s in seed_refs:
        nodes[get_id(s)]['highlight'] = True
    for s in seed_bioents:
        nodes[get_id(s)]['highlight'] = True
    for s in seed_biocons:
        nodes[get_id(s)]['highlight'] = True
    for s in seed_expts:
        nodes[get_id(s)]['highlight'] = True
    for s in seed_strains:
        nodes[get_id(s)]['highlight'] = True
    for s in seed_chems:
        nodes[get_id(s)]['highlight'] = True
    
    edges = dict()
    for k,v in l1_refs_all.iteritems():
        source = k
        if get_id(source) in nodes:
            sinks = set([x for x in v if get_id(x) in nodes])
            edges.update([create_edge(source, sink, 1) for sink in sinks])
    for k,v in l1_bioents_all.iteritems():
        source = k
        if get_id(source) in nodes:
            sinks = set([x for x in v if get_id(x) in nodes])
            edges.update([create_edge(source, sink, 1) for sink in sinks])
    for k,v in l1_biocons_all.iteritems():
        source = k
        if get_id(source) in nodes:
            sinks = set([x for x in v if get_id(x) in nodes])
            edges.update([create_edge(source, sink, 1) for sink in sinks])
    for k,v in l1_expts_all.iteritems():
        source = k
        if get_id(source) in nodes:
            sinks = set([x for x in v if get_id(x) in nodes])
            edges.update([create_edge(source, sink, 1) for sink in sinks])
    for k,v in l1_strains_all.iteritems():
        source = k
        if get_id(source) in nodes:
            sinks = set([x for x in v if get_id(x) in nodes])
            edges.update([create_edge(source, sink, 1) for sink in sinks])
    for k,v in l1_chems_all.iteritems():
        source = k
        if get_id(source) in nodes:
            sinks = set([x for x in v if get_id(x) in nodes])
            edges.update([create_edge(source, sink, 1) for sink in sinks])
            
    for k,v in l2_refs_all.iteritems():
        source = k
        if get_id(source) in nodes:
            sinks = set([x for x in v if get_id(x) in nodes])
            edges.update([create_edge(source, sink, 1) for sink in sinks])
    for k,v in l2_bioents_all.iteritems():
        source = k
        if get_id(source) in nodes:
            sinks = set([x for x in v if get_id(x) in nodes])
            edges.update([create_edge(source, sink, 1) for sink in sinks])
    for k,v in l2_biocons_all.iteritems():
        source = k
        if get_id(source) in nodes:
            sinks = set([x for x in v if get_id(x) in nodes])
            edges.update([create_edge(source, sink, 1) for sink in sinks])
    for k,v in l2_expts_all.iteritems():
        source = k
        if get_id(source) in nodes:
            sinks = set([x for x in v if get_id(x) in nodes])
            edges.update([create_edge(source, sink, 1) for sink in sinks])
    for k,v in l2_strains_all.iteritems():
        source = k
        if get_id(source) in nodes:
            sinks = set([x for x in v if get_id(x) in nodes])
            edges.update([create_edge(source, sink, 1) for sink in sinks])
    for k,v in l2_chems_all.iteritems():
        source = k
        if get_id(source) in nodes:
            sinks = set([x for x in v if get_id(x) in nodes])
            edges.update([create_edge(source, sink, 1) for sink in sinks])
            
    print len(nodes)
    print len(edges)
    if len(nodes) > 250:
        return {'dataSchema':schema, 'data': {'nodes': [], 'edges': []}}
    else:
        return {'dataSchema':schema, 'data': {'nodes': nodes.values(), 'edges': edges.values()}}
    
        
def get_related_references(bioents, biocons, experiments, strains, chemicals, evidence_filter):
    bioent_evidence = set()
    biocon_evidence = set()
    experiment_evidence = set()
    strain_evidence = set()
    chemical_evidence = set()
    
    if bioents is not None and len(bioents) > 0:
        bioent_ids = [x.id for x in bioents]
        
        #query = DBSession.query(Goevidence).filter(Goevidence.bioent_id.in_(bioent_ids)).options(joinedload('reference'))
        #bioent_evidence.update(query.all())
        
        #query = DBSession.query(Phenoevidence).filter(Phenoevidence.bioent_id.in_(bioent_ids)).options(joinedload('reference'))
        #bioent_evidence.update(query.all())
        
        query = DBSession.query(Bioentevidence).filter(Bioentevidence.bioent_id.in_(bioent_ids)).options(joinedload('reference'))
        bioent_evidence.update(query.all())
        
    if biocons is not None and len(biocons) > 0:
        biocon_ids = [x.id for x in biocons]
        
        query = DBSession.query(Goevidence).filter(Goevidence.biocon_id.in_(biocon_ids)).options(joinedload('reference'))
        biocon_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.biocon_id.in_(biocon_ids)).options(joinedload('reference'))
        biocon_evidence.update(query.all())
        
    if experiments is not None and len(experiments) > 0:
        experiment_ids = [x.id for x in experiments]
        
        query = DBSession.query(Evidence).filter(Evidence.experiment_id.in_(experiment_ids)).options(joinedload('reference'))
        experiment_evidence.update(query.all())

    if strains is not None and len(strains) > 0:
        strain_ids = [x.id for x in strains]
        
        query = DBSession.query(Evidence).filter(Evidence.strain_id.in_(strain_ids)).options(joinedload('reference'))
        strain_evidence.update(query.all())   

    if chemicals is not None and len(chemicals) > 0:
        chemical_ids = [x.id for x in chemicals]
        
        query = DBSession.query(EvidenceChemical).filter(EvidenceChemical.chemical_id.in_(chemical_ids)).options(joinedload('evidence'), joinedload('evidence.reference'))
        chemical_evidence.update(query.all())  
        
    reference_edges = {}
    for evidence in bioent_evidence:
        if evidence_filter(evidence):
            reference = evidence.reference
            if reference in reference_edges:
                reference_edges[reference].add(evidence.bioentity)
            else:
                reference_edges[reference] = set([evidence.bioentity])
    
    for evidence in biocon_evidence:
        if evidence_filter(evidence):
            reference = evidence.reference
            if reference in reference_edges:
                reference_edges[reference].add(evidence.bioconcept)
            else:
                reference_edges[reference] = set([evidence.bioconcept])
            
    for evidence in experiment_evidence:
        if evidence_filter(evidence):
            reference = evidence.reference
            if reference in reference_edges:
                reference_edges[reference].add(evidence.experiment)
            else:
                reference_edges[reference] = set([evidence.experiment])

    for evidence in strain_evidence:
        if evidence_filter(evidence):
            reference = evidence.reference
            if reference in reference_edges:
                reference_edges[reference].add(evidence.strain)
            else:
                reference_edges[reference] = set([evidence.strain])
            
    for chemevidence in chemical_evidence:
        chemical = chemevidence.chemical
        evidence = chemevidence.evidence
        if evidence_filter(evidence):
            reference = evidence.reference
            if reference in reference_edges:
                reference_edges[reference].add(chemical)
            else:
                reference_edges[reference] = set([chemical])
            
    return reference_edges

def get_related_experiments(bioents, biocons, references, strains, chemicals, evidence_filter):
    bioent_evidence = set()
    biocon_evidence = set()
    reference_evidence = set()
    strain_evidence = set()
    chemical_evidence = set()
    
    if bioents is not None and len(bioents) > 0:
        bioent_ids = [x.id for x in bioents]
        
        query = DBSession.query(Goevidence).filter(Goevidence.bioent_id.in_(bioent_ids)).options(joinedload('experiment'))
        bioent_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.bioent_id.in_(bioent_ids)).options(joinedload('experiment'))
        bioent_evidence.update(query.all())
        
        query = DBSession.query(Bioentevidence).filter(Bioentevidence.bioent_id.in_(bioent_ids)).options(joinedload('experiment'))
        bioent_evidence.update(query.all())
        
    if biocons is not None and len(biocons) > 0:
        biocon_ids = [x.id for x in biocons]
        
        query = DBSession.query(Goevidence).filter(Goevidence.biocon_id.in_(biocon_ids)).options(joinedload('experiment'))
        biocon_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.biocon_id.in_(biocon_ids)).options(joinedload('experiment'))
        biocon_evidence.update(query.all())
        
    if references is not None and len(references) > 0:
        reference_ids = [x.id for x in references]
        
        query = DBSession.query(Evidence).filter(Evidence.reference_id.in_(reference_ids)).options(joinedload('experiment'))
        reference_evidence.update(query.all())

    if strains is not None and len(strains) > 0:
        strain_ids = [x.id for x in strains]
        
        query = DBSession.query(Evidence).filter(Evidence.strain_id.in_(strain_ids)).options(joinedload('experiment'))
        strain_evidence.update(query.all())   

    if chemicals is not None and len(chemicals) > 0:
        chemical_ids = [x.id for x in chemicals]
        
        query = DBSession.query(EvidenceChemical).filter(EvidenceChemical.chemical_id.in_(chemical_ids)).options(joinedload('evidence'), joinedload('evidence.experiment'))
        chemical_evidence.update(query.all())  
        
    experiment_edges = {}
    for evidence in bioent_evidence:
        if evidence_filter(evidence):
            experiment = evidence.experiment
            if experiment in experiment_edges:
                experiment_edges[experiment].add(evidence.bioentity)
            else:
                experiment_edges[experiment] = set([evidence.bioentity])
    
    for evidence in biocon_evidence:
        if evidence_filter(evidence):
            experiment = evidence.experiment
            if experiment in experiment_edges:
                experiment_edges[experiment].add(evidence.bioconcept)
            else:
                experiment_edges[experiment] = set([evidence.bioconcept])
            
    for evidence in reference_evidence:
        if evidence_filter(evidence):
            experiment = evidence.experiment
            if experiment in experiment_edges:
                experiment_edges[experiment].add(evidence.reference)
            else:
                experiment_edges[experiment] = set([evidence.reference])

    for evidence in strain_evidence:
        if evidence_filter(evidence):
            experiment = evidence.experiment
            if experiment in experiment_edges:
                experiment_edges[experiment].add(evidence.strain)
            else:
                experiment_edges[experiment] = set([evidence.strain])
            
    for chemevidence in chemical_evidence:
        chemical = chemevidence.chemical
        evidence = chemevidence.evidence
        if evidence_filter(evidence):
            experiment = evidence.experiment
            if experiment in experiment_edges:
                experiment_edges[experiment].add(chemical)
            else:
                experiment_edges[experiment] = set([chemical])
            
    return experiment_edges

def get_related_strains(bioents, biocons, references, experiments, chemicals, evidence_filter):
    bioent_evidence = set()
    biocon_evidence = set()
    reference_evidence = set()
    experiment_evidence = set()
    chemical_evidence = set()
    
    if bioents is not None and len(bioents) > 0:
        bioent_ids = [x.id for x in bioents]
        
        query = DBSession.query(Goevidence).filter(Goevidence.bioent_id.in_(bioent_ids)).options(joinedload('strain'))
        bioent_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.bioent_id.in_(bioent_ids)).options(joinedload('strain'))
        bioent_evidence.update(query.all())
        
        query = DBSession.query(Bioentevidence).filter(Bioentevidence.bioent_id.in_(bioent_ids)).options(joinedload('strain'))
        bioent_evidence.update(query.all())
        
    if biocons is not None and len(biocons) > 0:
        biocon_ids = [x.id for x in biocons]
        
        query = DBSession.query(Goevidence).filter(Goevidence.biocon_id.in_(biocon_ids)).options(joinedload('strain'))
        biocon_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.biocon_id.in_(biocon_ids)).options(joinedload('strain'))
        biocon_evidence.update(query.all())
        
    if references is not None and len(references) > 0:
        reference_ids = [x.id for x in references]
        
        query = DBSession.query(Evidence).filter(Evidence.reference_id.in_(reference_ids)).options(joinedload('strain'))
        reference_evidence.update(query.all())

    if experiments is not None and len(experiments) > 0:
        experiment_ids = [x.id for x in experiments]
        
        query = DBSession.query(Evidence).filter(Evidence.experiment_id.in_(experiment_ids)).options(joinedload('strain'))
        experiment_evidence.update(query.all())   

    if chemicals is not None and len(chemicals) > 0:
        chemical_ids = [x.id for x in chemicals]
        
        query = DBSession.query(EvidenceChemical).filter(EvidenceChemical.chemical_id.in_(chemical_ids)).options(joinedload('evidence'), joinedload('evidence.strain'))
        chemical_evidence.update(query.all())  
        
    strain_edges = {}
    for evidence in bioent_evidence:
        if evidence_filter(evidence):
            strain = evidence.strain
            if strain in strain_edges:
                strain_edges[strain].add(evidence.bioentity)
            else:
                strain_edges[strain] = set([evidence.bioentity])
    
    for evidence in biocon_evidence:
        if evidence_filter(evidence):
            strain = evidence.strain
            if strain in strain_edges:
                strain_edges[strain].add(evidence.bioconcept)
            else:
                strain_edges[strain] = set([evidence.bioconcept])
            
    for evidence in reference_evidence:
        if evidence_filter(evidence):
            strain = evidence.strain
            if strain in strain_edges:
                strain_edges[strain].add(evidence.reference)
            else:
                strain_edges[strain] = set([evidence.reference])

    for evidence in experiment_evidence:
        if evidence_filter(evidence):
            strain = evidence.strain
            if strain in strain_edges:
                strain_edges[strain].add(evidence.experiment)
            else:
                strain_edges[strain] = set([evidence.experiment])
            
    for chemevidence in chemical_evidence:
        chemical = chemevidence.chemical
        evidence = chemevidence.evidence
        if evidence_filter(evidence):
            strain = evidence.strain
            if strain in strain_edges:
                strain_edges[strain].add(chemical)
            else:
                strain_edges[strain] = set([chemical])
            
    return strain_edges

def get_related_bioents(biocons, references, experiments, strains, chemicals, evidence_filter):
    biocon_evidence = set()
    reference_evidence = set()
    experiment_evidence = set()
    strain_evidence = set()
    chemical_evidence = set()
        
    if biocons is not None and len(biocons) > 0:
        biocon_ids = [x.id for x in biocons]
        
        query = DBSession.query(Goevidence).filter(Goevidence.biocon_id.in_(biocon_ids)).options(joinedload('bioentity'))
        biocon_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.biocon_id.in_(biocon_ids)).options(joinedload('bioentity'))
        biocon_evidence.update(query.all())
        
    if references is not None and len(references) > 0:
        reference_ids = [x.id for x in references]
        
        query = DBSession.query(Goevidence).filter(Goevidence.reference_id.in_(reference_ids)).options(joinedload('bioentity'))
        reference_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.reference_id.in_(reference_ids)).options(joinedload('bioentity'))
        reference_evidence.update(query.all())
        
        query = DBSession.query(Bioentevidence).filter(Bioentevidence.reference_id.in_(reference_ids)).options(joinedload('bioentity'))
        reference_evidence.update(query.all())
        
    if experiments is not None and len(experiments) > 0:
        experiment_ids = [x.id for x in experiments]
        
        query = DBSession.query(Goevidence).filter(Goevidence.experiment_id.in_(experiment_ids)).options(joinedload('bioentity'))
        experiment_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.experiment_id.in_(experiment_ids)).options(joinedload('bioentity'))
        experiment_evidence.update(query.all())
        
        query = DBSession.query(Bioentevidence).filter(Bioentevidence.experiment_id.in_(experiment_ids)).options(joinedload('bioentity'))
        experiment_evidence.update(query.all())

    if strains is not None and len(strains) > 0:
        strain_ids = [x.id for x in strains]
        
        query = DBSession.query(Goevidence).filter(Goevidence.strain_id.in_(strain_ids)).options(joinedload('bioentity'))
        strain_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.strain_id.in_(strain_ids)).options(joinedload('bioentity'))
        strain_evidence.update(query.all())
        
        query = DBSession.query(Bioentevidence).filter(Bioentevidence.strain_id.in_(strain_ids)).options(joinedload('bioentity'))
        strain_evidence.update(query.all())
        
    if chemicals is not None and len(chemicals) > 0:
        chemical_ids = [x.id for x in chemicals]
        
        query = DBSession.query(EvidenceChemical).filter(EvidenceChemical.chemical_id.in_(chemical_ids)).options(joinedload('evidence'))
        chemical_evidence.update(query.all())  
        
    bioent_edges = {}
    for evidence in biocon_evidence:
        if evidence_filter(evidence):
            bioent = evidence.bioentity
            if bioent in bioent_edges:
                bioent_edges[bioent].add(evidence.bioconcept)
            else:
                bioent_edges[bioent] = set([evidence.bioconcept])
     
    for evidence in reference_evidence:
        if evidence_filter(evidence):
            bioent = evidence.bioentity
            if bioent in bioent_edges:
                bioent_edges[bioent].add(evidence.reference)
            else:
                bioent_edges[bioent] = set([evidence.reference])
           
    for evidence in experiment_evidence:
        if evidence_filter(evidence):
            bioent = evidence.bioentity
            if bioent in bioent_edges:
                bioent_edges[bioent].add(evidence.experiment)
            else:
                bioent_edges[bioent] = set([evidence.experiment])

    for evidence in strain_evidence:
        if evidence_filter(evidence):
            bioent = evidence.bioentity
            if bioent in bioent_edges:
                bioent_edges[bioent].add(evidence.strain)
            else:
                bioent_edges[bioent] = set([evidence.strain])
                
    for chemevidence in chemical_evidence:
        chemical = chemevidence.chemical
        evidence = chemevidence.evidence
        if evidence_filter(evidence):
            bioent = evidence.bioentity
            if bioent in bioent_edges:
                bioent_edges[bioent].add(chemical)
            else:
                bioent_edges[bioent] = set([chemical])
            
    return bioent_edges

def get_related_biocons(bioents, references, experiments, strains, chemicals, evidence_filter):
    bioent_evidence = set()
    reference_evidence = set()
    experiment_evidence = set()
    strain_evidence = set()
    chemical_evidence = set()
        
    if bioents is not None and len(bioents) > 0:
        bioent_ids = [x.id for x in bioents]
        
        query = DBSession.query(Goevidence).filter(Goevidence.bioent_id.in_(bioent_ids)).options(joinedload('bioconcept'))
        bioent_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.bioent_id.in_(bioent_ids)).options(joinedload('bioconcept'))
        bioent_evidence.update(query.all())
        
    if references is not None and len(references) > 0:
        reference_ids = [x.id for x in references]
        
        query = DBSession.query(Goevidence).filter(Goevidence.reference_id.in_(reference_ids)).options(joinedload('bioconcept'))
        reference_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.reference_id.in_(reference_ids)).options(joinedload('bioconcept'))
        reference_evidence.update(query.all())
        
    if experiments is not None and len(experiments) > 0:
        experiment_ids = [x.id for x in experiments]
        
        query = DBSession.query(Goevidence).filter(Goevidence.experiment_id.in_(experiment_ids)).options(joinedload('bioconcept'))
        experiment_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.experiment_id.in_(experiment_ids)).options(joinedload('bioconcept'))
        experiment_evidence.update(query.all())

    if strains is not None and len(strains) > 0:
        strain_ids = [x.id for x in strains]
        
        query = DBSession.query(Goevidence).filter(Goevidence.strain_id.in_(strain_ids)).options(joinedload('bioconcept'))
        strain_evidence.update(query.all())
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.strain_id.in_(strain_ids)).options(joinedload('bioconcept'))
        strain_evidence.update(query.all())
        
    if chemicals is not None and len(chemicals) > 0:
        chemical_ids = [x.id for x in chemicals]
        
        query = DBSession.query(EvidenceChemical).filter(EvidenceChemical.chemical_id.in_(chemical_ids)).options(joinedload('evidence'))
        chemical_evidence.update(query.all())  
        
    biocon_edges = {}
    for evidence in bioent_evidence:
        if evidence_filter(evidence):
            biocon = evidence.bioconcept
            if biocon in biocon_edges:
                biocon_edges[biocon].add(evidence.bioentity)
            else:
                biocon_edges[biocon] = set([evidence.bioentity])
     
    for evidence in reference_evidence:
        if evidence_filter(evidence):
            biocon = evidence.bioconcept
            if biocon in biocon_edges:
                biocon_edges[biocon].add(evidence.reference)
            else:
                biocon_edges[biocon] = set([evidence.reference])
           
    for evidence in experiment_evidence:
        if evidence_filter(evidence):
            biocon = evidence.bioconcept
            if biocon in biocon_edges:
                biocon_edges[biocon].add(evidence.experiment)
            else:
                biocon_edges[biocon] = set([evidence.experiment])

    for evidence in strain_evidence:
        if evidence_filter(evidence):
            biocon = evidence.bioconcept
            if biocon in biocon_edges:
                biocon_edges[biocon].add(evidence.strain)
            else:
                biocon_edges[biocon] = set([evidence.strain])
            
    for chemevidence in chemical_evidence:
        chemical = chemevidence.chemical
        evidence = chemevidence.evidence
        if evidence_filter(evidence):
            biocon = evidence.bioconcept
            if biocon in biocon_edges:
                biocon_edges[biocon].add(chemical)
            else:
                biocon_edges[biocon] = set([chemical])
            
    return biocon_edges
    
def get_related_chemicals(bioents, biocons, references, experiments, strains, evidence_filter):
    bioent_evidence = set()
    biocon_evidence = set()
    reference_evidence = set()
    experiment_evidence = set()
    strain_evidence = set()
    
    if bioents is not None and len(bioents) > 0:
        bioent_ids = [x.id for x in bioents]
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.bioent_id.in_(bioent_ids)).options(joinedload('ev_chemicals'))
        bioent_evidence.update(query.all())
        
    if biocons is not None and len(biocons) > 0:
        biocon_ids = [x.id for x in biocons]
        
        query = DBSession.query(Phenoevidence).filter(Phenoevidence.biocon_id.in_(biocon_ids)).options(joinedload('ev_chemicals'))
        biocon_evidence.update(query.all())
        
    if experiments is not None and len(experiments) > 0:
        experiment_ids = [x.id for x in experiments]
        
        query = DBSession.query(Evidence).filter(Evidence.experiment_id.in_(experiment_ids)).options(joinedload('ev_chemicals'))
        experiment_evidence.update(query.all())

    if strains is not None and len(strains) > 0:
        strain_ids = [x.id for x in strains]
        
        query = DBSession.query(Evidence).filter(Evidence.strain_id.in_(strain_ids)).options(joinedload('ev_chemicals'))
        strain_evidence.update(query.all())   

    if references is not None and len(references) > 0:
        reference_ids = [x.id for x in references]
        
        query = DBSession.query(Evidence).filter(Evidence.reference_id.in_(reference_ids)).options(joinedload('ev_chemicals'))
        reference_evidence.update(query.all())   
        
    chemical_edges = {}
    for evidence in bioent_evidence:
        if evidence_filter(evidence):
            chemicals = evidence.chemicals
            for chemical in chemicals:
                if chemical in chemical_edges:
                    chemical_edges[chemical].add(evidence.bioentity)
                else:
                    chemical_edges[chemical] = set([evidence.bioentity])
    
    for evidence in biocon_evidence:
        if evidence_filter(evidence):
            chemicals = evidence.chemicals
            for chemical in chemicals:
                if chemical in chemical_edges:
                    chemical_edges[chemical].add(evidence.bioconcept)
                else:
                    chemical_edges[chemical] = set([evidence.bioconcept])
            
    for evidence in experiment_evidence:
        if evidence_filter(evidence):
            chemicals = evidence.chemicals
            for chemical in chemicals:
                if chemical in chemical_edges:
                    chemical_edges[chemical].add(evidence.experiment)
                else:
                    chemical_edges[chemical] = set([evidence.experiment])

    for evidence in strain_evidence:
        if evidence_filter(evidence):
            chemicals = evidence.chemicals
            for chemical in chemicals:
                if chemical in chemical_edges:
                    chemical_edges[chemical].add(evidence.strain)
                else:
                    chemical_edges[chemical] = set([evidence.strain])
            
    for evidence in reference_evidence:
        if evidence_filter(evidence):
            chemicals = evidence.chemicals
            for chemical in chemicals:
                if chemical in chemical_edges:
                    chemical_edges[chemical].add(evidence.reference)
                else:
                    chemical_edges[chemical] = set([evidence.reference])
            
    return chemical_edges    

def get_id(bio):
    return bio.type + str(bio.id)

if __name__ == "__main__":
    bioents = [get_bioent('YHR044C', 'LOCUS')]
    biocons = [get_biocon('increased_resistance_to_chemicals_in_repressible_mutant', 'PHENOTYPE')]
    references = [get_reference('3295876')]
    experiments = [get_experiment('heterozygous_diploid,_systematic_mutation_set')]
    strains = [get_strain('CEN.PK')]
    chemicals = [get_chemical('boric_acid')]
    
    l1_filter = lambda x, y: True
    l2_filter = lambda x, y: len(y) > 1
    
    create_graph(['BIOENTITY'], ['REFERENCE'], l1_filter, l2_filter, seed_biocons=biocons) 

def weed_out_by_evidence(neighbors, neighbor_evidence_count, max_count=100):
    if len(neighbors) < max_count:
        return neighbors, 1
    
    evidence_to_neighbors = {}
    for neigh in neighbors:
        evidence_count = neighbor_evidence_count[neigh]
        if evidence_count in evidence_to_neighbors:
            evidence_to_neighbors[evidence_count].append(neigh)
        else:
            evidence_to_neighbors[evidence_count] = [neigh]
            
    sorted_keys = sorted(evidence_to_neighbors.keys(), reverse=True)
    keep = []
    min_evidence_count = max(sorted_keys)
    for key in sorted_keys:
        ns = evidence_to_neighbors[key]
        if len(keep) + len(ns) < max_count:
            keep.extend(ns)
            min_evidence_count = key
    return keep, min_evidence_count
    
def create_interaction_graph(bioent):
        
    bioents = set()
    bioent_to_evidence = {}

    #bioents.update([interaction.get_opposite(bioent) for interaction in get_biorels('INTERACTION', bioent)])
    bioent_to_evidence.update([(interaction.get_opposite(bioent), interaction.evidence_count) for interaction in get_biorels('PHYSICAL_INTERACTION', bioent.id)])
    bioents.update(bioent_to_evidence.keys())

    bioents.add(bioent)
    max_evidence_cutoff = 0
    if len(bioent_to_evidence.values()) > 0:
        max_evidence_cutoff = max(bioent_to_evidence.values())
    bioent_to_evidence[bioent] = max_evidence_cutoff
    
    usable_bioents, min_evidence_count = weed_out_by_evidence(bioents, bioent_to_evidence)
    
    nodes = [create_interaction_node(b, bioent_to_evidence[b], bioent) for b in usable_bioents]
    id_to_bioent = dict([(bioent.id, bioent) for bioent in usable_bioents])
    
    node_ids = set([b.id for b in usable_bioents])
    
    interactions = get_interactions(node_ids)

    edges = []
    for interaction in interactions:
        if interaction.evidence_count >= min_evidence_count and interaction.source_bioent_id in node_ids and interaction.sink_bioent_id in node_ids:
            source_bioent = id_to_bioent[interaction.source_bioent_id]
            sink_bioent = id_to_bioent[interaction.sink_bioent_id]
            edges.append(create_interaction_edge(interaction, source_bioent, sink_bioent, interaction.evidence_count)) 
        
    return {'dataSchema':interaction_schema, 'data': {'nodes': nodes, 'edges': edges}, 
            'min_evidence_cutoff':min_evidence_count, 'max_evidence_cutoff':max_evidence_cutoff}

'''
-------------------------------Utils---------------------------------------
'''  


