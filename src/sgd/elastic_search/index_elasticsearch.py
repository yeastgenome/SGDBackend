from sqlalchemy import *
from src.sgd.convert import prepare_schema_connection
from src.sgd.convert import config
from src.sgd.model import nex
from src.sgd.model import perf
from elasticsearch import Elasticsearch
#import xlrd
import json

CLIENT_ADDRESS = 'http://52.41.106.165:9200/'# cluster alpha
INDEX_NAME = 'searchable_items_red'
DOC_TYPE = 'searchable_item'
RESET_INDEX = False
es = Elasticsearch(CLIENT_ADDRESS, retry_on_timeout=True)

# prep session
#nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_DBHOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
#perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, config.PERF_DBHOST, config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)

nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, config.PERF_HOST, config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
from src.sgd.model.nex.bioentity import Bioentity, Locus

from src.sgd.model.perf.core import Bioentity as PerfBioentity
from src.sgd.model.perf.core import Reference as PerfReference
from src.sgd.model.perf.bioentity_data import BioentityDetails as PerfBioentityDetails
from src.sgd.model.perf.bioconcept_data import BioconceptDetails as PerfBioconceptDetails
from src.sgd.model.perf.reference_data import ReferenceDetails
from src.sgd.model.nex.reference import Author
from src.sgd.model.nex.misc import Strain, Alias
from src.sgd.model.nex.bioconcept import Go
from src.sgd.model.nex.bioconcept import Phenotype
from src.sgd.model.nex.bioconcept import Observable
from src.sgd.model.nex.reference import Reference
from src.sgd.model.nex.bioitem import Contig
nex_session = nex_session_maker()
perf_session = perf_session_maker()

def setup_index():
    exists = es.indices.exists(INDEX_NAME)
    if RESET_INDEX and exists:
        es.indices.delete(INDEX_NAME)
    exists = es.indices.exists(INDEX_NAME)
    if not exists:
        es.indices.create(INDEX_NAME)
        put_mapping()
    return

def put_mapping():
    #PUT CLIENT_ADDRESS + searchable_items/
    mapping = '{"settings": {"index": {"max_result_window": 15000, "analysis": {"analyzer": {"default": {"type": "standard"}, "autocomplete": {"type": "custom", "filter": ["lowercase", "autocomplete_filter"], "tokenizer": "standard"}, "raw": {"type": "custom", "filter": ["lowercase"], "tokenizer": "keyword"}}, "filter": {"autocomplete_filter": {"min_gram": "1", "type": "edge_ngram", "max_gram": "20"}}}, "number_of_replicas": "1", "number_of_shards": "5"}}, "mappings": {"searchable_item": {"properties": {"biological_process": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}},"category": {"type": "string"}, "observable": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "qualifier": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "references": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "phenotype_loci": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "keys": {"type": "string"}, "secondary_sgdid": {"type": "string"}, "chemical": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "mutant_type": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "go_loci": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "strain": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "author": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "journal": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "year": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "reference_loci": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "ec_number": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "tc_number": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "cellular_component": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}},"description": {"type": "string"}, "sequence_history": {"type": "string"}, "gene_history": {"type": "string"}, "summary": {"type":"string"}, "feature_type": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}},"href": {"type": "string"}, "molecular_function": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}},"name": {"type": "string","analyzer": "autocomplete","fields": {"raw": {"type": "string","analyzer": "raw"}}}, "go_id": {"type": "string"}, "number_annotations": {"type": "integer"}, "name_description": {"type": "string"}, "synonyms": {"type": "string"}, "phenotypes": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}}}}}'
    return mapping

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def load_go_id_blacklist(list_filename):
    go_id_blacklist = set()
    for l in open(list_filename, 'r'):
        go_id_blacklist.add(l[:-1])
    return go_id_blacklist

