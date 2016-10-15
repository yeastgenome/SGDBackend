from src.sgd.convert import basic_convert

__author__ = 'sweng66'


def obi_starter(bud_session_maker):
    
    parent_to_children = dict()
    curation_status = dict()
    source = 'OBI Consortium'
    ## http://purl.obolibrary.org/obo/obi.owl
    terms = read_owl('src/sgd/convert/data/obi.owl', 
                     parent_to_children,
                     curation_status,
                     source)

    from src.sgd.convert import config
    dbuser = config.NEX_CREATED_BY

    for term in terms:
        if term.get('obiid') == None or term.get('display_name') == None:
            continue
        obiid = term['obiid']

        if ' ' in obiid or '/' in obiid:
            continue

        # if curation_status.get(obiid) is None or curation_status.get(obiid) != 'ready for release':
        #    continue
        

        print obiid, curation_status.get(obiid), term['display_name']

        if obiid not in parent_to_children:
            term['children'] = [] 
        else:
            children = []
            for child in parent_to_children[obiid]:
                child_id = child['obiid']
                if child_id not in curation_status:
                    child['created_by'] = dbuser
                    children.append(child)
            term['children'] = children

        term['created_by'] = dbuser
        term['source'] = { 'display_name': 'OBI Consortium'}
        obiid = obiid.replace(":", "_")
        term['urls'] = [{'display_name': 'Ontobee',
                         'link': 'http://www.ontobee.org/browser/rdf.php?o=OBI&iri=http://purl.obolibrary.org/obo/' + obiid,
                         'source': {'display_name': 'Ontobee'},
                         'url_type': 'Ontobee',
                         'created_by': dbuser},
                        {'display_name': 'OLS',
                         'link': 'http://www.ebi.ac.uk/ols/ontologies/obi/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F' + obiid,
                         'source': {'display_name': 'OLS'},
                         'url_type': 'OLS',
                         'created_by': dbuser},
                        {'display_name': 'BioPortal',
                         'link': 'https://bioportal.bioontology.org/ontologies/OBI/?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2F' + obiid,
                         'source': {'display_name': 'BioPortal'},
                         'url_type': 'BioPortal',
                         'created_by': dbuser}]
        yield term

    ## add NTR terms:                                                                                        
    files = ['src/sgd/convert/data/published_datasets_metadata_dataset-20160804.txt',
             'src/sgd/convert/data/GEO_metadata_reformatted_NOTinSPELL.tsv_dataset_OWL.txt',
             'src/sgd/convert/data/GEO_metadata_reformatted_inSPELL_cleaned-up.tsv_dataset-OWL.txt',
             'src/sgd/convert/data/non-GEO-dataset.tsv']

    found = {}
    i = 0
    for file in files:
        f = open(file)
        for line in f:
            if line.startswith('dataset'):
                continue
            line = line.strip()
            if line:
                pieces = line.split("\t")
                if len(pieces) > 7:
                    if pieces[7].startswith('NTR:'):
                        display_name = pieces[7].replace('NTR:', '')
                        if display_name not in found:
                            i = i + 1
                            found[display_name] = 1
                            yield { 'source': { 'display_name': 'SGD' },
                                    'obiid': 'NTR:' + str(i),
                                    'format_name': 'NTR:' + str(i),
                                    'display_name': display_name,
                                    'created_by': dbuser}
     
    for display_name in ['ChIP-exo',
                         'DNA sequence variation detection by snp array',
                         'DNA sequence variation detection by tiling array',
                         'Prediction',
                         'Serial analysis of gene expression',
                         'competitive growth assay analysis with microarrays',
                         'fluorescence detection assay',
                         'synthetic lethality analysis with microarrays',
                         'sequencing']:

        if display_name not in found:
            i = i + 1
            found[display_name] = 1
            yield { 'source': { 'display_name': 'SGD' },
                    'obiid': 'NTR:' + str(i),
                    'format_name': 'NTR:' + str(i),
                    'display_name': display_name,
                    'created_by': dbuser}



