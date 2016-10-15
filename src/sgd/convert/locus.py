from src.sgd.convert import basic_convert, remove_nones
from collections import OrderedDict
from sqlalchemy.orm import joinedload
from src.sgd.convert.util import get_relation_to_ro_id

__author__ = 'kpaskov, sweng66'

def load_urls(bud_session, source_to_id):
    from src.sgd.model.bud.general import FeatUrl, DbxrefFeat

    url_placement_mapping = url_placement()
    
    url_source_mapping = { 'Author': 'Publication',
                           'Colleague submission': 'Direct submission',
                           'DNASU Plasmid Repository': 'DNASU',
                           'HIP HOP profile database (Novartis)': 'HIP HOP profile database',
                           'HIPHOP chemogenomics database (UBC)': 'HIPHOP chemogenomics database',
                           'LoQate': 'LoQAte',
                           'LoQAtE': 'LoQAte',
                           'MRC': 'SUPERFAMILY',
                           'PlasmID Database': 'PlasmID',
                           'Publisher': 'Publication',
                           'Yeast Genetic Resource Center': 'YGRC',
                           'Yeast Microarray Global Viewer': 'yMGV',
                           'yeast snoRNA database at UMass Amherst': 'Yeast snoRNA database',
                           'Direct Submission': 'Direct submission',
                           'Hamap': 'HAMAP',
                           'PhosphoPep Database': 'PhosphoPep',
                           'ProSitePatterns': 'PROSITE',
                           'ProSiteProfiles': 'PROSITE',
                           'Prosite': 'PROSITE',
                           'SignalP_EUK': 'SignalP',
                           'SignalP_GRAM_POSITIVE': 'SignalP',
                           'Uniprot': 'UniProt',
                           'UniParc': 'UniProt',
                           'GenBank': 'GenBank/EMBL/DDBJ',
                           'NCBI BioProject': 'NCBI',
                           'GO Consortium': 'GOC',
                           'MetaboGeneCards': 'MetaboGeneCard'}

    feature_id_to_urls = {}

    for bud_obj in bud_session.query(FeatUrl).options(joinedload('url')):
        feature_id = bud_obj.feature_id
        old_url = bud_obj.url
        url_type = old_url.url_type
        link = old_url.url
        bud_locus = bud_obj.feature
        type = ''

        urls = []

        if feature_id in feature_id_to_urls:
            urls = feature_id_to_urls[feature_id]

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
            

            if source not in source_to_id:
                print "NEW SOURCE:", source
                continue

            urls.append(
                {'display_name': old_webdisplay.label_name,
                 'source_id': source_to_id[source],
                 'bud_id': old_url.id,
                 'url_type': type,
                 'placement': old_webdisplay.label_location if old_webdisplay.label_location not in url_placement_mapping else url_placement_mapping[old_webdisplay.label_location],
                 'link': link,
                 'date_created': str(old_url.date_created),
                 'created_by': old_url.created_by})

        feature_id_to_urls[feature_id] = urls

    for bud_obj in bud_session.query(DbxrefFeat).options(joinedload('dbxref'), joinedload('dbxref.dbxref_urls')).all():

        feature_id = bud_obj.feature_id
        bud_locus = bud_obj.feature
        old_urls = bud_obj.dbxref.urls
        dbxref_id = bud_obj.dbxref.dbxref_id
        
        urls = []
        if feature_id in feature_id_to_urls:
            urls = feature_id_to_urls[feature_id]

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


                if source not in source_to_id:
                    print "NEW SOURCE: ", source
                    continue

                urls.append(
                    {'display_name': old_webdisplay.label_name,
                     'source_id': source_to_id[source],
                     'bud_id': old_url.id,
                     'link': link,
                     'url_type': type,
                     'placement': old_webdisplay.label_location if old_webdisplay.label_location not in url_placement_mapping else url_placement_mapping[old_webdisplay.label_location],
                     'date_created': str(old_url.date_created),
                     'created_by': old_url.created_by})

        feature_id_to_urls[feature_id] = urls

    urls_to_return = {}
    for feature_id in feature_id_to_urls:
        urls = feature_id_to_urls[feature_id]
        urls.append({'display_name': 'Yeast Phenotype Ontology',
                     'source_id': source_to_id['SGD'],
                     'bud_id': feature_id,
                     'link': '/ontology/phenotype/ypo/overview',
                     'url_type': 'Internal web service',
                     'placement': 'LOCUS_PHENOTYPE_RESOURCES_ONTOLOGY',
                     'created_by': 'OTTO'})
        
        make_unique = dict([((x['display_name'], x['placement'], x['link']), x) for x in urls])
        urls_to_return[feature_id] = make_unique.values() 

    return urls_to_return


