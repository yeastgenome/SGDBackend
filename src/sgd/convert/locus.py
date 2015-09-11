from src.sgd.convert import basic_convert, remove_nones
from collections import OrderedDict
from sqlalchemy.orm import joinedload
from src.sgd.convert.util import get_relation_to_ro_id

__author__ = 'kpaskov, sweng66'

def load_urls(bud_locus, bud_session):
    from src.sgd.model.bud.general import FeatUrl, DbxrefFeat

    url_placement_mapping = url_placement()
    
    url_source_mapping = { 'Author': 'Publication',
                           'Colleague submission': 'Direct submission',
                           'DNASU Plasmid Repository': 'DNASU',
                           'HIP HOP profile database (Novartis)': 'HIP HOP profile database',
                           'HIPHOP chemogenomics database (UBC)': 'HIPHOP chemogenomics database',
                           'LoQate': 'LoQAtE',
                           'MRC': 'SUPERFAMILY',
                           'PlasmID Database': 'PlasmID',
                           'Publisher': 'Publication',
                           'Yeast Genetic Resource Center': 'YGRC',
                           'Yeast Microarray Global Viewer': 'yMGV',
                           'yeast snoRNA database at UMass Amherst': 'Yeast snoRNA database'}

    urls = []

    for bud_obj in bud_session.query(FeatUrl).options(joinedload('url')).filter_by(feature_id=bud_locus.id).all():
        old_url = bud_obj.url
        url_type = old_url.url_type
        link = old_url.url

        type = ''
        for old_webdisplay in old_url.displays:
            if url_type == 'query by SGDID':
                type = 'SGDID'
                link = link.replace('_SUBSTITUTE_THIS_', bud_locus.dbxref_id)
            elif url_type == 'query by SGD ORF name with anchor' or url_type == 'query by SGD ORF name' or url_type == 'query by ID assigned by database':
                link = link.replace('_SUBSTITUTE_THIS_', bud_locus.name)
                type = 'Systematic name'
            else:
                print "Can't handle this url. " + str(old_url.url_type)
                continue

            source = old_url.source
            if source in url_source_mapping:
                source = url_source_mapping.get(source)

            urls.append(
                {'display_name': old_webdisplay.label_name,
                 'source': {'display_name': source},
                 'bud_id': old_url.id,
                 'url_type': type,
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

                type = ''

                if url_type == 'query by SGD ORF name with anchor' or url_type == 'query by SGD ORF name':
                    link = link.replace('_SUBSTITUTE_THIS_', bud_locus.name)
                    type = 'Systematic name'
                elif url_type == 'query by ID assigned by database':
                    link = link.replace('_SUBSTITUTE_THIS_', str(dbxref_id))
                    type = 'External id'
                elif url_type == 'query by SGDID':
                    link = link.replace('_SUBSTITUTE_THIS_', bud_locus.dbxref_id)
                    type = 'SGDID'
                else:
                    print "Can't handle this url. " + str(old_url.url_type)
                    continue

                source = old_url.source
                if source in url_source_mapping:
                    source = url_source_mapping.get(source)

                urls.append(
                    {'display_name': old_webdisplay.label_name,
                     'source': {'display_name': source},
                     'bud_id': old_url.id,
                     'link': link,
                     'url_type': type,
                     'placement': old_webdisplay.label_location if old_webdisplay.label_location not in url_placement_mapping else url_placement_mapping[old_webdisplay.label_location],
                     'date_created': str(old_url.date_created),
                     'created_by': old_url.created_by})

    urls.append(
        {'display_name': 'SPELL',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': 'http://spell.yeastgenome.org/search/show_results?search_string=' + bud_locus.name,
         'url_type': 'Systematic name',
         'placement': 'LOCUS_EXPRESSION'})

    urls.append(
        {'display_name': 'Gene/Sequence Resources',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/cgi-bin/seqTools?back=1&seqname=' + bud_locus.name,
         'url_type': 'Systematic name',
         'placement': 'LOCUS_SEQUENCE'})

    urls.append(
        {'display_name': 'ORF Map',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/cgi-bin/ORFMAP/ORFmap?dbid=' + bud_locus.dbxref_id,
         'url_type': 'SGDID',
         'placement': 'LOCUS_SEQUENCE'})

    urls.append(
        {'display_name': 'GBrowse',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': 'http://browse.yeastgenome.org/fgb2/gbrowse/scgenome/?name=' + bud_locus.name,
         'url_type': 'Systematic name',
         'placement': 'LOCUS_SEQUENCE'})

    urls.append(
        {'display_name': 'BLASTN',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/blast-sgd?name=' + bud_locus.name,
         'url_type': 'Systematic name',
         'placement': 'LOCUS_SEQUENCE_SECTION'})

    urls.append(
        {'display_name': 'BLASTP',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/blast-sgd?name=' + bud_locus.name + '&suffix=prot',
         'url_type': 'Systematic name',
         'placement': 'LOCUS_SEQUENCE_SECTION'})

    urls.append(
        {'display_name': 'Yeast Phenotype Ontology',
         'source': {'display_name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/ontology/phenotype/ypo/overview',
         'url_type': 'Internal web service',
         'placement': 'LOCUS_PHENOTYPE_ONTOLOGY'})

    make_unique = dict([((x['display_name'], x['placement'], x['link']), x) for x in urls])
    return make_unique.values()


def load_aliases(bud_locus, bud_session, uniprot_id):
    from src.sgd.model.bud.feature import AliasFeature
    from src.sgd.model.bud.general import DbxrefFeat

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

    found_uniprot = {}
    for bud_obj in bud_session.query(DbxrefFeat).options(joinedload('dbxref'), joinedload('dbxref.dbxref_urls')).filter_by(feature_id=bud_locus.id).all():
        alias_type = bud_obj.dbxref.dbxref_type
        if alias_type == 'DBID Primary':
            continue
        if alias_type == 'DBID Secondary':
            alias_type = 'SGDID Secondary'
        if alias_type.startswith('UniProt'):
            alias_type = 'UniProtKB ID'
        display_name = bud_obj.dbxref.dbxref_id

        if alias_type.startswith('UniProt/Swiss'):
            found_uniprot[display_name] = 1

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
             'alias_type': alias_type,
             'bud_id': bud_obj.id,
             'date_created': str(bud_obj.dbxref.date_created),
             'created_by': bud_obj.dbxref.created_by}))

    if uniprot_id is not None and uniprot_id not in found_uniprot:
        aliases.append({'display_name': uniprot_id,
                        'source': {'display_name': 'Uniprot'},
                        'alias_type': 'Uniprot ID/Swiss-Prot ID'})

    return aliases