def load_go_slim(go_slim_mappingtab_file):
    genes = {}

    for line in open(go_slim_mappingtab_file, 'r'):
        entry = line.split('\t')

        if len(entry) != 7:
            print "Ignoring line: " + "\t".join(entry)

        if entry[4] not in ('cellular_component', 'molecular_function', 'biological_process', 'other'):
        
            if entry[2] not in genes:
                genes[entry[2]] = {'cellular_component': [], 'biological_process': [], 'molecular_function': []}
            
            if entry[3] == 'C':
                genes[entry[2]]['cellular_component'].append(entry[4])
            elif entry[3] == 'F':
                genes[entry[2]]['molecular_function'].append(entry[4])
            elif entry[3] == 'P':
                genes[entry[2]]['biological_process'].append(entry[4])

    return genes

def index_genes(delete=False):
    all_genes = nex_session.query(Bioentity).all()
    genes_go_slim = load_go_slim('../go_slim_mapping.tab')

    tc_numbers_db = nex_session.query(Alias).filter_by(category="TC number").all()
    tc_numbers = {}
    for tc in tc_numbers_db:
        tc_numbers[tc.format_name] = tc.display_name

    secondary_db = nex_session.query(Alias).filter_by(category="DBID Secondary").all()
    secondary_sgdids = {}
    for sid in secondary_db:
        secondary_sgdids[sid.format_name] = sid.display_name
    
    print 'Indexing ' + str(len(all_genes)) + ' genes'

    for gene in all_genes:
        if delete:
            try:
                es.delete(index=INDEX_NAME, doc_type=DOC_TYPE, id=gene.sgdid)
            except:
                print "ID " + str(gene.sgdid) + " not found."
        
        if gene.display_name == gene.format_name:
            _name = gene.display_name
        else:
            _name = gene.display_name + ' / ' + gene.format_name

        go_annotations = perf_session.query(PerfBioentityDetails).filter_by(obj_id=gene.id, class_type="GO").first()
        go_annotations_json = json.loads(go_annotations.json)

        cellular_component = set()
        biological_process = set()
        molecular_function = set()
        for go_annotation in go_annotations_json:
            if go_annotation['go']['go_aspect'] == 'molecular function':
                molecular_function.add(go_annotation['go']['display_name'] + ' (direct)')
            elif go_annotation['go']['go_aspect'] == 'cellular component':
                cellular_component.add(go_annotation['go']['display_name'] + ' (direct)')
            elif go_annotation['go']['go_aspect'] == 'biological process':
                biological_process.add(go_annotation['go']['display_name'] + ' (direct)')
            else:
                print "GO CATEGORY UNKNOWN!"
                
        perf_result = perf_session.query(PerfBioentity).filter_by(id=gene.id).first()
        perf_json = perf_result.to_json()

        history_sequence = set()
        gene_history = set()
        if perf_json['history']:
            for h in perf_json['history']:
                if h['history_type'] != 'LSP':
                    history_sequence.add("(" + h['date_created'] + ") " + strip_tags(h['note']))
                elif h['history_type'] == 'LSP':
                    gene_history.add("(" + h['date_created'] + ") " + strip_tags(h['note']))

        ecnumbers = set()
        if perf_json['ecnumbers']:
            for ec in perf_json['ecnumbers']:
                ecnumbers.add(ec['display_name'])
            
        phenotypes = set()
        for k in ['large_scale_phenotypes', 'classical_phenotypes']:
            for kk in perf_json['phenotype_overview'][k].keys():
                for phenotype in perf_json['phenotype_overview'][k][kk]:
                    phenotypes.add(phenotype['display_name'])
                
        go_slim = genes_go_slim.get(gene.sgdid)
        if go_slim:
            if go_slim.get('cellular_component'):
                for k in go_slim['cellular_component']:
                    cellular_component.add(k)
            if go_slim.get('molecular_function'):
                for k in go_slim['molecular_function']:
                    molecular_function.add(k)
            if go_slim.get('biological_process'):
                for k in go_slim['biological_process']:
                    biological_process.add(k)
                    
        key_values = [gene.display_name, gene.format_name, gene.sgdid, gene.uniprotid]
        if "reserved_name" in perf_json:
            key_values += [perf_json['reserved_name']['display_name']]
        
        keys = set([])
        for k in key_values:
            if k is not None:
                keys.add(k.lower())
            
        for alias in perf_json['aliases']:
            if not alias['protein']:
                keys.add(alias['display_name'].lower())

        paragraph = ""
        if perf_json['paragraph'] is not None:
            paragraph = strip_tags(perf_json['paragraph']['text'])

        obj = {
            'name': _name,
            'href': gene.link,
            'description': gene.description,
            'category': 'locus',
            'feature_type': gene.locus_type,

            'name_description': gene.name_description,
            'summary': paragraph,
            
            'phenotypes': list(phenotypes),
            'cellular_component': list(cellular_component - set(["cellular component", "cellular component (direct)"])),
            'biological_process': list(biological_process - set(["biological process", "biological process (direct)"])),
            'molecular_function': list(molecular_function - set(["molecular function", "molecular function (direct)"])),
            'ec_number': list(ecnumbers),
            'tc_number': tc_numbers.get(str(gene.id)),
            'secondary_sgdid': secondary_sgdids.get(str(gene.id)),
            'sequence_history': list(history_sequence),
            'gene_history': list(gene_history),

            'bioentity_id': gene.id,

            'keys': list(keys)
        }

        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=gene.sgdid)

