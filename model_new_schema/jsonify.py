'''
Created on Dec 5, 2012

@author: kpaskov
'''
from model_new_schema import subclasses
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.bioentity_declarative import Bioentity
from model_new_schema.biorelation import Biorelation
import json
import jsonpickle

def jsonify_obj(obj, full=True):
    if isinstance(obj, Bioentity):
        pickled = jsonpickle.encode(bioent_jsonify(obj, full))
    elif isinstance(obj, Bioconcept):
        pickled = jsonpickle.encode(biocon_jsonify(obj, full))
    elif isinstance(obj, Biorelation):
        pickled = jsonpickle.encode(biorel_jsonify(obj, full))
    else:
        pickled = jsonpickle.encode(obj, max_depth=3)
    json_dict = json.loads(pickled)
    return json.dumps(json_dict, sort_keys=True, indent=4)
    
def biocon_jsonify(biocon, full=True):
    serialized_obj = dict()
    for field in [x for x in dir(biocon) if not x.startswith('_') and x != 'metadata']:
        serialized_obj[field] = biocon.__getattribute__(field)    
        
    if full:
        bioent_evidence = biocon.bioentity_evidence
        bioent_evidence_full_obj = []
        for k,v in bioent_evidence.iteritems():
            bioent_evidence_obj = {"BIOENTITY": bioent_jsonify(k, full=False), "EVIDENCE": map(lambda x: evidence_jsonify(x), v)}
            bioent_evidence_full_obj.append(bioent_evidence_obj)
        serialized_obj['BIOENTITY_EVIDENCE'] = bioent_evidence_obj
    
    
    to_remove = ['_sa_instance_state', 'bioent_biocons', 'bioentity', 'bioentity_evidence']
    for key in to_remove:
        if key in serialized_obj:
            del serialized_obj[key]
    return serialized_obj

def bioent_jsonify(bioent, full=True):
    serialized_obj = dict()
    for field in [x for x in dir(bioent) if not x.startswith('_') and x != 'metadata']:
        serialized_obj[field] = bioent.__getattribute__(field)
        
    if full:
        for subclass_name in subclasses(Bioconcept):
            biocon_evidence = bioent.__get_objects_for_subclass__(subclass_name, evidence=True)
            biocon_evidence_full_obj = []
            for k,v in biocon_evidence.iteritems():
                biocon_evidence_obj = {"BIOCONCEPT": biocon_jsonify(k, full=False), "EVIDENCE": map(lambda x: evidence_jsonify(x), v)}
                biocon_evidence_full_obj.append(biocon_evidence_obj)
            serialized_obj[subclass_name] = biocon_evidence_full_obj
        for subclass_name in subclasses(Biorelation):
            serialized_obj[subclass_name] = map(lambda x: biorel_jsonify(x, full=False), bioent.__get_objects_for_subclass__(subclass_name))
    
    to_remove = ['_sa_instance_state', 'bioconcept', 'biorel_source', 'biorel_sink', 'biorelation', 'bioconcept_evidence', 'bioent_biocon']
    for key in to_remove:
        if key in serialized_obj:
            del serialized_obj[key]
    return serialized_obj

def biorel_jsonify(biorel, full=True):
    serialized_obj = dict()
    for field in [x for x in dir(biorel) if not x.startswith('_') and x != 'metadata']:
        serialized_obj[field] = biorel.__getattribute__(field)  
        
    serialized_obj['source_bioent_name'] = biorel.source_bioent.name
    serialized_obj['sink_bioent_name'] = biorel.sink_bioent.name
        
    if full:
        serialized_obj['source_bioent'] = bioent_jsonify(biorel.source_bioent, full=False)
        serialized_obj['sink_bioent'] = bioent_jsonify(biorel.sink_bioent, full=False)
        
    to_remove = ['_sa_instance_state', 'source_bioent', 'source_bioent']
    for key in to_remove:
        if key in serialized_obj:
            del serialized_obj[key]
    return serialized_obj

def evidence_jsonify(evidence, full=False):
    serialized_obj = dict()
    for field in [x for x in dir(evidence) if not x.startswith('_') and x != 'metadata']:
        serialized_obj[field] = evidence.__getattribute__(field)  
        
    to_remove = ['_sa_instance_state', 'experiment', 'reference']
    for key in to_remove:
        if key in serialized_obj:
            del serialized_obj[key]
            