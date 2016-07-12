from sqlalchemy import *
from src.sgd.convert import prepare_schema_connection
from src.sgd.convert import config
from src.sgd.model import nex
from src.sgd.model import perf
from elasticsearch import Elasticsearch
#import xlrd
import json

#CLIENT_ADDRESS = 'http://localhost:9200'
INDEX_NAME = 'searchable_items'
DOC_TYPE = 'searchable_item'
RESET_INDEX = False
es = Elasticsearch(CLIENT_ADDRESS, retry_on_timeout=True)

# prep session
nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, config.PERF_HOST, config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
from src.sgd.model.nex.bioentity import Bioentity, Locus

from src.sgd.model.perf.core import Bioentity as PerfBioentity
from src.sgd.model.perf.bioentity_data import BioentityDetails as PerfBioentityDetails
from src.sgd.model.perf.bioconcept_data import BioconceptDetails as PerfBioconceptDetails
from src.sgd.model.perf.reference_data import ReferenceDetails
from src.sgd.model.nex.reference import Author
from src.sgd.model.nex.misc import Strain
from src.sgd.model.nex.bioconcept import Go
from src.sgd.model.nex.bioconcept import Phenotype
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
    mapping = '{"settings": {"index": {"analysis": {"analyzer": {"default": {"type": "standard"}, "autocomplete": {"type": "custom", "filter": ["lowercase", "autocomplete_filter"], "tokenizer": "standard"}, "raw": {"type": "custom", "filter": ["lowercase"], "tokenizer": "keyword"}}, "filter": {"autocomplete_filter": {"min_gram": "1", "type": "edge_ngram", "max_gram": "20"}}}, "number_of_replicas": "1", "number_of_shards": "5"}}, "mappings": {"searchable_item": {"properties": {"biological_process": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}},"category": {"type": "string"}, "observable": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "qualifier": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "references": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "phenotype_loci": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "keys": {"type": "string"}, "chemical": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "mutant_type": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "go_loci": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "author": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "journal": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "year": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "reference_loci": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}, "cellular_component": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}},"description": {"type": "string"}, "summary": {"type":"string"}, "feature_type": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}},"href": {"type": "string"}, "molecular_function": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}},"name": {"type": "string","analyzer": "autocomplete","fields": {"raw": {"type": "string","analyzer": "raw"}}}, "go_id": {"type": "string"}, "number_annotations": {"type": "integer"}, "name_description": {"type": "string"}, "phenotypes": {"type": "string", "fields": {"raw": {"type": "string", "index": "not_analyzed"}}}}}}}'
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

def index_genes():
    print 'indexing genes'
    
    all_genes = nex_session.query(Bioentity).all()
    genes_go_slim = load_go_slim('../go_slim_mapping.tab')

    for gene in all_genes:
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
                print "GO CATEGORY UNKNOWN! Check this out:"
                import pdb; pdb.set_trace()
                
        perf_result = perf_session.query(PerfBioentity).filter_by(id=gene.id).first()
        perf_json = perf_result.to_json()

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
            'cellular_component': list(cellular_component),
            'biological_process': list(biological_process),
            'molecular_function': list(molecular_function),

            'bioentity_id': gene.id,

            'keys': list(keys)
        }
        
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=gene.sgdid)

def index_phenotypes():
    print 'indexing phenotypes'
    all_phenotypes = nex_session.query(Phenotype).all()
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
            references.add(annotation['reference']['display_name'])
            for prop in annotation['properties']:
                if prop['class_type'] == 'CHEMICAL':
                    chemical.add(prop['bioitem']['display_name'])
            mutant_type.add(annotation['mutant_type'])

        key_values = [phenotype.display_name, phenotype.format_name, phenotype.sgdid]
        
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
            'phenotype_loci': list(loci),
            'number_annotations': len(perf_json),
            'chemical': list(chemical),
            'mutant_type': list(mutant_type),
            
            'category': 'phenotype',

            'keys': list(keys)
        }

        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=phenotype.sgdid)

def index_contigs():
    print 'indexing contigs'

    all_contigs = nex_session.query(Contig).all()
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

            'keys': list(keys)
        }

        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=contig.id)
        
def index_authors():
    print 'indexing authors'

    all_authors = nex_session.query(Author).all()
    for author in all_authors:
        obj = {
            'name': author.display_name,
            'href': author.link,
            'description': '',
            'category': 'author'
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=author.id)

