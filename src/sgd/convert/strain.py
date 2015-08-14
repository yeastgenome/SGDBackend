from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

def strain_starter(bud_session_maker):
    from src.sgd.model.bud.cv import CVTerm
    bud_session = bud_session_maker()

    ### populate the info from the flat data file 
    f = open('src/sgd/convert/data/strain_info.txt', 'r')
    alternative_reference_strains = []
    strain_to_genotype = {}
    strain_to_description = {}
    strain_to_genbank = {}
    strain_to_assembly_stats = {}
    other_strains = []
    wiki_strains = set()
    sequence_download_strains = set()
    strain_to_source = {}
    strain_to_euroscarf = {}
    strain_paragraphs = {}
    for line in f:
        if line.startswith('#') or line == '':
            continue
        line = line.strip()
        pieces = line.split("\t")
        category = pieces.pop(0)
        if category.startswith('alternative'):
            alternative_reference_strains = pieces
        if category.startswith('strain_to_genotype'):
            strain_to_genotype[pieces[0]] = pieces[1]
        if category.startswith('strain_to_description'):
            strain_to_description[pieces[0]] = pieces[1]
        if category.startswith('strain_to_genbank'):
            strain_to_genbank[pieces[0]] = pieces[1]
        if category.startswith('strain_to_assembly_stats'):
            strain = pieces.pop(0)
            strain_to_assembly_stats[strain] = pieces 
        if category.startswith('other_strain'):
            if len(pieces) == 2:
                other_strains.append((pieces[0], pieces[1]))
            else:
                other_strains.append((pieces[0], ''))
        if category.startswith('wiki'):
            wiki_strains = set(pieces)
        if category.startswith('sequence_download'):
            sequence_download_strains = set(pieces)
        if category.startswith('strain_to_source'):
            strain_to_source[pieces[0]] = (pieces[1], pieces[2])
        if category.startswith('strain_to_euroscarf'):
            strain_to_euroscarf[pieces[0]] = pieces[1]
        if category.startswith('strain_paragraph'):
            strain = pieces.pop(0)
            desc = pieces.pop(0)
            strain_paragraphs[strain] = (desc, pieces)
            
    ### start loading
    from src.sgd.model.bud.cv import CVTerm

    bud_session = bud_session_maker()

    for bud_obj in bud_session.query(CVTerm).filter(CVTerm.cv_no==10).all():
        obj_json = remove_nones({'display_name': bud_obj.name,
                                 'source': {'display_name': 'SGD'},
                                 'description': bud_obj.definition if bud_obj.name not in strain_to_description else strain_to_description[bud_obj.name],
                                 'status': 'Reference' if bud_obj.name == 'S288C' else ('Alternative Reference' if bud_obj.name in alternative_reference_strains else (None if bud_obj.name == 'Other' else 'Other')),
                                
                                 'genotype': None if bud_obj.name not in strain_to_genotype else strain_to_genotype[bud_obj.name],
                                 'genbank_id': None if bud_obj.name not in strain_to_genbank else strain_to_genbank[bud_obj.name],
                                 'sgdid': 'S000' + bud_obj.name,
                                 'taxonomy': {'display_name': 'Saccharomyces cerevisiae'},
                                 'date_created': str(bud_obj.date_created),
                                 'created_by': bud_obj.created_by})
        if bud_obj.name in strain_to_assembly_stats:
            assembly_stats = strain_to_assembly_stats[bud_obj.name]
            obj_json['fold_coverage'] = assembly_stats[0]
            obj_json['scaffold_number'] = assembly_stats[1]
            obj_json['assembly_size'] = assembly_stats[2]
            obj_json['longest_scaffold'] = assembly_stats[3]
            obj_json['scaffold_nfifty'] = assembly_stats[4]
            obj_json['feature_count'] = assembly_stats[5]

        obj_json['urls'] = load_urls(bud_obj.name, obj_json.get('genbank_id'),
                                     wiki_strains, sequence_download_strains, 
                                     strain_to_source, strain_to_euroscarf)
        obj_json['documents'] = load_documents(bud_obj.name)
        yield obj_json

    for strain, description in other_strains:
        obj_json = {'display_name': strain,
                    'source': {'display_name': 'SGD'},
                    'description': description,
                    'sgdid': 'S000' + strain,
                    'taxonomy': {'display_name': 'Saccharomyces cerevisiae'},
                    'genotype': None if strain not in strain_to_genotype else strain_to_genotype[strain],
                    'genbank_id': None if strain not in strain_to_genbank else strain_to_genbank[strain],
                    'status': 'Reference' if bud_obj.name == 'S288C' else ('Alternative Reference' if strain in alternative_reference_strains else 'Other')}

        if strain in strain_to_assembly_stats:
            assembly_stats = strain_to_assembly_stats[strain]
            obj_json['fold_coverage'] = assembly_stats[0]
            obj_json['scaffold_number'] = assembly_stats[1]
            obj_json['assembly_size'] = assembly_stats[2]
            obj_json['longest_scaffold'] = assembly_stats[3]
            obj_json['scaffold_n50'] = assembly_stats[4]
            obj_json['feature_count'] = assembly_stats[5]

        obj_json['urls'] = load_urls(strain, obj_json.get('genbank_id'))
        obj_json['documents'] = load_documents(strain)
        yield obj_json

    bud_session.close()


