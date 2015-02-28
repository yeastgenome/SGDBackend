from src.sgd.convert import break_up_file
from sqlalchemy.orm import joinedload
from src.sgd.convert.from_bud import basic_convert

__author__ = 'kpaskov'


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

category_mapping = {
    'Mutant Strains': 'LOCUS_PHENOTYPE_MUTANT_STRAINS',
    'Phenotype Resources': 'LOCUS_PHENOTYPE_PHENOTYPE_RESOURCES',
    'Interaction Resources': 'LOCUS_INTERACTION',
    'Expression Resources': 'LOCUS_EXPRESSION',
    'Regulatory Role Resources': 'LOCUS_REGULATION',
    'Protein Information Homologs': 'LOCUS_PROTEIN_HOMOLOGS',
    'Analyze Sequence S288C vs. other species': 'LOCUS_PROTEIN_HOMOLOGS',
    'Protein databases/Other': 'LOCUS_PROTEIN_PROTEIN_DATABASES',
    'Localization Resources': 'LOCUS_PROEIN_LOCALIZATION',
    'Post-translational modifications': 'LOCUS_PROTEIN_MODIFICATIONS',
    'Analyze Sequence S288C only': 'LOCUS_SEQUENCE_S288C',
    'Analyze Sequence S288C vs. other species': 'LOCUS_SEQUENCE_OTHER_SPECIES',
    'Analyze Sequence S288C vs. other strains': 'LOCUS_SEQUENCE_OTHER_STRAINS',
    'Resources External Links': 'LOCUS_LSP'
}

def make_bioentity_url_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex import create_format_name
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Bioentity, Locus
    from src.sgd.model.bud.general import FeatUrl, DbxrefFeat
    def bioentity_url_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Bioentity).all()])

        for bud_obj in make_db_starter(bud_session.query(FeatUrl).options(joinedload('url')), 1000)():
            old_url = bud_obj.url
            url_type = old_url.url_type
            link = old_url.url

            bioentity_id = bud_obj.feature_id

            for old_webdisplay in old_url.displays:
                if bioentity_id in id_to_bioentity:
                    bioentity = id_to_bioentity[bioentity_id]
                    if url_type == 'query by SGDID':
                        link = link.replace('_SUBSTITUTE_THIS_', str(bioentity.sgdid))
                    elif url_type == 'query by SGD ORF name with anchor' or url_type == 'query by SGD ORF name' or url_type == 'query by ID assigned by database':
                        link = link.replace('_SUBSTITUTE_THIS_', str(bioentity.format_name))
                    else:
                        print "Can't handle this url. " + str(old_url.url_type)
                        yield None

                    category = None if old_webdisplay.label_location not in category_mapping else category_mapping[old_webdisplay.label_location]

                    yield {'display_name': old_webdisplay.label_name,
                           'link': link,
                           'source': key_to_source[create_format_name(old_url.source)],
                           'category': category,
                           'bioentity_id': bioentity_id,
                           'date_created': old_url.date_created,
                           'created_by': old_url.created_by}
                else:
                    #print 'Bioentity not found: ' + str(bioentity_id)
                    yield None

        for bud_obj in make_db_starter(bud_session.query(DbxrefFeat).options(joinedload('dbxref'), joinedload('dbxref.dbxref_urls')), 1000)():
            old_urls = bud_obj.dbxref.urls
            dbxref_id = bud_obj.dbxref.dbxref_id

            bioentity_id = bud_obj.feature_id
            for old_url in old_urls:
                for old_webdisplay in old_url.displays:
                    if bioentity_id in id_to_bioentity:
                        bioentity = id_to_bioentity[bioentity_id]
                        url_type = old_url.url_type
                        link = old_url.url

                        if url_type == 'query by SGD ORF name with anchor' or url_type == 'query by SGD ORF name':
                            link = link.replace('_SUBSTITUTE_THIS_', bioentity.format_name)
                        elif url_type == 'query by ID assigned by database':
                            link = link.replace('_SUBSTITUTE_THIS_', str(dbxref_id))
                        elif url_type == 'query by SGDID':
                            link = link.replace('_SUBSTITUTE_THIS_', bioentity.sgdid)
                        else:
                            print "Can't handle this url. " + str(old_url.url_type)
                            yield None

                        category = None if old_webdisplay.label_location not in category_mapping else category_mapping[old_webdisplay.label_location]

                        yield {'display_name': old_webdisplay.label_name,
                                   'link': link,
                                   'source': key_to_source[create_format_name(old_url.source)],
                                   'category': category,
                                   'bioentity_id': bioentity_id,
                                   'date_created': old_url.date_created,
                                   'created_by': old_url.created_by}
                    else:
                        #print 'Bioentity not found: ' + str(bioentity_id)
                        yield None

        for locus in nex_session.query(Locus).all():
            yield {'display_name': 'SPELL',
                        'link': 'http://spell.yeastgenome.org/search/show_results?search_string=' + locus.format_name,
                        'source': key_to_source['SGD'],
                        'category': 'LOCUS_EXPRESSION',
                        'bioentity_id': locus.id}
            yield {'display_name': 'Gene/Sequence Resources',
                        'link': '/cgi-bin/seqTools?back=1&seqname=' + locus.format_name,
                        'source': key_to_source['SGD'],
                        'category': 'LOCUS_SEQUENCE',
                        'bioentity_id': locus.id}
            yield {'display_name': 'ORF Map',
                        'link': '/cgi-bin/ORFMAP/ORFmap?dbid=' + locus.sgdid,
                        'source': key_to_source['SGD'],
                        'category': 'LOCUS_SEQUENCE',
                        'bioentity_id': locus.id}
            yield {'display_name': 'GBrowse',
                        'link': 'http://browse.yeastgenome.org/fgb2/gbrowse/scgenome/?name=' + locus.format_name,
                        'source': key_to_source['SGD'],
                        'category': 'LOCUS_SEQUENCE',
                        'bioentity_id': locus.id}

            yield {'display_name': 'BLASTN',
                        'link': '/cgi-bin/blast-sgd.pl?name=' + locus.format_name,
                        'source': key_to_source['SGD'],
                        'category': 'LOCUS_SEQUENCE_SECTION',
                        'bioentity_id': locus.id}
            yield {'display_name': 'BLASTP',
                        'link': '/cgi-bin/blast-sgd.pl?name=' + locus.format_name + '&suffix=prot',
                        'source': key_to_source['SGD'],
                        'category': 'LOCUS_SEQUENCE_SECTION',
                        'bioentity_id': locus.id}
            yield {'display_name': 'Yeast Phenotype Ontology',
                        'link': '/ontology/phenotype/ypo/overview',
                        'source': key_to_source['SGD'],
                        'category': 'LOCUS_PHENOTYPE_ONTOLOGY',
                        'bioentity_id': locus.id}

        bud_session.close()
        nex_session.close()
    return bioentity_url_starter

