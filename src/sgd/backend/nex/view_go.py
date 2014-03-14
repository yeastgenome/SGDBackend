from math import ceil

from src.sgd.backend.nex.query_tools import get_biofacts, get_paragraph, get_all_bioconcept_children, get_conditions, \
    get_relations
from src.sgd.model.nex.bioconcept import Bioconceptrelation, Bioconcept
from src.sgd.model.nex.bioentity import Bioentity
from src.sgd.model.nex.evidence import Goevidence
from src.sgd.backend.nex import DBSession, create_simple_table, query_limit, get_obj_id
from src.sgd.backend.nex.cache import get_obj, get_objs
from src.sgd.backend.nex.obj_to_json import condition_to_json, minimize_json, \
    evidence_to_json
from src.sgd.go_enrichment import query_batter


__author__ = 'kpaskov'

# -------------------------------Enrichment---------------------------------------
def make_enrichment(bioent_ids):
    bioent_format_names = [get_obj(Bioentity, bioent_id)['format_name'] for bioent_id in bioent_ids]
    enrichment_results = query_batter.query_go_processes(bioent_format_names)
    json_format = []
    for enrichment_result in enrichment_results:
        identifier = 'GO:' + str(int(enrichment_result[0][3:])).zfill(7)
        goterm_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='GO')
        if goterm_id is not None:
            goterm = get_obj(Bioconcept, goterm_id)
            json_format.append({'go': goterm,
                            'match_count': enrichment_result[1],
                            'pvalue': enrichment_result[2]})
        else:
            print 'Go term not found: ' + str(enrichment_result[0])
    return json_format

# -------------------------------Overview---------------------------------------
def make_overview(bioent_id):
    overview = {}

    gofacts = get_biofacts('GO', bioent_id=bioent_id)
    biocon_ids = [x.bioconcept_id for x in gofacts]

    slim_ids = set([x.parent_id for x in DBSession.query(Bioconceptrelation).filter(Bioconceptrelation.bioconrel_class_type == 'GO_SLIM').filter(Bioconceptrelation.child_id.in_(biocon_ids)).all()])
    overview['go_slim'] = sorted([minimize_json(x) for x in get_objs(Bioconcept, slim_ids).values()], key=lambda y: y['display_name'])

    paragraph = get_paragraph(bioent_id, 'GO')
    if paragraph is not None:
        overview['date_last_reviewed'] = paragraph.text

    return overview

# -------------------------------Details---------------------------------------
#This is a hack - we need to figure out what we're doing with these relationships, but right now it's unclear.
condition_format_name_to_display_name = {'activated by':	                'activated by',
                                        'dependent on':	                    'dependent on',
                                        'during':	                        'during',
                                        'exists during':	                'during',
                                        'happens during':	                'during',
                                        'has part':	                        'has part',
                                        'has regulation_target':	        'regulates',
                                        'in presence_of':	                'in presence of',
                                        'independent of':	                'independent of',
                                        'inhibited by':	                    'inhibited by',
                                        'localization dependent on':	    'localization requires',
                                        'modified by':	                    'modified by',
                                        'not during':	                    'except during',
                                        'not exists during':	            'except during',
                                        'not happens during':	            'except during',
                                        'not occurs at':	                'not at',
                                        'not occurs in':	                'not in',
                                        'occurs at':	                    'at',
                                        'occurs in':	                    'in',
                                        'part of':	                        'part of',
                                        'requires direct regulator':	    'requires direct regulation by',
                                        'requires localization':	        'only when located at',
                                        'requires modification':	        'only with modification',
                                        'requires regulation by':	        'requires regulation by',
                                        'requires regulator':	            'requires',
                                        'requires sequence feature':	    'requires',
                                        'requires substance':	            'requires',
                                        'requires target sequence feature':	'requires feature in target',
                                        'stabilizes':	                    'stabilizes'}

def get_go_evidence(locus_id, go_id, reference_id, with_children):
    query = DBSession.query(Goevidence)
    if locus_id is not None:
        query = query.filter_by(bioentity_id=locus_id)
    if reference_id is not None:
        query = query.filter_by(reference_id=reference_id)
    if go_id is not None:
        if with_children:
            child_ids = list(get_all_bioconcept_children(go_id))
            num_chunks = int(ceil(1.0*len(child_ids)/500))
            evidences = []
            for i in range(num_chunks):
                subquery = query.filter(Goevidence.bioconcept_id.in_(child_ids[i*500:(i+1)*500]))
                if len(evidences) + subquery.count() > query_limit:
                    return None
                evidences.extend([x for x in subquery.all()])
            return evidences
        else:
            query = query.filter_by(bioconcept_id=go_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None, go_id=None, reference_id=None, with_children=False):
    if locus_id is None and go_id is None and reference_id is None:
        return {'Error': 'No locus_id or go_id or reference_id given.'}

    goevidences = get_go_evidence(locus_id=locus_id, go_id=go_id, reference_id=reference_id, with_children=with_children)

    if goevidences is None:
        return {'Error': 'Too much data to display.'}

    id_to_conditions = {}
    for condition in get_conditions([x.id for x in goevidences]):
        evidence_id = condition.evidence_id
        if evidence_id in id_to_conditions:
            id_to_conditions[evidence_id].append(condition)
        else:
            id_to_conditions[evidence_id] = [condition]
    
    return create_simple_table(goevidences, make_evidence_row, id_to_conditions=id_to_conditions)