def index_phenotypes():
    all_phenotypes = nex_session.query(Phenotype).all()

    num_indexed = 0
    
    for phenotype in all_phenotypes:
        perf_result = perf_session.query(PerfBioconceptDetails).filter_by(obj_id=phenotype.id).filter_by(class_type="PHENOTYPE_LOCUS").first()
        perf_json = json.loads(perf_result.json)

        if len(perf_json) == 0:
            continue

        loci = set()
        references = set()
        chemical = set()
        mutant_type = set()
        for annotation in perf_json:
            loci.add(annotation['locus']['display_name'])

            reference = json.loads(perf_session.query(PerfReference).filter_by(id=annotation['reference']['id']).first().json)
            authors = []
            for author in reference['authors']:
                authors.append(author['display_name'])
            references.add(', '.join(authors) + ' (' + str(reference['year']) + ')')
            
            for prop in annotation['properties']:
                if prop['class_type'] == 'CHEMICAL':
                    chemical.add(prop['bioitem']['display_name'])
            mutant_type.add(annotation['mutant_type'])

        key_values = []

        keys = set([])
        for k in key_values:
            if k is not None:
                keys.add(k.lower())

        obj = {
            'name': phenotype.display_name,
            'href': phenotype.link,
            'description': phenotype.description,
            
            'observable': phenotype.observable.display_name,
            'qualifier': phenotype.qualifier,
            'references': list(references),
            'phenotype_loci': sorted(list(loci)),
            'number_annotations': len(perf_json),
            'chemical': list(chemical),
            'mutant_type': list(mutant_type),
            
            'category': 'phenotype',

            'keys': list(keys)
        }

        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=phenotype.format_name)
        num_indexed += 1
    
    print 'Indexing ' + str(num_indexed) + ' phenotypes'

def index_contigs():
    all_contigs = nex_session.query(Contig).all()

    print 'Indexing ' + str(len(all_contigs)) + ' contigs'
    
    for contig in all_contigs:
        key_values = [contig.display_name, contig.format_name, contig.gi_number, contig.genbank_accession]

        keys = set([])
        for k in key_values:
            if k is not None:
                keys.add(k.lower())

        obj = {
            'name': contig.display_name,
            'href': contig.link,
            'description': contig.description,
            'category': 'contig',

            'strain': str(contig.strain.display_name),
            'keys': list(keys)
        }

        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=contig.id)
        
def index_authors():
    all_authors = nex_session.query(Author).all()

    print 'Indexing ' + str(len(all_authors)) + ' authors'

    for author in all_authors:
        obj = {
            'name': author.display_name,
            'href': author.link,
            'description': '',
            'category': 'author'
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=author.id)

