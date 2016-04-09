from src.sgd.convert import basic_convert, remove_nones
from src.sgd.convert.util import get_strain_taxid_mapping

__author__ = 'sweng66'

SRC = 'SGD'

def pathway_summary_reference_starter(bud_session_maker):
 
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.pathway import Pathway, PathwaySummary

    nex_session = get_nex_session()

    pathwayId_to_pathway = dict([(x.biocyc_id, x) for x in nex_session.query(Pathway).all()])
    pathway_id_to_summary_id = dict([(x.pathway_id, x.id) for x in nex_session.query(PathwaySummary).all()])

    pmid_to_reference_id =  dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    
    f = open('src/sgd/convert/data/pathwaySummaries021916.txt', 'r')
    for line in f:
        entry = {}
        pieces = line.strip().split("\t")
        if len(pieces) < 4:
            continue
        pathway = pathwayId_to_pathway.get(pieces[0])
        if pathway is None:
            print "PATHWAY ID:", pieces[0], " is not in the database."
            continue
        pathway_id = pathway.id
        created_by = pathway.created_by
        summary_id = pathway_id_to_summary_id.get(pathway_id)
        if summary_id is None:
            continue
        pmids = pieces[3].replace(' cindy', '').strip(' ').strip('|').split('|')
        if len(pmids) == 0:
            continue
        i = 0
        found_ref = []
        for pmid in pmids:
            if "cindy" in pmid or "eurie" in pmid or pmid == '':
                continue
            reference_id = pmid_to_reference_id.get(int(pmid))
            if reference_id is None:
                print "The PMID: ", pmid, " is not in the REFERENCEDBENTITY table."
                continue
            if reference_id in found_ref:
                continue
            found_ref.append(reference_id)

            i = i + 1
            yield { "summary_id": summary_id,
                    "reference_id": reference_id,
                    "reference_order": i,
                    "source": { "display_name": 'SGD' },
                    "created_by": created_by }
        
def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, pathway_summary_reference_starter, 'pathway_summary_reference', lambda x: (x['summary_id'], x.get('reference_id'), x['reference_order']))



