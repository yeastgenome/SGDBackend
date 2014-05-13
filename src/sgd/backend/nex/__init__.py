from datetime import datetime
import json
import logging
import uuid
from math import ceil

from pyramid.response import Response
from sqlalchemy import func
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from src.sgd.backend.backend_interface import BackendInterface
from src.sgd.model import nex


__author__ = 'kpaskov'

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
query_limit = 25000

class SGDBackend(BackendInterface):
    def __init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory):
        class Base(object):
            __table_args__ = {'schema': schema, 'extend_existing':True}
                
        nex.Base = declarative_base(cls=Base)
        engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), pool_recycle=3600)

        DBSession.configure(bind=engine)
        nex.Base.metadata.bind = engine
        
        self.log = set_up_logging(log_directory, 'nex')
        
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
    def all_bioentities(self, chunk_size, offset):
        from src.sgd.model.nex.bioentity import Bioentity
        from src.sgd.model.nex.bioentity import Locus
        from src.sgd.model.nex.evidence import Phenotypeevidence, Goevidence, Regulationevidence, Geninteractionevidence, \
            Physinteractionevidence, DNAsequenceevidence
        from src.sgd.model.nex.paragraph import Bioentityparagraph
        return [x.to_json() for x in DBSession.query(Bioentity).with_polymorphic('*').limit(chunk_size).offset(offset).all()]

    def bioentity_list(self, bioent_ids):
        from src.sgd.model.nex.bioentity import Bioentity
        from src.sgd.model.nex.evidence import Phenotypeevidence, Goevidence, Regulationevidence, Geninteractionevidence, \
            Physinteractionevidence, DNAsequenceevidence
        from src.sgd.model.nex.paragraph import Bioentityparagraph
        num_chunks = int(ceil(1.0*len(bioent_ids)/500))
        bioentities = []
        for i in range(0, num_chunks):
            bioentities.extend(DBSession.query(Bioentity).filter(Bioentity.id.in_(bioent_ids[i*500:(i+1)*500])).all())
        return json.dumps([x.to_semi_json() for x in bioentities])

    def locustabs(self, locus_identifier, are_ids=False):
        from src.sgd.model.nex.auxiliary import Locustabs
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(DBSession.query(Locustabs).filter(Locustabs.id == locus_id).first().to_json())

    def all_locustabs(self, chunk_size, offset):
        from src.sgd.model.nex.auxiliary import Locustabs
        return [x.to_json() for x in DBSession.query(Locustabs).limit(chunk_size).offset(offset).all()]

    def all_locusentries(self, chunk_size, offset):
        from src.sgd.model.nex.bioentity import Locus
        return [x.to_semi_json() for x in DBSession.query(Locus).limit(chunk_size).offset(offset).all()]
    
    def locus(self, locus_identifier, are_ids=False):
        from src.sgd.model.nex.bioentity import Locus
        from src.sgd.model.nex.evidence import Phenotypeevidence, Goevidence, Regulationevidence, Geninteractionevidence, \
            Physinteractionevidence, DNAsequenceevidence
        from src.sgd.model.nex.paragraph import Bioentityparagraph
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(DBSession.query(Locus).filter_by(id=locus_id).first().to_json())

    def complex(self, complex_identifier, are_ids=False):
        from src.sgd.model.nex.bioentity import Complex
        from src.sgd.model.nex.evidence import Complexevidence
        if are_ids:
            complex_id = complex_identifier
        else:
            complex_id = get_obj_id(complex_identifier, class_type='BIOENTITY', subclass_type='COMPLEX')
        return None if complex_id is None else json.dumps(DBSession.query(Complex).filter_by(id=complex_id).first().to_json())

    #Bioconcept
    def all_bioconcepts(self, chunk_size, offset):
        from src.sgd.model.nex.bioconcept import Bioconcept
        return [x.to_min_json() for x in DBSession.query(Bioconcept).with_polymorphic('*').limit(chunk_size).offset(offset).all()]

    def ec_number(self, ec_number_identifier, are_ids=False):
        from src.sgd.model.nex.bioconcept import ECNumber
        if are_ids:
            ec_number_id = ec_number_identifier
        else:
            ec_number_id = get_obj_id(ec_number_identifier, class_type='BIOCONCEPT', subclass_type='ECNUMBER')
        return None if ec_number_id is None else json.dumps(DBSession.query(ECNumber).filter_by(id=ec_number_id).first().to_json())

    def phenotype(self, phenotype_identifier, are_ids=False):
        from src.sgd.model.nex.bioconcept import Phenotype
        from src.sgd.model.nex.evidence import Phenotypeevidence
        if are_ids:
            phenotype_id = phenotype_identifier
        else:
            phenotype_id = get_obj_id(phenotype_identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        return None if phenotype_id is None else json.dumps(DBSession.query(Phenotype).filter_by(id=phenotype_id).first().to_json())

    def observable(self, observable_identifier, are_ids=False):
        from src.sgd.model.nex.bioconcept import Observable
        from src.sgd.model.nex.evidence import Phenotypeevidence
        if are_ids:
            observable_id = observable_identifier
        else:
            observable_id = get_obj_id(observable_identifier, class_type='BIOCONCEPT', subclass_type='OBSERVABLE')
        return None if observable_id is None else json.dumps(DBSession.query(Observable).filter_by(id=observable_id).first().to_json())

    def go(self, go_identifier, are_ids=False):
        from src.sgd.model.nex.bioconcept import Go
        from src.sgd.model.nex.evidence import Goevidence
        if are_ids:
            go_id = go_identifier
        else:
            go_id = get_obj_id(go_identifier, class_type='BIOCONCEPT', subclass_type='GO')
        return None if go_id is None else json.dumps(DBSession.query(Go).filter_by(id=go_id).first().to_json())

    #Bioitem
    def all_bioitems(self, chunk_size, offset):
        from src.sgd.model.nex.bioitem import Bioitem
        return [x.to_json() for x in DBSession.query(Bioitem).with_polymorphic('*').limit(chunk_size).offset(offset).all()]

    def chemical(self, chemical_identifier, are_ids=False):
        from src.sgd.model.nex.bioitem import Chemical
        if are_ids:
            chemical_id = chemical_identifier
        else:
            chemical_id = get_obj_id(chemical_identifier, class_type='BIOITEM', subclass_type='CHEMICAL')
        return None if chemical_id is None else json.dumps(DBSession.query(Chemical).filter_by(id=chemical_id).first().to_json())

    def strain(self, strain_identifier, are_ids=False):
        from src.sgd.model.nex.misc import Strain
        from src.sgd.model.nex.paragraph import Strainparagraph
        if are_ids:
            strain_id = strain_identifier
        else:
            strain_id = get_obj_id(strain_identifier, class_type='STRAIN')
        return None if strain_id is None else json.dumps(DBSession.query(Strain).filter_by(id=strain_id).first().to_json())

    def all_strains(self, chunk_size, offset):
        from src.sgd.model.nex.misc import Strain
        from src.sgd.model.nex.paragraph import Strainparagraph
        return [x.to_json() for x in DBSession.query(Strain).limit(chunk_size).offset(offset).all()]

    def domain(self, domain_identifier, are_ids=False):
        from src.sgd.model.nex.bioitem import Domain
        if are_ids:
            domain_id = domain_identifier
        else:
            domain_id = get_obj_id(domain_identifier, class_type='BIOITEM', subclass_type='DOMAIN')
        return None if domain_id is None else json.dumps(DBSession.query(Domain).filter_by(id=domain_id).first().to_json())

    def contig(self, contig_identifier, are_ids=False):
        import view_sequence
        if are_ids:
            contig_id = contig_identifier
        else:
            contig_id = get_obj_id(contig_identifier, class_type='BIOITEM', subclass_type='CONTIG')
        return None if contig_id is None else json.dumps(view_sequence.make_contig(contig_id))

    #EC number
    def ec_number_details(self, locus_identifier=None, ec_number_identifier=None, are_ids=False):
        import view_ec_number
        if are_ids:
            locus_id = locus_identifier
            ec_number_id = ec_number_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            ec_number_id = None if ec_number_identifier is None else get_obj_id(ec_number_identifier, class_type='BIOCONCEPT', subclass_type='ECNUMBER')

        return json.dumps(view_ec_number.make_details(locus_id=locus_id, ec_number_id=ec_number_id))

    #Reference
    def all_references(self, chunk_size, offset):
        from src.sgd.model.nex.reference import Reference
        from src.sgd.model.nex.paragraph import Referenceparagraph
        from src.sgd.model.nex.evidence import Phenotypeevidence, Goevidence, Physinteractionevidence, \
            Geninteractionevidence, Regulationevidence, Literatureevidence
        return [x.to_json() for x in DBSession.query(Reference).limit(chunk_size).offset(offset).all()]

    def all_bibentries(self, chunk_size, offset):
        from src.sgd.model.nex.reference import Bibentry
        return [{'id': x.id, 'text': x.text} for x in DBSession.query(Bibentry).limit(chunk_size).offset(offset).all()]

    def reference_list(self, reference_ids):
        from src.sgd.model.nex.reference import Bibentry
        if reference_ids is None:
            return json.dumps({'Error': 'No locus_id or go_id given.'})
        return json.dumps([{'id': x.id, 'text': x.text} for x in DBSession.query(Bibentry).filter(Bibentry.id.in_(reference_ids)).all()])

    def all_authors(self, chunk_size, offset):
        from src.sgd.model.nex.reference import Author
        return [x.to_json() for x in DBSession.query(Author).limit(chunk_size).offset(offset).all()]

    def reference(self, reference_identifier, are_ids=False):
        from src.sgd.model.nex.reference import Reference
        from src.sgd.model.nex.paragraph import Referenceparagraph
        from src.sgd.model.nex.evidence import Phenotypeevidence, Goevidence, Physinteractionevidence, \
            Geninteractionevidence, Regulationevidence, Literatureevidence
        if are_ids:
            reference_id = reference_identifier
        else:
            reference_id = get_obj_id(reference_identifier, class_type='REFERENCE')
        return None if reference_id is None else json.dumps(DBSession.query(Reference).filter_by(id=reference_id).first().to_json())

    def author(self, author_identifier, are_ids=False):
        from src.sgd.model.nex.reference import Author
        if are_ids:
            author_id = author_identifier
        else:
            author_id = None if author_identifier is None else get_obj_id(author_identifier, class_type='AUTHOR')
        return None if author_id is None else json.dumps(DBSession.query(Author).filter_by(id=author_id).first().to_json())

    def references_this_week(self):
        from datetime import date, timedelta
        from src.sgd.model.nex.reference import Reference
        a_week_ago = date.today() - timedelta(days=8)
        return json.dumps([x.to_semi_json() for x in sorted(DBSession.query(Reference).filter(Reference.date_created > a_week_ago).all(), key=lambda x: x.date_created, reverse=True)])

    #Phenotype
    def phenotype_ontology_graph(self, observable_identifier, are_ids=False):
        import graph_tools
        from src.sgd.model.nex.evidence import Phenotypeevidence
        if are_ids:
            observable_id = observable_identifier
        else:
            observable_id = get_obj_id(observable_identifier, class_type='BIOCONCEPT', subclass_type='OBSERVABLE')
        return None if observable_id is None else json.dumps(graph_tools.make_ontology_graph(observable_id, 'OBSERVABLE', lambda x: True, lambda x: x.ancestor_type))

    def phenotype_details(self, locus_identifier=None, phenotype_identifier=None, observable_identifier=None, chemical_identifier=None, reference_identifier=None, with_children=False, are_ids=False):
        from src.sgd.backend.nex import view_phenotype
        if are_ids:
            locus_id = locus_identifier
            phenotype_id = phenotype_identifier
            observable_id = observable_identifier
            chemical_id = chemical_identifier
            reference_id = reference_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            phenotype_id = None if phenotype_identifier is None else get_obj_id(phenotype_identifier, class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
            observable_id = None if observable_identifier is None else get_obj_id(observable_identifier, class_type='BIOCONCEPT', subclass_type='OBSERVABLE')
            chemical_id = None if chemical_identifier is None else get_obj_id(chemical_identifier, class_type='BIOITEM', subclass_type='CHEMICAL')
            reference_id = None if reference_identifier is None else get_obj_id(reference_identifier, class_type='REFERENCE')
        
        return json.dumps(view_phenotype.make_details(locus_id=locus_id, phenotype_id=phenotype_id, observable_id=observable_id, chemical_id=chemical_id, reference_id=reference_id, with_children=with_children))

    def phenotype_graph(self, locus_identifier, are_ids=False):
        from src.sgd.backend.nex import graph_tools
        from src.sgd.model.nex.auxiliary import Bioconceptinteraction, Bioiteminteraction
        from src.sgd.model.nex.evidence import Phenotypeevidence

        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(graph_tools.make_graph(locus_id, Bioconceptinteraction, 'PHENOTYPE', 'LOCUS'))

    def locus_graph(self, locus_identifier, are_ids=False):
        from src.sgd.backend.nex import graph_tools
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(graph_tools.make_lsp_graph(locus_id))

    # Go
    def go_ontology_graph(self, go_identifier, are_ids=False):
        import graph_tools
        if are_ids:
            go_id = go_identifier
        else:
            go_id = get_obj_id(go_identifier, class_type='BIOCONCEPT', subclass_type='GO')
        return None if go_id is None else json.dumps(graph_tools.make_ontology_graph(go_id, 'GO', lambda x: True, lambda x: x.go_aspect))
    
    def go_details(self, locus_identifier=None, go_identifier=None, reference_identifier=None, with_children=False, are_ids=False):
        import view_go
        if are_ids:
            locus_id = locus_identifier
            go_id = go_identifier
            reference_id = reference_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            go_id = None if go_identifier is None else get_obj_id(go_identifier, class_type='BIOCONCEPT', subclass_type='GO')
            reference_id = None if reference_identifier is None else get_obj_id(reference_identifier, class_type='REFERENCE')
        return json.dumps(view_go.make_details(locus_id=locus_id, go_id=go_id, reference_id=reference_id, with_children=with_children))
    
    def go_enrichment(self, bioent_ids):
        from src.sgd.backend.nex import view_go
        return json.dumps(view_go.make_enrichment(bioent_ids))

    def go_graph(self, locus_identifier, are_ids=False):
        from src.sgd.backend.nex import graph_tools
        from src.sgd.model.nex.auxiliary import Bioconceptinteraction
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(graph_tools.make_graph(locus_id, Bioconceptinteraction, 'GO', 'LOCUS'))
       
    #Interaction
    def interaction_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        import view_interaction
        if are_ids:
            locus_id = locus_identifier
            reference_id = reference_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            reference_id = None if reference_identifier is None else get_obj_id(reference_identifier, class_type='REFERENCE')
        return json.dumps(view_interaction.make_details(locus_id=locus_id, reference_id=reference_id))
        
    def interaction_graph(self, locus_identifier, are_ids=False):
        import view_interaction
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_interaction.make_graph(locus_id))

    #Literature
    def literature_details(self, locus_identifier=None, reference_identifier=None, topic=None, are_ids=False):
        import view_literature
        if are_ids:
            locus_id = locus_identifier
            reference_id = reference_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            reference_id = None if reference_identifier is None else get_obj_id(reference_identifier, class_type='REFERENCE')
        return json.dumps(view_literature.make_details(locus_id=locus_id, reference_id=reference_id, topic=topic))
    
    def literature_graph(self, locus_identifier, are_ids=False):
        import view_literature
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_literature.make_graph(locus_id))

    #Protein
    def protein_domain_details(self, locus_identifier=None, domain_identifier=None, are_ids=False):
        import view_protein
        if are_ids:
            locus_id = locus_identifier
            domain_id = domain_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            domain_id = None if domain_identifier is None else get_obj_id(domain_identifier, class_type='BIOITEM', subclass_type='DOMAIN')
        return None if locus_id is None and domain_id is None else json.dumps(view_protein.make_details(locus_id=locus_id, domain_id=domain_id))

    def protein_domain_graph(self, locus_identifier, are_ids=False):
        import graph_tools
        from src.sgd.model.nex.auxiliary import Bioiteminteraction
        from src.sgd.model.nex.bioitem import Domain
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(graph_tools.make_graph(locus_id, Bioiteminteraction, 'DOMAIN', 'LOCUS'))

    def protein_phosphorylation_details(self, locus_identifier, are_ids=False):
        from src.sgd.backend.nex import view_protein
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_protein.make_phosphorylation_details(locus_id=locus_id))

    def protein_experiment_details(self, locus_identifier, are_ids=False):
        from src.sgd.backend.nex import view_protein
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_protein.make_protein_experiment_details(locus_id=locus_id))

    #Complex
    def complex_details(self, locus_identifier=None, complex_identifier=None, are_ids=False):
        import view_complex
        if are_ids:
            complex_id = complex_identifier
            locus_id = locus_identifier
        else:
            complex_id = get_obj_id(complex_identifier, class_type='BIOENTITY', subclass_type='COMPLEX')
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return json.dumps(view_complex.make_details(locus_id=locus_id, complex_id=complex_id))

    def complex_graph(self, complex_identifier, are_ids=False):
        import graph_tools
        from src.sgd.model.nex.auxiliary import Bioconceptinteraction, Bioentityinteraction
        from src.sgd.model.nex.bioentity import Complex

        if are_ids:
            complex_id = complex_identifier
        else:
            complex_id = get_obj_id(complex_identifier, class_type='BIOENTITY', subclass_type='COMPLEX')
        if complex_id is None:
            return None
        else:
            locus_ids = set([x.locus_id for x in DBSession.query(Complex).filter_by(id=complex_id).first().child_genes])
            return json.dumps({'go_graph': graph_tools.make_graph(complex_id, Bioconceptinteraction, 'GO', 'COMPLEX'),
                               'interaction_graph': graph_tools.make_interaction_graph(locus_ids, Bioentityinteraction, 'PHYSINTERACTION')})

    #Regulation
    def regulation_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        import view_regulation
        if are_ids:
            locus_id = locus_identifier
            reference_id = reference_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            reference_id = None if reference_identifier is None else get_obj_id(reference_identifier, class_type='REFERENCE')
        return json.dumps(view_regulation.make_details(locus_id=locus_id, reference_id=reference_id))
            
    def regulation_graph(self, locus_identifier, are_ids=False):
        import view_regulation
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_regulation.make_graph(locus_id))
    
    def regulation_target_enrichment(self, locus_identifier, are_ids=False):
        from src.sgd.backend.nex import view_regulation
        from src.sgd.backend.nex import view_go
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        target_ids = set([x['locus2']['id'] for x in view_regulation.make_details(locus_id=locus_id) if x['locus1']['id'] == locus_id])
        if len(target_ids) > 0:
            return json.dumps(view_go.make_enrichment(target_ids))
        else:
            return '[]'
      
    #Binding
    def binding_site_details(self, locus_identifier=None, are_ids=False):
        import view_sequence
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return json.dumps(view_sequence.make_binding_details(locus_id=locus_id))

    #Sequence
    def sequence_details(self, locus_identifier=None, contig_identifier=None, are_ids=False):
        import view_sequence
        if are_ids:
            locus_id = locus_identifier
            contig_id = contig_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            contig_id = None if contig_identifier is None else get_obj_id(contig_identifier, class_type='BIOITEM', subclass_type='CONTIG')
        return json.dumps(view_sequence.make_details(locus_id=locus_id, contig_id=contig_id))

    def neighbor_sequence_details(self, locus_identifier=None, are_ids=False):
        import view_sequence
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return json.dumps(view_sequence.make_neighbor_details(locus_id=locus_id))

    def bioentity_details(self, locus_identifier=None, are_ids=False):
        import view_protein
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return json.dumps(view_protein.make_bioentity_details(locus_id=locus_id))
    
    #Misc
    def all_disambigs(self, chunk_size, offset):
        from src.sgd.model.nex.auxiliary import Disambig
        return [x.to_json() for x in DBSession.query(Disambig).limit(chunk_size).offset(offset).all()]
      
#Useful methods
def create_simple_table(objs, f, **kwargs):
    table = []
    for obj in objs:
        entries = f(obj, **kwargs)
        table.append(entries)
    return table

def set_up_logging(log_directory, label):
    logging.basicConfig(format='%(asctime)s %(name)s: %(message)s', level=logging.ERROR)
    log = logging.getLogger(label)

    if log_directory is not None:
        hdlr = logging.FileHandler(log_directory + '/' + label + '.' + str(datetime.now().date()) + '.txt')
        formatter = logging.Formatter('%(asctime)s %(name)s: %(message)s')
        hdlr.setFormatter(formatter)
    else:
        hdlr = logging.NullHandler()
    log.addHandler(hdlr)
    log.setLevel(logging.INFO)
    log.propagate = False
    return log

def get_obj_ids(identifier, class_type=None, subclass_type=None, print_query=False):
    from src.sgd.model.nex.auxiliary import Disambig
    if identifier is None:
        return None

    query = DBSession.query(Disambig).filter(func.lower(Disambig.disambig_key) == func.lower(str(identifier)))
    if class_type is not None:
        query = query.filter(class_type == Disambig.class_type)
    if subclass_type is not None:
        query = query.filter(subclass_type == Disambig.subclass_type)
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