def index_observables():
    all_observables = nex_session.query(Observable).all()

    print 'Indexing ' + str(len(all_observables)) + ' observables'

    for observable in all_observables:
        key_values = []

        keys = set([])
        for k in key_values:
            if k is not None:
                keys.add(k.lower())

        obj = {
            'name': observable.display_name,
            'href': observable.link,
            'description': observable.description,
            'category': 'observable',

            'keys': list(keys)
        }

        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=observable.id)
        
def index_strains():
    all_strains = nex_session.query(Strain).all()

    print 'Indexing ' + str(len(all_strains)) + ' strains'

    for strain in all_strains:
        key_values = [strain.display_name, strain.format_name, strain.genbank_id]
        
        keys = set([])
        for k in key_values:
            if k is not None:
                keys.add(k.lower())

        obj = {
            'name': strain.display_name,
            'href': strain.link,
            'description': strain.description,
            'category': 'strain',

            'keys': list(keys)
        }
        
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=strain.id)

def index_go_terms():
    go_id_blacklist = load_go_id_blacklist('src/sgd/elastic_search/go_id_blacklist.lst')
    
    all_gos = nex_session.query(Go).all()

    num_indexed = 0
    for go in all_gos:
        if go.go_id in go_id_blacklist:
            continue
        
        loci = set()
        references = set()
        number_annotations = 0
        if go.locus_count > 0:
            perf_result = perf_session.query(PerfBioconceptDetails).filter_by(obj_id=go.id).filter_by(class_type="GO_LOCUS").first()
            perf_json = json.loads(perf_result.json)

            number_annotations = len(perf_json)
            
            for annotation in perf_json:
                if annotation['qualifier'] != 'NOT':
                    loci.add(annotation['locus']['display_name'])

                reference = json.loads(perf_session.query(PerfReference).filter_by(id=annotation['reference']['id']).first().json)
                authors = []
                for author in reference['authors']:
                    authors.append(author['display_name'])
                references.add(', '.join(authors) + ' (' + str(reference['year']) + ')')


        synonyms = [alias.display_name for alias in go.aliases]

        numerical_id = go.go_id.split(':')[1]
        key_values = [go.go_id, 'GO:' + str(int(numerical_id)), numerical_id, str(int(numerical_id))]

        keys = set([])
        for k in key_values:
            if k is not None:
                keys.add(k.lower())
            
        obj = {
            'name': go.display_name,
            'href': go.link,
            'description': go.description,

            'synonyms': synonyms,
            'go_id': go.go_id,
            'go_loci': sorted(list(loci)),
            'references': list(references),
            'number_annotations': number_annotations,
            
            'category': go.go_aspect.replace(' ', '_'),

            'keys': list(keys)
        }

        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=go.go_id)
        num_indexed += 1

    print 'Indexing ' + str(num_indexed) + ' GO terms'

def index_references():
    all_references = nex_session.query(Reference).all()

    secondary_db = nex_session.query(Alias).filter_by(category="DBID Secondary").all()
    secondary_sgdids = {}
    for sid in secondary_db:
        secondary_sgdids[sid.format_name] = sid.display_name

    print 'Indexing ' + str(len(all_references)) + ' references'

    for reference in all_references:
        perf_result = perf_session.query(ReferenceDetails).filter_by(obj_id=reference.id).filter_by(class_type="LITERATURE").first()

        loci = set()
        if perf_result:
            perf_json = json.loads(perf_result.json)

            for annotation in perf_json:
                loci.add(annotation['locus']['display_name'])

        reference_name = None
        if reference.journal:
            reference_name = reference.journal.display_name

        key_values = [reference.pubmed_central_id, reference.pubmed_id, "pmid: " + str(reference.pubmed_id), "pmid:" + str(reference.pubmed_id), "pmid " + str(reference.pubmed_id), reference.sgdid]

        keys = set([])
        for k in key_values:
            if k is not None:
                keys.add(str(k).lower())
                
        obj = {
            'name': reference.citation,
            'href': reference.link,
            'description': reference.abstract,

            'author': list(reference.author_names),
            'journal': reference_name,
            'year': reference.year,
            'reference_loci': sorted(list(loci)),
            'secondary_sgdid': secondary_sgdids.get(str(reference.id)),
            
            'category': 'reference',

            'keys': list(keys)
        }

        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=reference.sgdid)

