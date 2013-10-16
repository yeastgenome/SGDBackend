from model_new_schema.auxiliary import BioconceptAncestor, Biofact, \
    BioentityReference, Locustabs, Disambig
from model_new_schema.bioconcept import Bioconcept, BioconceptRelation
from model_new_schema.bioentity import Bioentity, Locus, Bioentityurl, Paragraph
from model_new_schema.chemical import Chemical
from model_new_schema.evelement import Experiment, Strain
from model_new_schema.evidence import EvidenceChemical
from model_new_schema.go import Goevidence, Go
from model_new_schema.interaction import Geninteractionevidence, \
    Physinteractionevidence
from model_new_schema.literature import Literatureevidence
from model_new_schema.misc import Url
from model_new_schema.phenotype import Phenotypeevidence, Phenotype
from model_new_schema.reference import Reference, Author, AuthorReference
from sgdbackend import DBSession
from sqlalchemy.orm import joinedload, subqueryload_all, subqueryload
from sqlalchemy.orm.util import with_polymorphic
from sqlalchemy.sql.expression import func, or_
import datetime
import math
import model_new_schema

session = DBSession

#Useful methods
def get_obj_ids(identifier, class_type=None, subclass_type=None, print_query=False):
    if identifier is None:
        return None
    
    query = session.query(Disambig).filter(Disambig.disambig_key==identifier.upper())
    if class_type is not None:
        query = query.filter(Disambig.class_type==class_type)
    if subclass_type is not None:
        query = query.filter(Disambig.subclass_type==subclass_type)
    disambigs = query.all()
    
    if print_query:
        print query
        
    if len(disambigs) > 0:
        return [(disambig.identifier, disambig.class_type, disambig.subclass_type) for disambig in disambigs]
    return None

def get_obj_id(identifier, class_type=None, subclass_type=None):
    objs_ids = get_obj_ids(identifier, class_type=class_type, subclass_type=subclass_type)
    obj_id = None if objs_ids is None or len(objs_ids) != 1 else objs_ids[0][0]
    return obj_id

def get_multi_obj_ids(identifiers, class_type=None, subclass_type=None, print_query=False):
    if identifiers is None:
        return None
    
    cleaned_up_ids = filter(None, [x.upper() for x in identifiers])
    query = session.query(Disambig).filter(Disambig.disambig_key.in_(cleaned_up_ids))
    if class_type is not None:
        query = query.filter(Disambig.class_type==class_type)
    if subclass_type is not None:
        query = query.filter(Disambig.subclass_type==subclass_type)
    disambigs = query.all()
    
    if print_query:
        print query
        
    disambig_dict = {}
    for disambig in disambigs:
        obj_id = disambig.identifier
        key = disambig.disambig_key
        
        if key in disambig_dict:
            disambig_dict[key].append(obj_id)
        else:
            disambig_dict[key] = [obj_id]
        
    return disambig_dict

#Used to create phenotype_overview table.
def get_chemical_id(chemical_name, print_query=False):
    query = session.query(Chemical).filter(Chemical.format_name==chemical_name)
    chemical = query.first()
    chemical_id = None
    if chemical is not None:
        chemical_id = chemical.id
    if print_query:
        print query
    return chemical_id

#Used to create chemical page.
def get_chemical(chemical_name, print_query=False):
    query = session.query(Chemical).filter(Chemical.format_name==chemical_name)
    chemical = query.first()
    return chemical

#Used to determine tabs on all pages.
def query_locustabs(bioentity_id, print_query=False):
    query = session.query(Locustabs).filter(Locustabs.id==bioentity_id)
    if print_query:
        print query
    return query.first()

#Used for Graph Views.
def get_experiment(experiment_name, print_query=False):
    query = session.query(Experiment).filter(Experiment.format_name==experiment_name)
    experiment = query.first()
    if print_query:
        print query
    return experiment

#Used for Graph Views.
def get_strain(strain_name, print_query=False):
    query = session.query(Strain).filter(Strain.format_name==strain_name)
    strain = query.first()
    if print_query:
        print query
    return strain

#Used for Interaction resources
def get_resources(category, bioent_id=None, print_query=False):
    if bioent_id is not None:
        query = session.query(Bioentityurl).filter(Bioentityurl.bioentity_id==bioent_id).filter(Bioentityurl.category==category)
    urls = query.all()
    if print_query:
        print query
    return urls

#Used for tests
def get_bioent_format_names(print_query=False):
    query = session.query(Bioentity.format_name)
    bioent_format_names = [x.format_name for x in query.all()]
    if print_query:
        print query
    return bioent_format_names

#Used for regulation_overview
def get_paragraph(bioent_id, class_type, print_query=False):
    query = session.query(Paragraph).filter(Paragraph.bioentity_id == bioent_id).filter(Paragraph.class_type == class_type)
    paragraph = query.first()
    if print_query:
        print query
    return paragraph

def get_disambigs(min_id, max_id, print_query=False):
    query = session.query(Disambig)
    if min_id is not None:
        query = query.filter(Disambig.id >= min_id)
    if max_id is not None:
        query = query.filter(Disambig.id < max_id)
    disambigs = query.all()
    if print_query:
        print_query
    return disambigs
        
#Used to break very large queries into a manageable size.
chunk_size = 500
def retrieve_in_chunks(ids, f):
    num_chunks = int(math.ceil(float(len(ids))/chunk_size))
    result = set()
    for i in range(0, num_chunks):
        min_index = i*chunk_size
        max_index = (i+1)*chunk_size
        if max_index > len(ids):
            chunk_ids = ids[min_index:]
        else:
            chunk_ids = ids[min_index:max_index]
        result.update(f(chunk_ids))
    return result
