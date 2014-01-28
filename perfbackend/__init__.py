from backend.backend_interface import BackendInterface
from go_enrichment import query_batter
from mpmath import ceil
from perfbackend_utils import set_up_logging
from pyramid.config import Configurator
from pyramid.renderers import JSONP
from pyramid.response import Response
from sqlalchemy import engine_from_config
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, joinedload, subqueryload
from sqlalchemy.schema import MetaData
from sqlalchemy.sql.expression import select
from zope.sqlalchemy import ZopeTransactionExtension
import json
import model_perf_schema
import uuid

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

class PerfBackend(BackendInterface):
    def __init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory):
        class Base(object):
            __table_args__ = {'schema': schema, 'extend_existing':True}
                
        model_perf_schema.SCHEMA = schema
        model_perf_schema.Base = declarative_base(cls=Base)

        engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), convert_unicode=True, pool_recycle=3600)

        DBSession.configure(bind=engine)
        model_perf_schema.Base.metadata.bind = engine
        
        self.log = set_up_logging(log_directory, 'perfbackend')
        
    #Renderer
    def get_renderer(self, method_name):
        return 'string'
    
    def response_wrapper(self, method_name, request):
        request_id = str(uuid.uuid4())
        callback = None if 'callback' not in request.GET else request.GET['callback']
        self.log.info(request_id + ' ' + method_name + ('' if 'identifier' not in request.matchdict else ' ' + request.matchdict['identifier']))
        def f(data):
            self.log.info(request_id + ' end')
            if callback is not None:
                return Response(body="%s(%s)" % (callback, data), content_type='application/json')
            else:
                return Response(body=data, content_type='application/json')
        return f
    
    #Bioentity
    def all_bioentities(self, min_id, max_id):
        from model_perf_schema.core import Bioentity
        return get_all(Bioentity, 'json', min_id, max_id)
    
    def bioentity_list(self, bioent_ids):
        from model_perf_schema.core import Bioentity
        return get_list(Bioentity, 'json', bioent_ids)
    
    #Locus
    def locus(self, identifier):
        from model_perf_schema.core import Bioentity
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_obj(Bioentity, 'json', bioent_id)
    
    def locustabs(self, identifier):
        from model_perf_schema.core import Bioentity
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_obj(Bioentity, 'locustabs_json', bioent_id)
    
    def all_locustabs(self, min_id, max_id):
        from model_perf_schema.core import Bioentity
        return get_all(Bioentity, 'locustabs_json', min_id, max_id)
    
    #Bioconcept
    def all_bioconcepts(self, min_id, max_id, callback=None):
        from model_perf_schema.core import Bioconcept
        return get_all(Bioconcept, 'json', min_id, max_id)
    
    def bioconcept_list(self, biocon_ids, callback=None):
        from model_perf_schema.core import Bioconcept
        return get_list(Bioconcept, 'json', biocon_ids)
    
    #Reference
    def reference(self, identifier):
        from model_perf_schema.core import Reference
        ref_id = get_obj_id(str(identifier).lower(), class_type='REFERENCE')
        return get_obj(Reference, 'json', ref_id)

    def author(self, identifier):
        from model_perf_schema.core import Author
        auth_id = get_obj_id(str(identifier).lower(), class_type='AUTHOR')
        return get_obj(Author, 'json', auth_id)

    def all_authors(self, min_id, max_id, callback=None):
        from model_perf_schema.core import Author
        return get_all(Author, 'json', min_id, max_id)

    def author_references(self, identifier):
        pass
       
    def all_references(self, min_id, max_id):
        from model_perf_schema.core import Reference
        return get_all(Reference, 'json', min_id, max_id)

    def all_bibentries(self, min_id, max_id):
        from model_perf_schema.core import Reference
        return get_all(Reference, 'bibentry_json', min_id, max_id)
    
    def reference_list(self, reference_ids):
        from model_perf_schema.core import Reference
        return get_list(Reference, 'bibentry_json', reference_ids)
    
    #Interaction
    def interaction_overview(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_overview(bioent_id, 'INTERACTION')
    
    def interaction_details(self, locus_identifier=None, reference_identifier=None):
        if locus_identifier is not None:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_evidence(bioent_id, 'INTERACTION')
        if reference_identifier is not None:
            ref_id = get_obj_id(str(reference_identifier).lower(), class_type='REFERENCE')
            return get_reference_evidence(ref_id, 'INTERACTION')
        return None
    
    def interaction_graph(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'INTERACTION')
    
    def interaction_resources(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_resources(bioent_id, 'INTERACTION')
    
    #Literature
    def literature_overview(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_overview(bioent_id, 'LITERATURE')
    
    def literature_details(self, locus_identifier=None, reference_identifier=None):
        if locus_identifier is not None:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_evidence(bioent_id, 'LITERATURE')
        if reference_identifier is not None:
            ref_id = get_obj_id(str(reference_identifier).lower(), class_type='REFERENCE')
            return get_reference_evidence(ref_id, 'LITERATURE')
        return None
    
    def literature_graph(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'LITERATURE')

    #GO
    def go_enrichment(self, bioent_ids, callback=None):
        from model_perf_schema.core import Bioentity, Bioconcept
        bioent_format_names = []
        num_chunks = ceil(1.0*len(bioent_ids)/500)
        for i in range(num_chunks):
            bioent_format_names.extend([json.loads(x.json)['format_name'] for x in DBSession.query(Bioentity).filter(Bioentity.id.in_(bioent_ids[i*500:(i+1)*500])).all()])
        enrichment_results = query_batter.query_go_processes(bioent_format_names)
        json_format = []
        
        for enrichment_result in enrichment_results:
            identifier = 'GO:' + str(int(enrichment_result[0][3:])).zfill(7)
            goterm_id = get_obj_id(str(identifier).lower(), 'BIOCONCEPT', 'GO')
            goterm = json.loads(get_obj(Bioconcept, 'json', goterm_id))
            json_format.append({'go': goterm,
                            'match_count': enrichment_result[1],
                            'pvalue': enrichment_result[2]})
        return json.dumps(json_format)

    def go(self, identifier):
        from model_perf_schema.core import Bioconcept
        biocon_id = get_obj_id(str(identifier).lower(), class_type='BIOCONCEPT', subclass_type='GO')
        return get_obj(Bioconcept, 'json', biocon_id)

    def go_details(self, locus_identifier=None, go_identifier=None, reference_identifier=None, with_children=False):
        if locus_identifier is not None:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_evidence(bioent_id, 'GO')
        elif go_identifier is not None:
            biocon_id = get_obj_id(str(go_identifier).lower(), class_type='BIOCONCEPT', subclass_type='GO')
            if with_children:
                return get_bioconcept_evidence(biocon_id, 'LOCUS_ALL_CHILDREN')
            else:
                return get_bioconcept_evidence(biocon_id, 'LOCUS')
        elif reference_identifier is not None:
            ref_id = get_obj_id(str(reference_identifier).lower(), class_type='REFERENCE')
            return get_reference_evidence(ref_id, 'GO')

    def go_graph(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'GO')

    def go_ontology_graph(self, identifier):
        biocon_id = get_obj_id(str(identifier).upper(), class_type='BIOCONCEPT', subclass_type='GO')
        return get_bioconcept_graph(biocon_id, 'ONTOLOGY')

    def go_overview(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_overview(bioent_id, 'GO')

    #Phenotype
    def phenotype(self, identifier):
        from model_perf_schema.core import Bioconcept
        biocon_id = get_obj_id(str(identifier).lower(), class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        return get_obj(Bioconcept, 'json', biocon_id)

    def phenotype_details(self, locus_identifier=None, phenotype_identifier=None, chemical_identifier=None, reference_identifier=None, with_children=False):
        if locus_identifier is not None:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_evidence(bioent_id, 'PHENOTYPE')
        elif phenotype_identifier is not None:
            biocon_id = get_obj_id(str(phenotype_identifier).lower(), class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
            if with_children:
                return get_bioconcept_evidence(biocon_id, 'LOCUS_ALL_CHILDREN')
            else:
                return get_bioconcept_evidence(biocon_id, 'LOCUS')
        elif reference_identifier is not None:
            ref_id = get_obj_id(str(reference_identifier).lower(), class_type='REFERENCE')
            return get_reference_evidence(ref_id, 'PHENOTYPE')
        elif chemical_identifier is not None:
            ref_id = get_obj_id(str(chemical_identifier).lower(), class_type='CHEMICAL')
            return get_chemical_evidence(ref_id, 'PHENOTYPE')

    def phenotype_ontology(self):
        pass

    def phenotype_graph(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'PHENOTYPE')

    def phenotype_ontology_graph(self, identifier):
        biocon_id = get_obj_id(str(identifier).lower(), class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        return get_bioconcept_graph(biocon_id, 'ONTOLOGY')

    def phenotype_overview(self, locus_identifier=None, phenotype_identifier=None):
        if locus_identifier is not None:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_overview(bioent_id, 'PHENOTYPE')
        elif phenotype_identifier is not None:
            biocon_id = get_obj_id(str(phenotype_identifier).lower(), class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
            pass
            #return get_bioconcept_overview(bioent_id, 'PHENOTYPE')

    def phenotype_resources(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_resources(bioent_id, 'PHENOTYPE')

    #Chemical
    def chemical(self, identifier):
        from model_perf_schema.core import Chemical
        chem_id = get_obj_id(str(identifier).lower(), class_type='CHEMICAL')
        return get_obj(Chemical, 'json', chem_id)

    def all_chemicals(self, min_id, max_id, callback=None):
        from model_perf_schema.core import Chemical
        return get_all(Chemical, 'json', min_id, max_id)
    
    #Protein
    def protein_domain_details(self, locus_identifier=None, reference_identifier=None):
        if locus_identifier is not None:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_evidence(bioent_id, 'DOMAIN')
        elif reference_identifier is not None:
            ref_id = get_obj_id(str(reference_identifier).lower(), class_type='REFERENCE')
            return get_reference_evidence(ref_id, 'DOMAIN')
    
    def regulation_overview(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_overview(bioent_id, 'REGULATION')
    
    def regulation_details(self, locus_identifier=None, reference_identifier=None):
        if locus_identifier is not None:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_evidence(bioent_id, 'REGULATION')
        elif reference_identifier is not None:
            ref_id = get_obj_id(str(reference_identifier).lower(), class_type='REFERENCE')
            return get_reference_evidence(ref_id, 'REGULATION')
    
    def regulation_graph(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'REGULATION')
    
    def regulation_target_enrichment(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_enrichment(bioent_id, 'REGULATION_TARGET')

    def regulation_paragraph(self, identifier):
        bioent_id = get_obj_id(str(identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_paragraph(bioent_id, 'REGULATION')
    
    #Binding
    def binding_site_details(self, locus_identifier=None, reference_identifier=None):
        if locus_identifier is not None:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_evidence(bioent_id, 'BINDING')
        elif reference_identifier is not None:
            ref_id = get_obj_id(str(reference_identifier).lower(), class_type='REFERENCE')
            return get_bioentity_evidence(ref_id, 'BINDING')

    #Misc
    def all_disambigs(self, min_id, max_id):
        from model_perf_schema.core import Disambig
        query = DBSession.query(Disambig)
        if min_id is not None:
            query = query.filter(Disambig.id >= min_id)
        if max_id is not None:
            query = query.filter(Disambig.id < max_id)
        disambigs = query.all()
        return json.dumps([{'id': disambig.id,
                            'disambig_key': disambig.disambig_key,
                            'class_type': disambig.class_type,
                            'subclass_type': disambig.subclass_type,
                            'identifier': disambig.obj_id} 
                        for disambig in disambigs]) 
        
#Useful methods

#Get obj/obj_id
def get_obj_ids(identifier, class_type=None, subclass_type=None, print_query=False):
    from model_perf_schema.core import Disambig
    
    if identifier is None:
        return None
    query = DBSession.query(Disambig).filter(Disambig.disambig_key==identifier)
    if class_type is not None:
        query = query.filter(Disambig.class_type==class_type)
    if subclass_type is not None:
        query = query.filter(Disambig.subclass_type==subclass_type)
    disambigs = query.all()
    
    if print_query:
        print query
        
    if len(disambigs) > 0:
        return [(disambig.obj_id, disambig.class_type, disambig.subclass_type) for disambig in disambigs]
    return None

def get_obj_id(identifier, class_type=None, subclass_type=None):
    objs_ids = get_obj_ids(identifier, class_type=class_type, subclass_type=subclass_type)
    obj_id = None if objs_ids is None or len(objs_ids) != 1 else objs_ids[0][0]
    return obj_id

def get_all(cls, col_name, min_id, max_id):
    query = DBSession.query(cls)
    if min_id is not None:
        query = query.filter(cls.id >= min_id)
    if max_id is not None:
        query = query.filter(cls.id < max_id)
    objs = query.all()
        
    return '[' + ', '.join(filter(None, [getattr(obj, col_name) for obj in objs])) + ']'

def get_list(cls, col_name, obj_ids):
    num_chunks = ceil(1.0*len(obj_ids)/500)
    objs = []
    for i in range(num_chunks):
        objs.extend(DBSession.query(cls).filter(cls.id.in_(obj_ids[i*500:(i+1)*500])).all())
    return '[' + ', '.join([getattr(obj, col_name) for obj in objs]) + ']'
            
def get_obj(cls, col_name, obj_id):
    if obj_id is not None:
        biocon = DBSession.query(cls).filter(cls.id == obj_id).first()
        return None if biocon is None else getattr(biocon, col_name)
    return None

#Get bioentity data

def get_bioentity_overview(bioentity_id, class_type):
    from model_perf_schema.bioentity_data import BioentityOverview
    if bioentity_id is not None:
        data = DBSession.query(BioentityOverview).filter(BioentityOverview.bioentity_id == bioentity_id).filter(BioentityOverview.class_type == class_type).first()
        return None if data is None else data.json
    return None
        
def get_bioentity_graph(bioentity_id, class_type):
    from model_perf_schema.bioentity_data import BioentityGraph
    if bioentity_id is not None:
        data = DBSession.query(BioentityGraph).filter(BioentityGraph.bioentity_id == bioentity_id).filter(BioentityGraph.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioentity_resources(bioentity_id, class_type):
    from model_perf_schema.bioentity_data import BioentityResources
    if bioentity_id is not None:
        data = DBSession.query(BioentityResources).filter(BioentityResources.bioentity_id == bioentity_id).filter(BioentityResources.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioentity_enrichment(bioentity_id, class_type):
    from model_perf_schema.bioentity_data import BioentityEnrichment
    if bioentity_id is not None:
        data = DBSession.query(BioentityEnrichment).filter(BioentityEnrichment.bioentity_id == bioentity_id).filter(BioentityEnrichment.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioentity_paragraph(bioentity_id, class_type):
    from model_perf_schema.bioentity_data import BioentityParagraph
    if bioentity_id is not None:
        data = DBSession.query(BioentityParagraph).filter(BioentityParagraph.bioentity_id == bioentity_id).filter(BioentityParagraph.class_type == class_type).first()
        return None if data is None else data.json
    return None

#Get bioconcept data

def get_bioconcept_graph(bioconcept_id, class_type):
    from model_perf_schema.bioconcept_data import BioconceptGraph
    if bioconcept_id is not None:
        data = DBSession.query(BioconceptGraph).filter(BioconceptGraph.bioentity_id == bioconcept_id).filter(BioconceptGraph.class_type == class_type).first()
        return None if data is None else data.json
    return None

# Get evidence

def get_bioentity_evidence(bioentity_id, class_type):
    from model_perf_schema.evidence import BioentityEvidence
    from datetime import datetime
    if bioentity_id is not None:
        print str(datetime.now()) + 'Start evidence'
        data = [x.evidence.json for x in DBSession.query(BioentityEvidence)
                    .filter(BioentityEvidence.bioentity_id == bioentity_id)
                    .filter(BioentityEvidence.class_type == class_type)
                    .options(subqueryload(BioentityEvidence.evidence)).all()]
        print str(datetime.now()) + 'Query finished'
        returnValue = "[" + (", ".join(data)) + "]"
        print str(datetime.now()) + 'String join finished'
        return returnValue
    return None

def get_bioconcept_evidence(bioconcept_id, class_type):
    from model_perf_schema.evidence import BioconceptEvidence
    if bioconcept_id is not None:
        data = [x.evidence.json for x in DBSession.query(BioconceptEvidence)
                    .filter(BioconceptEvidence.bioconcept_id == bioconcept_id)
                    .filter(BioconceptEvidence.class_type == class_type)
                    .options(subqueryload(BioconceptEvidence.evidence)).all()]
        return "[" + (", ".join(data)) + "]"
    return None

def get_reference_evidence(reference_id, class_type):
    from model_perf_schema.evidence import ReferenceEvidence
    if reference_id is not None:
        data = [x.evidence.json for x in DBSession.query(ReferenceEvidence)
                    .filter(ReferenceEvidence.reference_id == reference_id)
                    .filter(ReferenceEvidence.class_type == class_type)
                    .options(subqueryload(ReferenceEvidence.evidence)).all()]
        return "[" + (", ".join(data)) + "]"
    return None

def get_chemical_evidence(chemical_id, class_type):
    from model_perf_schema.evidence import BioentityEvidence
    if chemical_id is not None:
        data = [x.evidence.json for x in DBSession.query(BioentityEvidence)
                    .filter(BioentityEvidence.bioentity_id == chemical_id)
                    .filter(BioentityEvidence.class_type == class_type)
                    .options(subqueryload(BioentityEvidence.evidence)).all()]
        return "[" + (", ".join(data)) + "]"
    return None