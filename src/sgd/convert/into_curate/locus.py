from src.sgd.convert.into_curate import basic_convert, remove_nones
from collections import OrderedDict
from sqlalchemy.orm import joinedload

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
    'Protein databases/Other': 'LOCUS_PROTEIN_PROTEIN_DATABASES',
    'Localization Resources': 'LOCUS_PROEIN_LOCALIZATION',
    'Post-translational modifications': 'LOCUS_PROTEIN_MODIFICATIONS',
    'Analyze Sequence S288C only': 'LOCUS_SEQUENCE_S288C',
    'Analyze Sequence S288C vs. other species': 'LOCUS_SEQUENCE_OTHER_SPECIES',
    'Analyze Sequence S288C vs. other strains': 'LOCUS_SEQUENCE_OTHER_STRAINS',
    'Resources External Links': 'LOCUS_LSP'
}

url_type_mapping = {
    'Unknown': 'CGI',
    'query by ID assigned by database': 'External identifier',
    'query by SGD ORF name': 'Systematic name',
    'query by SGD ORF name with anchor': 'Systematic name',
    'query by SGDID': 'SGDID'
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
                {'name': old_webdisplay.label_name,
                 'source': {'name': old_url.source},
                 'bud_id': old_url.id,
                 'url_type': url_type_mapping[url_type],
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
                    {'name': old_webdisplay.label_name,
                     'source': {'name': old_url.source},
                     'bud_id': old_url.id,
                     'link': link,
                     'url_type': url_type_mapping[url_type],
                     'placement': old_webdisplay.label_location if old_webdisplay.label_location not in url_placement_mapping else url_placement_mapping[old_webdisplay.label_location],
                     'date_created': str(old_url.date_created),
                     'created_by': old_url.created_by})

    urls.append(
        {'name': 'SPELL',
         'source': {'name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': 'http://spell.yeastgenome.org/search/show_results?search_string=' + bud_locus.name,
         'url_type': 'CGI',
         'placement': 'LOCUS_EXPRESSION'})

    urls.append(
        {'name': 'Gene/Sequence Resources',
         'source': {'name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/cgi-bin/seqTools?back=1&seqname=' + bud_locus.name,
         'url_type': 'CGI',
         'placement': 'LOCUS_SEQUENCE'})

    urls.append(
        {'name': 'ORF Map',
         'source': {'name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/cgi-bin/ORFMAP/ORFmap?dbid=' + bud_locus.dbxref_id,
         'url_type': 'CGI',
         'placement': 'LOCUS_SEQUENCE'})

    urls.append(
        {'name': 'GBrowse',
         'source': {'name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': 'http://browse.yeastgenome.org/fgb2/gbrowse/scgenome/?name=' + bud_locus.name,
         'url_type': 'CGI',
         'placement': 'LOCUS_SEQUENCE'})

    urls.append(
        {'name': 'BLASTN',
         'source': {'name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/cgi-bin/blast-sgd.pl?name=' + bud_locus.name,
         'url_type': 'CGI',
         'placement': 'LOCUS_SEQUENCE_SECTION'})

    urls.append(
        {'name': 'BLASTP',
         'source': {'name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/cgi-bin/blast-sgd.pl?name=' + bud_locus.name + '&suffix=prot',
         'url_type': 'CGI',
         'placement': 'LOCUS_SEQUENCE_SECTION'})

    urls.append(
        {'name': 'Yeast Phenotype Ontology',
         'source': {'name': 'SGD'},
         'bud_id': bud_locus.id,
         'link': '/ontology/phenotype/ypo/overview',
         'url_type': 'CGI',
         'placement': 'LOCUS_PHENOTYPE_ONTOLOGY'})

    make_unique = dict([((x['name'], x['placement'], x['url_type']), x) for x in urls])
    return make_unique.values()


def load_aliases(bud_locus, bud_session, uniprot_id):
    from src.sgd.model.bud.feature import AliasFeature
    from src.sgd.model.bud.general import DbxrefFeat

    aliases = []
    for bud_obj in bud_session.query(AliasFeature).options(joinedload('alias')).filter_by(feature_id=bud_locus.id).all():
        #if bud_obj.alias_type in {'Uniform', 'Non-uniform', 'NCBI protein name', 'Retired name'}:
        aliases.append({
            'name': bud_obj.alias_name,
            'source': {'name': 'SGD'},
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
            {'name': display_name,
             'link': link,
             'source': {'name': bud_obj.dbxref.source},
             'alias_type': bud_obj.dbxref.dbxref_type,
             'bud_id': bud_obj.id,
             'date_created': str(bud_obj.dbxref.date_created),
             'created_by': bud_obj.dbxref.created_by}))

    if uniprot_id is not None:
        aliases.append(
            {'name': uniprot_id,
             'source': {'name': 'Uniprot'},
             'alias_type': 'Uniprot ID'})

    make_unique = dict([((x['name'], x['alias_type']), x) for x in aliases])
    return make_unique.values()

def load_relations(bud_feature, bud_session):
    from src.sgd.model.bud.feature import FeatRel

    relations = []
    for bud_obj in bud_session.query(FeatRel).filter_by(relationship_type='pair').filter_by(parent_id=bud_feature.id).all():
        relations.append(remove_nones({
            "systematic_name": bud_obj.parent.name,
            "relation_type": bud_obj.relationship_type,
            "date_created": str(bud_obj.date_created),
            "created_by": bud_obj.created_by
        }))
    return relations


def load_documents(bud_feature, bud_session):
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
             'source': {'name': 'SGD'},
             'bud_id': paragraph.id,
             'document_type': 'Paragraph',
             'document_order': paragraph_feat.order,
             'references': references,
             'date_created': str(paragraph.date_created),
             'created_by': paragraph.created_by})
    return documents


def locus_starter(bud_session_maker):
    from src.sgd.model.bud.feature import Feature

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

    #Create features
    for bud_obj in bud_session.query(Feature).options(joinedload('annotation')).all():
        if bud_obj.type not in non_locus_feature_types:
            sgdid = bud_obj.dbxref_id
            systematic_name = bud_obj.name
            obj_json = {'gene_name': bud_obj.gene_name,
                        'systematic_name': systematic_name,
                        'source': {
                            'name': bud_obj.source
                        },
                        'bud_id': bud_obj.id,
                        'sgdid': sgdid,
                        'dbentity_status': bud_obj.status,
                        'locus_type': bud_obj.type,
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
            obj_json['children'] = load_relations(bud_obj, bud_session)

            #Load documents
            obj_json['documents'] = load_documents(bud_obj, bud_session)
            if sgdid in sgdid_to_go_paragraph:
                obj_json['documents'].append(sgdid_to_go_paragraph[sgdid])
            if systematic_name in systematic_name_to_reg_paragraph:
                obj_json['documents'].append(systematic_name_to_reg_paragraph[systematic_name])

            yield obj_json

    bud_session.close()


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
                                                 'source': {'name': 'SGD'},
                                                 'document_type': 'Go'}
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
                                                         'source': {'name': 'SGD'},
                                                         'document_type': 'Regulation',
                                                         'references': references
                                                        }

    f.close()
    return systematic_name_to_paragraph


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
                    references.append({'sgdid': sgdid, 'reference_order': len(references)+1})
                    sgdids.add(sgdid)

    return new_omim_text, text, references


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, locus_starter, 'locus', lambda x: x['sgdid'])

if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')