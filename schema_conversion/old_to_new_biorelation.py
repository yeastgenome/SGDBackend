'''
Created on Feb 27, 2013

@author: kpaskov
'''

def interaction_to_biorel(interaction):
    from model_new_schema.biorelation import Biorelation
    
    bait_id = interaction.features['Bait'].id
    hit_id = interaction.features['Hit'].id
    if bait_id < hit_id:
        new_biorel = Biorelation('INTERACTION', bait_id, hit_id, biorel_id=interaction.id, created_by=interaction.created_by, date_created=interaction.date_created)
    else:
        new_biorel = Biorelation('INTERACTION', hit_id, bait_id, biorel_id=interaction.id, created_by=interaction.created_by, date_created=interaction.date_created)
    return new_biorel
        