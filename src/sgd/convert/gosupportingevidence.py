from src.sgd.convert import basic_convert
from src.sgd.convert.util import get_relation_to_ro_id, read_gpi_file, read_gpad_file, get_go_extension_link

__author__ = 'sweng66'

GPI_FILE = 'src/sgd/convert/data/gp_information.559292_sgd'
GPAD_FILE = 'src/sgd/convert/data/gp_association.559292_sgd'

def gosupportingevidence_starter(bud_session_maker):

    from src.sgd.model.nex.goannotation import Goannotation
    
    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    key_to_annotation_id = {}
    for x in nex_session.query(Goannotation).all():
        key = (x.dbentity_id, x.go_id, x.eco_id, x.reference_id, x.annotation_type, x.source.display_name, x.go_qualifier)
        key_to_annotation_id[key] = x.id

    ## load the annotations with source = 'SGD' and the annotations with go_evidence = 'IEA' from GPAD file

    [uniprot_to_date_assigned, uniprot_to_sgdid_list] = read_gpi_file(GPI_FILE)

    get_extension = 0
    get_support = 1
    data = read_gpad_file(GPAD_FILE, bud_session, nex_session, uniprot_to_date_assigned,
                          uniprot_to_sgdid_list, get_extension, get_support)

    for x in data:

        key = (x['dbentity_id'], x['go_id'], x['eco_id'], x['reference_id'], x['annotation_type'], x['source'], x['go_qualifier'])
        annotation_id = key_to_annotation_id.get(key)

        if annotation_id is None:
            print "The goannotatuon key: ", key, " is not in GOANNOTATION table."
            continue
        
        groups = x['gosupport'].split('|')
        group_id = 0
        for group in groups:
            if group.startswith('With:Not_supplied'):
                break
            dbxref_ids = group.split(',')
            group_id = group_id + 1
            for dbxref_id in dbxref_ids:
                link = get_go_extension_link(dbxref_id)
                if link.startswith('Unknown'):
                    print "Unknown ID: ", dbxref_id
                    continue
                evidence_type = 'with'
                if dbxref_id.startswith('GO:'):
                    evidence_type = 'from'

                yield { 'annotation_id': annotation_id,
                        'group_id': group_id,
                        'evidence_type': evidence_type,
                        'dbxref_id': dbxref_id,
                        'link': link }

    f.close()

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

    goref_dbxref = get_go_supporting_data(bud_session)

    for bud_obj in bud_session.query(GoRef).all():

        annotation = bud_obj.go_annotation

        if annotation.source == 'SGD' and annotation.annotation_type == 'manually curated':
            continue

        if annotation.annotation_type == 'computational' and annotation.go_evidence == 'IEA':
            continue

        gosupportingevidence = goref_dbxref.get(bud_obj.id)

        if gosupportingevidence is None:
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

        key = (locus_id, go_id, eco_id, reference_id, annotation.annotation_type, annotation.source, qualifier)
        annotation_id = key_to_annotation_id.get(key)

        if annotation_id is None:
            print "The goannotatuon key: ", key, " is not in GOANNOTATION table."
            continue
        
        for x in gosupportingevidence:
            x['annotation_id'] = annotation_id
            yield x
            
    bud_session.close()

def get_go_supporting_data(bud_session):

    from src.sgd.model.bud.go import GorefDbxref

    goref_dbxref = {}
    for x in bud_session.query(GorefDbxref).all():
        id = ''
        if x.dbxref.dbxref_type.startswith('DBID'):
            id = 'SGD:' + x.dbxref.dbxref_id
        elif x.dbxref.dbxref_type.startswith('EC'):
            id = 'EC:' + x.dbxref.dbxref_id
        elif x.dbxref.dbxref_type.startswith('UniProt/Swiss'):
            id = 'UniProtKB:' + x.dbxref.dbxref_id
        elif x.dbxref.dbxref_type.startswith('UniProtKB Subcellular'):
            id = 'UniProtKB-SubCell:' + x.dbxref.dbxref_id
        elif x.dbxref.dbxref_type.startswith('UniProtKB Keyword'):
            id = 'UniProtKB-KW:' + x.dbxref.dbxref_id
        elif x.dbxref.dbxref_type.startswith('UniPathway'):
            id = 'UniPathway:' + x.dbxref.dbxref_id
        elif x.dbxref.dbxref_type.startswith('InterPro'):
            id = 'InterPro:' + x.dbxref.dbxref_id
        elif x.dbxref.dbxref_type.startswith('DNA accession'):
            id = 'EMBL:' + x.dbxref.dbxref_id
        elif x.dbxref.dbxref_type.startswith('Protein version'):
            id = 'protein_id:' + x.dbxref.dbxref_id
        elif x.dbxref.source == 'MGI':
            id = 'MGI:' + x.dbxref.dbxref_id
        elif x.dbxref.dbxref_type.startswith('PANTHER'):
            id = 'PANTHER:' + x.dbxref.dbxref_id
        elif x.dbxref.dbxref_type.startswith('HAMAP'):
            id = 'HAMAP:' + x.dbxref.dbxref_id
        link = get_link(id)
        if link == 'Unknown':
            print "Unknown DBXREF ID: ", id
            continue
        group = []
        group_id = 1
        if x.goref_id in goref_dbxref:
            group = goref_dbxref[x.goref_id]
            group_id = len(goref_dbxref[x.goref_id]) + 1
        group.append({ 'group_id': group_id,
                       'evidence_type': x.support_type.lower(),
                       'dbxref_id': id,
                       'link': link })
        goref_dbxref[x.goref_id] = group

    return goref_dbxref

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, gosupportingevidence_starter, 'gosupportingevidence', lambda x: (x['annotation_id'], x['group_id'], x['dbxref_id'], x['link'], x['evidence_type']))


