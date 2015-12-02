from src.sgd.convert import basic_convert
from src.sgd.convert.util import get_relation_to_ro_id, read_gpi_file, read_gpad_file

__author__ = 'sweng66'

TAXON_ID = "TAX:4932"
GPI_FILE = 'src/sgd/convert/data/gp_information.559292_sgd'
GPAD_FILE = 'src/sgd/convert/data/gp_association.559292_sgd'

def goannotation_starter(bud_session_maker):

    from src.sgd.model.nex.taxonomy import Taxonomy
    
    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)
    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return
        
    ## load the annotations with source = 'SGD' and the annotations with go_evidence = 'IEA' from GPAD file

    [uniprot_to_date_assigned, uniprot_to_sgdid_list] = read_gpi_file(GPI_FILE)

    data = read_gpad_file(GPAD_FILE, bud_session, nex_session, uniprot_to_date_assigned, uniprot_to_sgdid_list)

    for x in data:
        source = x.pop('source')
        x['source'] = { 'display_name': source}
        x['taxonomy_id'] = taxonomy_id
        yield x

    ## only load the annotations with annotation_type = 'manually curated' and source != 'SGD'
    ## and the annotations with annotation_type = 'high-throughput' and source = 'SGD'
    ## into NEX2 from BUD
    
    from src.sgd.model.nex.go import Go
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.eco import EcoAlias

    from src.sgd.model.bud.go import Go as Go_bud
    from src.sgd.model.bud.go import GoRef

    goid_to_go_id = dict([(x.goid, x.id) for x in nex_session.query(Go).all()])
    bud_id_to_reference_id = dict([(x.bud_id, x.id) for x in nex_session.query(Reference).all()])
    bud_id_to_locus_id= dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    evidence_to_eco_id = dict([(x.display_name, x.eco_id) for x in nex_session.query(EcoAlias).all()])
    
    qualifier_mapping = { "P": "involved in", "F": "enables", "C": "part of" }

    go_no_to_goid = {}
    goid_to_qualifier = {}
    for x in bud_session.query(Go_bud).all():
        goid = str(x.go_go_id)
        while len(goid) < 7:
            goid = '0' + goid
        goid = "GO:" + goid
        go_no_to_goid[x.id] = goid
        goid_to_qualifier[goid] = qualifier_mapping[x.go_aspect]

    for bud_obj in bud_session.query(GoRef).all():

        annotation = bud_obj.go_annotation

        if annotation.source == 'SGD' and annotation.annotation_type == 'manually curated':
            continue
    
        if annotation.annotation_type == 'computational' and annotation.go_evidence == 'IEA':
            continue

        locus_id = bud_id_to_locus_id.get(annotation.feature_id)
        if locus_id is None:
            print "The feature_no = ", annotation.feature_id, " is not in LOCUSDBENTITY table."
            continue

        eco_id = evidence_to_eco_id.get(annotation.go_evidence)
        if eco_id is None:
            print "The go_evidence = ", annotation.go_evidence, " is not in the ECO table."
            continue

        goid = go_no_to_goid[annotation.go_id]
        go_id = goid_to_go_id.get(goid)
        if go_id is None:
            print "The GOID = ", goid, " is not in GO table."
            continue

        reference_id = bud_id_to_reference_id.get(bud_obj.reference_id)
        if reference_id is None:
            print "The reference_no = ", bud_obj.reference_id, " is not in REFERENCEDBENTITY table."
            continue

        qualifier = bud_obj.qualifier
        if qualifier is None:
            qualifier = goid_to_qualifier[goid]

        obj_json = { 'source': {'display_name': annotation.source},
                     'dbentity_id': locus_id,
                     'reference_id': reference_id,
                     'taxonomy_id': taxonomy_id,
                     'go_id': go_id,
                     'eco_id': eco_id,
                     'annotation_type': annotation.annotation_type,
                     'go_qualifier': qualifier,
                     'bud_id': bud_obj.id,
                     'date_assigned': str(annotation.date_last_reviewed),
                     'date_created': str(bud_obj.date_created),
                     'created_by': bud_obj.created_by }
        yield obj_json
        
    bud_session.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, goannotation_starter, 'goannotation', lambda x: (x['dbentity_id'], x['annotation_type'], x['reference_id'], x['go_id'], x['eco_id']))


