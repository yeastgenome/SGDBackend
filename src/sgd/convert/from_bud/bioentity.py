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

            ann = bud_obj.annotation
            if ann is not None:
                name_description = ann.name_description
                headline = ann.headline
                description = ann.description

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
                                      'description': description,
                                      'gene_name': bud_obj.gene_name,
                                      'date_created': bud_obj.date_created,
                                      'created_by': bud_obj.created_by}
        bud_session.close()
        nex_session.close()
    return locus_starter

#--------------------- Convert Complex ---------------------
def make_complex_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioconcept import Go

    def complex_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_go = dict([(x.unique_key(), x) for x in nex_session.query(Go).all()])

        for row in make_file_starter('src/sgd/convert/data/go_complexes.txt', offset=2)():
            go_key = (row[2], 'GO')
            go = None if go_key not in key_to_go else key_to_go[go_key]
            if go is None:
                print 'Go not found: ' + str(go_key)
                yield None

            source = key_to_source['SGD']
            yield {'source': source,
                            'go': go,
                            'cellular_localization': row[3]}

        nex_session.close()
    return complex_starter

# --------------------- Convert Bioentity Tabs ---------------------
def make_bioentity_tab_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Locus

    def bioentity_tab_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        for locus in nex_session.query(Locus).all():
            show_summary = 1
            show_history = 1
            show_wiki = 1

            if locus.bioent_status != 'Active':
                yield {'id': locus.id,
                           'summary_tab': show_summary,
                           'sequence_tab': 0,
                           'history_tab': show_history,
                           'literature_tab': 0,
                           'go_tab': 0,
                           'phenotype_tab': 0,
                           'interaction_tab': 0,
                           'expression_tab': 0,
                           'regulation_tab': 0,
                           'protein_tab': 0,
                           'wiki_tab': show_wiki}

            yes_sequence = {'ORF', 'ncRNA', 'tRNA', 'centromere', 'mating_locus', 'gene_cassette', 'ARS', 'telomere', 'long_terminal_repeat', 'transposable_element_gene', 'rRNA', 'snoRNA ', 'snRNA'}
            show_sequence = 1 if locus.locus_type in yes_sequence else 0

            show_literature = 1

            no_go = {'ARS', 'ARS consensus sequence', 'mating_locus', 'X_element_combinatorial_repeats',
                     'X_element_core_sequence', "Y'_element", 'centromere', 'long_terminal_repeat',
                     'telomere', 'telomeric_repeat', 'retrotransposon', 'gene_cassette', 'multigene locus'}
            show_go = 0 if locus.locus_type in no_go else 1

            no_phenotype = {'ARS', 'ARS consensus sequence', 'mating_locus', 'X_element_combinatorial_repeats',
                     'X_element_core_sequence', "Y'_element", 'centromere', 'LONG_TERMINAL_REPEAT',
                     'telomere', 'telomeric_repeat', 'retrotransposon', 'gene_cassette'}
            show_phenotype = 0 if locus.locus_type in no_phenotype else 1

            no_interactions = {'ARS', 'ARS consensus sequence', 'mating_locus', 'X_element_combinatorial_repeats',
                     'X_element_core_sequence', "Y'_element", 'centromere', 'long_terminal_repeat',
                     'telomere', 'telomeric_repeat', 'retrotransposon', 'gene_cassette', 'multigene locus',
                     'not in systematic sequence of S288C', 'not physically mapped'}
            show_interactions = 0 if locus.locus_type in no_interactions else 1

            no_expression = {'ARS', 'ARS consensus sequence', 'mating_locus', 'X_element_combinatorial_repeats',
                     'X_element_core_sequence', "Y'_element", 'centromere', 'long_terminal_repeat',
                     'telomere', 'telomeric_repeat', 'retrotransposon', 'gene_cassette', 'multigene locus',
                     'not in systematic sequence of S288C', 'not physically mapped', 'transposable_element_gene',
                     'pseudogene', 'ncRNA', 'snoRNA', 'tRNA', 'rRNA', 'snRNA'}
            show_expression = 0 if locus.locus_type in no_expression else 1

            no_regulation = {'ARS', 'ARS consensus sequence', 'mating_locus', 'X_element_combinatorial_repeats',
                     'X_element_core_sequence', "Y'_element", 'centromere', 'long_terminal_repeat',
                     'telomere', 'telomeric_repeat', 'retrotransposon', 'gene_cassette', 'multigene locus',
                     'not in systematic sequence of S288C', 'not physically mapped'}
            show_regulation = 0 if locus.locus_type in no_regulation else 1

            no_protein = {'ARS', 'ARS consensus sequence', 'mating_locus', 'X_element_combinatorial_repeats',
                     'X_element_core_sequence', "Y'_element", 'centromere', 'long_terminal_repeat',
                     'telomere', 'telomeric_repeat', 'retrotransposon', 'gene_cassette', 'multigene locus',
                     'not in systematic sequence of S288C', 'not physically mapped',
                     'ncRNA', 'snoRNA', 'tRNA', 'rRNA', 'snRNA'}
            show_protein = 0 if locus.locus_type in no_protein else 1

            yield {'id': locus.id,
                           'summary_tab': show_summary,
                           'sequence_tab': show_sequence,
                           'history_tab': show_history,
                           'literature_tab': show_literature,
                           'go_tab': show_go,
                           'phenotype_tab': show_phenotype,
                           'interaction_tab': show_interactions,
                           'expression_tab': show_expression,
                           'regulation_tab': show_regulation,
                           'protein_tab': show_protein,
                           'wiki_tab': show_wiki}
        bud_session.close()
        nex_session.close()
    return bioentity_tab_starter

# --------------------- Convert Alias ---------------------
def make_bioentity_alias_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Bioentity, Complex
    from src.sgd.model.bud.feature import AliasFeature
    from src.sgd.model.bud.general import DbxrefFeat

    def bioentity_alias_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        bioentity_ids = set([x.id for x in nex_session.query(Bioentity.id).all()])

        for bud_obj in bud_session.query(AliasFeature).options(joinedload('alias')).all():
            bioentity_id = bud_obj.feature_id
            if bioentity_id in bioentity_ids:
                yield {'display_name': bud_obj.alias_name,
                       'source': key_to_source['SGD'],
                       'category': bud_obj.alias_type,
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
                    link = bud_obj.dbxref.urls[0].url.replace('_SUBSTITUTE_THIS_', display_name)

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

        for complex in nex_session.query(Complex).all():
            for alias in complex.go.aliases:
                yield {'display_name': alias.display_name,
                       'source': alias.source,
                       'category': 'SGDID',
                       'bioentity_id': complex.id,
                       'is_external_id': 1}
        bud_session.close()
        nex_session.close()
    return bioentity_alias_starter

# --------------------- Convert Relation ---------------------
def make_bioentity_relation_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Complex

    def bioentity_relation_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        go_id_to_complex = dict([(x.go_id, x) for x in nex_session.query(Complex).all()])

        for complex in nex_session.query(Complex).all():
            for relation in complex.go.parents:
                if relation.child_id in go_id_to_complex and relation.parent_id in go_id_to_complex:
                    parent = go_id_to_complex[relation.parent_id]
                    child = go_id_to_complex[relation.child_id]
                    yield {'source': key_to_source['SGD'],
                           'relation_type': 'is a',
                           'parent_id': parent.id,
                           'child_id': child.id}

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