def load_relations(bud_feature, bud_session):
    from src.sgd.model.bud.feature import FeatRel

    relations = []
    for bud_obj in bud_session.query(FeatRel).filter_by(parent_id=bud_feature.id).all():
        if bud_obj.relationship_type == 'pair':
            continue
        relations.append(remove_nones({
            "systematic_name": bud_obj.parent.name,
            "source": { "display_name": bud_obj.parent.source},
            "bud_id": bud_obj.id,
            "ro_id": get_relation_to_ro_id(bud_obj.relationship_type.replace('_', ' ')),
            "date_created": str(bud_obj.date_created),
            "created_by": bud_obj.created_by
        }))
    return relations


def load_summaries(bud_feature, bud_session):
    from src.sgd.model.bud.general import ParagraphFeat

    documents = []

    #LSP
    paragraph_feats = bud_session.query(ParagraphFeat).filter_by(feature_id=bud_feature.id).all()
    for paragraph_feat in paragraph_feats:
        paragraph = paragraph_feat.paragraph
        paragraph_html, paragraph_text, references = clean_paragraph(paragraph.text)

        documents.append(
            {'text': paragraph_text,
             'html': paragraph_html,
             'source': {'display_name': 'SGD'},
             'bud_id': paragraph.id,
             'summary_type': 'Gene',
             'summary_order': paragraph_feat.order,
             'references': references,
             'date_created': str(paragraph.date_created),
             'created_by': paragraph.created_by})

    return documents