def load_aliases(bud_session, source_to_id):
    from src.sgd.model.bud.feature import AliasFeature
    from src.sgd.model.bud.general import DbxrefFeat

    feature_id_to_aliases = {}
    for bud_obj in bud_session.query(AliasFeature).options(joinedload('alias')).all():
        #if bud_obj.alias_type in {'Uniform', 'Non-uniform', 'NCBI protein name', 'Retired name'}:
        feature_id = bud_obj.feature_id
        aliases = []
        if feature_id in feature_id_to_aliases:
            aliases = feature_id_to_aliases[feature_id]
        aliases.append({
            'display_name': bud_obj.alias_name,
            'source_id': source_to_id['SGD'],
            'bud_id': bud_obj.id,
            'alias_type': bud_obj.alias_type,
            'date_created': str(bud_obj.date_created),
            'created_by': bud_obj.created_by})
        feature_id_to_aliases[feature_id] = aliases

    found_uniprot = {}
    for bud_obj in bud_session.query(DbxrefFeat).options(joinedload('dbxref'), joinedload('dbxref.dbxref_urls')).all():
        feature_id = bud_obj.feature_id
        alias_type = bud_obj.dbxref.dbxref_type
        if alias_type == 'DBID Primary':
            continue
        if alias_type == 'DBID Secondary':
            alias_type = 'SGDID Secondary'
        if alias_type.startswith('UniProt') or alias_type.startswith('Uniprot') :
            alias_type = 'UniProtKB ID'
        display_name = bud_obj.dbxref.dbxref_id

        if alias_type.startswith('UniProt'):
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
        
        alias_source_mapping = { 'UniParc': 'UniProt',
                                 'GenBank': 'GenBank/EMBL/DDBJ',
                                 'RefSeq': 'NCBI',
                                 'NCBI Gene': 'NCBI',
                                 'NCBI TPA': 'NCBI'}

        source =  bud_obj.dbxref.source
        if source in alias_source_mapping:
            source = alias_source_mapping.get(source)
 

        if source not in source_to_id:
            print "NEW SOURCE: ", source
            continue


        aliases = []
        if feature_id in feature_id_to_aliases:
            aliases = feature_id_to_aliases[feature_id]
        
        aliases.append(remove_nones(
            {'display_name': display_name,
             'link': link,
             'source_id': source_to_id[source],
             'alias_type': alias_type,
             'bud_id': bud_obj.id,
             'date_created': str(bud_obj.dbxref.date_created),
             'created_by': bud_obj.dbxref.created_by}))
        feature_id_to_aliases[feature_id] = aliases

    return [feature_id_to_aliases, found_uniprot]