def read_owl(filename, parent_to_children, curation_status, source):

    from src.sgd.convert.util import get_relation_to_ro_id
    ro_id = get_relation_to_ro_id('is a')

    terms = []
    f = open(filename, 'r')
    term = None
    # parent_child_pair = {}

    start_ontology = 0
    parents = []

    for line in f:

        if line.startswith('          '):
            continue

        line = line.strip()
        
        if '<obo:IAO_0000114 rdf:resource="http://purl.obolibrary.org/obo/' in line:
            pieces = line.split('>')
            status = pieces[1].replace("<!-- ", "").replace(" --", "")
            if term.get('obiid'):
                curation_status[term['obiid']] = status
            # if status == 'ready for release':
            #    print "STATUS=", status
            continue

        if '<obo:IAO_0000115 xml:lang="en">' in line:
            line = line.replace('<obo:IAO_0000115 xml:lang="en">', '')
            line = line.replace('</obo:IAO_0000115>', '')
            if term is not None:
                term['description'] = line

            continue

        if '<rdfs:subClassOf rdf:resource="http://purl.obolibrary.org/obo/' in line or '<owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/' in line or '<owl:someValuesFrom rdf:resource="http://purl.obolibrary.org/obo/' in line:
            line = line.replace('<rdfs:subClassOf rdf:resource="http://purl.obolibrary.org/obo/', '')
            line = line.replace('<owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/', '')
            line = line.replace('<owl:someValuesFrom rdf:resource="http://purl.obolibrary.org/obo/', '')
            line = line.replace('"', '')
            pieces = line.split('>')
            parent = pieces[0].replace("_", ":").replace("/", "")
            if term and term.get('obiid'):
                parents.append(parent)
                print "PARENT="+parent+":"
            
            continue
        
        

        if ('Property rdf:about="http://purl.obolibrary.org/obo/' in line or '<owl:Class rdf:about="http://purl.obolibrary.org/obo/' in line or '<owl:NamedIndividual rdf:about="http://purl.obolibrary.org/obo/' in line or '<owl:Thing rdf:about="http://purl.obolibrary.org/obo/' in line) and "><" in line:
 
            start_ontology = 1
            
            line = line.replace('<owl:AnnotationProperty rdf:about="http://purl.obolibrary.org/obo/', '')
            line = line.replace('<owl:DatatypeProperty rdf:about="http://purl.obolibrary.org/obo/', '')
            line = line.replace('<owl:ObjectProperty rdf:about="http://purl.obolibrary.org/obo/', '')
            line = line.replace('<owl:Class rdf:about="http://purl.obolibrary.org/obo/', '')
            line = line.replace('<owl:NamedIndividual rdf:about="http://purl.obolibrary.org/obo/', '')
            line = line.replace('<owl:Thing rdf:about="http://purl.obolibrary.org/obo/', '')
            line = line.replace('"', '')
            pieces = line.split('>')
            obiid = pieces[0].replace("_", ":")
            display_name = pieces[1].replace("<!-- ", "").replace(" --", "")

            # print "OBI ID: "+obiid+", display_name="+display_name+":"

            term = { 'source': { 'display_name': source },
                     'obiid': obiid,
                     'format_name': obiid,
                     'display_name': display_name }
            continue

        if line in ['</owl:AnnotationProperty>',
                   '</owl:DatatypeProperty>',
                   '</owl:ObjectProperty>',
                   '</owl:Class>', 
                   '</owl:NamedIndividual>',
                   '</owl:Thing>']:

            if term is not None:
                
                start_ontology = 0

                if len(parents) > 0:
                    for parent in parents:
                        if parent not in parent_to_children:
                            parent_to_children[parent] = []
                        parent_to_children[parent].append({'obiid': term['obiid'],
                                                           'format_name': term['format_name'],
                                                           'display_name': term.get('display_name'),
                                                           'source': {'display_name': source},
                                                           'description': str(term.get('description')),
                                                           'ro_id': ro_id})
                terms.append(term)
                parents = []
                term = None
            continue

        # if start_ontology == 0:
        #    continue
                       

    f.close()

    return terms




if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, obi_starter, 'obi', lambda x: x['display_name'])




