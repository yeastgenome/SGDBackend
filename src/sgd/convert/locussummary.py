from src.sgd.convert import basic_convert, remove_nones
from src.sgd.convert.util import link_gene_names
from collections import OrderedDict
from sqlalchemy.orm import joinedload

__author__ = 'sweng66'


def locussummary_starter(bud_session_maker):
    from src.sgd.model.bud.general import ParagraphFeat
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.reference import Reference


    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    # Load gene paragraphs => summary_type = 'Gene'                                                
    
    bud_id_to_dbentity_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])      
                
    paragraph_feats = bud_session.query(ParagraphFeat).all()
    for paragraph_feat in paragraph_feats:
        paragraph = paragraph_feat.paragraph
        paragraph_html, paragraph_text, references = clean_paragraph(paragraph.text)

        yield {'locus_id': bud_id_to_dbentity_id[paragraph_feat.feature_id],
               'text': paragraph_text,
               'html': paragraph_html,
               'source': {'display_name': 'SGD'},
               'bud_id': paragraph.id,
               'summary_type': 'Gene',
               'summary_order': paragraph_feat.order,
               'references': references,
               'date_created': str(paragraph.date_created),
               'created_by': paragraph.created_by}

    # load GO annotation functions => summary_type = 'Function'

    sgdid_to_dbentity_id = dict([(x.sgdid, x.id) for x in nex_session.query(Locus).all()])

    f = open('src/sgd/convert/data/gp_information.559292_sgd', 'U')
    for line in f:
        pieces = line.split('\t')
        if len(pieces) >= 8:
            sgdid = pieces[8]
            if sgdid.startswith('SGD:'):
                sgdid = sgdid[4:]
                go_annotation = [x[22:].strip() for x in pieces[9].split('|') if x.startswith('go_annotation_summary')]
                if len(go_annotation) == 1:
                    yield {'locus_id': sgdid_to_dbentity_id[sgdid],
                           'text': go_annotation[0],
                           'html': go_annotation[0],
                           'source': {'display_name': 'SGD'},
                           'summary_type': 'Function',
                           'summary_order': 1,
                           'created_by': 'OTTO'}
    f.close()

    # load phenotype summaries => summary_type = 'Phenotype'

    name_to_dbentity = dict([(x.systematic_name, x) for x in nex_session.query(Locus).all()])

    files = ['src/sgd/convert/data/PhenotypeSummaries032015.txt',
             'src/sgd/convert/data/15-6phenoSummariesTyposFixed.txt',
             'src/sgd/convert/data/15-7phenoSummaries.txt',
             'src/sgd/convert/data/15-8phenoSummaries.txt',
             'src/sgd/convert/data/15-9phenoSummaries.txt',
             'src/sgd/convert/data/15-10phenoSummaries.txt',
             'src/sgd/convert/data/15-11phenoSummaries.txt',
             'src/sgd/convert/data/15-12phenoSummaries.txt',
             'src/sgd/convert/data/16-1phenoSummaries.txt',
             'src/sgd/convert/data/16-2phenoSummaries.txt',
             'src/sgd/convert/data/16-3phenoSummaries.txt',
             'src/sgd/convert/data/16-4phenoSummaries.txt',
             'src/sgd/convert/data/16-5phenoSummaries.txt',
             'src/sgd/convert/data/16-6phenoSummaries.txt',
             'src/sgd/convert/data/16-7phenoSummaries.txt',
             'src/sgd/convert/data/16-9phenoSummaries.txt']


    for file in files:
        f = open(file, 'U')
        for line in f:
            pieces = line.split('\t')
            dbentity = name_to_dbentity.get(pieces[0])
            if dbentity is None:
                continue
             
            yield {'locus_id': dbentity.id,
                   'text': pieces[1],
                   'html': link_gene_names(pieces[1], {dbentity.display_name, dbentity.format_name, dbentity.display_name + 'P', dbentity.format_name + 'P'}, nex_session), 
                   'source': {'display_name': 'SGD'},
                   'summary_type': 'Phenotype',
                   'summary_order': 1,
                   'created_by': 'OTTO'
            }

    # load regulation paragraphs => summary_type = 'Regulation'

    pmid_to_sgdid = dict([(x.pmid, x.sgdid) for x in nex_session.query(Reference).all()])

    files = ['src/sgd/convert/data/regulationSummaries',
             'src/sgd/convert/data/15-8regulationSummaries.txt',
             'src/sgd/convert/data/15-9regulationSummaries.txt',
             'src/sgd/convert/data/15-10regulationSummaries.txt',
             'src/sgd/convert/data/15-11regulationSummaries.txt',
             'src/sgd/convert/data/16-1regulationSummaries.txt',
             'src/sgd/convert/data/16-2regulationSummaries.txt',
             'src/sgd/convert/data/16-3regulationSummaries.txt',
             'src/sgd/convert/data/16-4regulationSummaries.txt',
             'src/sgd/convert/data/16-5regulationSummaries.txt']

    
    for file in files:
        f = open(file, 'U')
        for line in f:
            pieces = line.split('\t')
            dbentity = name_to_dbentity.get(pieces[0])
            if dbentity is None:
                continue

            references = []
            
            pmid_list = pieces[3].replace(' ', '')
            pmids = pmid_list.split('|')
            order = 0



            print "pmids=", pmids




            for pmid in pmids:
                sgdid = pmid_to_sgdid.get(int(pmid))
                if sgdid is None:
                    print "PMID=", pmid, " is not in the database"
                    continue
                order = order + 1
                references.append({'sgdid': sgdid, 'reference_order': order})


                print "order=", order, ", sgdid=", sgdid




            yield {'locus_id': dbentity.id,
                   'text': pieces[2],
                   'html': link_gene_names(pieces[2], {dbentity.display_name, dbentity.format_name, dbentity.display_name + 'P', dbentity.format_name + 'P'}, nex_session),
                   'source': {'display_name': 'SGD'},
                   'summary_type': 'Regulation',
                   'summary_order': 1,
                   'created_by': 'OTTO',
                   'references': references}

    f.close()

    bud_session.close()


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
                    replacement = '<a href="/search?is_quick=true&q=' + block[1:end_index] + '">' + block[end_index+1:final_end_index] + '</a>'
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
                    references.append({'sgdid': sgdid, 'reference_order': order, 'created_by': 'OTTO'})
                    sgdids.add(sgdid)
            
    return new_omim_text, text, references




if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, locussummary_starter, 'locussummary', lambda x: (x['locus_id'], x['summary_type'], x['summary_order']))

