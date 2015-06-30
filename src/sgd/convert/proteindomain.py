from src.sgd.convert.into_curate import basic_convert, remove_nones
from sqlalchemy.sql.expression import or_

__author__ = 'kpaskov'

def load_urls(obj_json):
    urls = []
    source = obj_json['source']['display_name']
    display_name = obj_json['display_name']

    if source == 'JASPAR':
        link = 'http://jaspar.binf.ku.dk/cgi-bin/jaspar_db.pl?rm=present&collection=CORE&ID=' + display_name
    elif source == 'SMART':
        link = "http://smart.embl-heidelberg.de/smart/do_annotation.pl?DOMAIN=" + display_name
    elif source == 'Pfam':
        link = "http://pfam.sanger.ac.uk/family?type=Family&entry=" + display_name
    elif source == 'Gene3D':
        link = "http://www.cathdb.info/version/latest/superfamily/" + display_name[6:]
    elif source == 'SUPERFAMILY':
        link = "http://supfam.org/SUPERFAMILY/cgi-bin/scop.cgi?ipid=" + display_name
    elif source == 'SignalP':
        link = None
    elif source == 'PANTHER':
        link = "http://www.pantherdb.org/panther/family.do?clsAccession=" + display_name
    elif source == 'TIGRFAM':
        link = "http://www.jcvi.org/cgi-bin/tigrfams/HmmReportPage.cgi?acc=" + display_name
    elif source == 'PRINTS':
        link = "http:////www.bioinf.man.ac.uk/cgi-bin/dbbrowser/sprint/searchprintss.cgi?display_opts=Prints&amp;category=None&amp;queryform=false&amp;prints_accn=" + display_name
    elif source == 'ProDom':
        link = "http://prodom.prabi.fr/prodom/current/cgi-bin/request.pl?question=DBEN&amp;query=" + display_name
    elif source == 'PIRSF':
        link = "http://pir.georgetown.edu/cgi-bin/ipcSF?id=" + display_name
    elif source == 'PROSITE':
        link = "http://prodom.prabi.fr/prodom/cgi-bin/prosite-search-ac?" + display_name
    elif source == 'PROSITE':
        link = "http://prodom.prabi.fr/prodom/cgi-bin/prosite-search-ac?" + display_name
    elif source == 'Phobius':
        link = None
    elif source == '-':
        link = None

    if link is not None:
        urls.append({'display_name': display_name,
                     'link': link,
                     'source': {'display_name': 'SGD'},
                     'url_type': 'External'})

    if 'interpro_id' in obj_json:
        urls.append({'display_name': obj_json['interpro_id'],
                     'link': 'http://www.ebi.ac.uk/interpro/entry/' + obj_json['interpro_id'],
                     'source': {'display_name': 'InterPro'},
                     'url_type': 'Interpro'})
    return urls

def proteindomain_starter(bud_session_maker):
    from src.sgd.model.bud.general import Dbxref

    bud_session = bud_session_maker()

    panther_id_to_description = {}
    f = open('src/sgd/convert/data/PANTHER9.0_HMM_classifications.txt', 'r')
    for line in f:
        row = line.split('\t')
        panther_id_to_description[row[0]] = row[1].lower()
    f.close()

    f = open('src/sgd/convert/data/domains.tab', 'r')
    for line in f:
        row = line.split('\t')
        source = row[3].strip()
        if source == 'Coils':
            source = '-'

        display_name = row[4].strip()
        descriptions = [row[5].strip()]
        interpro_id = None
        if len(row) >= 13:
            interpro_id = row[11].strip()
            descriptions.append(row[12].strip())

        if source == 'PANTHER' and display_name in panther_id_to_description:
            descriptions.append(panther_id_to_description[display_name])

        description = ';'.join([x for x in descriptions if x != '' and x is not None])
        if interpro_id == '':
            interpro_id = None

        obj_json = remove_nones({'display_name': display_name,
               'source': {'display_name': source},
               'description': description,
               'interpro_id': interpro_id
        })
        obj_json['urls'] = load_urls(obj_json)
        yield obj_json
    f.close()

    f = open('src/sgd/convert/data/TF_family_class_accession04302013.txt', 'r')
    for line in f:
        row = line.split('\t')
        description = 'Class: ' + row[4] + ', Family: ' + row[3]
        obj_json = {'display_name': row[0],
               'source': {'display_name': 'JASPAR'},
               'description': description}
        obj_json['urls'] = load_urls(obj_json)
        yield obj_json

    yield {'display_name': 'predicted signal peptide',
           'source': {'display_name': 'SignalP'},
           'description': 'predicted signal peptide'}
    yield {'display_name': 'predicted transmembrane domain',
           'source': {'display_name': 'TMHMM'},
           'description': 'predicted transmembrane domain'}

    for bud_obj in bud_session.query(Dbxref).filter(or_(Dbxref.dbxref_type == 'PANTHER', Dbxref.dbxref_type == 'Prosite')).all():
        display_name = bud_obj.dbxref_id
        dbxref_type = bud_obj.dbxref_type
        source = bud_obj.source

        description = bud_obj.dbxref_name
        if source == 'PANTHER' and display_name in panther_id_to_description:
            description += ('; ' + panther_id_to_description[description])

        obj_json = remove_nones({'display_name': bud_obj.dbxref_id,
                                 'source': {'display_name': source},
                                 'description': description})
        obj_json['urls'] = load_urls(obj_json)
        yield obj_json

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, proteindomain_starter, 'proteindomain', lambda x: x['display_name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')
