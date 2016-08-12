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

from elasticsearch import Elasticsearch, TransportError

__author__ = 'kpaskov'

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

SEARCH_ES_INDEX = 'searchable_items'

import datetime

class PerfBackend(BackendInterface):
    def __init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory, esearch_addr=None):
        class Base(object):
            __table_args__ = {'schema': schema, 'extend_existing':True}

        perf.Base = declarative_base(cls=Base)

        engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), pool_recycle=3600)

        DBSession.configure(bind=engine)
        perf.Base.metadata.bind = engine

        self.log = set_up_logging(log_directory, 'perf')

        if esearch_addr:
            self.es = Elasticsearch(esearch_addr, timeout=5, retry_on_timeout=True)

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

    def alignments(self, strain_ids=None, limit=None, offset=None):
        from src.sgd.model.perf.core import Orphan
        alignment = DBSession.query(Orphan).filter_by(url='alignments').first().json
        if strain_ids is None and limit is None:
            return alignment
        else:
            alignment = json.loads(alignment)

            if strain_ids is not None:
                try:
                    strain_ids = [int(strain_id) for strain_id in strain_ids]
                    strain_ids.append(1)
                except Exception:
                    return None

                good_indices = []
                for i, strain in enumerate(alignment['strains']):
                    if strain['id'] in strain_ids:
                        good_indices.append(i)

                for locus in alignment['loci']:
                    locus['dna_scores'] = [locus['dna_scores'][i] for i in good_indices]
                    locus['protein_scores'] = [locus['protein_scores'][i] for i in good_indices]

            if limit is not None:
                try:
                    limit = int(limit)
                    if offset is not None:
                        offset = int(offset)
                    else:
                        offset = 0
                except Exception:
                    return None

                alignment['loci'] = [x for i, x in enumerate(alignment['loci']) if i >= offset and i <= offset + limit]

            return json.dumps(alignment)

    def alignment_bioent(self, locus_identifier=None, strain_ids=None, are_ids=False):
        if locus_identifier is not None:
            if are_ids:
                bioent_id = locus_identifier
            else:
                bioent_id = get_obj_id(str(locus_identifier).upper(), class_type='BIOENTITY', subclass_type='LOCUS')

            alignment = get_bioentity_details(bioent_id, 'ALIGNMENT')

            if alignment is None:
                return alignment

            if strain_ids is None:
                return alignment
            else:

                alignment = json.loads(alignment)
                try:
                    strain_ids = set([int(strain_id) for strain_id in strain_ids])
                    strain_ids.add(1)
                except Exception:
                    return None

                alignment['aligned_dna_sequences'] = [x for x in alignment['aligned_dna_sequences'] if x['strain_id'] in strain_ids]
                alignment['aligned_protein_sequences'] = [x for x in alignment['aligned_protein_sequences'] if x['strain_id'] in strain_ids]

                from src.sgd.backend import calculate_variant_data
                alignment['variant_data_dna'] = calculate_variant_data('DNA', alignment['aligned_dna_sequences'], alignment['introns'])
                alignment['variant_data_protein'] = calculate_variant_data('Protein', alignment['aligned_protein_sequences'], alignment['introns'])

                return json.dumps(alignment)
        return None

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

    def get_search_results(self, params):
        query = params['q'].lower() if 'q' in params.keys() else ''
        limit = params['limit'] if 'limit' in params.keys() else 10
        offset = params['offset'] if 'offset' in params.keys() else 0
        category = params['category'] if 'category' in params.keys() else ''
        sort_by = params['sort_by'] if 'sort_by' in params.keys() else ''

        #locus filters
        feature_type = params.get('feature type')
        phenotype = params.get('phenotype')
        cellular_component = params.get('cellular component')
        biological_process = params.get('biological process')
        molecular_function = params.get('molecular function')

        # phenotype filters
        qualifier = params.get('qualifier')
        references = params.get('references')
        phenotype_locus = params.get('phenotype_locus')
        chemical = params.get('chemical')
        mutant_type = params.get('mutant_type')

        #go terms
        go_id = params.get('go_id')
        term_name = params.get('term_name')
        go_locus = params.get('go_locus')

        # format: (GET param name, ES param name)
        locus_subcategories = [('feature type', 'feature_type'), ('molecular function', 'molecular_function'), ('phenotype', 'phenotypes'), ('cellular component', 'cellular_component'), ('biological process', 'biological_process')]

        phenotype_subcategories = [("observable", "observable"), ("qualifier", "qualifier"), ("references", "references"), ("phenotype_locus", "phenotype_loci"), ("chemical", "chemical"), ("mutant_type", "mutant_type")]

        go_subcategories = [("go_locus", "go_loci")]

        reference_subcategories = [("author", "author"), ("journal", "journal"), ("year", "year"), ("reference_locus", "reference_loci")]

        multi_match_fields = ["summary", "name_description", "phenotypes", "cellular_component", "biological_process", "molecular_function", "observable", "qualifier", "references", "phenotype_loci", "chemical", "mutant_type", "go_loci", "author", "journal", "year", "reference_loci", "synonyms", "ec_number", "gene_history", "sequence_history", "secondary_sgdid", "tc_number"]

        for special_char in ['-', '.']:
            if special_char in query:
                query = "\"" + query + "\""
                break

        if query == '':
            es_query = { 'match_all': {} }
        else:
            es_query = {
                "bool": {
                    "must_not" : {
                        "match" : {
                            "category" : "colleagues"
                        }
                    },
                    
                    "should": [
                        {
                            "match_phrase_prefix": {
                                "name": {
                                    "query": query,
                                    "boost": 4,
                                    "max_expansions": 30,
                                    "analyzer": "standard"
                                }
                            }
                        },
                        {
                            "match_phrase_prefix": {
                                "keys": {
                                    "query": query,
                                    "boost": 4,
                                    "max_expansions": 12,
                                    "analyzer": "standard"
                                }
                            }
                        },
                        {
                            "match_phrase": {
                                "name": {
                                    "query": query,
                                    "boost": 40,
                                    "analyzer": "standard"
                                }
                            }
                        },                        
                        {
                            "match": {
                                "description": {
                                    "query": query,
                                    "boost": 3,
                                    "analyzer": "standard"
                                }
                            }
                        },
                        {
                            "match_phrase": {
                                "keys": {
                                    "query": query,
                                    "boost": 50,
                                    "analyzer": "standard"
                                }
                            }
                        },
                        {
                            "multi_match": {
                                "query": query,
                                "type": "best_fields",
                                "fields": multi_match_fields,
                                "boost": 3
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            }

            if (query[0] in ('"', "'") and query[-1] in ('"', "'")):
                new_conditions = []
                for cond in es_query['bool']['should'][2:4]:
                    new_conditions.append({'match_phrase_prefix': cond.pop(cond.keys()[0])})
                multi_fields = {
                    "multi_match": {
                        "query": query,
                        "type": "phrase_prefix",
                        "fields": multi_match_fields,
                        "boost": 3
                    }
                }
                es_query['bool']['should'] = [es_query['bool']['should'][0]] + new_conditions + [multi_fields]

        if category != '':
            es_query = {
                'filtered': {
                    'query': es_query,
                    'filter': {
                        'bool': {
                            'must': [{'term': { 'category': category}}]
                        }
                    }
                }
            }

            if category == 'locus':
                for item in locus_subcategories:
                    if params.getall(item[0]):
                        for param in params.getall(item[0]):
                            es_query['filtered']['filter']['bool']['must'].append({'term': {(item[1]+".raw"): param}})

            elif category == 'phenotype':
                for item in phenotype_subcategories:
                    if params.getall(item[0]):
                        for param in params.getall(item[0]):
                            es_query['filtered']['filter']['bool']['must'].append({'term': {(item[1]+".raw"): param}})

            elif category == 'reference':
                for item in reference_subcategories:
                    if params.getall(item[0]):
                        for param in params.getall(item[0]):
                            es_query['filtered']['filter']['bool']['must'].append({'term': {(item[1]+".raw"): param}})
                        
            elif (category in ['biological_process', 'cellular_component', 'molecular_function']):
                for item in go_subcategories:
                    if params.getall(item[0]):
                        for param in params.getall(item[0]):
                            es_query['filtered']['filter']['bool']['must'].append({'term': {(item[1]+".raw"): param}})

        if query == '' and category == '':
            results_search_body = {
                "query": {
                    "function_score": {
                        "query": es_query,
                        "random_score": { "seed" : 12345 }
                    }
                },
                'highlight' : {
                    'fields' : {}
                }
            }
        else:
            results_search_body = {
                'query': es_query,
                'sort': [
                    '_score',
                    {'number_annotations': {'order': 'desc'}}
                ],
                'highlight' : {
                    'fields' : {}
                }
            }

        if sort_by == 'alphabetical':
            results_search_body['sort'] = [
                {
                    "name.raw": {
                        "order": "asc"
                    }
                }
            ]
        elif sort_by == 'annotation':
            results_search_body['sort'] = [
                {
                    "number_annotations": {
                        "order": "desc"
                    }
                }
            ]

        highlight_fields = ['name', 'description'] + multi_match_fields
        for field in highlight_fields:
            results_search_body['highlight']['fields'][field] = {}
        
        response_fields = ['name', 'href', 'description', 'category', 'bioentity_id', 'phenotype_loci', 'go_loci', 'reference_loci']
        results_search_body['_source'] = response_fields + ['keys']
        
#        if category == 'download':
#            results_search_body['_source'].append('data')

        search_results = self.es.search(index=SEARCH_ES_INDEX, body=results_search_body, size=limit, from_=offset)

        formatted_results = []

        for r in search_results['hits']['hits']:
            raw_obj = r.get('_source')

            obj = {}
            for field in response_fields:
                obj[field] = raw_obj.get(field)
                
            obj['highlights'] = r.get('highlight')

#            if obj["category"] == "download":
#                obj["download_metadata"] = {}
#                obj["download_metadata"]["pubmed_ids"] = raw_obj["data"].get("Series_pubmed_id")
#                obj["download_metadata"]["sample_ids"] = raw_obj["data"].get("Sample_geo_accession")
#                obj["download_metadata"]["download_url"] = "http://yeastgenome.org/download-fake-geo/" + obj["name"]
#                obj["download_metadata"]["title"] = raw_obj["data"].get("Series_title")
#                obj["download_metadata"]["citations"] = ["Park E, et al. (2015) Structure of a Bud6/Actin Complex Reveals a Novel WH2-like Actin Monomer Recruitment Motif. Structure 23(8):1492-9"]
#                obj["download_metadata"]["summary"] = raw_obj["data"].get("Series_summary")
#                obj["download_metadata"]["experiment_types"] = raw_obj["data"].get("Series_type")
#                obj["download_metadata"]["keywords"] = raw_obj["data"].get("Spell_tags")

            formatted_results.append(obj)

        if search_results['hits']['total'] == 0:
            response_obj = {
                'results': formatted_results,
                'total': search_results['hits']['total'],
                'aggregations': []
            }
            return json.dumps(response_obj)

        if query:
            for i in xrange(len(search_results['hits']['hits'])):
                if query.lower().strip() in search_results['hits']['hits'][i].get('_source').get('keys'):
                    formatted_results[i]['is_quick'] = True
        
        if category == '':
            formatted_agg = []
            agg_query_body = {
                'query': es_query,
                'size': 0,
                'aggs': {
                    'categories': {
                        'terms': { 'field': 'category' }
                    },
                    'feature_type': {
                        'terms': {'field': 'feature_type'}
                    }
                }
            }
            agg_response = self.es.search(index=SEARCH_ES_INDEX, body=agg_query_body)
        
            formatted_agg = []
            category_obj = {'values': [], 'key': 'category'}
            for category in agg_response['aggregations']['categories']['buckets']:
                category_obj['values'].append({'key': category['key'], 'total': category['doc_count']})
            formatted_agg.append(category_obj)
    
        elif category == 'locus':
            agg_query_body = {
                'query': es_query,
                'size': 0,
                'aggs': {
                    'feature_type': {
                        'terms': {'field': 'feature_type.raw', 'size': 999}
                    },
                    'molecular_function': {
                        'terms': {'field': 'molecular_function.raw', 'size': 999}
                    },
                    'phenotypes': {
                        'terms': {'field': 'phenotypes.raw', 'size': 999}
                    },
                    'cellular_component' : {
                        'terms': {'field': 'cellular_component.raw', 'size': 999}
                    },
                    'biological_process': {
                        'terms': {'field': 'biological_process.raw', 'size': 999}
                    }
                }
            }

            agg_response = self.es.search(index=SEARCH_ES_INDEX, body=agg_query_body)
        
            formatted_agg = []

            for agg_info in locus_subcategories:
                agg_obj = {'key': agg_info[0], 'values': []}
                for agg in agg_response['aggregations'][agg_info[1]]['buckets']:
                    agg_obj['values'].append({'key': agg['key'], 'total': agg['doc_count']})
                formatted_agg.append(agg_obj)

        elif category == 'phenotype':
            agg_query_body = {
                'query': es_query,
                'size': 0,
                'aggs': {
                    'observable': {
                        'terms': {'field': 'observable.raw', 'size': 999}
                    },
                    'qualifier': {
                        'terms': {'field': 'qualifier.raw', 'size': 999}
                    },
                    'references': {
                        'terms': {'field': 'references.raw', 'size': 999}
                    },
                    'phenotype_loci' : {
                        'terms': {'field': 'phenotype_loci.raw', 'size': 999}
                    },
                    'chemical': {
                        'terms': {'field': 'chemical.raw', 'size': 999}
                    },
                    'mutant_type': {
                        'terms': {'field': 'mutant_type.raw', 'size': 999}
                    }
                }
            }

            agg_response = self.es.search(index=SEARCH_ES_INDEX, body=agg_query_body)
        
            formatted_agg = []

            for agg_info in phenotype_subcategories:
                if agg_info[0] == 'phenotype_locus':
                    agg_obj = {'key': 'locus', 'values': []}
                elif agg_info[0] == 'mutant_type':
                    agg_obj = {'key': 'mutant type', 'values': []}
                else:
                    agg_obj = {'key': agg_info[0], 'values': []}
                for agg in agg_response['aggregations'][agg_info[1]]['buckets']:
                    agg_obj['values'].append({'key': agg['key'], 'total': agg['doc_count']})
                formatted_agg.append(agg_obj)
                
        elif (category in ['biological_process', 'cellular_component', 'molecular_function']):
            agg_query_body = {
                'query': es_query,
                'size': 0,
                'aggs': {
                    'go_loci': {
                        'terms': {'field': 'go_loci.raw', 'size': 999}
                    }
                }
            }

            agg_response = self.es.search(index=SEARCH_ES_INDEX, body=agg_query_body)
        
            formatted_agg = []

            for agg_info in go_subcategories:
                if agg_info[0] == 'go_locus':
                    agg_obj = {'key': 'locus', 'values': []}
                else:
                    agg_obj = {'key': agg_info[0], 'values': []}
                for agg in agg_response['aggregations'][agg_info[1]]['buckets']:
                    agg_obj['values'].append({'key': agg['key'], 'total': agg['doc_count']})
                formatted_agg.append(agg_obj)

        elif category == 'reference':
            agg_query_body = {
                'query': es_query,
                'size': 0,
                'aggs': {
                    'author': {
                        'terms': {'field': 'author.raw', 'size': 999}
                    },
                    'journal': {
                        'terms': {'field': 'journal.raw', 'size': 999}
                    },
                    'year': {
                        'terms': {'field': 'year.raw', 'size': 999}
                    },
                    'reference_loci' : {
                        'terms': {'field': 'reference_loci.raw', 'size': 999}
                    }
                }
            }

            agg_response = self.es.search(index=SEARCH_ES_INDEX, body=agg_query_body)
        
            formatted_agg = []

            for agg_info in reference_subcategories:
                if agg_info[0] == 'reference_locus':
                    agg_obj = {'key': 'locus', 'values': []}
                else:
                    agg_obj = {'key': agg_info[0], 'values': []}
                for agg in agg_response['aggregations'][agg_info[1]]['buckets']:
                    agg_obj['values'].append({'key': agg['key'], 'total': agg['doc_count']})
                formatted_agg.append(agg_obj)

        else:
            formatted_agg = []
            
        response_obj = {
            'results': formatted_results,
            'total': search_results['hits']['total'],
            'aggregations': formatted_agg
        }
        
        return json.dumps(response_obj)

    def search_sequence_objects(self, params):
        query = params['query'] if 'query' in params.keys() else ''
        query = query.lower()
        offset = int(params['offset']) if 'offset' in params.keys() else 0
        limit = int(params['limit']) if 'limit' in params.keys() else 1000

        query_type = 'wildcard' if '*' in query else 'match_phrase'
        if query == '':
            search_body = {
                'query': { 'match_all': {} },
                'sort': { 'absolute_genetic_start': { 'order': 'asc' }}
            }
        elif ',' in query:
            original_query_list = query.split(',')
            query_list = []
            for item in original_query_list:
                query_list.append(item.strip())
            search_body = {
                'query': {
                    'filtered': {
                        'filter': {
                            'terms': {
                                '_all': query_list
                            }
                        }
                    }
                }
            }
        else:
            search_body = {
                'query': {
                    query_type: {
                        '_all': query
                    }
                }
            }

        search_body['_source'] = ['sgdid', 'name', 'href', 'absolute_genetic_start', 'format_name', 'dna_scores', 'protein_scores', 'snp_seqs']
        res = self.es.search(index='sequence_objects', body=search_body, size=limit, from_=offset)
        simple_hits = []
        for hit in res['hits']['hits']:
            simple_hits.append(hit['_source'])
        formatted_response = {
            'loci': simple_hits,
            'total': res['hits']['total'],
            'offset': offset
        }
        return json.dumps(formatted_response)

    # get individual feature
    def get_sequence_object(self, locus_repr):
        id = locus_repr.upper()
        try:
            res = self.es.get(index='sequence_objects', id=id)['_source']
            return json.dumps(res)
        except TransportError:
            return Response(status_code=404)

    def autocomplete_results(self, params):
        if params.get("q") is None:
            return Response(status_code=422)

        query = params['q']
        search_body = {
            "query": {
                "bool": {
                    "must": {
                        "match": {
                            "name": {
                                "query": query,
                                "analyzer": "standard"
                            }
                        }
                    },
                    "must_not": { "match": { "category": "reference" }, "match": { "category": "download" }},
                    "should": [
                        {
                            "match": {
                                "category": {
                                    "query": "locus",
                                    "boost": 4
                                }
                            }
                        }
                    ]
                }
            }
        }
        res = self.es.search(index=SEARCH_ES_INDEX, body=search_body)
        simplified_results = []
        for hit in res['hits']['hits']:
            obj = {
                'name': hit['_source']['name'],
                'href': hit['_source']['href'],
                'category': hit['_source']['category']
            }
            simplified_results.append(obj)

        unique = []
        for hit in simplified_results:
            if hit not in unique:
                unique.append(hit)

        return json.dumps({"results": unique})
        
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
