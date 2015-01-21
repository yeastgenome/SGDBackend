from datetime import datetime
import json
import logging
import uuid

from mpmath import ceil
from pyramid.response import Response
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import func
from zope.sqlalchemy import ZopeTransactionExtension

from src.sgd.backend.backend_interface import BackendInterface
from src.sgd.go_enrichment import query_batter
from src.sgd.model import perf


__author__ = 'kpaskov'

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

import datetime

class PerfBackend(BackendInterface):
    def __init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory):
        class Base(object):
            __table_args__ = {'schema': schema, 'extend_existing':True}

        perf.Base = declarative_base(cls=Base)

        engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), convert_unicode=True, pool_recycle=3600)

        DBSession.configure(bind=engine)
        perf.Base.metadata.bind = engine

        self.log = set_up_logging(log_directory, 'perf')

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
    def all_bioentities(self, chunk_size, offset):
        from src.sgd.model.perf.core import Bioentity
        return [x.to_json() for x in DBSession.query(Bioentity).order_by(Bioentity.id.desc()).limit(chunk_size).offset(offset).all()]

    def bioentity_list(self, bioent_ids):
        from src.sgd.model.perf.core import Locusentry
        return get_list(Locusentry, 'json', bioent_ids)

    #Locus
    def locus(self, locus_identifier):
        from src.sgd.model.perf.core import Bioentity
        bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        bioentity = DBSession.query(Bioentity).filter_by(id=bioent_id).first().json
        return bioentity

    def locustabs(self, locus_identifier):
        from src.sgd.model.perf.core import Locustab
        bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return DBSession.query(Locustab).filter_by(id=bioent_id).first().json

    def all_locustabs(self, chunk_size, offset):
        from src.sgd.model.perf.core import Locustab
        return [x.to_json() for x in DBSession.query(Locustab).order_by(Locustab.id.desc()).limit(chunk_size).offset(offset).all()]

    def all_locusentries(self, chunk_size, offset):
        from src.sgd.model.perf.core import Locusentry
        return [x.to_json() for x in DBSession.query(Locusentry).order_by(Locusentry.id.desc()).limit(chunk_size).offset(offset).all()]

    #Bioconcept
    def all_bioconcepts(self, chunk_size, offset):
        from src.sgd.model.perf.core import Bioconcept
        return [x.to_json() for x in DBSession.query(Bioconcept).order_by(Bioconcept.id.desc()).limit(chunk_size).offset(offset).all()]

    def bioconcept_list(self, biocon_ids, callback=None):
        from src.sgd.model.perf.core import Bioconcept
        return get_list(Bioconcept, 'json', biocon_ids)

    #Reference
    def reference(self, reference_identifier, are_ids=False):
        from src.sgd.model.perf.core import Reference
        if are_ids:
            ref_id = reference_identifier
        else:
            ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
        return str(get_obj(Reference, 'json', ref_id))

    def author(self, author_identifier):
        from src.sgd.model.perf.core import Author
        auth_id = get_obj_id(str(author_identifier), class_type='AUTHOR')
        return get_obj(Author, 'json', auth_id)

    def all_authors(self, chunk_size, offset):
        from src.sgd.model.perf.core import Author
        return [x.to_json() for x in DBSession.query(Author).order_by(Author.id.desc()).limit(chunk_size).offset(offset).all()]

    def all_references(self, chunk_size, offset):
        from src.sgd.model.perf.core import Reference
        return [x.to_json() for x in DBSession.query(Reference).order_by(Reference.id.desc()).limit(chunk_size).offset(offset).all()]

    def all_bibentries(self, chunk_size, offset):
        from src.sgd.model.perf.core import Bibentry
        return [x.to_json() for x in DBSession.query(Bibentry).order_by(Bibentry.id.desc()).limit(chunk_size).offset(offset).all()]

    def reference_list(self, reference_ids):
        from src.sgd.model.perf.core import Bibentry
        return get_list(Bibentry, 'json', reference_ids)

    def references_this_week(self):
        from src.sgd.model.perf.core import Orphan
        return DBSession.query(Orphan).filter_by(url='references_this_week').first().json

    def snapshot(self):
        from src.sgd.model.perf.core import Orphan
        return DBSession.query(Orphan).filter_by(url='snapshot').first().json

    def alignments(self):
        from src.sgd.model.perf.core import Orphan
        return DBSession.query(Orphan).filter_by(url='alignments').first().json

    def tag_list(self):
        from src.sgd.model.perf.core import Orphan
        return DBSession.query(Orphan).filter_by(url='tag_list').first().json

    def locus_list(self, list_type):
        from src.sgd.model.perf.core import Orphan
        print 'locus_list.' + list_type.lower()
        return DBSession.query(Orphan).filter(func.lower(Orphan.url) == 'locus_list.' + list_type.lower()).first().json

    def strain(self, strain_identifier):
        from src.sgd.model.perf.core import Strain
        strain_id = get_obj_id(str(strain_identifier), class_type='STRAIN')
        return get_obj(Strain, 'json', strain_id)

    def all_strains(self, chunk_size, offset):
        from src.sgd.model.perf.core import Strain
        return [x.to_json() for x in DBSession.query(Strain).order_by(Strain.id.desc()).limit(chunk_size).offset(offset).all()]

    def experiment(self, experiment_identifier):
        from src.sgd.model.perf.core import Experiment
        experiment_id = get_obj_id(str(experiment_identifier), class_type='EXPERIMENT')
        return get_obj(Experiment, 'json', experiment_id)

    def all_experiments(self, chunk_size, offset):
        from src.sgd.model.perf.core import Experiment
        return [x.to_json() for x in DBSession.query(Experiment).order_by(Experiment.id.desc()).limit(chunk_size).offset(offset).all()]

    def all_tags(self, chunk_size, offset):
        from src.sgd.model.perf.core import Tag
        return [x.to_json() for x in DBSession.query(Tag).order_by(Tag.id.desc()).limit(chunk_size).offset(offset).all()]

    #Bioitem
    def all_bioitems(self, chunk_size, offset):
        from src.sgd.model.perf.core import Bioitem
        return [x.to_json() for x in DBSession.query(Bioitem).order_by(Bioitem.id.desc()).limit(chunk_size).offset(offset).all()]

    #Interaction
    def interaction_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'INTERACTION')
        if reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'INTERACTION')
        return None

    def interaction_graph(self, locus_identifier, are_ids=False):
        if are_ids:
            bioent_id = locus_identifier
        else:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'INTERACTION')

    #Literature
    def literature_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'LITERATURE')
        if reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'LITERATURE')
        return None

    def literature_graph(self, locus_identifier, are_ids=False):
        if are_ids:
            bioent_id = locus_identifier
        else:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'LITERATURE')

    #GO
    def go_enrichment(self, bioent_ids, callback=None):
        from src.sgd.model.perf.core import Bioentity, Bioconcept
        bioent_format_names = []
        num_chunks = ceil(1.0*len(bioent_ids)/500)
        for i in range(num_chunks):
            bioent_format_names.extend([json.loads(x.json)['format_name'] for x in DBSession.query(Bioentity).filter(Bioentity.id.in_(bioent_ids[i*500:(i+1)*500])).all()])
        enrichment_results = query_batter.query_go_processes(bioent_format_names)
        json_format = []

        for enrichment_result in enrichment_results:
            identifier = 'GO:' + str(int(enrichment_result[0][3:])).zfill(7)
            goterm_id = get_obj_id(str(identifier).upper(), 'BIOCONCEPT', 'GO')
            goterm = json.loads(get_obj(Bioconcept, 'json', goterm_id))
            json_format.append({'go': goterm,
                            'match_count': enrichment_result[1],
                            'pvalue': enrichment_result[2]})
        return json.dumps(json_format)

    def go(self, go_identifier, are_ids=False):
        from src.sgd.model.perf.core import Bioconcept
        if are_ids:
            biocon_id = go_identifier
        else:
            biocon_id = get_obj_id(str(go_identifier).upper() if str(go_identifier).upper().startswith('GO') else str(go_identifier).lower(), class_type='BIOCONCEPT', subclass_type='GO')
        return get_obj(Bioconcept, 'json', biocon_id)

    def go_details(self, locus_identifier=None, go_identifier=None, reference_identifier=None, with_children=False, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'GO')
        elif go_identifier is not None:
            if are_ids:
                biocon_id = go_identifier
            else:
                biocon_id = get_obj_id(go_identifier, class_type='BIOCONCEPT', subclass_type='GO')
            if with_children:
                return get_bioconcept_details(biocon_id, 'GO_LOCUS_ALL_CHILDREN')
            else:
                return get_bioconcept_details(biocon_id, 'GO_LOCUS')
        elif reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'GO')

    def go_graph(self, locus_identifier, are_ids=False):
        if are_ids:
            bioent_id = locus_identifier
        else:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'GO')

    def go_ontology_graph(self, go_identifier, are_ids=False):
        if are_ids:
            biocon_id = go_identifier
        else:
            biocon_id = get_obj_id(str(go_identifier).upper() if str(go_identifier).upper().startswith('GO') else str(go_identifier).lower(), class_type='BIOCONCEPT', subclass_type='GO')
        return get_bioconcept_graph(biocon_id, 'GO_ONTOLOGY')

    #Phenotype
    def phenotype(self, phenotype_identifier, are_ids=False):
        from src.sgd.model.perf.core import Bioconcept
        if are_ids:
            biocon_id = phenotype_identifier
        else:
            biocon_id = get_obj_id(str(phenotype_identifier).lower(), class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
        return get_obj(Bioconcept, 'json', biocon_id)

    def observable(self, observable_identifier, are_ids=False):
        from src.sgd.model.perf.core import Bioconcept
        if are_ids:
            biocon_id = observable_identifier
        else:
            biocon_id = get_obj_id(str(observable_identifier).lower(), class_type='BIOCONCEPT', subclass_type='OBSERVABLE')
        return get_obj(Bioconcept, 'json', biocon_id)

    def chemical(self, chemical_identifier, are_ids=False):
        from src.sgd.model.perf.core import Bioitem
        if are_ids:
            bioitem_id = chemical_identifier
        else:
            bioitem_id = get_obj_id(str(chemical_identifier).lower(), class_type='BIOITEM', subclass_type='CHEMICAL')
        return get_obj(Bioitem, 'json', bioitem_id)

    def phenotype_details(self, locus_identifier=None, phenotype_identifier=None, observable_identifier=None, chemical_identifier=None, reference_identifier=None, with_children=False, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'PHENOTYPE')
        elif observable_identifier is not None:
            if are_ids:
                biocon_id = observable_identifier
            else:
                biocon_id = get_obj_id(str(observable_identifier).lower(), class_type='BIOCONCEPT', subclass_type='OBSERVABLE')
            if with_children:
                return get_bioconcept_details(biocon_id, 'OBSERVABLE_LOCUS_ALL_CHILDREN')
            else:
                return get_bioconcept_details(biocon_id, 'OBSERVABLE_LOCUS')
        elif phenotype_identifier is not None:
            if are_ids:
                biocon_id = phenotype_identifier
            else:
                biocon_id = get_obj_id(str(phenotype_identifier).lower(), class_type='BIOCONCEPT', subclass_type='PHENOTYPE')
            return get_bioconcept_details(biocon_id, 'PHENOTYPE_LOCUS')
        elif reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'PHENOTYPE')
        elif chemical_identifier is not None:
            if are_ids:
                chem_id = chemical_identifier
            else:
                chem_id = get_obj_id(str(chemical_identifier).lower(), class_type='BIOITEM', subclass_type='CHEMICAL')
            return get_bioitem_details(chem_id, 'PHENOTYPE')

    def phenotype_graph(self, locus_identifier, are_ids=False):
        if are_ids:
            bioent_id = locus_identifier
        else:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'PHENOTYPE')

    def phenotype_ontology_graph(self, phenotype_identifier, are_ids=False):
        if are_ids:
            biocon_id = phenotype_identifier
        else:
            biocon_id = get_obj_id(str(phenotype_identifier).lower(), class_type='BIOCONCEPT', subclass_type='OBSERVABLE')
        return get_bioconcept_graph(biocon_id, 'PHENOTYPE_ONTOLOGY')

    #Protein
    def domain(self, domain_identifier, are_ids=False):
        from src.sgd.model.perf.core import Bioitem
        if are_ids:
            bioitem_id = domain_identifier
        else:
            bioitem_id = get_obj_id(str(domain_identifier).lower(), class_type='BIOITEM', subclass_type='DOMAIN')
        return get_obj(Bioitem, 'json', bioitem_id)

    def protein_domain_details(self, locus_identifier=None, reference_identifier=None, domain_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'PROTEIN_DOMAIN')
        elif reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'PROTEIN_DOMAIN')
        elif domain_identifier is not None:
            if are_ids:
                domain_id = domain_identifier
            else:
                domain_id = get_obj_id(str(domain_identifier).upper(), class_type='BIOITEM', subclass_type='DOMAIN')
            return get_bioitem_details(domain_id, 'PROTEIN_DOMAIN_LOCUS')

    def protein_domain_graph(self, locus_identifier, are_ids=False):
        if are_ids:
            bioent_id = locus_identifier
        else:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'PROTEIN_DOMAIN')

    def regulation_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'REGULATION')
        elif reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'REGULATION')

    def regulation_graph(self, locus_identifier, are_ids=False):
        if are_ids:
            bioent_id = locus_identifier
        else:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'REGULATION')

    def regulation_target_enrichment(self, locus_identifier, are_ids=False):
        if are_ids:
            bioent_id = locus_identifier
        else:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_enrichment(bioent_id, 'REGULATION')

    def domain_enrichment(self, domain_identifier, are_ids=False):
        if are_ids:
            domain_id = domain_identifier
        else:
            domain_id = get_obj_id(str(domain_identifier).upper(), class_type='BIOITEM', subclass_type='DOMAIN')
        return get_bioitem_enrichment(domain_id, 'ENRICHMENT')

    #Binding
    def binding_site_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'BINDING_SITE')
        elif reference_identifier is not None:
            if are_ids:
                ref_id = reference_identifier
            else:
                ref_id = get_obj_id(str(reference_identifier).upper(), class_type='REFERENCE')
            return get_reference_details(ref_id, 'BINDING_SITE')

    #EC Number
    def ec_number(self, ec_number_identifier, are_ids=False):
        from src.sgd.model.perf.core import Bioconcept
        if are_ids:
            biocon_id = ec_number_identifier
        else:
            biocon_id = get_obj_id(str(ec_number_identifier).lower(), class_type='BIOCONCEPT', subclass_type='ECNUMBER')
        return get_obj(Bioconcept, 'json', biocon_id)

    def ec_number_details(self, locus_identifier=None, ec_number_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'EC_NUMBER')
        elif ec_number_identifier is not None:
            if are_ids:
                ref_id = ec_number_identifier
            else:
                ref_id = get_obj_id(str(ec_number_identifier).upper(), class_type='BIOCONCEPT', subclass_type='ECNUMBER')
            return get_bioconcept_details(ref_id, 'EC_NUMBER_LOCUS')

    # Sequence
    def contig(self, contig_identifier, are_ids=False):
        from src.sgd.model.perf.core import Bioitem
        if are_ids:
            bioitem_id = contig_identifier
        else:
            bioitem_id = get_obj_id(str(contig_identifier).lower(), class_type='BIOITEM', subclass_type='CONTIG')
        return get_obj(Bioitem, 'json', bioitem_id)

    def reserved_name(self, reserved_name_identifier, are_ids=False):
        from src.sgd.model.perf.core import Bioitem
        if are_ids:
            bioitem_id = reserved_name_identifier
        else:
            bioitem_id = get_obj_id(str(reserved_name_identifier).lower(), class_type='BIOITEM', subclass_type='RESERVEDNAME')
        return get_obj(Bioitem, 'json', bioitem_id)

    def protein_experiment_details(self, locus_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'PROTEIN_EXPERIMENT')

    def protein_phosphorylation_details(self, locus_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'PROTEIN_PHOSPHORYLATION')

    def posttranslational_details(self, locus_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'POSTTRANSLATIONAL')

    def sequence_details(self, locus_identifier=None, contig_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'SEQUENCE')
        elif contig_identifier is not None:
            if are_ids:
                contig_id = contig_identifier
            else:
                contig_id = get_obj_id(str(contig_identifier).upper(), class_type='BIOITEM', subclass_type='CONTIG')
            return get_bioitem_details(contig_id, 'SEQUENCE')

    def neighbor_sequence_details(self, locus_identifier, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'NEIGHBOR_SEQUENCE')
        return None

    #Expression
    def expression_details(self, locus_identifier=None, datasetcolumn_identifier=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
            return get_bioentity_details(bioent_id, 'EXPRESSION')
        elif datasetcolumn_identifier is not None:
            if are_ids:
                datasetcolumn_id = datasetcolumn_identifier
            else:
                datasetcolumn_id = get_obj_id(str(datasetcolumn_identifier).upper(), class_type='BIOITEM', subclass_type='DATASETCOLUMN')
            return get_bioitem_details(datasetcolumn_id, 'EXPRESSION')

    def expression_graph(self, locus_identifier, are_ids=False):
        if are_ids:
            bioent_id = locus_identifier
        else:
            bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')
        return get_bioentity_graph(bioent_id, 'EXPRESSION')

    def dataset(self, dataset_identifier, are_ids=False):
        from src.sgd.model.perf.core import Bioitem
        if are_ids:
            bioitem_id = dataset_identifier
        else:
            bioitem_id = get_obj_id(str(dataset_identifier).lower(), class_type='BIOITEM', subclass_type='DATASET')
        return get_obj(Bioitem, 'json', bioitem_id)

    def datasetcolumn(self, datasetcolumn_identifier, are_ids=False):
        from src.sgd.model.perf.core import Bioitem
        if are_ids:
            bioitem_id = datasetcolumn_identifier
        else:
            bioitem_id = get_obj_id(str(datasetcolumn_identifier).lower(), class_type='BIOITEM', subclass_type='DATASETCOLUMN')
        return get_obj(Bioitem, 'json', bioitem_id)

    def tag(self, tag_identifier, are_ids=False):
        from src.sgd.model.perf.core import Tag
        if are_ids:
            bioitem_id = tag_identifier
        else:
            bioitem_id = get_obj_id(str(tag_identifier).lower(), class_type='TAG')
        return get_obj(Tag, 'json', bioitem_id)

    #Misc
    def all_disambigs(self, chunk_size, offset):
        from src.sgd.model.perf.core import Disambig
        return [x.to_json() for x in DBSession.query(Disambig).order_by(Disambig.id.desc()).limit(chunk_size).offset(offset).all()]

        
#Useful methods

#Get obj/obj_id
def get_obj_ids(identifier, class_type=None, subclass_type=None, print_query=False):
    from src.sgd.model.perf.core import Disambig
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
        return [(disambig.obj_id, disambig.class_type, disambig.subclass_type) for disambig in disambigs]
    return None

disambig = {}

def get_obj_id(identifier, class_type=None, subclass_type=None):
    key = (class_type, subclass_type, identifier)
    if key in disambig:
        obj_id = disambig[(class_type, subclass_type, identifier)]
    else:
        objs_ids = get_obj_ids(identifier, class_type=class_type, subclass_type=subclass_type)
        obj_id = None if objs_ids is None or len(objs_ids) == 0 else objs_ids[0][0]
        if len(disambig) < 200000:
            disambig[key] = obj_id
    return obj_id

def get_all(cls, col_name, chunk_size, offset):
    return '[' + ', '.join(filter(None, [getattr(obj, col_name) for obj in DBSession.query(cls).limit(chunk_size).offset(offset).all()])) + ']'

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

def get_bioentity_graph(bioentity_id, class_type):
    from src.sgd.model.perf.bioentity_data import BioentityGraph
    if bioentity_id is not None:
        data = DBSession.query(BioentityGraph).filter(BioentityGraph.obj_id == bioentity_id).filter(BioentityGraph.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioentity_enrichment(bioentity_id, class_type):
    from src.sgd.model.perf.bioentity_data import BioentityEnrichment
    if bioentity_id is not None:
        data = DBSession.query(BioentityEnrichment).filter(BioentityEnrichment.obj_id == bioentity_id).filter(BioentityEnrichment.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioentity_details(bioentity_id, class_type):
    from src.sgd.model.perf.bioentity_data import BioentityDetails
    if bioentity_id is not None:
        data = DBSession.query(BioentityDetails).filter(BioentityDetails.obj_id == bioentity_id).filter(BioentityDetails.class_type == class_type).first()
        return None if data is None else data.json
    return None

#Get bioconcept data

def get_bioconcept_graph(bioconcept_id, class_type):
    from src.sgd.model.perf.bioconcept_data import BioconceptGraph
    if bioconcept_id is not None:
        data = DBSession.query(BioconceptGraph).filter(BioconceptGraph.obj_id == bioconcept_id).filter(BioconceptGraph.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioconcept_details(bioconcept_id, class_type):
    from src.sgd.model.perf.bioconcept_data import BioconceptDetails
    if bioconcept_id is not None:
        data = DBSession.query(BioconceptDetails).filter(BioconceptDetails.obj_id == bioconcept_id).filter(BioconceptDetails.class_type == class_type).first()
        return None if data is None else data.json
    return None

#Get reference data

def get_reference_details(reference_id, class_type):
    from src.sgd.model.perf.reference_data import ReferenceDetails
    if reference_id is not None:
        data = DBSession.query(ReferenceDetails).filter(ReferenceDetails.obj_id == reference_id).filter(ReferenceDetails.class_type == class_type).first()
        return None if data is None else data.json
    return None

#Get bioitem data

def get_bioitem_details(bioitem_id, class_type):
    from src.sgd.model.perf.bioitem_data import BioitemDetails
    if bioitem_id is not None:
        data = DBSession.query(BioitemDetails).filter(BioitemDetails.obj_id == bioitem_id).filter(BioitemDetails.class_type == class_type).first()
        return None if data is None else data.json
    return None

def get_bioitem_enrichment(bioitem_id, class_type):
    from src.sgd.model.perf.bioitem_data import BioitemEnrichment
    if bioitem_id is not None:
        data = DBSession.query(BioitemEnrichment).filter(BioitemEnrichment.obj_id == bioitem_id).filter(BioitemEnrichment.class_type == class_type).first()
        return None if data is None else data.json
    return None

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