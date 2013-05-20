from model_new_schema.bioconcept import Bioconcept, BioconAncestor, \
    BioconRelation
from model_new_schema.bioentity import Bioentity, Gene, BioentRelation
from model_new_schema.biofact import Biofact
from model_new_schema.go import Goevidence, Go
from model_new_schema.interaction import Interevidence, Interaction
from model_new_schema.phenotype import Phenoevidence, Phenotype
from model_new_schema.reference import Reference, Author
from model_new_schema.search import Typeahead
from model_new_schema.sequence import Sequence
from sgd2.models import DBSession
from sqlalchemy.orm import joinedload, subqueryload_all
from sqlalchemy.orm.util import with_polymorphic
from sqlalchemy.sql.expression import func
import math

biocon_type_to_class = {'PHENOTYPE':Phenotype, 'GO':Go}
biorel_type_to_class = {'INTERACTION':Interaction}
def get_biocon(biocon_name, biocon_type):
    biocon = DBSession.query(with_polymorphic(Bioconcept, [biocon_type_to_class[biocon_type]])).filter(Bioconcept.biocon_type==biocon_type).filter(Bioconcept.official_name==biocon_name).first()
    return biocon

def get_biocon_id(biocon_name, biocon_type):
    biocon = DBSession.query(Bioconcept).filter(Bioconcept.biocon_type==biocon_type).filter(Bioconcept.official_name==biocon_name).first()
    if biocon is not None:
        return biocon.id
    return None

def get_bioent(bioent_name):
    bioent = DBSession.query(Bioentity).filter(Bioentity.official_name==bioent_name).first()
    return bioent

def get_biorel(biorel_name, biorel_type):
    biorel = DBSession.query(BioentRelation).filter(BioentRelation.biorel_type==biorel_type).filter(BioentRelation.official_name==biorel_name).first()
    return biorel

def get_reference(reference_name):
    reference = None
    try:
        float(reference_name)
        reference = DBSession.query(Reference).options(joinedload('author_references'), joinedload('author_references.author')).filter(Reference.pubmed_id == reference_name).first() 
        if reference is None:
            reference = DBSession.query(Reference).filter(Reference.id == reference_name).first()
    except:
        pass
    if reference is None:
        reference = DBSession.query(Reference).filter(Reference.dbxref_id == reference_name).first() 
    return reference

def get_author(author_name):
    author = DBSession.query(Author).options(joinedload('author_references')).filter(Author.name==author_name).first()
    return author
 

def get_biorels(biorel_type, bioent):
    biorel_class = biorel_type_to_class[biorel_type]
    querycls = with_polymorphic(BioentRelation, [biorel_class])
    biorels = set(DBSession.query(querycls).options(joinedload(querycls.source_bioent), joinedload(querycls.sink_bioent)).filter(querycls.biorel_type==biorel_type).filter(querycls.source_bioent_id == bioent.id))
    biorels.update(DBSession.query(querycls).options(joinedload(querycls.source_bioent), joinedload(querycls.sink_bioent)).filter(querycls.biorel_type==biorel_type).filter(querycls.sink_bioent_id == bioent.id))
    
    #return [biorel for biorel in bioent.biorelations if biorel.biorel_type == biorel_type]
    return biorels

#Used for interaction graph
def get_interactions(bioent_ids):
    #bioentbiorels = DBSession.query(BioentBiorel).options(joinedload(BioentBiorel.biorel)).filter(BioentBiorel.bioent_id.in_(bioent_ids))
    #interactions = [bioentbiorel.biorel for bioentbiorel in bioentbiorels if bioentbiorel.biorel.biorel_type=='INTERACTION' and bioentbiorel.biorel.source_bioent_id in bioent_ids and bioentbiorel.biorel.sink_bioent_id in bioent_ids]
    querycls = with_polymorphic(BioentRelation, [Interaction])
    
    interactions = set(DBSession.query(querycls).filter(querycls.biorel_type=='INTERACTION').filter(querycls.source_bioent_id.in_(bioent_ids)).all())
    interactions.update(DBSession.query(querycls).filter(querycls.biorel_type=='INTERACTION').filter(querycls.sink_bioent_id.in_(bioent_ids)).all())
    return interactions

def get_biofacts(biocon_type, biocon=None, bioent=None):
    if biocon is None and bioent is None:
        raise Exception()
    
    query = DBSession.query(Biofact).options(joinedload('bioentity'), joinedload('bioconcept')).filter(Biofact.biocon_type==biocon_type)
    if bioent is not None:
        query = query.filter(Biofact.bioent_id==bioent.id)
    if biocon is not None:
        query = query.filter(Biofact.biocon_id==biocon.id)
    return query.all()

def get_biocon_family(biocon):
    biocon_class = biocon_type_to_class[biocon.biocon_type]
    family = set([biocon])
    biocon_ancs = DBSession.query(BioconAncestor).options(joinedload(BioconAncestor.ancestor_biocon.of_type(biocon_class))).filter(BioconAncestor.child_id==biocon.id).all()
    family.update([biocon_anc.ancestor_biocon for biocon_anc in biocon_ancs])
    
    biocon_children = DBSession.query(BioconRelation).options(joinedload(BioconRelation.child_biocon.of_type(biocon_class))).filter(BioconRelation.parent_id==biocon.id).all()
    family.update([biocon_child.child_biocon for biocon_child in biocon_children])
    
    child_ids = set([biocon_child.child_biocon.id for biocon_child in biocon_children])
    all_ids = set([b.id for b in family])
    
    return {'family':family, 'child_ids':child_ids, 'all_ids':all_ids}