def index_strains():
    print 'indexing strains'
    all_strains = nex_session.query(Strain).all()
    print(len(all_strains))
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
    print 'indexing GO terms'
    all_gos = nex_session.query(Go).all()
    for go in all_gos:
        loci = set()
        number_annotations = 0
        if go.locus_count > 0:
            perf_result = perf_session.query(PerfBioconceptDetails).filter_by(obj_id=go.id).filter_by(class_type="GO_LOCUS").first()
            perf_json = json.loads(perf_result.json)

            number_annotations = len(perf_json)
            
            for annotation in perf_json:
                loci.add(annotation['locus']['display_name'])

        if number_annotations == 0:
            continue
        
        key_values = [go.display_name, go.format_name, go.go_id]
        
        keys = set([])
        for k in key_values:
            if k is not None:
                keys.add(k.lower())
            
        obj = {
            'name': go.display_name,
            'href': go.link,
            'description': go.description,

            'go_id': go.go_id,
            'go_loci': list(loci),
            'number_annotations': number_annotations,
            
            'category': go.go_aspect.replace(' ', '_'),

            'keys': list(keys)
        }

        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=go.go_id)
        
def index_references():
    print 'indexing references'
    all_references = nex_session.query(Reference).all()
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
            'reference_loci': list(loci),
            
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
    print "indexing downloads from xls file: " + filename
    downloads = xls_to_dict(filename)
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
    print "indexing downloads form json file: " + filename

    with open(filename, 'r') as content_file:
        content = content_file.read()
    downloads = json.loads(content)

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
    print "indexing toolbar links"
    links = [("Gene List", "http://yeastmine.yeastgenome.org/yeastmine/bag.do", None, 'resource', None),
             ("Yeastmine", "http://yeastmine.yeastgenome.org", None, 'resource', None),
             ("Submit Data", "/cgi-bin/submitData.pl", None, 'resource', None),
             ("SPELL", "http://spell.yeastgenome.org", None, 'resource', None),
             ("BLAST", "/blast-sgd", None, 'resource', None),
             ("Fungal BLAST", "/blast-fungal", None, 'resource', None),
             ("Go Term Finder", "/cgi-bin/GO/goTermFinder.pl", None, 'resource', None),
             ("Go Slim Mapper", "/cgi-bin/GO/goSlimMapper.pl", None, 'resource', None),
             ("Pattern Matching", "/cgi-bin/PATMATCH/nph-patmatch", None, 'resource', None),
             ("Design Primers", "/cgi-bin/web-primer", None, 'resource', None),
             ("Restriction Mapper", "/cgi-bin/PATMATCH/RestrictionMapper", None, 'resource', None),
             ("Download", "/download-data/sequence", None, 'resource', None),
             ("Genome Browser", "/browse", None, 'resource', None),
             ("Gene/Sequence Resources", "/cgi-bin/seqTools", None, 'resource', None),
             ("Download Genome", "http://downloads.yeastgenome.org/sequence/S288C_reference/genome_releases/", None, 'resource', None),
             ("Genome Snapshot", "/genomesnapshot", None, 'resource', None),
             ("Chromosome History", "/cgi-bin/chromosomeHistory.pl", None, 'resource', None),
             ("Systematic Sequencing Table", "/cache/chromosomes.shtml", None, 'resource', None),
             ("Original Sequence Papers", "http://wiki.yeastgenome.org/index.php/Original_Sequence_Papers", None, 'resource', None),
             ("Variant Viewer", "/variant-viewer", None, 'resource', None),
             ("Align Strain Sequences", "/cgi-bin/FUNGI/alignment.pl", None, 'resource', None),
             ("Synteny Viewer", "/cgi-bin/FUNGI/FungiMap", None, 'resource', None),
             ("Fungal Alignment", "/cgi-bin/FUNGI/showAlign", None, 'resource', None),
             ("PDB Search", "/cgi-bin/protein/get3d", None, 'resource', None),
             ("UniProtKB", "http://www.uniprot.org/", None, 'resource', None),
             ("InterPro (EBI)", "http://www.ebi.ac.uk/interpro/", None, 'resource', None),
             ("HomoloGene (NCBI)", "http://www.ncbi.nlm.nih.gov/homologene", None, 'resource', None),
             ("YGOB (Trinity College)", "http://wolfe.gen.tcd.ie/ygob/", None, 'resource', None),
             ("GO Term Finder", "/cgi-bin/GO/goTermFinder.pl", None, 'resource', None),
             ("GO Slim Mapper", "/cgi-bin/GO/goSlimMapper.pl", None, 'resource', None),
             ("GO Slim Mapping File", "http://downloads.yeastgenome.org/curation/literature/go_slim_mapping.tab", None, 'resource', None),
             ("Expression", "http://spell.yeastgenome.org/", None, 'resource', None),
             ("Biochemical Pathways", "http://pathway.yeastgenome.org/", None, 'resource', None),
             ("Browse All Phenotypes", "/ontology/phenotype/ypo/overview", None, 'resource', None),
             ("Interactions", "/interaction_search", None, 'resource', None),
             ("YeastGFP", "http://yeastgfp.yeastgenome.org/", None, 'resource', None),
             ("GO Consortium", "http://www.geneontology.org/", None, 'resource', None),
             ("BioGRID (U. Toronto)", "http://thebiogrid.org/", None, 'resource', None),
             ("Full-text Search", "http://textpresso.yeastgenome.org/", None, 'resource', None),
             ("New Yeast Papers", "/reference/recent", None, 'resource', None),
             ("YeastBook", "http://www.genetics.org/site/misc/yeastbook.xhtml", None, 'resource', None),
             ("Genome-wide Analysis Papers", "/cache/genome-wide-analysis.html", None, 'resource', None),
             ("PubMed (NCBI)", "http://www.ncbi.nlm.nih.gov/pubmed/", None, 'resource', None),
             ("PubMed Central (NCBI)", "http://www.ncbi.nlm.nih.gov/pmc/", None, 'resource', None),
             ("Google Scholar", "http://scholar.google.com/", None, 'resource', None),
             ("Find a Colleague", "/cgi-bin/colleague/colleagueInfoSearch", None, 'resource', None),
             ("Add or Update Info", "/cgi-bin/colleague/colleagueSearch", None, 'resource', None),
             ("Find a Yeast Lab", "/cache/yeastLabs.html", None, 'resource', None),
             ("Career Resources", "http://wiki.yeastgenome.org/index.php/Career_Resources", None, 'resource', None),
             ("Future", "http://wiki.yeastgenome.org/index.php/Meetings#Upcoming_Conferences_.26_Courses", None, 'resource', None),
             ("Yeast Genetics", "http://wiki.yeastgenome.org/index.php/Meetings#Past_Yeast_Meetings", None, 'resource', None),
             ("Submit a Gene Registration", "/cgi-bin/registry/geneRegistry", None, 'resource', None),
             ("Gene Registry", "/help/community/gene-registry", None, 'resource', None),
             ("Nomenclature Conventions", "/help/community/nomenclature-conventions", None, 'resource', None),
             ("Global Gene Hunter", "/cgi-bin/geneHunter", None, 'resource', None),
             ("Strains and Constructs", "http://wiki.yeastgenome.org/index.php/Strains", None, 'resource', None),
             ("Reagents", "http://wiki.yeastgenome.org/index.php/Reagents", None, 'resource', None),
             ("Protocols and Methods", "http://wiki.yeastgenome.org/index.php/Methods", None, 'resource', None),
             ("Physical & Genetic Maps", "http://wiki.yeastgenome.org/index.php/Combined_Physical_and_Genetic_Maps_of_S._cerevisiae", None, 'resource', None),
             ("Genetic Maps", "http://wiki.yeastgenome.org/index.php/Yeast_Mortimer_Maps_-_Edition_12", None, 'resource', None),
             ("Sequence", "http://wiki.yeastgenome.org/index.php/Historical_Systematic_Sequence_Information", None, 'resource', None),
             ("Gene Summary Paragraphs", "/cache/geneSummarytable.html", None, 'resource', None),
             ("Wiki", "http://wiki.yeastgenome.org/index.php/Main_Page", None, 'resource', None),
             ("Resources", "http://wiki.yeastgenome.org/index.php/External_Links", None, 'resource', None)]
    for l in links:
        obj = {
            'name': l[0],
            'href': l[1],
            'description': l[2],
            'category': l[3],
            'data': l[4],
            'keys': []
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=l[1])
    
def main():
#    setup_index()
    
#    index_toolbar_links()
#    index_strains()
#    index_phenotypes()

    index_genes()

#    index_contigs()
    index_go_terms()

#    index_references()

#### - NOPE    index_downloads_from_xls('./src/sgd/elastic_search/geo_datasets_highlighted.xls')
#    index_downloads_from_json('./downloadable_files.json')
##### - NOPE    index_authors()
    
    # experiments
    # pages

main()
