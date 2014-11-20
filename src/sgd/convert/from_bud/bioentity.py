from sqlalchemy.orm import joinedload

from src.sgd.convert import break_up_file
from src.sgd.convert.transformers import make_db_starter, make_file_starter

__author__ = 'kpaskov'

# --------------------- Convert Locus ---------------------
non_locus_feature_types = {
    'ARS consensus sequence',
    'binding_site',
    'CDEI',
    'CDEII',
    'CDEIII',
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
    'X_element_combinatorial_repeats',
    'X_element_core_sequence',
    "Y'_element",
    'uORF',
    'W_region',
    'X_region',
    'Y_region',
    'Z1_region',
    'Z2_region'
}

def make_locus_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.feature import Feature
    def locus_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        #Cache
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        sgdid_to_uniprotid = {}
        for line in break_up_file('src/sgd/convert/data/YEAST_559292_idmapping.dat'):
            if line[1].strip() == 'SGD':
                sgdid_to_uniprotid[line[2].strip()] = line[0].strip()

        #From feature
        for bud_obj in bud_session.query(Feature).options(joinedload('annotation')).all():
            display_name = bud_obj.gene_name
            if display_name is None:
                display_name = bud_obj.name

            name_description = None
            headline = None
            description = None
            qualifier = None
            genetic_position = None

            ann = bud_obj.annotation
            if ann is not None:
                name_description = ann.name_description
                headline = ann.headline
                description = ann.description
                qualifier = ann.qualifier
                genetic_position = ann.genetic_position

            sgdid = bud_obj.dbxref_id

            source_key = bud_obj.source
            source = None if source_key not in key_to_source else key_to_source[source_key]

            if bud_obj.type not in non_locus_feature_types:
                yield {'id': bud_obj.id,
                                      'display_name': display_name,
                                      'format_name':bud_obj.name,
                                      'source': source,
                                      'sgdid': sgdid,
                                      'uniprotid': None if sgdid not in sgdid_to_uniprotid else sgdid_to_uniprotid[sgdid],
                                      'bioent_status': bud_obj.status,
                                      'locus_type': bud_obj.type,
                                      'name_description': name_description,
                                      'headline': headline,
                                      'qualifier': qualifier,
                                      'description': description,
                                      'gene_name': bud_obj.gene_name,
                                      'genetic_position': genetic_position,
                                      'date_created': bud_obj.date_created,
                                      'created_by': bud_obj.created_by}

        bud_session.close()
        nex_session.close()
    return locus_starter