def fix_display_name(condition):
    if 'role' in condition and condition['role'] in condition_format_name_to_display_name:
        condition['role'] = condition_format_name_to_display_name[condition['role']]
    return condition

def make_evidence_row(goevidence, id_to_conditions): 
    bioentity_id = goevidence.bioentity_id
    bioconcept_id = goevidence.bioconcept_id

    obj_json = evidence_to_json(goevidence).copy()
    obj_json['bioentity'] = minimize_json(get_obj(Bioentity, bioentity_id), include_format_name=True)
    obj_json['bioconcept'] = minimize_json(get_obj(Bioconcept, bioconcept_id))
    obj_json['bioconcept']['aspect'] = get_obj(Bioconcept, bioconcept_id)['go_aspect']
    obj_json['bioconcept']['go_id'] = get_obj(Bioconcept, bioconcept_id)['go_id']
    obj_json['conditions'] = [] if goevidence.id not in id_to_conditions else [fix_display_name(condition_to_json(x)) for x in id_to_conditions[goevidence.id]]
    obj_json['code'] = goevidence.go_evidence
    obj_json['method'] = goevidence.annotation_type
    obj_json['qualifier'] = goevidence.qualifier
    obj_json['date_created'] = str(goevidence.date_created)
    return obj_json

# -------------------------------Ontology Graph---------------------------------------
def create_node(biocon, is_focus):
    if is_focus:
        sub_type = 'FOCUS'
    else:
        sub_type = biocon['go_aspect']
    return {'data':{'id':'Node' + str(biocon['id']), 'name':biocon['display_name'] + ' (' + str(biocon['count']) + ')', 'link': biocon['link'],
                    'sub_type':sub_type}}

def create_edge(biocon1_id, biocon2_id, label):
    return {'data':{'target': 'Node' + str(biocon1_id), 'source': 'Node' + str(biocon2_id), 'name':label}}

def make_ontology_graph(phenotype_id):
    all_children = None
    children = get_relations(Bioconceptrelation, 'GO', parent_ids=[phenotype_id])    
    parents = get_relations(Bioconceptrelation, 'GO', child_ids=[phenotype_id])
    if len(parents) > 0:
        grandparents = get_relations(Bioconceptrelation, 'GO', child_ids=[parent.parent_id for parent in parents])
        greatgrandparents = get_relations(Bioconceptrelation, 'GO', child_ids=[parent.parent_id for parent in grandparents])
        greatgreatgrandparents = get_relations(Bioconceptrelation, 'GO', child_ids=[parent.parent_id for parent in greatgrandparents])
        nodes = []
        nodes.append(create_node(get_obj(Bioconcept, phenotype_id), True))
        
        child_ids = set([x.child_id for x in children])
        parent_ids = set([x.parent_id for x in parents])
        parent_ids.update([x.parent_id for x in grandparents])
        parent_ids.update([x.parent_id for x in greatgrandparents])
        parent_ids.update([x.parent_id for x in greatgreatgrandparents])
        
        child_id_to_child = get_objs(Bioconcept, child_ids)
        parent_id_to_parent = get_objs(Bioconcept, parent_ids)
        viable_ids = set([k for k, v in child_id_to_child.iteritems() if v['child_count'] > 0])

        #If there are too many children, hide some.
        all_children = []
        hidden_children_count = 0
        if len(viable_ids) > 8:
            all_children = sorted(get_objs(Bioconcept, viable_ids).values(), key=lambda x: x['display_name'])
            hidden_children_count = len(viable_ids)-7
            viable_ids = set(list(viable_ids)[:7])

        viable_ids.update([k for k, v in parent_id_to_parent.iteritems() if v['child_count'] > 0])
        viable_ids.add(phenotype_id)
        
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])
        nodes.extend([create_node(v, False) for k, v in parent_id_to_parent.iteritems() if k in viable_ids])

        relations = set()
        relations.update(children)
        relations.update(parents)
        relations.update(grandparents)
        relations.update(greatgrandparents)
        relations.update(greatgreatgrandparents)
        edges = [create_edge(x.child_id, x.parent_id, x.relation_type) for x in relations if x.child_id in viable_ids and x.parent_id in viable_ids]

        if hidden_children_count > 0:
            nodes.insert(0, {'data':{'id':'NodeMoreChildren', 'name':str(hidden_children_count) + ' more children', 'link': None, 'sub_type':get_obj(Bioconcept, phenotype_id)['go_aspect']}})
            edges.insert(0, {'data':{'target': 'NodeMoreChildren', 'source': 'Node' + str(phenotype_id), 'name':None}})

    else:
        #grandchildren = get_relations(Bioconceptrelation, 'GO', parent_ids=[x.child_id for x in children])
        
        child_ids = set([x.child_id for x in children])
        #child_ids.update([x.child_id for x in grandchildren])
        
        child_id_to_child = get_objs(Bioconcept, child_ids)
        viable_ids = set([k for k, v in child_id_to_child.iteritems() if v['child_count'] > 0])
        viable_ids.add(phenotype_id)
        
        nodes = []
        nodes.append(create_node(get_obj(Bioconcept, phenotype_id), True))
        nodes.extend([create_node(v, False) for k, v in child_id_to_child.iteritems() if k in viable_ids])

        relations = set()
        relations.update(children)
        #relations.update(grandchildren)
        edges = [create_edge(x.child_id, x.parent_id, x.relation_type) for x in relations if x.child_id in viable_ids and x.parent_id in viable_ids]

    return {'nodes': list(nodes), 'edges': edges, 'all_children': all_children}