def xls_to_dict(filename):
    workbook = xlrd.open_workbook(filename)
    
    sheet = workbook.sheet_by_index(0)
    header = sheet.row(0)

    sheet_json = {}

    for i in xrange(1, sheet.nrows):
        row = sheet.row(i)

        filename = row[0].value

        if sheet_json.get(filename) is None:
            sheet_json[filename] = {}
            for i in xrange(1, len(header)):
#                sheet_json[filename][header[i].value] = None
                sheet_json[filename][header[i].value] = []

        for i in xrange(1, len(row)):
            value_to_be_added = str(row[i].value).split("|")
            
            if row[i].value not in sheet_json[filename][header[i].value]:
                sheet_json[filename][header[i].value] += value_to_be_added
            continue
            
            if sheet_json[filename][header[i].value] is None:
                sheet_json[filename][header[i].value] = str(row[i].value)
            else:
                if isinstance(sheet_json[filename][header[i].value], list):
                    if row[i].value not in sheet_json[filename][header[i].value]:
                        sheet_json[filename][header[i].value].append(str(row[i].value))
                elif sheet_json[filename][header[i].value] != row[i].value:
                    sheet_json[filename][header[i].value] = [sheet_json[filename][header[i].value], str(row[i].value)]

    return sheet_json
        
def index_downloads_from_xls(filename):
    downloads = xls_to_dict(filename)

    print 'Indexing ' + str(len(downloads)) + ' download links from xls file: ' + filename

    for d in downloads:
        obj = {
            'name': d,
            'href': None,
            'description': None,
            'category': 'download',
            'data': downloads[d]
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=downloads[d]['Series_geo_accession'])

def index_downloads_from_json(filename):
    with open(filename, 'r') as content_file:
        content = content_file.read()
    downloads = json.loads(content)

    print 'Indexing ' + str(len(downloads)) + ' downloads form json file: ' + filename

    processed = {}
    i = 0
    for d in downloads:
        if processed.get(d['url']):
            processed[d['url'] + '?' + str(i)] = {
                'name': d['name'],
                'href': d['url'] + '?' + str(i),
                'description': d['description'],
                'category': 'download',
                'keys': []
            }
            i += 1
        else:
            processed[d['url']] = {
                'name': d['name'],
                'href': d['url'],
                'description': d['description'],
                'category': 'download',
                'keys': []
            }

    for d in processed:
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=processed[d], id=processed[d]['href'])

