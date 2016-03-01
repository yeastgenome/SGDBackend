from sqlalchemy import *
from src.sgd.convert import prepare_schema_connection
from src.sgd.convert import config
from src.sgd.model import nex
from src.sgd.model import perf
from elasticsearch import Elasticsearch
import xlrd
import json

#CLIENT_ADDRESS = 'http://localhost:9200'
CLIENT_ADDRESS = 'http://54.200.43.123:9200/'
INDEX_NAME = 'searchable_items'
DOC_TYPE = 'searchable_item'
RESET_INDEX = False
es = Elasticsearch(CLIENT_ADDRESS, retry_on_timeout=True)

# prep session
nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
perf_session_maker = prepare_schema_connection(perf, config.PERF_DBTYPE, config.PERF_HOST, config.PERF_DBNAME, config.PERF_SCHEMA, config.PERF_DBUSER, config.PERF_DBPASS)
from src.sgd.model.nex.bioentity import Bioentity, Locus
from src.sgd.model.perf.core import Bioentity as PerfBioentity
from src.sgd.model.nex.reference import Author
from src.sgd.model.nex.misc import Strain
from src.sgd.model.nex.bioconcept import Go
from src.sgd.model.nex.bioconcept import Phenotype
from src.sgd.model.nex.reference import Reference
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
    mapping = '{"settings": {"index": {"analysis": {"analyzer": {"autocomplete": {"type": "custom", "filter": ["lowercase", "autocomplete_filter"], "tokenizer": "standard"}, "raw": {"type": "custom", "filter": ["lowercase"], "tokenizer": "keyword"}}, "filter": {"autocomplete_filter": {"min_gram": "1", "type": "edge_ngram", "max_gram": "20"}}}, "number_of_replicas": "1", "number_of_shards": "5"}}, "mappings": {"searchable_item": {"properties": {"biological_process": {"type": "string", "index": "not_analyzed"},"category": {"type": "string"},"cellular_component": {"type": "string", "index": "not_analyzed"},"description": {"type": "string"},"feature_type": {"type": "string", "index": "not_analyzed"},"href": {"type": "string"},"molecular_function": {"type": "string", "index": "not_analyzed"},"name": {"type": "string","analyzer": "autocomplete","fields": {"raw": {"type": "string","analyzer": "raw"}}},"phenotypes": {"type": "string","index": "not_analyzed"}}}}}'
    return mapping

def index_genes():
    print 'indexing genes'
    
    all_genes = nex_session.query(Bioentity).all()

    for gene in all_genes:
        if gene.display_name == gene.format_name:
            _name = gene.display_name
        else:
            _name = gene.display_name + ' / ' + gene.format_name

        perf_result = perf_session.query(PerfBioentity).filter_by(id=gene.id).first()
        perf_json = perf_result.to_json()

        phenotypes = set()
        for k in ['large_scale_phenotypes', 'classical_phenotypes']:
            for kk in perf_json['phenotype_overview'][k].keys():
                for phenotype in perf_json['phenotype_overview'][k][kk]:
                    phenotypes.add(phenotype['display_name'])
                    
        cellular_component = set()
        for k in ['htp_cellular_component_terms', 'manual_cellular_component_terms']:
            for term in perf_json['go_overview'][k]:
                cellular_component.add(term['term']['display_name'])
        
        biological_process = set()
        for k in ['htp_biological_process_terms', 'manual_biological_process_terms']:
            for term in perf_json['go_overview'][k]:
                biological_process.add(term['term']['display_name'])
        
        molecular_function = set()
        for k in ['htp_molecular_function_terms', 'manual_molecular_function_terms']:
            for term in perf_json['go_overview'][k]:
                molecular_function.add(term['term']['display_name'])

        obj = {
            'name': _name,
            'href': gene.link,
            'description': gene.headline,
            'category': 'locus',
            'feature_type': gene.locus_type,
            'phenotypes': list(phenotypes),
            'cellular_component': list(cellular_component),
            'biological_process': list(biological_process),
            'molecular_function': list(molecular_function)
        }

        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=gene.sgdid)

def index_phenotypes():
    print 'indexing phenotypes'
    all_phenotypes = nex_session.query(Phenotype).all()
    for phenotype in all_phenotypes:
        obj = {
            'name': phenotype.display_name,
            'href': phenotype.link,
            'description': phenotype.description,
            'category': 'phenotype'
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=phenotype.sgdid)

