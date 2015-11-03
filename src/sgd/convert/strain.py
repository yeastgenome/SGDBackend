from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

SRC = 'SGD'
DEFAULT_TAXON_ID = 4932

def strain_starter(bud_session_maker):
 
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.taxonomy import Taxonomy

    f = open('src/sgd/convert/data/strain_paragraph.tab', 'r')

    nex_session = get_nex_session()
    pmid_to_reference_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
        
    summary = {}

    for line in f:
        if line.startswith('S.STRAIN_ID'):
            continue
        line = line.strip()
        pieces = line.split("\t")
        display_name = pieces[1]

        # "date_edited", pieces[6],

        reference_id = pmid_to_reference_id.get(int(pieces[10]))
        if reference_id is None:
            print "The pmid: ", pieces[10], " is not in REFERENCEDBENTITY table."
            continue

        references = [{'reference_id': reference_id,
                       'reference_order': 1,
                       'source': {'display_name': SRC } } ]

        #              'date_created': pieces[7],
        #              'created_by': pieces[8] } ]

        summary[display_name] = { "source": {'display_name': SRC},
                                  "summary_type": 'Strain',
                                  "text": pieces[4],
                                  "html": pieces[5],
                                  "references": references } 

    f.close()

    f = open('src/sgd/convert/data/strain_info.txt', 'r')

    wiki_strains = set()
    sequence_download_strains = set()
    strain_to_source = {}
    strain_to_euroscarf = {}

    for line in f:
        if line.startswith('#') or line == '':
            continue
        line = line.strip()
        pieces = line.split("\t")
        category = pieces.pop(0)
        if category.startswith('wiki'):
            wiki_strains = set(pieces)
        if category.startswith('sequence_download'):
            sequence_download_strains = set(pieces)
        if category.startswith('strain_to_source'):
            strain_to_source[pieces[0]] = (pieces[1], pieces[2])
        if category.startswith('strain_to_euroscarf'):
            strain_to_euroscarf[pieces[0]] = pieces[1]
                                  
    f.close()

    strain_display_name_to_taxid_mapping = get_strain_taxid_mapping()
    
    # i = 10000000

    f = open('src/sgd/convert/data/strainInfoForNex2-093015.txt', 'r')
    for line in f:
        if line.startswith('STRAIN_ID') or line == '':
            continue
        if line.startswith('STRAINS TO DELETE'):
            break
        line = line.strip()
        line = line.replace('(null)', '')
        pieces = line.split("\t")

        if len(pieces) < 17:
            continue
        
        strain_id = pieces[0]
        format_name = pieces[1]
        display_name = pieces[2]
        link = pieces[3]
        # source_id = pieces[4]
        description = pieces[5]
        strain_type = pieces[6] if pieces[6] else 'Other'
        genotype = pieces[7]
        genbank_id = pieces[8]
        assembly_size = int(pieces[9]) if pieces[9] else None
        fold_coverage = float(pieces[10]) if pieces[10] else None
        scaffold_number = int(pieces[11]) if pieces[11] else None
        longest_scaffold = int(pieces[12]) if pieces[12] else None
        scaffold_nfifty = int(pieces[13]) if pieces[13] else None
        feature_count = int(pieces[14]) if pieces[14] else None
        date_created = pieces[15].split(' ')[0]
        created_by = pieces[16]

        taxon_id = strain_display_name_to_taxid_mapping.get(display_name)
        if taxon_id is None:
            taxon_id = DEFAULT_TAXON_ID
                                  
        taxonomy_id = taxid_to_taxonomy_id.get(taxon_id)
        if taxonomy_id is None:
            print "The taxon_id: ", taxon_id, " is not in the Taxonomy table."
            continue

        ## 'description': description,

        obj_json = remove_nones({'display_name': display_name,
                                 'format_name': format_name,
                                 'link': link,
                                 'source': {'display_name': SRC},
                                 'dbentity_status': 'Active',
                                 'strain_type': strain_type,
                                 'genotype': genotype,
                                 'genbank_id': genbank_id,
                                 'taxonomy_id': taxonomy_id,
                                 'date_created': str(date_created),
                                 'created_by': created_by,
                                 'fold_coverage': fold_coverage, 
                                 'scaffold_number': scaffold_number,
                                 'assembly_size': assembly_size,
                                 'longest_scaffold': longest_scaffold,
                                 'scaffold_nfifty': scaffold_nfifty,
                                 'feature_count': feature_count })


        # i = i + 1
        # sgdid = 'S0' + str(i) 
        # obj_json['sgdid'] = sgdid


        obj_json['urls'] = load_urls(display_name, genbank_id,
                                     wiki_strains, sequence_download_strains, 
                                     strain_to_source, strain_to_euroscarf)
        if summary.get(display_name):
            obj_json['summaries'] = [ summary[display_name] ]

        
        yield obj_json

        # print str(obj_json)

    f.close()


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()