def load_aliases(bud_session):
    from src.sgd.model.bud.feature import Feature, Annotation, AliasFeature
    from src.sgd.model.bud.general import DbxrefFeat, Note, NoteFeat

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
                 'link': None,
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
    return bud_id_to_aliases

def locus_starter(bud_session_maker):
    from src.sgd.model.bud.feature import Feature

    bud_session = bud_session_maker()

    #Load uniprot ids
    sgdid_to_uniprotid = {}
    for line in break_up_file('src/sgd/convert/data/YEAST_559292_idmapping.dat'):
        if line[1].strip() == 'SGD':
            sgdid_to_uniprotid[line[2].strip()] = line[0].strip()

    #Load aliases
    bud_id_to_aliases = load_aliases(bud_session)

    #Create features
    for bud_obj in bud_session.query(Feature).options(joinedload('annotation')).all():
        if bud_obj.type not in non_locus_feature_types:
            sgdid = bud_obj.dbxref_id
            obj_json = {'gene_name': bud_obj.gene_name,
                        'systematic_name':bud_obj.name,
                        'source': {
                            'display_name': bud_obj.source
                        },
                        'sgdid': sgdid,
                        'uniprotid': None if sgdid not in sgdid_to_uniprotid else sgdid_to_uniprotid[sgdid],
                        'dbentity_status': bud_obj.status,
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
                obj_json['genetic_position'] = None if ann.genetic_position is None else str(ann.genetic_position)

            if bud_obj.id in bud_id_to_aliases:
                obj_json['aliases'] = bud_id_to_aliases[bud_obj.id]

            yield obj_json

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, locus_starter, 'locus', lambda x: x['systematic_name'])

if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

