'''
Created on Jul 10, 2013

@author: kpaskov
'''

from backend_test import check_biocon, check_evidence, check_obj
import json

def test_phenotype_structure(model, identifier='cell_cycle_progression_in_G1_phase'):
    response = json.loads(model.phenotype(identifier))
    assert response is not None
    check_biocon(response)

def test_phenotype_overview_structure(model, identifier='YFL039C'):
    response = json.loads(model.phenotype_overview(locus_identifier=identifier))
    assert response is not None
    assert 'mutant_types' in response
    assert 'mutant_to_count' in response
    assert 'strain_list' in response
    assert 'strain_to_count' in response
    assert 'experiment_types' in response
    
def test_phenotype_details_structure(model, identifier='YFL039C'):
    response = json.loads(model.phenotype_details(locus_identifier=identifier))
    assert response is not None
    for entry in response:
        check_evidence(entry)
        assert 'bioconcept' in entry
        assert 'bioentity' in entry
        assert 'condition' in entry
        
        check_obj(entry['bioconcept'])
        check_obj(entry['bioentity'])