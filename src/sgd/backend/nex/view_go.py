from math import ceil

from src.sgd.backend.nex.query_tools import get_all_bioconcept_children
from src.sgd.model.nex.bioconcept import Go
from src.sgd.model.nex.bioentity import Locus
from src.sgd.model.nex.evidence import Goevidence
from src.sgd.backend.nex import DBSession, query_limit, get_obj_id
from src.sgd.go_enrichment import query_batter
from sqlalchemy.orm import joinedload
import json

__author__ = 'kpaskov'

# -------------------------------Enrichment---------------------------------------
def make_enrichment(bioent_ids):
    print len(bioent_ids)
    bioent_ids = list(set(bioent_ids))
    bioent_format_names = []
    num_chunks = int(ceil(1.0*len(bioent_ids)/500))
    for i in range(0, num_chunks):
        bioent_format_names.extend([x.format_name for x in DBSession.query(Locus).filter(Locus.id.in_(bioent_ids[i*500:(i+1)*500])).all()])
    enrichment_results = query_batter.query_go_processes(bioent_format_names)
    json_format = []
    for enrichment_result in enrichment_results:
        identifier = 'GO:' + str(int(enrichment_result[0][3:])).zfill(7)
        goterm_id = get_obj_id(identifier, class_type='BIOCONCEPT', subclass_type='GO')
        if goterm_id is not None:
            goterm = DBSession.query(Go).filter_by(id=goterm_id).first().to_json()
            json_format.append({'go': goterm,
                            'match_count': enrichment_result[1],
                            'pvalue': enrichment_result[2]})
        else:
            print 'Go term not found: ' + str(enrichment_result[0])
    return json_format

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
        query = query.filter_by(locus_id=locus_id)
    if reference_id is not None:
        query = query.filter_by(reference_id=reference_id)
    if go_id is not None:
        if with_children:
            child_ids = list(get_all_bioconcept_children(go_id))
            num_chunks = int(ceil(1.0*len(child_ids)/500))
            evidences = []
            for i in range(num_chunks):
                subquery = query.filter(Goevidence.go_id.in_(child_ids[i*500:(i+1)*500]))
                if len(evidences) + subquery.count() > query_limit:
                    return None
                evidences.extend([x for x in subquery.all()])
            return evidences
        else:
            query = query.filter_by(go_id=go_id)

    if query.count() > query_limit:
        return None
    return query.all()

def make_details(locus_id=None, go_id=None, reference_id=None, with_children=False):
    if locus_id is None and go_id is None and reference_id is None:
        return {'Error': 'No locus_id or go_id or reference_id given.'}

    goevidences = get_go_evidence(locus_id=locus_id, go_id=go_id, reference_id=reference_id, with_children=with_children)

    if goevidences is None:
        return {'Error': 'Too much data to display.'}

    return '[' + ', '.join([x.json for x in goevidences if x.json is not None]) + ']'

def fix_display_name(condition):
    if 'role' in condition and condition['role'] in condition_format_name_to_display_name:
        condition['role'] = condition_format_name_to_display_name[condition['role']]
    return condition