def locus_starter(bud_session_maker):

    from src.sgd.model.bud.feature import Feature

    #Load uniprot ids
    sgdid_to_uniprotid = {}
    # http://mirror.ufs.ac.za/datasets/uniprot/current_release/knowledgebase/idmapping/by_organism/YEAST_559292_idmapping.dat.gz
    f = open('src/sgd/convert/data/YEAST_559292_idmapping.dat', 'r')
    for line in f:
        pieces = line.split('\t')
        if pieces[1].strip() == 'SGD':
            sgdid_to_uniprotid[pieces[2].strip()] = pieces[0].strip()
    f.close()

    ## get some data from nex
    nex_session = get_nex_session()
    from src.sgd.model.nex.source import Source
    from src.sgd.model.nex.locus import Locus
    source_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Source).all()])
    name_to_id = dict([(x.systematic_name, x.id) for x in nex_session.query(Locus).all()])
    nex_session.close()
    ## end nex session

    print "Retrieing URLs and ALIASES from BUD..."

    bud_session = bud_session_maker()

    ## updated so get all URLs and Aliases at the same time  
    feature_id_to_urls = load_urls(bud_session, source_to_id)
    [feature_id_to_aliases, found_uniprot] = load_aliases(bud_session, source_to_id)
    bud_session.close()

    print "Retrieving FEATURE data from BUD..."

    bud_session = bud_session_maker()

    #Create features
    # for bud_obj in bud_session.query(Feature).options(joinedload('annotation')).all():
    features = bud_session.query(Feature).options(joinedload('annotation')).all()
    
    bud_session.close()

    print "Loading data into NEX..."

    for bud_obj in features:

        # if bud_obj.type not in non_locus_feature_types:
        sgdid = bud_obj.dbxref_id
        systematic_name = bud_obj.name

        if systematic_name in name_to_id:
            continue
        

        feature_type = bud_obj.type
        if feature_type.startswith('not in'):
            feature_type = 'ORF'
        if feature_type.startswith('TF') or feature_type.startswith('not physically'):
            continue

        # 'so_id': term_to_so[feature_type].id,
        obj_json = {'gene_name': bud_obj.gene_name,
                    'systematic_name': systematic_name,
                    'source_id': source_to_id[bud_obj.source],
                    'bud_id': bud_obj.id,
                    'sgdid': sgdid,
                    'dbentity_status': bud_obj.status,
                    'date_created': str(bud_obj.date_created),
                    'created_by': bud_obj.created_by}

        ann = bud_obj.annotation
        if ann is not None:
            obj_json['name_description'] = ann.name_description
            obj_json['headline'] = ann.headline
            if ann.qualifier is not None:
                obj_json['qualifier'] = ann.qualifier
            obj_json['description'] = ann.description
            if ann.genetic_position is not None:
                obj_json['genetic_position'] = str(ann.genetic_position)

        obj_json = remove_nones(obj_json)


        #Load aliases
        aliases = []
        if bud_obj.id in feature_id_to_aliases:
            aliases = feature_id_to_aliases[bud_obj.id]
        if sgdid in sgdid_to_uniprotid:
            uniprot_id = sgdid_to_uniprotid[sgdid]
            if uniprot_id not in found_uniprot:                            
                aliases.append({'display_name': uniprot_id,                
                                'source_id': source_to_id['EBI'],
                                'alias_type': 'UniProtKB ID',
                                'created_by': 'OTTO'})                                        
        obj_json['aliases'] = aliases
        
        #Load urls
        obj_json['urls'] = []
        if bud_obj.id in feature_id_to_urls:
            obj_json['urls'] = feature_id_to_urls[bud_obj.id]

        obj_json['summaries'] = []
        
        obj_json['tabs'] = get_tabs(bud_obj.status, feature_type) 

        print obj_json['systematic_name']

        yield obj_json

    # bud_session.close()


def url_placement():

    return { 'Analyze Sequence S288C only': 'LOCUS_SEQUENCE_S288C',
             'Analyze Sequence S288C vs. other strains': 'LOCUS_SEQUENCE_OTHER_STRAINS',
             'Analyze Sequence S288C vs. other species': 'LOCUS_SEQUENCE_OTHER_SPECIES', 
             'Expression Resources': 'LOCUS_EXPRESSION_RESOURCES',
             'Homologs': 'LOCUS_PROTEIN_RESOURCES_HOMOLOGS',
             'Interaction Resources': 'LOCUS_INTERACTION_RESOURCES',
             'Localization Resources': 'LOCUS_PROTEIN_RESOURCES_LOCALIZATION',
             'Maps & Displays': 'GENE_SEQ_RESOURCES_DISPLAY_MAPS',
             'Mutant Strains': 'LOCUS_PHENOTYPE_RESOURCES_MUTANT_STRAINS',
             'Phenotype Resources': 'LOCUS_PHENOTYPE_RESOURCES_PHENOTYPE_RESOURCES',
             'Post-translational modifications': 'LOCUS_PROTEIN_RESOURCES_PTM',
             'Protein databases': 'LOCUS_PROTEIN_RESOURCES_PROTEIN_DATABASES',
             'Regulation Resources': 'LOCUS_REGULATION_RESOURCES',
             'Resources External Links': 'LOCUS_LSP_RESOURCES',
             'Retrieve Sequences': 'CHROMOSOME_RETRIEVE_SEQUENCES',
             'Sequence Analysis Tools': 'CHROMOSOME_SEQUENCE_ANALYSIS_TOOLS',
             'Sequence Information Retrieve sequences': 'GENE_SEQ_RESOURCES_SEQUENCE_RETRIEVAL'}


