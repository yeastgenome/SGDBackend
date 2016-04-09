from src.sgd.convert import basic_convert

__author__ = 'sweng66'

TAXON_ID = "TAX:4932"

def pathwayannotation_starter(bud_session_maker):

    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.pathway import Pathway
    from src.sgd.model.nex.ec import Ec
    
    nex_session = get_nex_session()
    
    ecid_to_ec_id = dict([(x.ecid, x.id) for x in nex_session.query(Ec).all()])
    gene_name_to_locus_id = dict([(x.gene_name, x.id) for x in nex_session.query(Locus).all()])
    pathway_name_to_pathway_id = dict([(x.display_name, x.id) for x in nex_session.query(Pathway).all()])
    pmid_to_reference_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    sgdid_to_reference_id = dict([(x.sgdid, x.id) for x in nex_session.query(Reference).all()])
    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])

    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)

    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return
    
    f = open('src/sgd/convert/data/biochemical_pathways.tab.txt', 'r')

    for line in f:
        line = line.strip()
        pieces = line.split("\t")
        pathway_name = pieces[0]
        if len(pieces) < 3:
            # only has pathway name and enzyme name
            continue
        ec_number = pieces[2]
        if len(pieces) < 4:
            # no gene name
            continue
        gene_name = pieces[3]
        refs = None
        if len(pieces) > 4:
            refs = pieces[4]

        # print pathway_name, ec_number, gene_name, refs
        pathway_id = pathway_name_to_pathway_id.get(pathway_name)
        if pathway_id is None:
            print "The pathway name: ", pathway_name, " is not in the database."
            continue
        dbentity_id = gene_name_to_locus_id.get(gene_name)
        if dbentity_id is None:
            print "The gene name: ", gene_name, " is not in the database."
            continue
        ec_id = ecid_to_ec_id.get("EC:" + ec_number)

        data = { "dbentity_id": dbentity_id,
                 "source": { "display_name": 'SGD' },
                 "taxonomy_id": taxonomy_id,
                 "pathway_id": pathway_id }

        if ec_id is not None:
            data['ec_id'] = ec_id
                 
        if refs:
            ref_list = refs.split('|')
            for ref in ref_list:
                items = ref.split(':')
                reference_id = None
                if items[0] == 'PMID':
                    reference_id = pmid_to_reference_id.get(int(items[1]))
                elif items[0] == 'SGD_REF':
                    reference_id = sgdid_to_reference_id.get(items[1])
                if reference_id is None:
                    print "The REFERENCE: ", ref, " is not in the database."
                else:
                    this_data = data
                    this_data['reference_id'] = reference_id
                    yield this_data
        else:
            yield data

    nex_session.close()


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, pathwayannotation_starter, 'pathwayannotation', lambda x: (x['dbentity_id'], x['pathway_id'], x.get('ec_id'), x.get('reference_id')))


