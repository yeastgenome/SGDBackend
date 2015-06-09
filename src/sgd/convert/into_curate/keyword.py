from src.sgd.convert.into_curate import basic_convert, remove_nones

__author__ = 'kpaskov'

definitions = {
    'amino acid metabolism':        'The cellular reactions and pathways used in the biosynthesis and catabolism of amino acids.',
    'amino acid utilization':       'Utilization of different amino acids, combinations of amino acids, or altered levels of amino acids (e.g. amino acid limitation) during nutritional shifts.',
    'carbon utilization':           'Utilization of different carbon sources, or altered quantities of the same carbon source (e.g. carbon limitation) using nutritional shifts.',
    'cell aging':                   'Progression of a cell from its inception to the end of its lifespan, including replicative aging (number of cell divisions a cell undergoes before dying) and chronological aging (number of days a culture remains viable in stationary phase).',
    'cell cycle regulation':        'Modulation of the rate or extent of progression through the cell cycle.',
    'cell morphogenesis':           'Changes in the size or shape of a cell during vegetative growth, or during developmental processes such as conjugation or filamentation.',
    'cell wall organization':       'The organization and biogenesis of the cell wall from constituent parts and the response to cell wall stress.',
    'cellular ion homeostasis':     'Processes involved in the maintenance of an internal steady state of ions within the cell.',
    'chemical stimulus':            'Changes in the state or activity of yeast cells as a result of a chemical stimulus.',
    'chromatin organization':       'Specification, formation and/or maintenance of the physical structure of eukaryotic chromatin via nucleosomes, including chromatin remodeling.',
    'cofactor metabolism':          'The cellular reactions and pathways used in the biosynthesis and catabolism of cofactors.',
    'diauxic shift':                'The switch from rapid fermentative growth in the presence of a rich carbon source to slower exponential growth by aerobic respiration using ethanol once the preferred carbon source has been exhausted.',
    'DNA damage stimulus':          'Changes in the state or activity of yeast cells as a result of treatment with a DNA damaging stimulus.',
    'evolution':                    'The change over time in inherited trait(s) within a population of cells either in the absence or presence of selective forces.',
    'fermentation':                 'The conversion of carbohydrates to carbon dioxide and alcohol under low oxygen or anaerobic conditions.',
    'filamentous growth':           'A developmental process triggered by nutritional deprivation in which yeast cells grow in a threadlike, filamentous shape, including invasive and pseudohyphal growth.',
    'heat shock':                   'Changes in the state or activity of yeast cells as a result of a temperature stimulus above the optimal temperature.',
    'histone modification':         'Modification of amino acid residue(s) within a histone protein, by reversible processes including methylation, acetylation and ubiquitionation.',
    'lipid metabolism':             'The processes involved in the biosynthesis and degradation of lipids.',
    'mating':                       'The process by which mating pheromone causes yeast cells to form a short conjugation tube and fuse resulting in the union of cellular and genetic information and formation of a zygote.',
    'metal or metalloid ion stress':    'Changes in the state or activity of yeast resulting from the addition or deprivation of a metal ion or metalloid and the impact of mutations on this cellular stressor.',
    'mitotic cell cycle':           'An ordered series of events, grouped by phase (G1, S, G2, and M) where chromosomal DNA is replicated and then segregated into daughter cells.',
    'mRNA processing':              'Processes involved in the conversion of a primary transcript into one or more mature mRNA(s) prior to translation.',
    'nitrogen utilization':         'Utilization of different nitrogen sources, or altered quantities of the same nitrogen source (e.g. nitrogen limitation) using nutritional shifts.',
    'nutrient utilization':         'Alterations in the quality and/or quantity of nutrients during nutritional shifts or nutritional limitation, other than simple alterations in carbon source, nitrogen source, phosphate source, sulfur source, or amino acids.',
    'osmotic stress':               'Changes in the state or activity of yeast as a result of a treatment that increases (hyperosmotic) or decreases (hypoosmotic) the concentration of solutes around a cell.',
    'oxidative stress':             'Changes in the state or activity of yeast cells as a result of exposure to reactive oxygen species, such as hydrogen peroxide (H2O2).',
    'oxygen level alteration':      'Changes in the state or activity of yeast as a result of a stimulus reflecting an increase, decrease or absence of oxygen.',
    'phosphorus utilization':       'Utilization of different phosphate sources, or altered quantities of the same phosphate source (e.g. phosphate limitation) using nutritional shifts.',
    'protein dephosphorylation':    'Removal of phosphate group(s) from target proteins.',
    'protein glycosylation':        'Modification of proteins by the addition or removal of sugar residue(s).',
    'protein phosphorylation':      'The addition of phosphate group(s) to target protein(s).',
    'proteolysis':                  'The hydrolysis of a peptide bond(s) within a protein resulting in the breakdown of that protein.',
    'radiation':                    'Changes in the state or activity of yeast resulting from an electromagnetic radiation stimulus, such as gamma radiation, ionizing radiation and X-rays.',
    'respiration':                  'The process of generating energy through the oxidation of organic compounds with oxygen as the final electron acceptor.',
    'response to unfolded protein':    'Response to treatments such as DTT, tunicamycin, heat or to mutations that activate the unfolded protein response.',
    'RNA catabolism':               'Reactions and pathways that result in the breakdown of RNA.',
    'signaling':                    'Pathways that transmit and amplify molecular signals to activate or inhibit a cellular process or processes.',
    'sporulation':                  'A complex differentiation process induced by starvation that results in the production of stress resistant spores, after DNA replication and two rounds of meiosis.',
    'starvation':                   'Changes in the state or activity of yeast cells as a result of a removal or deprivation of one or more nutrients.',
    'stationary phase entry':       'Entry into a nonproliferative state after yeast cells have exhausted nutrients that is characterized by cell cycle arrest, cell wall thickening, accumulation of reserve carbohydrates, and acquisition of thermotolerance.',
    'stationary phase maintenance':    'Maintenance of a nonproliferative state induced by starvation and characterized by cell cycle arrest, cell wall thickening, accumulation of reserve carbohydrates, and acquisition of thermotolerance.',
    'stress':                       'Changes in the state or activity of yeast as a result of a treatment or mutation that results in stress and the associated stress response.',
    'sulfur utilization':           'Utilization of different sulfur sources, or altered quantities of the same sulfur source (e.g. sulfur limitation) using nutritional shifts.',
    'transcription':                'The synthesis of RNA from a DNA template by RNA polymerase, and accessory factors.',
    'translational regulation':    'Modulation of the frequency, rate or extent of protein formation by translation of mRNA.',
    'ubiquitin or ULP modification':    'The covalent attachment or removal of ubiquitin or ubiquitin-like proteins (ULPs) from target protein(s).',
    'not yet curated':              'The dataset has not yet been assigned a tag or tags.'
}

