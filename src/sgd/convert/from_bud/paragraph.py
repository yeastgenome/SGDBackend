import logging
import sys

from src.sgd.convert.transformers import make_db_starter, make_file_starter


__author__ = 'kpaskov'

strain_paragraphs = {'S288C': ('S288C is a widely used laboratory strain, designed by Robert Mortimer for biochemical studies, and specifically selected to be non-flocculent with a minimal set of nutritional requirements.  S288C is the strain used in the systematic sequencing project, the reference sequence stored in SGD. S288C does not form pseudohyphae. In addition, since it has a mutated copy of HAP1, it is not a good strain for mitochondrial studies. It has an allelic variant of MIP1 which increases petite frequency. S288C is gal2- and does not use galactose anaerobically.', [3519363]),
              'YJM789': ('YJM789 is the haploid form of an opportunistic pathogen derived from a yeast isolated from the lung of an immunocompromised patient in 1989. YJM789 has a reciprocal translocation relative to S288C and AWRI1631, between chromosomes VI and X, as well as a large inversion in chromosome XIV. YJM789 is useful for infection studies and quantitative genetics owing to its divergent phenotype, which includes flocculence, heat tolerance, and deadly virulence.', [2671026, 17652520, 18778279]),
              'M22': ('M22 was collected in an Italian vineyard.  It has a reciprocal translocation between chromosomes VIII and XVI relative to S288C. This translocation is common in vineyard and wine yeast strains, leads to increased sulfite resistance.', [18769710, 12368245]),
              'YPS163': ('YPS163 was isolated in 1999 from the soil beneath an oak tree (Quercus rubra) in a Pennsylvania woodland.  YPS163 is freeze tolerant, a phenotype associated with its increased expression of aquaporin AQY2.', [12702333, 15059259]),
              'AWRI1631': ('AWRI1631 is Australian wine yeast, a robust fermenter and haploid derivative of South African commercial wine strain N96.', [18778279]),
              'JAY291': ('JAY291 is a non-flocculent haploid derivative of Brazilian industrial bioethanol strain PE-2; it produces high levels of ethanol and cell mass, and is tolerant to heat and oxidative stress. JAY291 is highly divergent to S288C, RM11-1a and YJM789, and contains well-characterized alleles at several genes of known relation to thermotolerance and fermentation performance.', [19812109]),
              'EC1118': ('EC1118, a diploid commercial yeast, is probably the most widely used wine-making strain worldwide based on volume produced. In the Northern hemisphere, it is also known as Premier Cuvee or Prise de Mousse; it is a reliably aggressive fermenter, and makes clean but somewhat uninteresting wines. EC1118 is more diverged from S288C and YJM789 than from RM11-1a and AWRI1631.  EC1118 has three unique regions from 17 to 65 kb in size on chromosomes VI, XIV and XV, encompassing 34 genes related to key fermentation characteristics, such as metabolism and transport of sugar or nitrogen. There are >100 genes present in S288C that are missing from EC1118.', [19805302])
}

# --------------------- Convert Paragraph ---------------------
def make_paragraph_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.bud.go import GoFeature
    def paragraph_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in nex_session.query(Locus).all()])

        #Strain
        for strain_key, paragraph in strain_paragraphs.iteritems():
            if strain_key in key_to_strain:
                yield {
                    'source': key_to_source['SGD'],
                    'text': paragraph[0],
                    'class_type': 'STRAIN',
                    'format_name': strain_key,
                    'display_name': strain_key
                }
            else:
                print 'Strain not found: ' + str(strain_key)
                yield None

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