def get_tabs(status, feature_type):

    if status == 'Merged' or status == 'Deleted':
        return {
            'has_summary': '1',
            'has_sequence': '0',
            'has_sequence_section': '1',
            'has_history': '0',
            'has_literature': '0',
            'has_go': '0',
            'has_phenotype': '0',
            'has_interaction': '0',
            'has_expression': '0',
            'has_regulation': '0',
            'has_protein': '0',
        }
    elif feature_type == 'ORF' or feature_type == 'blocked_reading_frame':
        return {
            'has_summary': '1',
            'has_sequence': '1',
            'has_sequence_section': '1',
            'has_history': '0',
            'has_literature': '1',
            'has_go': '1',
            'has_phenotype': '1',
            'has_interaction': '1',
            'has_expression': '1',
            'has_regulation': '1',
            'has_protein': '1',
        }
    elif feature_type in {'ARS', 'origin_of_replication', 'matrix_attachment_site', 'centromere',
                          'gene_group', 'long_terminal_repeat', 'telomere', 
                          'mating_type_region', 'silent_mating_type_cassette_array', 
                          'LTR_retrotransposon'}:
        return {
            'has_summary': '1',
            'has_sequence': '1',
            'has_sequence_section': '1',
            'has_history': '0',
            'has_literature': '1',
            'has_go': '0',
            'has_phenotype': '0',
            'has_interaction': '0',
            'has_expression': '0',
            'has_regulation': '0',
            'has_protein': '0',
        }
    elif feature_type == 'transposable_element_gene':
        return {
            'has_summary': '1',
            'has_sequence': '1',
            'has_sequence_section': '1',
            'has_history': '0',
            'has_literature': '1',
            'has_go': '1',
            'has_phenotype': '1',
            'has_interaction': '1',
            'has_expression': '0',
            'has_regulation': '0',
            'has_protein': '1',
        }
    elif feature_type == 'pseudogene':
        return {
            'has_summary': '1',
            'has_sequence': '1',
            'has_sequence_section': '1',
            'has_history': '0',
            'has_literature': '1',
            'has_go': '1',
            'has_phenotype': '1',
            'has_interaction': '1',
            'has_expression': '0',
            'has_regulation': '1',
            'has_protein': '1',
        }
    elif feature_type in {'rRNA_gene', 'ncRNA_gene', 'snRNA_gene', 'snoRNA_gene', 'tRNA_gene', 'telomerase_RNA_gene'}:
        return {
            'has_summary': '1',
            'has_sequence': '1',
            'has_sequence_section': '1',
            'has_history': '0',
            'has_literature': '1',
            'has_go': '1',
            'has_phenotype': '1',
            'has_interaction': '1',
            'has_expression': '0',
            'has_regulation': '1',
            'has_protein': '0',
        }
    elif feature_type in {'not in systematic sequence of S288C', 'not physically mapped'}:
        return {
            'has_summary': '1',
            'has_sequence': '0',
            'has_sequence_section': '0',
            'has_history': '0',
            'has_literature': '1',
            'has_go': '1',
            'has_phenotype': '1',
            'has_interaction': '1',
            'has_expression': '0',
            'has_regulation': '0',
            'has_protein': '0',
        }
    elif feature_type in {'intein_encoding_region'}:
        return {
            'has_summary': '1',
            'has_sequence': '0',
            'has_sequence_section': '0',
            'has_history': '0',
            'has_literature': '1',
            'has_go': '0',
            'has_phenotype': '0',
            'has_interaction': '0',
            'has_expression': '0',
            'has_regulation': '0',
            'has_protein': '0',
        }
    else:
        # raise Exception('feature_type: ' + feature_type + ' is invalid.')
        return {
            'has_summary': '0',
            'has_sequence': '0',
            'has_sequence_section': '0',
            'has_history': '0',
            'has_literature': '0',
            'has_go': '0',
            'has_phenotype': '0',
            'has_interaction': '0',
            'has_expression': '0',
            'has_regulation': '0',
            'has_protein': '0',
        }


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, locus_starter, 'locus', lambda x: x['sgdid'])