def get_strain_taxid_mapping():

    #  need to figure the taxid for "D273-10B",  "JK9-3d", "SEY6210", "Sigma1278b", "X2180-1A"     

    return { "S288C":      559292,
             "CEN.PK":     889517,
             "FL100":      947036,
             "RM11-1a":    285006,
             "SK1":        580239,
             "W303":       580240,
             "Y55":        580230,
             "Sigma1278b": 658763,
             "D273-10B":   DEFAULT_TAXON_ID,
             "JK9-3d":     DEFAULT_TAXON_ID,
             "SEY6210":    DEFAULT_TAXON_ID,
             "X2180-1A":   DEFAULT_TAXON_ID,
             'Other':      DEFAULT_TAXON_ID }


def load_urls(strain, genbank_id, wiki_strains, sequence_download_strains, strain_to_source, strain_to_euroscarf):
    urls = []

    if strain in wiki_strains:
        urls.append({'display_name': 'Wiki',
                     'link': 'http://wiki.yeastgenome.org/index.php/Commonly_used_strains#' + strain,
                     'source': {'display_name': SRC},
                     'url_type': 'Wiki'})

    if strain in sequence_download_strains:
                urls.append({'display_name': 'Download Sequence',
                     'link': 'http://downloads.yeastgenome.org/sequence/strains/' + strain,
                     'source': {'display_name': SRC},
                     'url_type': 'Download'})

    if strain in strain_to_source:
        urls.append({'display_name': strain_to_source[strain][0],
                     'link': strain_to_source[strain][1],
                     'source': {'display_name': SRC},
                     'url_type': 'External id'})

    if strain in strain_to_euroscarf:
        urls.append({'display_name': 'EUROSCARF:' + strain_to_euroscarf[strain],
                     'link': 'http://web.uni-frankfurt.de/fb15/mikro/euroscarf/data/' + strain + '.html',
                     'source': {'display_name': SRC},
                     'url_type': 'External id'})

    if genbank_id:

        urls.append({'display_name': genbank_id,
                     'link': 'http://www.ncbi.nlm.nih.gov/nuccore/' + genbank_id if strain != 'S288C' else 'http://www.ncbi.nlm.nih.gov/assembly/GCF_000146045.2/',
                     'source': {'display_name': SRC},
                     'url_type': 'GenBank'})

    if strain == 'S288C':
        urls.append({'display_name': 'Download Sequence',
                     'link': 'http://www.yeastgenome.org/download-data/sequence',
                     'source': {'display_name': SRC},
                     'url_type': 'Download'})

    urls.append({'display_name': 'PubMed',
                 'link': 'http://www.ncbi.nlm.nih.gov/pubmed/?term=saccharomyces+cerevisiae+' + strain,
                 'source': {'display_name': SRC},
                 'url_type': 'PubMed'})

    return urls


def load_summaries(strain):
    summaries = []
    if strain in strain_paragraphs:
        paragraph = strain_paragraphs[strain]
        summaries.append({
            'source': {'display_name': 'SGD'},
            'summary_type': 'Paragraph',
            'text': paragraph[0],
            'html': paragraph[0],
            'references': [{'pubmed_id': pubmed_id, 'reference_order': i+1} for (i, pubmed_id) in enumerate(paragraph[1])]
            })

    return summaries

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, strain_starter, 'strain', lambda x: x['display_name'])


