from datetime import datetime
import json
import logging
import uuid
import re
from math import ceil

from pyramid.response import Response
from sqlalchemy import func, distinct
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from src.sgd.backend.backend_interface import BackendInterface
from src.sgd.model import nex
import random
from sqlalchemy.orm import joinedload

from elasticsearch import Elasticsearch, TransportError

__author__ = 'kpaskov'

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
query_limit = 25000

SEARCH_ES_INDEX = 'searchable_items_blue'

class SGDBackend(BackendInterface):
    def __init__(self, dbtype, dbhost, dbname, schema, dbuser, dbpass, log_directory, esearch_addr=None):
        class Base(object):
            __table_args__ = {'schema': schema, 'extend_existing':True}

        nex.Base = declarative_base(cls=Base)
        engine = create_engine("%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname), pool_recycle=3600)

        DBSession.configure(bind=engine)
        nex.Base.metadata.bind = engine
        
        self.log = set_up_logging(log_directory, 'nex')

        if esearch_addr:
            self.es = Elasticsearch(esearch_addr, timeout=5, retry_on_timeout=True)

        
    def get_renderer(self, method_name):
        return 'string'
    
    def response_wrapper(self, method_name, request):
        request_id = str(uuid.uuid4())
        callback = None if 'callback' not in request.GET else request.GET['callback']
        self.log.info(request_id + ' ' + method_name + ('' if 'identifier' not in request.matchdict else ' ' + request.matchdict['identifier']))
        def f(data):
            self.log.info(request_id + ' end')

            if isinstance(data, Response):
                return data

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
        return [x.to_json() for x in DBSession.query(Bioentity).with_polymorphic('*').order_by(Bioentity.id.asc()).limit(chunk_size).offset(offset).all()]

    def all_tags(self, chunk_size, offset):
        from src.sgd.model.nex.misc import Tag
        from src.sgd.model.nex.bioitem import BioitemTag
        return [x.to_json() for x in DBSession.query(Tag).with_polymorphic('*').limit(chunk_size).offset(offset).all()]

    def tag_list(self):
        from src.sgd.model.nex.misc import Tag
        return json.dumps([x.to_min_json(include_description=True) for x in DBSession.query(Tag).all()])

    def locus_list(self, list_type):
        from src.sgd.model.nex.bioentity import Locus
        from src.sgd.model.nex import locus_types

        list_types = dict([(x.lower(), x) for x in locus_types])
        if list_type.lower() in list_types:
            locus_type = list_types[list_type.lower()]
            return json.dumps({
                                'list_name': locus_type,
                                'locii': [x.to_min_json(include_description=True) for x in DBSession.query(Locus).filter_by(bioent_status='Active').filter_by(locus_type=locus_type).all()]
            })

    def alignments(self, strain_ids=None, limit=None, offset=None):
        from src.sgd.model.nex.misc import Strain
        from src.sgd.model.nex.bioentity import Locus
        from src.sgd.model.nex.evidence import Alignmentevidence, DNAsequenceevidence

        ordered_strains = ['S288C', 'X2180-1A', 'SEY6210', 'W303', 'JK9-3d', 'FL100', 'CEN.PK', 'D273-10B', 'Sigma1278b', 'RM11-1a', 'SK1', 'Y55']
        strains = [x.to_min_json() for x in DBSession.query(Strain).filter_by(status='Reference').all()]
        strains.extend([x.to_min_json() for x in DBSession.query(Strain).filter_by(status='Alternative Reference').all()])
        strains.sort(key=lambda x: float('infinity') if x['display_name'] not in ordered_strains else ordered_strains.index(x['display_name']))

        if strain_ids is not None:
            strains = [x for x in strains if str(x['id']) in strain_ids]

        strain_id_to_index = dict([(x['id'], i) for i, x in enumerate(strains)])

        locus_ids = [x.locus_id for x in DBSession.query(DNAsequenceevidence).filter_by(strain_id=1).filter_by(dna_type='GENOMIC').order_by(DNAsequenceevidence.contig_id, DNAsequenceevidence.start).limit(limit).offset(offset).all()]
        locuses = []

        chunk_size = 500
        for i in range(0, len(locus_ids), chunk_size):
            new_locus_ids = locus_ids[i:i+chunk_size]
            id_to_new_locus = dict()

            for x in DBSession.query(Locus).filter(Locus.id.in_(set(new_locus_ids))):
                if x.locus_type == 'ORF' or x.locus_type == 'blocked_reading_frame':
                    obj_json = x.to_min_json()
                    obj_json['headline'] = x.headline
                    obj_json['qualifier'] = x.qualifier
                    obj_json['sgdid'] = x.sgdid
                    obj_json['locus_type'] = x.locus_type
                    obj_json['dna_scores'] = [None for _ in strains]
                    obj_json['protein_scores'] = [None for _ in strains]

                    id_to_new_locus[x.id] = obj_json

            alignment_evidences = DBSession.query(Alignmentevidence).filter(Alignmentevidence.locus_id.in_(set(new_locus_ids))).all()

            for alignment_evidence in alignment_evidences:
                if alignment_evidence.strain_id in strain_id_to_index and alignment_evidence.locus_id in id_to_new_locus.keys():
                    strain_index = strain_id_to_index[alignment_evidence.strain_id]
                    if alignment_evidence.sequence_type == 'Genomic DNA':
                        id_to_new_locus[alignment_evidence.locus_id]['dna_scores'][strain_index] = alignment_evidence.similarity_score
                    elif alignment_evidence.sequence_type == 'Protein':
                        id_to_new_locus[alignment_evidence.locus_id]['protein_scores'][strain_index] = alignment_evidence.similarity_score

            locuses.extend([id_to_new_locus[locus_id] for locus_id in new_locus_ids if locus_id in id_to_new_locus])

        print len(locuses)

        return json.dumps({'loci': locuses,
                           'strains': strains,
                           'graph_data': {}})
        return None

    def alignment_bioent(self, locus_identifier=None, strain_ids=None, are_ids=False):
        import view_sequence
        from src.sgd.backend import calculate_variant_data
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        alignment = json.dumps(view_sequence.make_alignment(locus_id=locus_id))

        if strain_ids is None:
            return alignment
        else:
            try:
                strain_ids = [int(strain_id) for strain_id in strain_ids]
                strain_ids.append(1)
            except Exception:
                return None
            alignment = json.loads(alignment)
            alignment['aligned_dna_sequences'] = [x for x in alignment['aligned_dna_sequences'] if x['strain_id'] in strain_ids]
            alignment['aligned_protein_sequences'] = [x for x in alignment['aligned_protein_sequences'] if x['strain_id'] in strain_ids]

            alignment['variant_data_dna'] = calculate_variant_data('DNA', alignment['aligned_dna_sequences'], alignment['introns'])
            alignment['variant_data_protein'] = calculate_variant_data('Protein', alignment['aligned_protein_sequences'], alignment['introns'])
            return json.dumps(alignment)

    def snapshot(self):
        #Go
        from src.sgd.model.nex.bioconcept import Go, Bioconceptrelation
        from src.sgd.model.nex.evidence import Goevidence, Goslimevidence
        from src.sgd.model.nex import locus_types
        id_to_go_slim = dict([(x.id, x) for x in DBSession.query(Go).filter_by(is_slim=1).all()])
        go_slim_terms = []
        go_relationships = [['Child', 'Parent']]
        for go_term in id_to_go_slim.values():
            obj_json = go_term.to_min_json()
            obj_json['descendant_annotation_gene_count'] = len(go_term.goslim_evidences)
            obj_json['direct_annotation_gene_count'] = go_term.locus_count
            obj_json['is_root'] = go_term.is_root
            go_slim_terms.append(obj_json)

            parents = [x.parent for x in go_term.parents if x.relation_type == 'is a']
            while parents is not None and len(parents) > 0:
                new_parents = []
                for parent in parents:
                    if parent.id in id_to_go_slim:
                        go_relationships.append([go_term.id, parent.id])
                        break
                    else:
                        new_parents.extend([x.parent for x in parent.parents if x.relation_type == 'is a'])
                parents = new_parents
        annotated_to_other_bp = DBSession.query(Goslimevidence).filter_by(go_id=None).filter_by(aspect='P').count()
        annotated_to_other_mf = DBSession.query(Goslimevidence).filter_by(go_id=None).filter_by(aspect='F').count()
        annotated_to_other_cc = DBSession.query(Goslimevidence).filter_by(go_id=None).filter_by(aspect='C').count()

        #Phenotype
        from src.sgd.model.nex.bioconcept import Observable, Bioconceptrelation
        from src.sgd.model.nex.evidence import Phenotypeevidence
        phenotype_slim_ids = set([x.parent_id for x in DBSession.query(Bioconceptrelation).filter_by(relation_type='PHENOTYPE_SLIM').all()])
        phenotypes = DBSession.query(Observable).filter(Observable.id.in_(phenotype_slim_ids)).all()
        phenotype_slim_terms = []
        phenotype_relationships = [['Child', 'Parent']]
        for phenotype in phenotypes:
            obj_json = phenotype.to_min_json()
            obj_json['descendant_annotation_gene_count'] = phenotype.descendant_locus_count
            obj_json['direct_annotation_gene_count'] = phenotype.locus_count
            obj_json['is_root'] = phenotype.is_root
            phenotype_slim_terms.append(obj_json)

            parents = [x.parent for x in phenotype.parents if x.relation_type == 'is a']
            while parents is not None and len(parents) > 0:
                new_parents = []
                for parent in parents:
                    if parent.id in phenotype_slim_ids:
                        phenotype_relationships.append([phenotype.id, parent.id])
                        break
                    else:
                        new_parents.extend([x.parent for x in parent.parents if x.relation_type == 'is a'])
                parents = new_parents

        #Sequence
        from src.sgd.model.nex.bioentity import Locus
        from src.sgd.model.nex.bioitem import Contig
        from src.sgd.model.nex.evidence import DNAsequenceevidence
        from src.sgd.model.nex.misc import Strain

        id_to_strain = dict([(x.id, x) for x in DBSession.query(Strain)])
        contigs = DBSession.query(Contig).filter(Contig.strain_id == 1).all()
        labels = list(locus_types)
        labels.append('Verified')
        labels.append('Dubious')
        labels.append('Uncharacterized')

        contig_id_to_index = {}
        label_to_index = {}
        for contig in contigs:
            contig_id_to_index[contig.id] = len(contig_id_to_index)
        for label in labels:
            label_to_index[label] = len(label_to_index)

        locuses = DBSession.query(Locus).filter_by(bioent_status='Active').all()
        locus_id_to_label_index = dict([(x.id, label_to_index[x.locus_type]) for x in locuses if x.locus_type in label_to_index])
        locus_id_to_char_label_index = dict([(x.id, label_to_index[x.qualifier]) for x in locuses if x.qualifier is not None])

        data = [([0]*len(contigs)) for _ in range(len(labels))]

        print 'ready', len(labels), len(contigs), len(data), len(data[0])

        for evidence in DBSession.query(DNAsequenceevidence).filter_by(dna_type='GENOMIC').filter(DNAsequenceevidence.contig_id.in_(contig_id_to_index.keys())).all():
            locus_id = evidence.locus_id
            label_index = None if evidence.locus_id not in locus_id_to_label_index else locus_id_to_label_index[locus_id]
            contig_index = None if evidence.contig_id not in contig_id_to_index else contig_id_to_index[evidence.contig_id]
            if label_index is not None and contig_index is not None:
                data[label_index][contig_index] += 1

            if locus_id in locus_id_to_char_label_index and contig_index is not None:
                char_label_index = locus_id_to_char_label_index[locus_id]
                if char_label_index is not None:
                    data[char_label_index][contig_index] += 1

        columns = []
        for x in contigs:
            obj_json = x.to_min_json()
            obj_json['strain'] = id_to_strain[x.strain_id].to_min_json()
            obj_json['length'] = len(x.residues)
            columns.append(obj_json)

        return json.dumps({'phenotype_slim_terms': phenotype_slim_terms, 'phenotype_slim_relationships': phenotype_relationships,
                           'go_slim_terms': go_slim_terms, 'go_slim_relationships': go_relationships,
                           'go_annotated_to_other_bp': annotated_to_other_bp,
                           'go_annotated_to_other_mf': annotated_to_other_mf,
                           'go_annotated_to_other_cc': annotated_to_other_cc,
                           'data': data, 'columns': columns, 'rows': labels})

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
        return [x.to_json() for x in DBSession.query(Locustabs).order_by(Locustabs.id.desc()).limit(chunk_size).offset(offset).all()]

    def all_locusentries(self, chunk_size, offset):
        from src.sgd.model.nex.bioentity import Locus
        return [x.to_semi_json() for x in DBSession.query(Locus).order_by(Locus.id.desc()).limit(chunk_size).offset(offset).all()]
    
    def locus(self, locus_identifier, are_ids=False):
        from src.sgd.model.nex.bioentity import Locus
        from src.sgd.model.nex.evidence import Phenotypeevidence, Goevidence, Regulationevidence, Geninteractionevidence, \
            Physinteractionevidence, DNAsequenceevidence, Domainevidence, Historyevidence
        from src.sgd.model.nex.paragraph import Bioentityparagraph
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(DBSession.query(Locus).filter_by(id=locus_id).first().to_json())

    #Bioconcept
    def all_bioconcepts(self, chunk_size, offset):
        from src.sgd.model.nex.bioconcept import Bioconcept
        from src.sgd.model.nex.evidence import Phenotypeevidence
        from src.sgd.model.nex.evidence import Goevidence
        return [x.to_json() for x in DBSession.query(Bioconcept).with_polymorphic('*').order_by(Bioconcept.id.desc()).limit(chunk_size).offset(offset).all()]

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
        from src.sgd.model.nex.paragraph import Referenceparagraph
        from src.sgd.model.nex.evidence import DNAsequenceevidence
        return [x.to_json() for x in DBSession.query(Bioitem).with_polymorphic('*').order_by(Bioitem.id.desc()).limit(chunk_size).offset(offset).all()]

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
        from src.sgd.model.nex.bioitem import Contig
        return [x.to_json() for x in DBSession.query(Strain).order_by(Strain.id.desc()).limit(chunk_size).offset(offset).all()]

    def experiment(self, experiment_identifier, are_ids=False):
        from src.sgd.model.nex.misc import Experiment
        from src.sgd.model.nex.evidence import Goevidence, Geninteractionevidence, Physinteractionevidence, Phenotypeevidence, Regulationevidence, Bindingevidence, Proteinexperimentevidence
        if are_ids:
            experiment_id = experiment_identifier
        else:
            experiment_id = get_obj_id(experiment_identifier, class_type='EXPERIMENT')
        return None if experiment_id is None else json.dumps(DBSession.query(Experiment).filter_by(id=experiment_id).first().to_json())

    def all_experiments(self, chunk_size, offset):
        from src.sgd.model.nex.misc import Experiment
        return [x.to_json() for x in DBSession.query(Experiment).order_by(Experiment.id.desc()).limit(chunk_size).offset(offset).all()]

    def domain(self, domain_identifier, are_ids=False):
        from src.sgd.model.nex.bioitem import Domain
        if are_ids:
            domain_id = domain_identifier
        else:
            domain_id = get_obj_id(domain_identifier, class_type='BIOITEM', subclass_type='DOMAIN')
        return None if domain_id is None else json.dumps(DBSession.query(Domain).filter_by(id=domain_id).first().to_json())

    def reserved_name(self, reserved_name_identifier, are_ids=False):
        from src.sgd.model.nex.bioitem import Reservedname
        if are_ids:
            reserved_name_id = reserved_name_identifier
        else:
            reserved_name_id = get_obj_id(reserved_name_identifier, class_type='BIOITEM', subclass_type='RESERVEDNAME')
        return None if reserved_name_id is None else json.dumps(DBSession.query(Reservedname).filter_by(id=reserved_name_id).first().to_json())

    def contig(self, contig_identifier, are_ids=False):
        import view_sequence
        if are_ids:
            contig_id = contig_identifier
        else:
            contig_id = get_obj_id(contig_identifier, class_type='BIOITEM', subclass_type='CONTIG')
        return None if contig_id is None else json.dumps(view_sequence.make_contig(contig_id))

    def dataset(self, dataset_identifier, are_ids=False):
        from src.sgd.model.nex.bioitem import Dataset
        from src.sgd.model.nex.paragraph import Referenceparagraph
        from src.sgd.model.nex.evidence import Phenotypeevidence, Goevidence, Physinteractionevidence, \
            Geninteractionevidence, Regulationevidence, Literatureevidence
        if are_ids:
            dataset_id = dataset_identifier
        else:
            dataset_id = get_obj_id(dataset_identifier, class_type='BIOITEM', subclass_type='DATASET')
        return None if dataset_id is None else json.dumps(DBSession.query(Dataset).filter_by(id=dataset_id).first().to_json())

    def tag(self, tag_identifier, are_ids=False):
        from src.sgd.model.nex.misc import Tag
        if are_ids:
            tag_id = tag_identifier
        else:
            tag_id = get_obj_id(tag_identifier, class_type='TAG')
        return None if tag_id is None else json.dumps(DBSession.query(Tag).filter_by(id=tag_id).first().to_json())

    #EC number
    def ec_number_details(self, locus_identifier=None, ec_number_identifier=None, are_ids=False):
        import view_ec_number
        if are_ids:
            locus_id = locus_identifier
            ec_number_id = ec_number_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            ec_number_id = None if ec_number_identifier is None else get_obj_id(ec_number_identifier, class_type='BIOCONCEPT', subclass_type='ECNUMBER')

        return view_ec_number.make_details(locus_id=locus_id, ec_number_id=ec_number_id)

    #Reference
    def all_references(self, chunk_size, offset):
        from src.sgd.model.nex.reference import Reference
        from src.sgd.model.nex.paragraph import Referenceparagraph
        from src.sgd.model.nex.evidence import Phenotypeevidence, Goevidence, Physinteractionevidence, \
            Geninteractionevidence, Regulationevidence, Literatureevidence
        return [x.to_json() for x in DBSession.query(Reference).order_by(Reference.id.desc()).limit(chunk_size).offset(offset).all()]

    def all_bibentries(self, chunk_size, offset):
        from src.sgd.model.nex.reference import Bibentry
        return [{'id': x.id, 'text': x.text} for x in DBSession.query(Bibentry).order_by(Bibentry.id.desc()).limit(chunk_size).offset(offset).all()]

    def reference_list(self, reference_ids):
        from src.sgd.model.nex.reference import Bibentry
        if reference_ids is None:
            return json.dumps({'Error': 'No locus_id or go_id given.'})
        return json.dumps([{'id': x.id, 'text': x.text} for x in DBSession.query(Bibentry).filter(Bibentry.id.in_(reference_ids)).all()])

    def all_authors(self, chunk_size, offset):
        from src.sgd.model.nex.reference import Author
        return [x.to_json() for x in DBSession.query(Author).order_by(Author.id.desc()).limit(chunk_size).offset(offset).all()]

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
        return json.dumps({'start': str(a_week_ago),
                            'end': str(date.today()),
                            'references': [x.to_semi_json() for x in sorted(DBSession.query(Reference).filter(Reference.date_created > a_week_ago).all(), key=lambda x: (-int(x.year), x.display_name) )]})

    #Phenotype
    def phenotype_ontology_graph(self, observable_identifier, are_ids=False):
        import graph_tools
        from src.sgd.model.nex.evidence import Phenotypeevidence
        if are_ids:
            observable_id = observable_identifier
        else:
            observable_id = get_obj_id(observable_identifier, class_type='BIOCONCEPT', subclass_type='OBSERVABLE')
        return None if observable_id is None else json.dumps(graph_tools.make_ontology_graph(observable_id, 'OBSERVABLE', lambda x: True, lambda x: None if not hasattr(x, 'ancestor_type') else x.ancestor_type))

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
        
        return view_phenotype.make_details(locus_id=locus_id, phenotype_id=phenotype_id, observable_id=observable_id, chemical_id=chemical_id, reference_id=reference_id, with_children=with_children)

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

    #Expression
    def expression_details(self, locus_identifier=None, are_ids=False):
        from src.sgd.backend.nex import view_expression
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')

        return view_expression.make_details(locus_id=locus_id)

    def expression_graph(self, locus_identifier, are_ids=False):
        import view_expression
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_expression.make_graph(locus_id))

    # Go
    def go_ontology_graph(self, go_identifier, are_ids=False):
        import graph_tools
        from src.sgd.model.nex.evidence import Goevidence
        if are_ids:
            go_id = go_identifier
        else:
            go_id = get_obj_id(go_identifier, class_type='BIOCONCEPT', subclass_type='GO')
        return None if go_id is None else json.dumps(graph_tools.make_ontology_graph(go_id, 'GO', lambda x: True, lambda x: ''))
    
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
        return view_go.make_details(locus_id=locus_id, go_id=go_id, reference_id=reference_id, with_children=with_children)
    
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
        return view_interaction.make_details(locus_id=locus_id, reference_id=reference_id)
        
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
        return view_literature.make_details(locus_id=locus_id, reference_id=reference_id, topic=topic)
    
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
        return None if locus_id is None and domain_id is None else view_protein.make_details(locus_id=locus_id, domain_id=domain_id)

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
        return None if locus_id is None else view_protein.make_phosphorylation_details(locus_id=locus_id)

    def posttranslational_details(self, locus_identifier, are_ids=False):
        from src.sgd.backend.nex import view_protein
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else view_protein.make_posttranslational_details(locus_id=locus_id)

    def protein_experiment_details(self, locus_identifier, are_ids=False):
        from src.sgd.backend.nex import view_protein
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else view_protein.make_protein_experiment_details(locus_id=locus_id)

    def history_details(self, locus_identifier, are_ids=False):
        from src.sgd.backend.nex import view_history
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else view_history.make_details(locus_id=locus_id)

    #Regulation
    def regulation_details(self, locus_identifier=None, reference_identifier=None, are_ids=False):
        import view_regulation
        if are_ids:
            locus_id = locus_identifier
            reference_id = reference_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
            reference_id = None if reference_identifier is None else get_obj_id(reference_identifier, class_type='REFERENCE')
        return view_regulation.make_details(locus_id=locus_id, reference_id=reference_id)
            
    def regulation_graph(self, locus_identifier, are_ids=False):
        import view_regulation
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return None if locus_id is None else json.dumps(view_regulation.make_graph(locus_id))
    
    def regulation_target_enrichment(self, locus_identifier, are_ids=False):
        from src.sgd.model.nex.evidence import Regulationevidence
        from src.sgd.backend.nex import view_go
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        target_ids = set([x.locus2_id for x in DBSession.query(Regulationevidence).filter_by(locus1_id=locus_id).all()])
        if len(target_ids) > 0:
            return json.dumps(view_go.make_enrichment(target_ids))
        else:
            return '[]'

    def domain_enrichment(self, domain_identifier, are_ids=False):
        from src.sgd.model.nex.evidence import Domainevidence
        from src.sgd.backend.nex import view_go
        if are_ids:
            domain_id = domain_identifier
        else:
            domain_id = get_obj_id(domain_identifier, class_type='BIOITEM', subclass_type='DOMAIN')
        target_ids = set([x.locus_id for x in DBSession.query(Domainevidence).filter_by(domain_id=domain_id).all()])
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
        return view_sequence.make_binding_details(locus_id=locus_id)

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

    def alignment_details(self, locus_identifier=None, are_ids=False):
        import view_sequence
        if are_ids:
            locus_id = locus_identifier
        else:
            locus_id = None if locus_identifier is None else get_obj_id(locus_identifier, class_type='BIOENTITY', subclass_type='LOCUS')
        return json.dumps(view_sequence.make_alignment_details(locus_id=locus_id))
    
    #Misc
    def all_disambigs(self, chunk_size, offset):
        from src.sgd.model.nex.auxiliary import Disambig
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

        contig_subcategories = [("strain", "strain")]

        multi_match_fields = ["summary", "name_description", "phenotypes", "cellular_component", "biological_process", "molecular_function", "observable", "qualifier", "references", "phenotype_loci", "chemical", "mutant_type", "go_loci", "author", "journal", "year", "reference_loci", "synonyms", "ec_number", "gene_history", "sequence_history", "secondary_sgdid", "tc_number", "strain"]

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
                                    "boost": 3,
                                    "max_expansions": 30,
                                    "analyzer": "standard"
                                }
                            }
                        },
                        {
                            "match_phrase_prefix": {
                                "keys": {
                                    "query": query,
                                    "boost": 35,
                                    "max_expansions": 12,
                                    "analyzer": "standard"
                                }
                            }
                        },
                        {
                            "match_phrase": {
                                "name": {
                                    "query": query,
                                    "boost": 80,
                                    "analyzer": "standard"
                                }
                            }
                        },                        
                        {
                            "match": {
                                "description": {
                                    "query": query,
                                    "boost": 1,
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
                                "boost": 1
                            }
                        },
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
                },
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

            elif category == 'contig':
                for item in contig_subcategories:
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
        
        search_results = self.es.search(index=SEARCH_ES_INDEX, body=results_search_body, size=limit, from_=offset)            

        formatted_results = []

        for r in search_results['hits']['hits']:
            raw_obj = r.get('_source')

            obj = {}
            for field in response_fields:
                obj[field] = raw_obj.get(field)
                
            obj['highlights'] = r.get('highlight')

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
                if query.replace('"', '').lower().strip() in search_results['hits']['hits'][i].get('_source').get('keys'):
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

        elif category == 'contig':
            agg_query_body = {
                'query': es_query,
                'size': 0,
                'aggs': {
                    'strain': {
                        'terms': {'field': 'strain.raw', 'size': 999}
                    }
                }
            }

            agg_response = self.es.search(index=SEARCH_ES_INDEX, body=agg_query_body)
        
            formatted_agg = []

            for agg_info in contig_subcategories:
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

def get_random_obj_id(class_type, subclass_type):
    from src.sgd.model.nex.auxiliary import Disambig
    query = DBSession.query(Disambig)
    if class_type is not None:
        query = query.filter(class_type == Disambig.class_type)
    if subclass_type is not None:
        query = query.filter(subclass_type == Disambig.subclass_type)

    all_ids = list(set([x.identifier for x in query.all()]))
    return random.choice(all_ids)


def get_obj_id(identifier, class_type=None, subclass_type=None):
    if identifier.lower() == 'random':
        obj_id = get_random_obj_id(class_type, subclass_type)
    else:
        objs_ids = get_obj_ids(identifier, class_type=class_type, subclass_type=subclass_type)
        obj_id = None if objs_ids is None or len(objs_ids) == 0 else objs_ids[0][0]
    return obj_id
