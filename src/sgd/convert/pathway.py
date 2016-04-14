from src.sgd.convert import basic_convert, remove_nones
from src.sgd.convert.util import get_strain_taxid_mapping, link_gene_names

__author__ = 'sweng66'

SRC = 'SGD'

def pathway_starter(bud_session_maker):
 
    from src.sgd.model.bud.general import Dbxref
    from src.sgd.model.nex.reference import Reference

    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    pmid_to_reference_id =  dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    
    pathwayID2record = get_record()

    for x in bud_session.query(Dbxref).filter_by(dbxref_type='Pathway ID').all():
        
        display_name = x.dbxref_name
        format_name = display_name.replace(" ", "_")
        link = '/pathway/' + format_name + '/overview'
    
        record = pathwayID2record.get(x.dbxref_id)

        alias_list = None
        summary_text = None
        pmid_list = None
        created_by = None
        if record is not None:
            alias_list = record.get('aliases')
            summary_text = record.get('summary_text')
            pmid_list = record.get('pmids')
            created_by = record.get('created_by')
        aliases = load_aliases(alias_list, created_by)
        summaries = load_summaries(summary_text, pmid_list, pmid_to_reference_id, 
                                   created_by, nex_session)

        urls = load_urls(x.dbxref_id, created_by)

        data = { "source": { 'display_name': SRC },
                 "display_name": display_name,
                 "format_name": format_name,
                 "link": link,
                 "subclass": 'PATHWAY',
                 "dbentity_status": 'Active',
                 "biocyc_id": x.dbxref_id,
                 "bud_id": x.id,
                 "urls": urls,
                 "aliases": aliases,
                 "summaries": summaries }

        if created_by is not None:
            data['created_by'] = created_by.upper()
        
        yield data


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

def load_urls(biocyc_id, created_by):

    urls = []

    url1 = {'display_name': 'BioCyc',
            'link': 'http://www.biocyc.org/YEAST/NEW-IMAGE?type=PATHWAY&object=' + biocyc_id,
            'source': {'display_name': 'BioCyc'},
            'url_type': 'BioCyc'}
    url2 = {'display_name': 'YeastPathways',
            'link': 'http://pathway.yeastgenome.org/YEAST/new-image?type=PATHWAY&object=' + biocyc_id + '&detail-level=2',
            'source': {'display_name': 'SGD'},
            'url_type': 'YeastPathways'}

    if created_by is not None:
        url1['created_by'] = created_by.upper()
        url2['created_by'] = created_by.upper()

    urls.append(url1)
    urls.append(url2)

    return urls


def get_record():

    id2record = {} 
    f = open('src/sgd/convert/data/pathwaySummaries021916.txt', 'r')
    for line in f:   
        entry = {}
        pieces = line.strip().split("\t") 
        if len(pieces) < 2:                                                        
            continue        
        if pieces[1] != '':
            entry['aliases'] = pieces[1]
        if len(pieces) > 2:
            entry['summary_text'] = pieces[2]
        if len(pieces) > 3:
            if pieces[3] in ['cindy', 'eurie']:
                entry['created_by'] = pieces[3]
            elif pieces[3].endswith(' cindy'):
                entry['created_by'] = 'cindy'
                entry['pmids'] = pieces[3].replace(' cindy', '')
            elif pieces[3]:
                entry['pmids'] = pieces[3]
        if len(pieces) > 4:
            entry['created_by'] = pieces[4]
        id2record[pieces[0]] = entry

    f.close()
    return id2record
    
def load_aliases(aliasList, created_by): 
    if aliasList is None:
        return []
    aliases = []
    for alias in aliasList.split('|'):
        alias = { 'source': {'display_name': 'SGD'}, 
                  'alias_type': 'Synonym',
                  'display_name': alias }
        if created_by is not None:
            alias['created_by'] = created_by.upper()
        aliases.append(alias)
    
    return aliases


def load_summaries(text, pmidList, pmid_to_reference_id, created_by, nex_session):

    if text is None:
        return []

    refs = []
    if pmidList:
        pmids = pmidList.strip(' ').strip('|').split("|")
        refs = []
        i = 0
        for pmid in pmids:
            if pmid == '':
                continue
            reference_id = pmid_to_reference_id.get(int(pmid))
            if reference_id is None:
                print "The pmid=", pmid, " for summary is not in the database."
                continue
            i = i + 1
            refs.append({'reference_id': reference_id,
                         'reference_order': i})

    summary = { 'source': {'display_name': 'SGD'},
                'summary_type': 'Metabolic',
                'text': remove_html_tags(text),
                'html': link_gene_names(text, {}, nex_session),
                'references': refs }

    if created_by is not None:
        summary['created_by'] = created_by.upper()

    return [summary]

def remove_html_tags(text):
    return text.replace("<p>", "").replace("</p>", "").replace("<i>", "").replace("</i>", "").replace("<sub>", "").replace("</sub>", "")
    

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, pathway_starter, 'pathway', lambda x: x['display_name'])


