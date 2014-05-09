from sqlalchemy.orm import joinedload

from src.sgd.convert import break_up_file
from src.sgd.convert.transformers import make_db_starter, make_file_starter

__author__ = 'kpaskov'

# --------------------- Convert Locus ---------------------
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
        for bud_obj in make_db_starter(bud_session.query(Feature).options(joinedload('annotation')), 1000)():
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
def make_complex_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioconcept import Go

    def complex_starter():
        bud_session = bud_session_maker()
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

        bud_session.close()
        nex_session.close()
    return complex_starter

# --------------------- Convert Bioentity Tabs ---------------------
def make_bioentity_tab_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Locus

    def bioentity_tab_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        for locus in make_db_starter(nex_session.query(Locus), 1000)():
            show_summary = 1
            show_history = 1
            show_sequence = 1
            show_wiki = 1

            if locus.bioent_status != 'Active':
                yield {'id': locus.id,
                           'summary_tab': show_summary,
                           'sequence_tab': show_sequence,
                           'history_tab': show_history,
                           'literature_tab': 0,
                           'go_tab': 0,
                           'phenotype_tab': 0,
                           'interaction_tab': 0,
                           'expression_tab': 0,
                           'regulation_tab': 0,
                           'protein_tab': 0,
                           'wiki_tab': show_wiki}

            show_literature = 1

            no_go = {'ARS', 'ARS_CONSENSUS_SEQUENCE', 'MATING_LOCUS', 'X_ELEMENT_COMBINATORIAL_REPEATS',
                     'X_ELEMENT_CORE_SEQUENCE', "Y'_ELEMENT", 'CENTROMERE', 'LONG_TERMINAL_REPEAT',
                     'TELOMERE', 'TELOMERIC_REPEAT', 'RETROTRANSPOSON', 'GENE_CASSETTE', 'MULTIGENE_LOCUS'}
            show_go = 0 if locus.locus_type in no_go else 1

            no_phenotype = {'ARS', 'ARS_CONSENSUS_SEQUENCE', 'MATING_LOCUS', 'X_ELEMENT_COMBINATORIAL_REPEATS',
                     'X_ELEMENT_CORE_SEQUENCE', "Y'_ELEMENT", 'CENTROMERE', 'LONG_TERMINAL_REPEAT',
                     'TELOMERE', 'TELOMERIC_REPEAT', 'RETROTRANSPOSON', 'GENE_CASSETTE'}
            show_phenotype = 0 if locus.locus_type in no_phenotype else 1

            no_interactions = {'ARS', 'ARS_CONSENSUS_SEQUENCE', 'MATING_LOCUS', 'X_ELEMENT_COMBINATORIAL_REPEATS',
                     'X_ELEMENT_CORE_SEQUENCE', "Y'_ELEMENT", 'CENTROMERE', 'LONG_TERMINAL_REPEAT',
                     'TELOMERE', 'TELOMERIC_REPEAT', 'RETROTRANSPOSON', 'GENE_CASSETTE', 'MULTIGENE_LOCUS',
                     'NOT_IN_SYSTEMATIC_SEQUENCE_OF_S288C', 'NOT_PHYSICALLY_MAPPED'}
            show_interactions = 0 if locus.locus_type in no_interactions else 1

            no_expression = {'ARS', 'ARS_CONSENSUS_SEQUENCE', 'MATING_LOCUS', 'X_ELEMENT_COMBINATORIAL_REPEATS',
                     'X_ELEMENT_CORE_SEQUENCE', "Y'_ELEMENT", 'CENTROMERE', 'LONG_TERMINAL_REPEAT',
                     'TELOMERE', 'TELOMERIC_REPEAT', 'RETROTRANSPOSON', 'GENE_CASSETTE', 'MULTIGENE_LOCUS',
                     'NOT_IN_SYSTEMATIC_SEQUENCE_OF_S288C', 'NOT_PHYSICALLY_MAPPED', 'TRANSPOSABLE_ELEMENT_GENE',
                     'PSEUDOGENE', 'NCRNA', 'SNORNA', 'TRNA', 'RRNA', 'SNRNA'}
            show_expression = 0 if locus.locus_type in no_expression else 1

            no_regulation = {'ARS', 'ARS_CONSENSUS_SEQUENCE', 'MATING_LOCUS', 'X_ELEMENT_COMBINATORIAL_REPEATS',
                     'X_ELEMENT_CORE_SEQUENCE', "Y'_ELEMENT", 'CENTROMERE', 'LONG_TERMINAL_REPEAT',
                     'TELOMERE', 'TELOMERIC_REPEAT', 'RETROTRANSPOSON', 'GENE_CASSETTE', 'MULTIGENE_LOCUS',
                     'NOT_IN_SYSTEMATIC_SEQUENCE_OF_S288C', 'NOT_PHYSICALLY_MAPPED'}
            show_regulation = 0 if locus.locus_type in no_regulation else 1

            no_protein = {'ARS', 'ARS_CONSENSUS_SEQUENCE', 'MATING_LOCUS', 'X_ELEMENT_COMBINATORIAL_REPEATS',
                     'X_ELEMENT_CORE_SEQUENCE', "Y'_ELEMENT", 'CENTROMERE', 'LONG_TERMINAL_REPEAT',
                     'TELOMERE', 'TELOMERIC_REPEAT', 'RETROTRANSPOSON', 'GENE_CASSETTE', 'MULTIGENE_LOCUS',
                     'NOT_IN_SYSTEMATIC_SEQUENCE_OF_S288C', 'NOT_PHYSICALLY_MAPPED',
                     'NCRNA', 'SNORNA', 'TRNA', 'RRNA', 'SNRNA'}
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

        for bud_obj in make_db_starter(bud_session.query(AliasFeature).options(joinedload('alias')), 1000)():
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
                print 'Bioentity not found: ' + str(bioentity_id)
                yield None

        for bud_obj in make_db_starter(bud_session.query(DbxrefFeat).options(joinedload('dbxref'), joinedload('dbxref.dbxref_urls')), 1000)():
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
                print 'Bioentity not found: ' + str(bioentity_id)
                yield None

        for complex in make_db_starter(nex_session.query(Complex), 1000)():
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

        for complex in make_db_starter(nex_session.query(Complex), 1000)():
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
def make_bioentity_url_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex import create_format_name
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Bioentity
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

                    yield {'display_name': old_webdisplay.label_name,
                           'link': link,
                           'source': key_to_source[create_format_name(old_url.source)],
                           'category': old_webdisplay.label_location,
                           'bioentity_id': bioentity_id,
                           'date_created': old_url.date_created,
                           'created_by': old_url.created_by}
                else:
                    print 'Bioentity not found: ' + str(bioentity_id)
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

                        yield {'display_name': old_webdisplay.label_name,
                                   'link': link,
                                   'source': key_to_source[create_format_name(old_url.source)],
                                   'category': old_webdisplay.label_location,
                                   'bioentity_id': bioentity_id,
                                   'date_created': old_url.date_created,
                                   'created_by': old_url.created_by}
                    else:
                        print 'Bioentity not found: ' + str(bioentity_id)
                        yield None

        bud_session.close()
        nex_session.close()
    return bioentity_url_starter