keyword_mapping = {
    'cell aging': 'aging',
    'Aging': 'aging',
    'Cell growth and development': 'cell morphogenesis',
    'Chromatin, telomeres, centromeres': 'chromatin organization',
    'Evolution/phylogenetics': 'evolution',
    'Cell cycle': 'mitotic cell cycle',
    'Other': 'other',
    'Signalling': 'signaling',
    'Environmental sensing and stress response': 'stress',
    'Transcription and gene expression': 'transcription',
    'Translation and protein synthesis': 'translational regulation',
    'Bioinformatics/computational biology': 'bioinformatics/computational biology',
    'Cytoskeleton and molecular motors': 'cytoskeleton and molecular motors',
    'Functional genomics/proteomics': 'functional genomics/proteomics',
    'Metabolism and metabolic regulation': 'metabolism and metabolic regulation',
    'Nuclear structure/function': 'nuclear structure/function',
    'Organelles, biogenesis, structure, and function': 'organelles, biogenesis, structure, and function',
    'Prions': 'prions',
    'Protein structure/folding': 'protein structure/folding',
    'Protein trafficking, localization and degradation': 'protein trafficking, localization and degradation',
    'Transposons': 'transposons',
}


def keyword_starter(bud_session_maker):
    f = open('src/sgd/convert/data/microarray_05_14/pmid_filename_gse_conds_tags_file_20150416_forNex.txt', 'r')
    for line in f:
        row = line.split('\t')
        tag = row[6].strip()
        for t in [x.strip() for x in tag.split('|')]:
            yield remove_nones({
                'name': t if t not in keyword_mapping else keyword_mapping[t],
                'description': definitions.get(t),
                'source': {'name': 'SGD'}
            })
    f.close()

    from src.sgd.model.bud.colleague import Keyword
    bud_session = bud_session_maker()
    for bud_obj in bud_session.query(Keyword).filter_by(source='Curator-defined').all():
        yield {'name': bud_obj.keyword if bud_obj.keyword not in keyword_mapping else keyword_mapping[bud_obj.keyword],
               'source': {'name': bud_obj.source},
               'bud_id': bud_obj.id,
               'date_created': str(bud_obj.date_created),
               'created_by': bud_obj.created_by}
    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, keyword_starter, 'keyword', lambda x: x['name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

