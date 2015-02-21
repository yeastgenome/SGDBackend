__author__ = 'kpaskov'
import json
from src.sgd.convert import break_up_file
from sqlalchemy.orm import joinedload

non_locus_feature_types = {
    'ARS_consensus_sequence',
    'binding_site',
    'centromere_DNA_Element_I',
    'centromere_DNA_Element_II',
    'centromere_DNA_Element_III',
    'CDS',
    'chromosome',
    'external_transcribed_spacer_region',
    'five_prime_UTR_intron',
    'insertion',
    'internal_transcribed_spacer_region',
    'intron',
    'mRNA',
    'non_transcribed_region',
    'noncoding_exon',
    'not physically mapped',
    'plasmid',
    'plus_1_translational_frameshift',
    'repeat_region',
    'TF_binding_site',
    'TF_binding_sites',
    'telomeric_repeat',
    'X_element_combinatorial_repeat',
    'X_element',
    "Y_prime_element",
    'uORF',
    'W_region',
    'X_region',
    'Y_region',
    'Z1_region',
    'Z2_region'
}

def locus_starter(bud_session_maker):
    from src.sgd.model.bud.feature import Feature, Annotation, AliasFeature
    from src.sgd.model.bud.general import DbxrefFeat, Note, NoteFeat

    bud_session = bud_session_maker()

    #Load uniprot ids
    sgdid_to_uniprotid = {}
    for line in break_up_file('src/sgd/convert/data/YEAST_559292_idmapping.dat'):
        if line[1].strip() == 'SGD':
            sgdid_to_uniprotid[line[2].strip()] = line[0].strip()

    #Load aliases
    bud_id_to_aliases = dict()
    for bud_obj in bud_session.query(AliasFeature).options(joinedload('alias')).all():
        bud_id = bud_obj.feature_id
        if bud_id not in bud_id_to_aliases:
            bud_id_to_aliases[bud_id] = []

        if bud_obj.alias_type in {'Uniform', 'Non-uniform', 'NCBI protein name', 'Retired name'}:
            bud_id_to_aliases[bud_id].append(
                {'display_name': bud_obj.alias_name,
                 'source': {'display_name': 'SGD'},
                 'bud_id': bud_obj.id,
                 'alias_type': bud_obj.alias_type,
                 'date_created': str(bud_obj.date_created),
                 'created_by': bud_obj.created_by})

    for bud_obj in bud_session.query(DbxrefFeat).options(joinedload('dbxref'), joinedload('dbxref.dbxref_urls')).all():
        bud_id = bud_obj.feature_id
        if bud_id not in bud_id_to_aliases:
            bud_id_to_aliases[bud_id] = []

        display_name = bud_obj.dbxref.dbxref_id
        link = None
        if len(bud_obj.dbxref.urls) > 0:
            if len(bud_obj.dbxref.urls) == 1:
                link = bud_obj.dbxref.urls[0].url.replace('_SUBSTITUTE_THIS_', display_name)
            else:
                for url in bud_obj.dbxref.urls:
                    for display in url.displays:
                        if display.label_location == 'Resources External Links':
                            link = url.url.replace('_SUBSTITUTE_THIS_', display_name)

        bud_id_to_aliases[bud_id].append(
            {'display_name': display_name,
             'link': link,
             'source': {'display_name': bud_obj.dbxref.source},
             'alias_type': bud_obj.dbxref.dbxref_type,
             'bud_id': bud_obj.id,
             'date_created': str(bud_obj.dbxref.date_created),
             'created_by': bud_obj.dbxref.created_by})

    #Create features
    for bud_obj in bud_session.query(Feature).options(joinedload('annotation')).all():
        if bud_obj.type not in non_locus_feature_types:
            sgdid = bud_obj.dbxref_id
            obj_json = {'bud_id': bud_obj.id,
                        'gene_name': bud_obj.gene_name,
                        'systematic_name':bud_obj.name,
                        'source': {
                            'display_name': bud_obj.source
                        },
                        'sgdid': sgdid,
                        'uniprotid': None if sgdid not in sgdid_to_uniprotid else sgdid_to_uniprotid[sgdid],
                        'dbent_status': bud_obj.status,
                        'locus_type': bud_obj.type,
                        'gene_name': bud_obj.gene_name,
                        'bud_id': bud_obj.id,
                        'date_created': str(bud_obj.date_created),
                        'created_by': bud_obj.created_by}

            ann = bud_obj.annotation
            if ann is not None:
                obj_json['name_description'] = ann.name_description
                obj_json['headline'] = ann.headline
                obj_json['qualifier'] = ann.qualifier
                obj_json['description'] = ann.description
                obj_json['genetic_position'] = str(ann.genetic_position)

            if bud_obj.id in bud_id_to_aliases:
                obj_json['aliases'] = bud_id_to_aliases[bud_obj.id]

            yield obj_json

    bud_session.close()

if __name__ == '__main__':

    from src.sgd.backend.curate import CurateBackend
    from src.sgd.model import bud
    from src.sgd.convert import config
    from src.sgd.convert import prepare_schema_connection

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)
    curate_backend = CurateBackend(config.NEX_DBTYPE, 'curator-dev-db', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS, config.log_directory)

    accumulated_status = dict()
    for obj_json in locus_starter(bud_session_maker):
        output = curate_backend.update_object('locus', obj_json)
        status = json.loads(output)['status']
        if status == 'Error':
            print output
        if status not in accumulated_status:
            accumulated_status[status] = 0
        accumulated_status[status] += 1
    print 'convert.locus', accumulated_status

