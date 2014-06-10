from src.sgd.backend.tests import conftest

__author__ = 'kpaskov'

def check_obj(obj_json):
    if obj_json is not None:
        assert 'id' in obj_json
        assert 'link' in obj_json
        assert 'display_name' in obj_json

def check_url(url):
    if url is not None:
        assert 'link' in url
        assert 'display_name' in url

def check_evidence(evidence):
    assert 'id' in evidence
    if (evidence.has_key('properties') and len(evidence['properties']) > 0):
        assert 'class_type' in evidence['properties'][0]
    assert 'strain' in evidence
    assert 'source' in evidence
    assert 'reference' in evidence
    assert 'experiment' in evidence
    assert 'note' in evidence

    check_obj(evidence['strain'])
    check_obj(evidence['reference'])
    check_obj(evidence['experiment'])

    #assert 'conditions' in evidence  Not always there.
    if evidence.has_key('conditions'):
        for cond in evidence['conditions']:
            check_condition(cond)

def check_condition(condition):
    assert 'note' in condition
    assert 'role' in condition
    if 'obj' in condition:
        check_obj(condition['obj'])