def index_toolbar_links():
    links = [("Gene List", "http://yeastmine.yeastgenome.org/yeastmine/bag.do",  []),
             ("Yeastmine", "http://yeastmine.yeastgenome.org",  'yeastmine'),
             ("Submit Data", "/cgi-bin/submitData.pl",  []),
             ("SPELL", "http://spell.yeastgenome.org",  'spell'),
             ("BLAST", "/blast-sgd",  'blast'),
             ("Fungal BLAST", "/blast-fungal",  'blast'),
             ("Pattern Matching", "/cgi-bin/PATMATCH/nph-patmatch",  []),
             ("Design Primers", "/cgi-bin/web-primer",  []),
             ("Restriction Mapper", "/cgi-bin/PATMATCH/RestrictionMapper",  []),
             ("Download", "/download-data/sequence",  'download'),
             ("Genome Browser", "/browse",  []),
             ("Gene/Sequence Resources", "/cgi-bin/seqTools",  []),
             ("Download Genome", "http://downloads.yeastgenome.org/sequence/S288C_reference/genome_releases/",  'download'),
             ("Genome Snapshot", "/genomesnapshot",  []),
             ("Chromosome History", "/cgi-bin/chromosomeHistory.pl",  []),
             ("Systematic Sequencing Table", "/cache/chromosomes.shtml",  []),
             ("Original Sequence Papers", "http://wiki.yeastgenome.org/index.php/Original_Sequence_Papers",  []),
             ("Variant Viewer", "/variant-viewer",  []),
             ("Align Strain Sequences", "/cgi-bin/FUNGI/alignment.pl",  []),
             ("Synteny Viewer", "/cgi-bin/FUNGI/FungiMap",  []),
             ("Fungal Alignment", "/cgi-bin/FUNGI/showAlign",  []),
             ("PDB Search", "/cgi-bin/protein/get3d",  'pdb'),
             ("GO Term Finder", "/cgi-bin/GO/goTermFinder.pl",  'go'),
             ("GO Slim Mapper", "/cgi-bin/GO/goSlimMapper.pl",  'go'),
             ("GO Slim Mapping File", "http://downloads.yeastgenome.org/curation/literature/go_slim_mapping.tab",  'go'),
             ("Expression", "http://spell.yeastgenome.org/#",  []),
             ("Biochemical Pathways", "http://pathway.yeastgenome.org/",  []),
             ("Browse All Phenotypes", "/ontology/phenotype/ypo/overview",  []),
             ("Interactions", "/interaction_search",  []),
             ("YeastGFP", "http://yeastgfp.yeastgenome.org/",  'yeastgfp'),
             ("Full-text Search", "http://textpresso.yeastgenome.org/",  'texxtpresso'),
             ("New Yeast Papers", "/reference/recent",  []),
             ("Genome-wide Analysis Papers", "/cache/genome-wide-analysis.html",  []),
             ("Find a Colleague", "/cgi-bin/colleague/colleagueInfoSearch",  []),
             ("Add or Update Info", "/cgi-bin/colleague/colleagueSearch",  []),
             ("Find a Yeast Lab", "/cache/yeastLabs.html",  []),
             ("Career Resources", "http://wiki.yeastgenome.org/index.php/Career_Resources",  []),
             ("Future", "http://wiki.yeastgenome.org/index.php/Meetings#Upcoming_Conferences_.26_Courses",  []),
             ("Yeast Genetics", "http://wiki.yeastgenome.org/index.php/Meetings#Past_Yeast_Meetings",  []),
             ("Submit a Gene Registration", "/cgi-bin/registry/geneRegistry",  []),
             ("Gene Registry", "/help/community/gene-registry",  []),
             ("Nomenclature Conventions", "/help/community/nomenclature-conventions",  []),
             ("Global Gene Hunter", "/cgi-bin/geneHunter",  []),
             ("Strains and Constructs", "http://wiki.yeastgenome.org/index.php/Strains",  []),
             ("Reagents", "http://wiki.yeastgenome.org/index.php/Reagents",  []),
             ("Protocols and Methods", "http://wiki.yeastgenome.org/index.php/Methods",  []),
             ("Physical & Genetic Maps", "http://wiki.yeastgenome.org/index.php/Combined_Physical_and_Genetic_Maps_of_S._cerevisiae",  []),
             ("Genetic Maps", "http://wiki.yeastgenome.org/index.php/Yeast_Mortimer_Maps_-_Edition_12",  []),
             ("Sequence", "http://wiki.yeastgenome.org/index.php/Historical_Systematic_Sequence_Information",  []),
             ("Gene Summary Paragraphs", "/cache/geneSummarytable.html",  []),
             ("Wiki", "http://wiki.yeastgenome.org/index.php/Main_Page",  'wiki'),
             ("Resources", "http://wiki.yeastgenome.org/index.php/External_Links",  [])]

    print 'Indexing ' + str(len(links)) + ' toolbar links'

    for l in links:
        obj = {
            'name': l[0],
            'href': l[1],
            'description': None,
            'category': 'resource',
            'keys': l[2]
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=l[1])
    
def main():
#    index_downloads_from_json('./downloadable_files.json')
#    index_toolbar_links()
#    index_observables()
#    index_strains()
#    index_phenotypes()
#    index_genes()
#    index_go_terms()
    index_references()

main()