def locus_starter(bud_session_maker):
    from src.sgd.model.bud.feature import Feature
    from src.sgd.model.nex.so import So

    bud_session = bud_session_maker()

    #Load uniprot ids
    sgdid_to_uniprotid = {}
    f = open('src/sgd/convert/data/YEAST_559292_idmapping.dat', 'r')
    for line in f:
        pieces = line.split('\t')
        if pieces[1].strip() == 'SGD':
            sgdid_to_uniprotid[pieces[2].strip()] = pieces[0].strip()
    f.close()

    #Load paragraphs
    sgdid_to_go_paragraph = load_go_paragraphs()
    systematic_name_to_reg_paragraph = load_reg_paragraphs()

    nex_session = get_nex_session() 
    term_to_so = dict([(x.display_name, x) for x in nex_session.query(So).all()])

    #Create features
    for bud_obj in bud_session.query(Feature).options(joinedload('annotation')).all():
        # if bud_obj.type not in non_locus_feature_types:
        sgdid = bud_obj.dbxref_id
        systematic_name = bud_obj.name
        feature_type = bud_obj.type
        if feature_type.startswith('not in'):
            feature_type = 'ORF'
        if feature_type.startswith('TF') or feature_type.startswith('not physically'):
            continue

        obj_json = {'gene_name': bud_obj.gene_name,
                    'systematic_name': systematic_name,
                    'source': {
                        'display_name': bud_obj.source
                    },
                    'bud_id': bud_obj.id,
                    'sgdid': sgdid,
                    'dbentity_status': bud_obj.status,
                    'so_id': term_to_so[feature_type].id,
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

        #Load children
        # obj_json['children'] = load_relations(bud_obj, bud_session)
        obj_json['children'] = []

        #Load various summaries
        # obj_json['summaries'] = load_summaries(bud_obj, bud_session)
        # if sgdid in sgdid_to_go_paragraph:
        #    obj_json['summaries'].append(sgdid_to_go_paragraph[sgdid])
        # if systematic_name in systematic_name_to_reg_paragraph:
        #    obj_json['summaries'].append(systematic_name_to_reg_paragraph[systematic_name])
        obj_json['summaries'] = []
        
        obj_json['tabs'] = get_tabs(bud_obj.status, feature_type) 

        print obj_json['systematic_name']

        yield obj_json

    bud_session.close()


def url_placement():

    return {'Mutant Strains': 'LOCUS_PHENOTYPE_MUTANT_STRAINS',
            'Phenotype Resources': 'LOCUS_PHENOTYPE_PHENOTYPE_RESOURCES',
            'Interaction Resources': 'LOCUS_INTERACTION',
            'Expression Resources': 'LOCUS_EXPRESSION',
            'Regulatory Role Resources': 'LOCUS_REGULATION',
            'Protein Information Homologs': 'LOCUS_PROTEIN_HOMOLOGS',
            'Protein databases/Other': 'LOCUS_PROTEIN_PROTEIN_DATABASES',
            'Localization Resources': 'LOCUS_PROEIN_LOCALIZATION',
            'Post-translational modifications': 'LOCUS_PROTEIN_MODIFICATIONS',
            'Analyze Sequence S288C only': 'LOCUS_SEQUENCE_S288C',
            'Analyze Sequence S288C vs. other species': 'LOCUS_SEQUENCE_OTHER_SPECIES',
            'Analyze Sequence S288C vs. other strains': 'LOCUS_SEQUENCE_OTHER_STRAINS',
            'Resources External Links': 'LOCUS_LSP'}


def load_go_paragraphs():
    sgdid_to_paragraph = dict()
    f = open('src/sgd/convert/data/gp_information.559292_sgd', 'U')
    for line in f:
        pieces = line.split('\t')
        if len(pieces) >= 8:
            sgdid = pieces[8]
            if sgdid.startswith('SGD:'):
                sgdid = sgdid[4:]
                go_annotation = [x[22:].strip() for x in pieces[9].split('|') if x.startswith('go_annotation_summary')]
                if len(go_annotation) == 1:
                    sgdid_to_paragraph[sgdid] = {'text': go_annotation[0],
                                                 'html': go_annotation[0],
                                                 'source': {'display_name': 'SGD'},
                                                 'summary_type': 'Go'}
    f.close()
    return sgdid_to_paragraph


def load_reg_paragraphs():
    systematic_name_to_paragraph = dict()
    f = open('src/sgd/convert/data/regulationSummaries', 'U')
    for line in f:
        pieces = line.split('\t')
        systematic_name = pieces[0]

        references = list(OrderedDict.fromkeys([int(x) for x in pieces[3].strip().split('|') if x != 'references' and x != '']))
        references = [{'pubmed_id': x, 'reference_order': i+1} for i, x in enumerate(references)]

        systematic_name_to_paragraph[systematic_name] = {'text': pieces[2],
                                                         'html': pieces[2],
                                                         'source': {'display_name': 'SGD'},
                                                         'summary_type': 'Regulation',
                                                         'references': references}

    f.close()
    return systematic_name_to_paragraph

def get_tabs(status, feature_type):

    if status == 'Merged' or status == 'Deleted':
        return {
            'has_summary': 1,
            'has_sequence': 0,
            'has_sequence_section': 1,
            'has_history': 0,
            'has_literature': 0,
            'has_go': 0,
            'has_phenotype': 0,
            'has_interaction': 0,
            'has_expression': 0,
            'has_regulation': 0,
            'has_protein': 0,
        }
    elif feature_type == 'ORF' or feature_type == 'blocked_reading_frame':
        return {
            'has_summary': 1,
            'has_sequence': 1,
            'has_sequence_section': 1,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 1,
            'has_phenotype': 1,
            'has_interaction': 1,
            'has_expression': 1,
            'has_regulation': 1,
            'has_protein': 1,
        }
    elif feature_type in {'ARS', 'origin_of_replication', 'matrix_attachment_site', 'centromere',
                          'gene_group', 'long_terminal_repeat', 'telomere', 
                          'mating_type_region', 'silent_mating_type_cassette_array', 
                          'LTR_retrotransposon'}:
        return {
            'has_summary': 1,
            'has_sequence': 1,
            'has_sequence_section': 1,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 0,
            'has_phenotype': 0,
            'has_interaction': 0,
            'has_expression': 0,
            'has_regulation': 0,
            'has_protein': 0,
        }
    elif feature_type == 'transposable_element_gene':
        return {
            'has_summary': 1,
            'has_sequence': 1,
            'has_sequence_section': 1,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 1,
            'has_phenotype': 1,
            'has_interaction': 1,
            'has_expression': 0,
            'has_regulation': 0,
            'has_protein': 1,
        }
    elif feature_type == 'pseudogene':
        return {
            'has_summary': 1,
            'has_sequence': 1,
            'has_sequence_section': 1,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 1,
            'has_phenotype': 1,
            'has_interaction': 1,
            'has_expression': 0,
            'has_regulation': 1,
            'has_protein': 1,
        }
    elif feature_type in {'rRNA_gene', 'ncRNA_gene', 'snRNA_gene', 'snoRNA_gene', 'tRNA_gene', 'telomerase_RNA_gene'}:
        return {
            'has_summary': 1,
            'has_sequence': 1,
            'has_sequence_section': 1,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 1,
            'has_phenotype': 1,
            'has_interaction': 1,
            'has_expression': 0,
            'has_regulation': 1,
            'has_protein': 0,
        }
    elif feature_type in {'not in systematic sequence of S288C', 'not physically mapped'}:
        return {
            'has_summary': 1,
            'has_sequence': 0,
            'has_sequence_section': 0,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 1,
            'has_phenotype': 1,
            'has_interaction': 1,
            'has_expression': 0,
            'has_regulation': 0,
            'has_protein': 0,
        }
    elif feature_type in {'intein_encoding_region'}:
        return {
            'has_summary': 1,
            'has_sequence': 0,
            'has_sequence_section': 0,
            'has_history': 0,
            'has_literature': 1,
            'has_go': 0,
            'has_phenotype': 0,
            'has_interaction': 0,
            'has_expression': 0,
            'has_regulation': 0,
            'has_protein': 0,
        }
    else:
        # raise Exception('feature_type: ' + feature_type + ' is invalid.')
        return {
            'has_summary': 0,
            'has_sequence': 0,
            'has_sequence_section': 0,
            'has_history': 0,
            'has_literature': 0,
            'has_go': 0,
            'has_phenotype': 0,
            'has_interaction': 0,
            'has_expression': 0,
            'has_regulation': 0,
            'has_protein': 0,
        }


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

def clean_paragraph(text):

    # Replace bioentities
    feature_blocks = text.split('<feature:')
    if len(feature_blocks) > 1:
        new_bioentity_text = feature_blocks[0]
        for block in feature_blocks[1:]:
            end_index = block.find('>')
            final_end_index = block.find('</feature>')
            if final_end_index > end_index >= 0:
                if block[1:end_index].endswith('*'):
                    replacement = '<a href="/cgi-bin/search/luceneQS.fpl?query=' + block[1:end_index] + '">' + block[end_index+1:final_end_index] + '</a>'
                    new_bioentity_text += replacement
                else:
                    sgdid = 'S' + block[1:end_index].zfill(9)
                    new_bioentity_text += '<a href="/locus/' + sgdid + '">' + block[end_index+1:final_end_index] + '</a>'

                new_bioentity_text += block[final_end_index+10:]
            else:
                new_bioentity_text += block
    else:
        new_bioentity_text = text

    # Replace go
    go_blocks = new_bioentity_text.split('<go:')
    if len(go_blocks) > 1:
        new_go_text = go_blocks[0]
        for block in go_blocks[1:]:
            end_index = block.find('>')
            final_end_index = block.find('</go>')
            if final_end_index > end_index >= 0:
                goid = int(block[0:end_index])
                new_go_text += '<a href="/go/' + str(goid) + '">' + block[end_index+1:final_end_index] + '</a>'
                new_go_text += block[final_end_index+5:]
            else:
                new_go_text += block
    else:
        new_go_text = new_bioentity_text

    # Replace MetaCyc
    metacyc_blocks = new_go_text.split('<MetaCyc:')
    if len(metacyc_blocks) > 1:
        new_metacyc_text = metacyc_blocks[0]
        for block in metacyc_blocks[1:]:
            end_index = block.find('>')
            final_end_index = block.find('</MetaCyc>')
            if final_end_index > end_index >= 0:
                replacement = '<a href="http://pathway.yeastgenome.org/YEAST/NEW-IMAGE?type=PATHWAY&object=' + block[0:end_index] + '">' + block[end_index+1:final_end_index] + '</a>'
                new_metacyc_text += replacement
                new_metacyc_text += block[final_end_index+10:]
            else:
                new_metacyc_text += block
    else:
        new_metacyc_text = new_go_text

    # Replace OMIM
    omim_blocks = new_metacyc_text.split('<OMIM:')
    if len(omim_blocks) > 1:
        new_omim_text = omim_blocks[0]
        for block in omim_blocks[1:]:
            end_index = block.find('>')
            final_end_index = block.find('</OMIM>')
            if final_end_index > end_index >= 0:
                replacement = '<a href="http://www.omim.org/entry/' + block[0:end_index] + '">' + block[end_index+1:final_end_index] + '</a>'
                new_omim_text += replacement
                new_omim_text += block[final_end_index+7:]
            else:
                new_omim_text += block
    else:
        new_omim_text = new_metacyc_text

    # Pull references
    references = []
    sgdids = set()
    reference_blocks = new_omim_text.split('<reference:')
    if len(reference_blocks) > 1:
        for block in reference_blocks[1:]:
            end_index = block.find('>')
            if end_index >= 0:
                sgdid = block[0:end_index]
                if sgdid not in sgdids:
                    order = len(references)+1
                    references.append({'sgdid': sgdid, 'reference_order': order})
                    sgdids.add(sgdid)
            
    return new_omim_text, text, references


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, locus_starter, 'locus', lambda x: x['sgdid'])

