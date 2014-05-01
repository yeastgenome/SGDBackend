import logging
import sys

from src.sgd.convert.transformers import make_db_starter, make_file_starter


__author__ = 'kpaskov'

# --------------------- Convert Paragraph ---------------------
def make_paragraph_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.go import GoFeature
    def paragraph_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in nex_session.query(Locus).all()])

        #Go
        for gofeature in make_db_starter(bud_session.query(GoFeature), 1000)():
            bioentity_key = (gofeature.feature.name, 'LOCUS')
            source_key = gofeature.source

            if bioentity_key in key_to_bioentity and source_key in key_to_source:
                yield {
                    'bioentity': key_to_bioentity[bioentity_key],
                    'source': key_to_source[source_key],
                    'text': str(gofeature.date_last_reviewed),
                    'date_created': gofeature.date_created,
                    'created_by': gofeature.created_by,
                    'class_type': 'GO'
                }
            else:
                print 'Bioentity or source not found: ' + str(bioentity_key) + ' ' + str(source_key)
                yield None

        #Regulation
        for row in make_file_starter('src/sgd/convert/data/RegulationSummaries04102014.txt')():
            bioentity_key = (row[0], 'LOCUS')

            if bioentity_key in key_to_bioentity:
                yield {
                    'bioentity': key_to_bioentity[bioentity_key],
                    'source': key_to_source['SGD'],
                    'text': row[2],
                    'class_type': 'REGULATION'
                }
            else:
                print 'Bioentity not found: ' + str(bioentity_key)
                yield None

        bud_session.close()
        nex_session.close()
    return paragraph_starter

# --------------------- Convert ParagraphReference ---------------------
def make_paragraph_reference_starter(nex_session_maker):
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.paragraph import Paragraph
    from src.sgd.model.nex.reference import Reference
    def paragraph_reference_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in nex_session.query(Locus).all()])
        key_to_paragraph = dict([(x.unique_key(), x) for x in nex_session.query(Paragraph).all()])
        pubmed_id_to_reference = dict([(x.pubmed_id, x) for x in nex_session.query(Reference).all()])

        #Regulation
        for row in make_file_starter('src/sgd/convert/data/RegulationSummaries04102014.txt')():
            bioentity_key = (row[0], 'LOCUS')
            paragraph_key = (row[0], 'REGULATION')
            for pubmed_id in [int(x) for x in row[3].strip().split('|') if x != 'references' and x != '']:
                if bioentity_key in key_to_bioentity and paragraph_key in key_to_paragraph and pubmed_id in pubmed_id_to_reference:
                    yield {
                        'bioentity': key_to_bioentity[bioentity_key],
                        'source': key_to_source['SGD'],
                        'paragraph': key_to_paragraph[paragraph_key],
                        'reference': pubmed_id_to_reference[pubmed_id],
                        'class_type': 'REGULATION'
                    }
                else:
                    print 'Bioentity or paragraph or reference not found: ' + str(bioentity_key) + ' ' + str(paragraph_key) + ' ' + str(pubmed_id)
                    yield None

        nex_session.close()
    return paragraph_reference_starter
