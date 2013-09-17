from model_new_schema.auxiliary import BioconceptAncestor, Biofact, BioentityReference
from model_new_schema.bioconcept import Bioconcept, BioconceptRelation
from model_new_schema.bioentity import Bioentity, Locus, Bioentityurl
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
from sgdbackend.models import DBSession
from sqlalchemy.orm import joinedload, subqueryload_all, subqueryload
from sqlalchemy.orm.util import with_polymorphic
from sqlalchemy.sql.expression import func, or_
import datetime
import math
import model_new_schema

session = DBSession

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
