from src.sgd.convert import break_up_file
from sqlalchemy.orm import joinedload
from src.sgd.convert.from_bud import basic_convert, remove_nones

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

url_placement_mapping = {
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


def load_urls(bud_locus, bud_session):
    from src.sgd.model.bud.general import FeatUrl, DbxrefFeat

    urls = []

    for bud_obj in bud_session.query(FeatUrl).options(joinedload('url')).filter_by(feature_id=bud_locus.id).all():
        old_url = bud_obj.url
        url_type = old_url.url_type
        link = old_url.url

        for old_webdisplay in old_url.displays:
            if url_type == 'query by SGDID':
                link = link.replace('_SUBSTITUTE_THIS_', bud_locus.dbxref_id)
            elif url_type == 'query by SGD ORF name with anchor' or url_type == 'query by SGD ORF name' or url_type == 'query by ID assigned by database':
                link = link.replace('_SUBSTITUTE_THIS_', bud_locus.name)
            else:
                print "Can't handle this url. " + str(old_url.url_type)

            urls.append(
                {'display_name': old_webdisplay.label_name,
                 'source': {'display_name': old_url.source},
                 'bud_id': old_url.id,
                 'url_type': url_type,
                 'placement': old_webdisplay.label_location if old_webdisplay.label_location not in url_placement_mapping else url_placement_mapping[old_webdisplay.label_location],
                 'link': link,
                 'date_created': str(old_url.date_created),
                 'created_by': old_url.created_by})

    for bud_obj in bud_session.query(DbxrefFeat).options(joinedload('dbxref'), joinedload('dbxref.dbxref_urls')).filter_by(feature_id=bud_locus.id).all():
        old_urls = bud_obj.dbxref.urls
        dbxref_id = bud_obj.dbxref.dbxref_id

        for old_url in old_urls:
            for old_webdisplay in old_url.displays:
                url_type = old_url.url_type
                link = old_url.url

                if url_type == 'query by SGD ORF name with anchor' or url_type == 'query by SGD ORF name':
                    link = link.replace('_SUBSTITUTE_THIS_', bud_locus.name)
                elif url_type == 'query by ID assigned by database':
                    link = link.replace('_SUBSTITUTE_THIS_', str(dbxref_id))
                elif url_type == 'query by SGDID':
                    link = link.replace('_SUBSTITUTE_THIS_', bud_locus.dbxref_id)
                else:
                    print "Can't handle this url. " + str(old_url.url_type)

                urls.append(
                    {'display_name': old_webdisplay.label_name,
                     'source': {'display_name': old_url.source},
                     'bud_id': old_url.id,
                     'link': link,
                     'url_type': url_type,
                     'placement': old_webdisplay.label_location if old_webdisplay.label_location not in url_placement_mapping else url_placement_mapping[old_webdisplay.label_location],
                     'date_created': str(old_url.date_created),
                     'created_by': old_url.created_by})

    urls.append(
        {'display_name': 'SPELL',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': 'http://spell.yeastgenome.org/search/show_results?search_string=' + bud_locus.name,
         'url_type': 'Unknown',
         'placement': 'LOCUS_EXPRESSION'})

    urls.append(
        {'display_name': 'Gene/Sequence Resources',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/cgi-bin/seqTools?back=1&seqname=' + bud_locus.name,
         'url_type': 'Unknown',
         'placement': 'LOCUS_SEQUENCE'})

    urls.append(
        {'display_name': 'ORF Map',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/cgi-bin/ORFMAP/ORFmap?dbid=' + bud_locus.dbxref_id,
         'url_type': 'Unknown',
         'placement': 'LOCUS_SEQUENCE'})

    urls.append(
        {'display_name': 'GBrowse',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': 'http://browse.yeastgenome.org/fgb2/gbrowse/scgenome/?name=' + bud_locus.name,
         'url_type': 'Unknown',
         'placement': 'LOCUS_SEQUENCE'})

    urls.append(
        {'display_name': 'BLASTN',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/cgi-bin/blast-sgd.pl?name=' + bud_locus.name,
         'url_type': 'Unknown',
         'placement': 'LOCUS_SEQUENCE_SECTION'})

    urls.append(
        {'display_name': 'BLASTP',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/cgi-bin/blast-sgd.pl?name=' + bud_locus.name + '&suffix=prot',
         'url_type': 'Unknown',
         'placement': 'LOCUS_SEQUENCE_SECTION'})

    urls.append(
        {'display_name': 'Yeast Phenotype Ontology',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/ontology/phenotype/ypo/overview',
         'url_type': 'Unknown',
         'placement': 'LOCUS_PHENOTYPE_ONTOLOGY'})

    make_unique = dict([((x['display_name'], x['placement'], x['link']), x) for x in urls])
    return make_unique.values()


def load_aliases(bud_locus, bud_session, uniprot_id):
    from src.sgd.model.bud.feature import Feature, Annotation, AliasFeature
    from src.sgd.model.bud.general import DbxrefFeat, Note, NoteFeat

    aliases = []
    for bud_obj in bud_session.query(AliasFeature).options(joinedload('alias')).filter_by(feature_id=bud_locus.id).all():
        #if bud_obj.alias_type in {'Uniform', 'Non-uniform', 'NCBI protein name', 'Retired name'}:
        aliases.append({
            'display_name': bud_obj.alias_name,
            'source': {'display_name': 'SGD'},
            'bud_id': bud_obj.id,
            'alias_type': bud_obj.alias_type,
            'date_created': str(bud_obj.date_created),
            'created_by': bud_obj.created_by})

    for bud_obj in bud_session.query(DbxrefFeat).options(joinedload('dbxref'), joinedload('dbxref.dbxref_urls')).filter_by(feature_id=bud_locus.id).all():
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

        aliases.append(remove_nones(
            {'display_name': display_name,
             'link': link,
             'source': {'display_name': bud_obj.dbxref.source},
             'alias_type': bud_obj.dbxref.dbxref_type,
             'bud_id': bud_obj.id,
             'date_created': str(bud_obj.dbxref.date_created),
             'created_by': bud_obj.dbxref.created_by}))

    if uniprot_id is not None:
        aliases.append(
            {'display_name': uniprot_id,
             'source': {'display_name': 'Uniprot'},
             'alias_type': 'Uniprot ID'})

    return aliases


def locus_starter(bud_session_maker):
    from src.sgd.model.bud.feature import Feature

    bud_session = bud_session_maker()

    #Load uniprot ids
    sgdid_to_uniprotid = {}
    for line in break_up_file('src/sgd/convert/data/YEAST_559292_idmapping.dat'):
        if line[1].strip() == 'SGD':
            sgdid_to_uniprotid[line[2].strip()] = line[0].strip()

    #Create features
    for bud_obj in bud_session.query(Feature).options(joinedload('annotation')).all():
        if bud_obj.type not in non_locus_feature_types:
            sgdid = bud_obj.dbxref_id
            obj_json = {'gene_name': bud_obj.gene_name,
                        'systematic_name':bud_obj.name,
                        'source': {
                            'display_name': bud_obj.source
                        },
                        'bud_id': bud_obj.id,
                        'sgdid': sgdid,
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

            obj_json = remove_nones(obj_json)

            #Load aliases
            obj_json['aliases'] = load_aliases(bud_obj, bud_session, None if sgdid not in sgdid_to_uniprotid else sgdid_to_uniprotid[sgdid])

            #Load urls
            obj_json['urls'] = load_urls(bud_obj, bud_session)

            print obj_json['systematic_name']
            yield obj_json

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, locus_starter, 'locus', lambda x: x['sgdid'])

if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