def get_biocon_biocons(biocon_ids):
    biocon_ids = set(biocon_ids)
    related_biocon_biocons = set()
    
    ancestor_in_list = DBSession.query(BioconRelation).filter(BioconRelation.parent_biocon_id.in_(biocon_ids)).all()
    related_biocon_biocons.update([biocon_biocon for biocon_biocon in ancestor_in_list if biocon_biocon.child_biocon_id in biocon_ids])
    
    child_in_list = DBSession.query(BioconRelation).filter(BioconRelation.child_biocon_id.in_(biocon_ids)).all()
    related_biocon_biocons.update([biocon_biocon for biocon_biocon in child_in_list if biocon_biocon.parent_biocon_id in biocon_ids])
    
    return related_biocon_biocons

def get_related_biofacts(biocon_ids, biocon_type):
    biocon_class = biocon_type_to_class[biocon_type]
    biofacts = DBSession.query(Biofact).options(joinedload('bioentity'), joinedload(Biofact.bioconcept.of_type(biocon_class))).filter(Biofact.biocon_id.in_(biocon_ids)).all()
    return biofacts

#Get Evidence
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
def get_go_evidence(bioent_id=None, biocon_id=None, reference_id=None):
    query = DBSession.query(Goevidence).options(joinedload('reference'), joinedload(Goevidence.bioentity), joinedload(Goevidence.goterm))
    if bioent_id is not None:
        query = query.filter(Goevidence.bioent_id==bioent_id)
    if biocon_id is not None:
        query = query.filter(Goevidence.biocon_id==biocon_id)
    if reference_id is not None:
        query = query.filter(Goevidence.reference_id==reference_id)
    
    evidences = query.all()
    return evidences

def get_phenotype_evidence(bioent_id=None, biocon_id=None, reference_id=None):
    query = DBSession.query(Phenoevidence).options(joinedload('reference'), joinedload('gene'), joinedload('phenotype'))
    if bioent_id is not None:
        query = query.filter(Phenoevidence.bioent_id==bioent_id)
    if biocon_id is not None:
        query = query.filter(Phenoevidence.biocon_id==biocon_id)
    if reference_id is not None:
        query = query.filter(Phenoevidence.reference_id==reference_id)
    
    evidences = query.all()
    return evidences

def get_interaction_evidence(biorels):
    biorel_ids = [biorel.id for biorel in biorels]
    def f(chunk_biorel_ids):
        return DBSession.query(Interevidence).options(joinedload('reference')).filter(Interevidence.biorel_id.in_(chunk_biorel_ids)).all()
    
    evidences = retrieve_in_chunks(biorel_ids, f)

    return evidences

def get_interaction_evidence_ref(reference):
    return set(DBSession.query(Interevidence).options(joinedload('reference'), joinedload('biorel')).filter(Interevidence.reference_id==reference.id).all())

def get_sequences(bioent):
    id_to_type = {}
    if bioent.bioent_type == 'GENE':
        id_to_type[bioent.id] = 'GENE'
        for transcript in bioent.transcripts:
            id_to_type[transcript.id] = 'TRANSCRIPT'
            id_to_type.update([(protein_id, 'PROTEIN') for protein_id in transcript.protein_ids])
    elif bioent.bioent_type == 'TRANSCRIPT':
        id_to_type[bioent.id] = 'TRANSCRIPT'
        id_to_type[bioent.gene_id] = 'GENE'
        id_to_type.update([(protein_id, 'PROTEIN') for protein_id in bioent.protein_ids])
    elif bioent.bioent_type == 'PROTEIN':
        id_to_type[bioent.id] = 'PROTEIN'
        id_to_type[bioent.transcript_id] = 'TRANSCRIPT'
        id_to_type[bioent.transcript.gene_id] = 'GENE'
         
    seqs = DBSession.query(Sequence).options(joinedload('seq_tags')).filter(Sequence.bioent_id.in_(id_to_type.keys())).all()
    return seqs, id_to_type;
    
def search(search_strs, bio_type):   
    for search_str in search_strs:  
        if bio_type != None:
            search_results = DBSession.query(Typeahead).filter(Typeahead.name == search_str.lower()).filter(Typeahead.bio_type == bio_type).all()        
        else:
            search_results = DBSession.query(Typeahead).filter(Typeahead.name == search_str.lower()).all()
    
    return search_results
        
def typeahead(search_str):
    possible = DBSession.query(Typeahead).filter(func.upper(Typeahead.name) == search_str).filter(Typeahead.use_for_typeahead == 'Y').all()
    return possible

def get_objects(search_results):
    tuple_to_obj = dict()
    bioent_ids = [search_result.bio_id for search_result in search_results if search_result.bio_type == 'GENE']
    biocon_ids = [search_result.bio_id for search_result in search_results if search_result.bio_type in {'PHENOTYPE', 'GO'}]
    reference_ids = [search_result.bio_id for search_result in search_results if search_result.bio_type == 'REFERENCE']    
    
    if len(bioent_ids) > 0:
        bioents = DBSession.query(Bioentity).options(joinedload('aliases')).filter(Bioentity.id.in_(bioent_ids)).all()
        tuple_to_obj.update([((obj.type, obj.id), obj) for obj in bioents])
    
    if len(biocon_ids) > 0:
        biocons = DBSession.query(Bioconcept).filter(Bioconcept.id.in_(biocon_ids)).all()
        tuple_to_obj.update([((obj.type, obj.id), obj) for obj in biocons])
     
    if len(reference_ids) > 0:   
        refs = DBSession.query(Reference).options(joinedload('abst')).filter(Reference.id.in_(reference_ids)).all()
        tuple_to_obj.update([((obj.type, obj.id), obj) for obj in refs])
        
    ordered_objects = []    
    for result in search_results:
        ordered_objects.append(tuple_to_obj[(result.bio_type, result.bio_id)])
    return ordered_objects
        
        
        
    
    
    