def load_urls(strain, genbank_id, wiki_strains, sequence_download_strains, strain_to_source, strain_to_euroscarf):
    urls = []

    if strain in wiki_strains:
        urls.append({'display_name': 'Wiki',
                     'link': 'http://wiki.yeastgenome.org/index.php/Commonly_used_strains#' + strain,
                     'source': {'display_name': 'SGD'},
                     'url_type': 'wiki'})

    if strain in sequence_download_strains:
                urls.append({'display_name': 'Download Sequence',
                     'link': 'http://downloads.yeastgenome.org/sequence/strains/' + strain,
                     'source': {'display_name': 'SGD'},
                     'url_type': 'download'})

    if strain in strain_to_source:
        urls.append({'display_name': strain_to_source[strain][0],
                     'link': strain_to_source[strain][1],
                     'source': {'display_name': 'SGD'},
                     'url_type': 'source'})

    if strain in strain_to_euroscarf:
        urls.append({'display_name': 'EUROSCARF:' + strain_to_euroscarf[strain],
                     'link': 'http://web.uni-frankfurt.de/fb15/mikro/euroscarf/data/' + strain + '.html',
                     'source': {'display_name': 'SGD'},
                     'url_type': 'source'})

    if genbank_id is not None:
        urls.append({'display_name': genbank_id,
                     'link': 'http://www.ncbi.nlm.nih.gov/nuccore/' + genbank_id if strain != 'S288C' else 'http://www.ncbi.nlm.nih.gov/assembly/GCF_000146045.2/',
                     'source': {'display_name': 'SGD'},
                     'url_type': 'genbank'})

    if strain == 'S288C':
        urls.append({'display_name': 'Download Sequence',
                     'link': 'http://www.yeastgenome.org/download-data/sequence',
                     'source': {'display_name': 'SGD'},
                     'url_type': 'download'})

    urls.append({'display_name': 'PubMed',
                 'link': 'http://www.ncbi.nlm.nih.gov/pubmed/?term=saccharomyces+cerevisiae+' + strain,
                 'source': {'display_name': 'SGD'},
                 'url_type': 'pubmed'})

    return urls


def load_documents(strain):
    documents = []
    if strain in strain_paragraphs:
        paragraph = strain_paragraphs[strain]
        documents.append({
            'source': {'display_name': 'SGD'},
            'document_type': 'Paragraph',
            'text': paragraph[0],
            'html': paragraph[0],
            'references': [{'pubmed_id': pubmed_id, 'reference_order': i+1} for (i, pubmed_id) in enumerate(paragraph[1])]
            })

    return documents

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, strain_starter, 'strain', lambda x: x['display_name'])