def index_authors():
    print 'indexing authors'
    # get nex format of all authors
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
    for strain in all_strains:
        obj = {
            'name': strain.display_name,
            'href': strain.link,
            'description': strain.description,
            'category': 'strain'
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=strain.id)

def index_go_terms():
    print 'indexing GO terms'
    all_gos = nex_session.query(Go).all()
    for go in all_gos:
        obj = {
            'name': go.display_name,
            'href': go.link,
            'description': go.description,
            'category': go.go_aspect.replace(' ', '_')
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=go.sgdid)

def index_references():
    print 'indexing references'
    all_references = nex_session.query(Reference).all()
    for reference in all_references:
        obj = {
            'name': reference.citation,
            'href': reference.link,
            'description': reference.abstract,
            'category': 'reference'
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

def index_toolbar_links():
    print "indexing toolbar links"
    links = [("Gene List", "http://yeastmine.yeastgenome.org/yeastmine/bag.do", None, 'resource', None),
             ("BLAST", "http://yeastgenome.org/blast-sgd", None, 'resource', None),
             ("Fungal BLAST", "http://yeastgenome.org/blast-fungal", None, 'resource', None),
             ("Go Term Finder", "http://www.yeastgenome.org/cgi-bin/GO/goTermFinder.pl", None, 'resource', None),
             ("Go Slim Mapper", "http://www.yeastgenome.org/cgi-bin/GO/goSlimMapper.pl", None, 'resource', None),
             ("Pattern Matching", "http://www.yeastgenome.org/cgi-bin/PATMATCH/nph-patmatch", None, 'resource', None),
             ("Design Primers", "http://www.yeastgenome.org/cgi-bin/web-primer", None, 'resource', None),
             ("Restriction Mapper", "http://www.yeastgenome.org/cgi-bin/PATMATCH/RestrictionMapper", None, 'resource', None),
             ("Download", "http://www.yeastgenome.org/download-data/sequence", None, 'resource', None),
             ("Genome Browser", "http://browse.yeastgenome.org/fgb2/gbrowse/scgenome/", None, 'resource', None),
             ("Gene/Sequence Resources", "http://www.yeastgenome.org/cgi-bin/seqTools", None, 'resource', None),
             ("Download Genome", "http://downloads.yeastgenome.org/sequence/S288C_reference/genome_releases/", None, 'resource', None),
             ("Genome Snapshot", "http://www.yeastgenome.org/genomesnapshot", None, 'resource', None),
             ("Chromosome History", "http://www.yeastgenome.org/cgi-bin/chromosomeHistory.pl", None, 'resource', None),
             ("Systematic Sequencing Table", "http://www.yeastgenome.org/cache/chromosomes.shtml", None, 'resource', None),
             ("Original Sequence Papers", "http://wiki.yeastgenome.org/index.php/Original_Sequence_Papers", None, 'resource', None),
             ("Variant Viewer", "http://www.yeastgenome.org/variant-viewer", None, 'resource', None),
             ("Align Strain Sequences", "http://www.yeastgenome.org/cgi-bin/FUNGI/alignment.pl", None, 'resource', None),
             ("Synteny Viewer", "http://www.yeastgenome.org/cgi-bin/FUNGI/FungiMap", None, 'resource', None),
             ("Fungal Alignment", "http://www.yeastgenome.org/cgi-bin/FUNGI/showAlign", None, 'resource', None),
             ("PDB Search", "http://www.yeastgenome.org/cgi-bin/protein/get3d", None, 'resource', None),
             ("UniProtKB", "http://www.uniprot.org/", None, 'resource', None),
             ("InterPro (EBI)", "http://www.ebi.ac.uk/interpro/", None, 'resource', None),
             ("HomoloGene (NCBI)", "http://www.ncbi.nlm.nih.gov/homologene", None, 'resource', None),
             ("YGOB (Trinity College)", "http://wolfe.gen.tcd.ie/ygob/", None, 'resource', None),
             ("GO Term Finder", "http://www.yeastgenome.org/cgi-bin/GO/goTermFinder.pl", None, 'resource', None),
             ("GO Slim Mapper", "http://www.yeastgenome.org/cgi-bin/GO/goSlimMapper.pl", None, 'resource', None),
             ("GO Slim Mapping File", "http://downloads.yeastgenome.org/curation/literature/go_slim_mapping.tab", None, 'resource', None),
             ("Expression", "http://spell.yeastgenome.org/", None, 'resource', None),
             ("Biochemical Pathways", "http://pathway.yeastgenome.org/", None, 'resource', None),
             ("Browse All Phenotypes", "http://yeastgenome.org/ontology/phenotype/ypo/overview", None, 'resource', None),
             ("Interactions", "http://www.yeastgenome.org/cgi-bin/interaction_search", None, 'resource', None),
             ("YeastGFP", "http://yeastgfp.yeastgenome.org/", None, 'resource', None),
             ("GO Consortium", "http://www.geneontology.org/", None, 'resource', None),
             ("BioGRID (U. Toronto)", "http://thebiogrid.org/", None, 'resource', None),
             ("Full-text Search", "http://textpresso.yeastgenome.org/", None, 'resource', None),
             ("New Yeast Papers", "http://www.yeastgenome.org/reference/recent", None, 'resource', None),
             ("YeastBook", "http://www.genetics.org/site/misc/yeastbook.xhtml", None, 'resource', None),
             ("Genome-wide Analysis Papers", "http://www.yeastgenome.org/cache/genome-wide-analysis.html", None, 'resource', None),
             ("PubMed (NCBI)", "http://www.ncbi.nlm.nih.gov/pubmed/", None, 'resource', None),
             ("PubMed Central (NCBI)", "http://www.ncbi.nlm.nih.gov/pmc/", None, 'resource', None),
             ("Google Scholar", "http://scholar.google.com/", None, 'resource', None),
             ("Find a Colleague", "http://www.yeastgenome.org/cgi-bin/colleague/colleagueInfoSearch", None, 'resource', None),
             ("Add or Update Info", "http://www.yeastgenome.org/cgi-bin/colleague/colleagueSearch", None, 'resource', None),
             ("Find a Yeast Lab", "http://www.yeastgenome.org/cache/yeastLabs.html", None, 'resource', None),
             ("Career Resources", "http://wiki.yeastgenome.org/index.php/Career_Resources", None, 'resource', None),
             ("Future", "http://wiki.yeastgenome.org/index.php/Meetings#Upcoming_Conferences_.26_Courses", None, 'resource', None),
             ("Yeast Genetics", "http://wiki.yeastgenome.org/index.php/Meetings#Past_Yeast_Meetings", None, 'resource', None),
             ("Submit a Gene Registration", "http://www.yeastgenome.org/cgi-bin/registry/geneRegistry", None, 'resource', None),
             ("Gene Registry", "http://www.yeastgenome.org/help/community/gene-registry", None, 'resource', None),
             ("Nomenclature Conventions", "http://www.yeastgenome.org/help/community/nomenclature-conventions", None, 'resource', None),
             ("Global Gene Hunter", "http://www.yeastgenome.org/cgi-bin/geneHunter", None, 'resource', None),
             ("Strains and Constructs", "http://wiki.yeastgenome.org/index.php/Strains", None, 'resource', None),
             ("Reagents", "http://wiki.yeastgenome.org/index.php/Reagents", None, 'resource', None),
             ("Protocols and Methods", "http://wiki.yeastgenome.org/index.php/Methods", None, 'resource', None),
             ("Physical & Genetic Maps", "http://wiki.yeastgenome.org/index.php/Combined_Physical_and_Genetic_Maps_of_S._cerevisiae", None, 'resource', None),
             ("Genetic Maps", "http://wiki.yeastgenome.org/index.php/Yeast_Mortimer_Maps_-_Edition_12", None, 'resource', None),
             ("Sequence", "http://wiki.yeastgenome.org/index.php/Historical_Systematic_Sequence_Information", None, 'resource', None),
             ("Gene Summary Paragraphs", "http://www.yeastgenome.org/cache/geneSummarytable.html", None, 'resource', None),
             ("Wiki", "http://wiki.yeastgenome.org/index.php/Main_Page", None, 'resource', None),
             ("Resources", "http://wiki.yeastgenome.org/index.php/External_Links", None, 'resource', None)]
    for l in links:
        obj = {
            'name': l[0],
            'href': l[1],
            'description': l[2],
            'category': l[3],
            'data': l[4]
        }
        es.index(index=INDEX_NAME, doc_type=DOC_TYPE, body=obj, id=l[1])
    
def main():
#    setup_index()
#    index_genes()
#    index_phenotypes()
    index_authors()
    index_strains()
    index_go_terms()
    index_references()

    index_downloads_from_xls('./src/sgd/elastic_search/geo_datasets_highlighted.xls')

    index_toolbar_links()

    # experiments
    # pages

main()
