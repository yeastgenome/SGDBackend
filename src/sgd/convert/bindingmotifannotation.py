from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

source = 'YeTFaSCo'
TAXON_ID = "TAX:4932"

def bindingmotifannotation_starter(bud_session_maker):

    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.reference import Reference

    nex_session = get_nex_session()

    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)
    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return
    name_to_dbentity_id = dict([(x.systematic_name, x.id) for x in nex_session.query(Locus).all()])
    pmid_to_reference_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])

    ## downloaded from http://yetfasco.ccbr.utoronto.ca/downloads.php
    file_name = "src/sgd/convert/data/yetfasco_data.txt"
    f = open(file_name, 'rU')
    
    for line in f:
        row = line.split(';')
        quality = row[8][1:-1]
        if quality != 'High':
            continue        
        name = row[2][1:-1].upper()
        dbentity_id = name_to_dbentity_id.get(name)
        if dbentity_id is None:
            print "The name: ", name, " is not in the LOCUSDBENTITY table."
            continue
        reference_id = None
        if row[10] != '':
            pmid = int(row[10][1:-1])
            reference_id = pmid_to_reference_id.get(pmid)
        motif_id = row[3][1:-1]
        link = 'http://yetfasco.ccbr.utoronto.ca/MotViewLong.php?PME_sys_qf2=' + motif_id
        sub_id = row[4][1:-1]
        logo_url = '/static/img/yetfasco/' + name + '_' + motif_id + '.' + sub_id + '.png'

        data = { 'dbentity_id': dbentity_id,
                'source': { "display_name": source },
                'taxonomy_id': taxonomy_id,
                'link': link,
                'motif_id': int(motif_id),
                'logo_url': logo_url }

        if reference_id is not None:
            data['reference_id'] = reference_id

        yield data

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()
   
if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, bindingmotifannotation_starter, 'bindingmotifannotation', lambda x: (x['dbentity_id'], x['taxonomy_id'], x['motif_id']))
