from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

SRC = 'SGD'

def strain_summary_reference_starter(bud_session_maker):
 
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.strain import Strain, StrainSummary

    f = open('src/sgd/convert/data/strain_paragraph.tab', 'r')

    nex_session = get_nex_session()
    pmid_to_reference_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    display_name_to_strain_id =  dict([(x.display_name, x.id) for x in nex_session.query(Strain).all()])
    strain_id_to_summary_id =  dict([(x.strain_id, x.id) for x in nex_session.query(StrainSummary).all()])

    data = {}
    
    for line in f:
        if line.startswith('S.STRAIN_ID'):
            continue
        line = line.strip()
        pieces = line.split("\t")
        display_name = pieces[1]

        strain_id = display_name_to_strain_id.get(display_name)
        if strain_id is None:
            print "The strain: ", display_name, " is not in the STRAINDBENTITY table."
            continue

        summary_id = strain_id_to_summary_id.get(strain_id)
        if summary_id is None:
            print "The strain: ", display_name, " doesn't have summary."
            continue
        
        if summary_id in data:
            pmids = data[summary_id]
        else:
            pmids = []
        pmids.append(int(pieces[10]))
        data[summary_id] = pmids
        
    for summary_id in data:
        pmids = sorted(data[summary_id], key=int, reverse=True)
        ref_index = 0
        for pmid in pmids:
            reference_id = pmid_to_reference_id.get(pmid)
            if reference_id is None:
                print "The pmid: ", pmid, " is not in REFERENCEDBENTITY table."
                continue
            ref_index = ref_index + 1
            yield { 'reference_id': reference_id,
                    'reference_order': ref_index,
                    'source': {'display_name': SRC },
                    'summary_id': summary_id } 
        
            # print summary_id, reference_id, ref_index

    f.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, strain_summary_reference_starter, 'strain_summary_reference', lambda x: (x['summary_id'], x['reference_id'], x['reference_order']))
 