# --------------------- Convert Bioentity Tabs ---------------------
def make_bioentity_tab_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Locus

    def bioentity_tab_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        for locus in nex_session.query(Locus).all():
            if locus.bioent_status == 'Merged' or locus.bioent_status == 'Deleted':
                yield {
                    'id': locus.id,
                    'summary_tab': 1,
                    'sequence_tab': 0,
                    'history_tab': 0,
                    'literature_tab': 0,
                    'go_tab': 0,
                    'phenotype_tab': 0,
                    'interaction_tab': 0,
                    'expression_tab': 0,
                    'regulation_tab': 0,
                    'protein_tab': 0,
                    'wiki_tab': 0
                }
            elif locus.locus_type == 'ORF' or locus.locus_type == 'blocked_reading_frame':
                yield {
                    'id': locus.id,
                    'summary_tab': 1,
                    'sequence_tab': 1,
                    'history_tab': 0,
                    'literature_tab': 1,
                    'go_tab': 1,
                    'phenotype_tab': 1,
                    'interaction_tab': 1,
                    'expression_tab': 1,
                    'regulation_tab': 1,
                    'protein_tab': 1,
                    'wiki_tab': 0
                }
            elif locus.locus_type in {'ARS', 'origin_of_replication', 'matrix_attachment_site', 'centromere',
                                      'gene_group', 'long_terminal_repeat', 'telomere', 'mating_type_region',
                                      'silent_mating_type_cassette_array', 'LTR_retrotransposon'}:
                yield {
                    'id': locus.id,
                    'summary_tab': 1,
                    'sequence_tab': 1,
                    'history_tab': 0,
                    'literature_tab': 1,
                    'go_tab': 0,
                    'phenotype_tab': 0,
                    'interaction_tab': 0,
                    'expression_tab': 0,
                    'regulation_tab': 0,
                    'protein_tab': 0,
                    'wiki_tab': 0
                }
            elif locus.locus_type == 'transposable_element_gene':
                yield {
                    'id': locus.id,
                    'summary_tab': 1,
                    'sequence_tab': 1,
                    'history_tab': 0,
                    'literature_tab': 1,
                    'go_tab': 1,
                    'phenotype_tab': 1,
                    'interaction_tab': 1,
                    'expression_tab': 0,
                    'regulation_tab': 0,
                    'protein_tab': 1,
                    'wiki_tab': 0
                }
            elif locus.locus_type == 'pseudogene':
                yield {
                    'id': locus.id,
                    'summary_tab': 1,
                    'sequence_tab': 1,
                    'history_tab': 0,
                    'literature_tab': 1,
                    'go_tab': 1,
                    'phenotype_tab': 1,
                    'interaction_tab': 1,
                    'expression_tab': 0,
                    'regulation_tab': 1,
                    'protein_tab': 1,
                    'wiki_tab': 0
                }
            elif locus.locus_type in {'rRNA_gene', 'ncRNA_gene', 'snRNA_gene', 'snoRNA_gene', 'tRNA_gene', 'telomerase_RNA_gene'}:
                yield {
                    'id': locus.id,
                    'summary_tab': 1,
                    'sequence_tab': 1,
                    'history_tab': 0,
                    'literature_tab': 1,
                    'go_tab': 1,
                    'phenotype_tab': 1,
                    'interaction_tab': 1,
                    'expression_tab': 0,
                    'regulation_tab': 1,
                    'protein_tab': 0,
                    'wiki_tab': 0
                }
            elif locus.locus_type in {'not in systematic sequence', 'not physically mapped'}:
                yield {
                    'id': locus.id,
                    'summary_tab': 1,
                    'sequence_tab': 1,
                    'history_tab': 0,
                    'literature_tab': 1,
                    'go_tab': 1,
                    'phenotype_tab': 1,
                    'interaction_tab': 1,
                    'expression_tab': 0,
                    'regulation_tab': 0,
                    'protein_tab': 0,
                    'wiki_tab': 0
                }

        bud_session.close()
        nex_session.close()
    return bioentity_tab_starter

# --------------------- Convert Bioentity Quality ---------------------
def make_bioentity_quality_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.bud.feature import Annotation as OldAnnotation, FeatureProperty as OldFeatureProperty
    def bioentity_quality_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for old_annotation in bud_session.query(OldAnnotation).all():
            bioentity_id = old_annotation.feature_id

            if bioentity_id in id_to_bioentity:

                if old_annotation.qualifier is not None:
                    yield {'source': key_to_source['SGD'],
                                   'bioentity': id_to_bioentity[bioentity_id],
                                   'display_name': 'Qualifier',
                                   'value': old_annotation.qualifier,
                                   'date_created': old_annotation.date_created,
                                   'created_by': old_annotation.created_by}

                if old_annotation.name_description is not None:
                    yield {'source': key_to_source['SGD'],
                                   'bioentity': id_to_bioentity[bioentity_id],
                                   'display_name': 'Name Description',
                                   'value': old_annotation.name_description,
                                   'date_created': old_annotation.date_created,
                                   'created_by': old_annotation.created_by}

                if old_annotation.description is not None:
                    yield {'source': key_to_source['SGD'],
                                   'bioentity': id_to_bioentity[bioentity_id],
                                   'display_name': 'Description',
                                   'value': old_annotation.description,
                                   'date_created': old_annotation.date_created,
                                   'created_by': old_annotation.created_by}

                if old_annotation.genetic_position is not None:
                    yield {'source': key_to_source['SGD'],
                                   'bioentity': id_to_bioentity[bioentity_id],
                                   'display_name': 'Genetic Position',
                                   'value': old_annotation.genetic_position,
                                   'date_created': old_annotation.date_created,
                                   'created_by': old_annotation.created_by}

                if old_annotation.headline is not None:
                    yield {'source': key_to_source['SGD'],
                                   'bioentity': id_to_bioentity[bioentity_id],
                                   'display_name': 'Headline',
                                   'value': old_annotation.headline,
                                   'date_created': old_annotation.date_created,
                                   'created_by': old_annotation.created_by}
            else:
                #print 'Could not find  bioentity: ' + str(bioentity_id)
                yield None

        for bioentity in id_to_bioentity.values():
            yield {'source': key_to_source['SGD'],
                               'bioentity': bioentity,
                               'display_name': 'Gene Name',
                               'value': bioentity.gene_name}

            yield {'source': key_to_source['SGD'],
                               'bioentity': bioentity,
                               'display_name': 'Feature Type',
                               'value': bioentity.locus_type}

            yield {'source': key_to_source['SGD'],
                               'bioentity': bioentity,
                               'display_name': 'ID',
                               'value': bioentity.id}

        for feature_property in bud_session.query(OldFeatureProperty).all():
            bioentity_id = feature_property.feature_id
            if bioentity_id in id_to_bioentity:
                yield {'source': key_to_source['SGD'],
                               'bioentity': id_to_bioentity[bioentity_id],
                               'display_name': feature_property.property_type,
                               'value': feature_property.property_value}
            else:
                #print 'Could not find bioentity: ' + str(bioentity_id)
                yield None

        bud_session.close()
        nex_session.close()
    return bioentity_quality_starter

# --------------------- Convert Alias ---------------------
def make_bioentity_alias_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.bud.feature import AliasFeature
    from src.sgd.model.bud.general import DbxrefFeat, Note, NoteFeat

    def bioentity_alias_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        bioentity_ids = set([x.id for x in nex_session.query(Bioentity.id).all()])

        for bud_obj in bud_session.query(AliasFeature).options(joinedload('alias')).all():
            if bud_obj.alias_type in {'Uniform', 'Non-uniform', 'NCBI protein name', 'Retired name'}:
                bioentity_id = bud_obj.feature_id
                if bioentity_id in bioentity_ids:
                    yield {'display_name': bud_obj.alias_name,
                           'source': key_to_source['SGD'],
                           'category': 'Alias' if bud_obj.alias_type == 'Uniform' or bud_obj.alias_type == 'Non-uniform' else bud_obj.alias_type,
                           'bioentity_id': bioentity_id,
                           'is_external_id': 0,
                           'date_created': bud_obj.date_created,
                           'created_by': bud_obj.created_by}
                else:
                    yield None

        for bud_obj in bud_session.query(DbxrefFeat).options(joinedload('dbxref'), joinedload('dbxref.dbxref_urls')).all():
            display_name = bud_obj.dbxref.dbxref_id
            bioentity_id = bud_obj.feature_id
            if bioentity_id in bioentity_ids:
                link = None
                if len(bud_obj.dbxref.urls) > 0:
                    if len(bud_obj.dbxref.urls) == 1:
                        link = bud_obj.dbxref.urls[0].url.replace('_SUBSTITUTE_THIS_', display_name)
                    else:
                        for url in bud_obj.dbxref.urls:
                            for display in url.displays:
                                if display.label_location == 'Resources External Links':
                                    link = url.url.replace('_SUBSTITUTE_THIS_', display_name)

                yield {'display_name': display_name,
                       'link': link,
                       'source': key_to_source[bud_obj.dbxref.source.replace('/', '-')],
                       'category': bud_obj.dbxref.dbxref_type,
                       'bioentity_id': bioentity_id,
                       'is_external_id': 1,
                       'date_created': bud_obj.dbxref.date_created,
                       'created_by': bud_obj.dbxref.created_by}
            else:
                yield None

        bud_session.close()
        nex_session.close()
    return bioentity_alias_starter

# --------------------- Convert Relation ---------------------
def make_bioentity_relation_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.feature import FeatRel

    def bioentity_relation_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for relation in bud_session.query(FeatRel).filter_by(relationship_type='pair').all():
            yield {'source': key_to_source['SGD'],
                           'relation_type': 'paralog',
                           'parent_id': relation.parent_id,
                           'child_id': relation.child_id}

            yield {'source': key_to_source['SGD'],
                           'relation_type': 'paralog',
                           'parent_id': relation.child_id,
                           'child_id': relation.parent_id}

        bud_session.close()
        nex_session.close()
    return bioentity_relation_starter

# --------------------- Convert Url ---------------------
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
