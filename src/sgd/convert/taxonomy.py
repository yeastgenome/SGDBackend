from src.sgd.convert import basic_convert, remove_nones
from sqlalchemy.orm import joinedload


__author__ = 'kpaskov'
## updated by sweng66


def load_aliases(bud_obj, bud_session, secondary_common_name):
    from src.sgd.model.bud.taxonomy import TaxonomyAlias

    aliases = []
    for alias_obj in bud_session.query(TaxonomyAlias).filter_by(taxon_id=bud_obj.id).all():
        aliases.append(remove_nones({
            "display_name": alias_obj.synonym,
            "alias_type": 'Synonym',
            "source": {'display_name': 'NCBI'},
            "bud_id": int(alias_obj.id)
        }))

    for common_name in secondary_common_name:
        aliases.append({
            "display_name": common_name,
            "alias_type": 'Secondary common name',
            "source": {'display_name': 'NCBI'}
        })

    return aliases


def load_relations(bud_obj, bud_session):
    from src.sgd.model.bud.taxonomy import TaxonomyRelation

    relations = []
    for relation_obj in bud_session.query(TaxonomyRelation).filter_by(parent_id=bud_obj.id).filter_by(generation=1).all():
        relations.append(remove_nones({
            "display_name": relation_obj.child.name,
            'source': {'display_name': 'NCBI'},
            "relation_type": 'is a'
        }))
    return relations


def taxonomy_starter(bud_session_maker):
    from src.sgd.model.bud.taxonomy import TaxonomyRelation
    bud_session = bud_session_maker()

    # only load taxonomy for family "Saccharomycetaceae" (taxon_id=4893) and lower
    for relation in bud_session.query(TaxonomyRelation).options(joinedload(TaxonomyRelation.child)).filter_by(parent_id=4893).all():
        bud_obj = relation.child
    
        obj_json = {'display_name': bud_obj.name,                  
                    'taxid': int(bud_obj.id),
                    'rank': bud_obj.rank,    
                    'source': {'display_name': 'NCBI'},
                    'date_created': str(bud_obj.date_created),                  
                    'created_by': bud_obj.created_by}     

        common_name_str = bud_obj.common_name
        
        secondary_common_name = []
        if common_name_str != None:
            common_name_list = common_name_str.split("|") 
            name = common_name_list.pop(0)
            obj_json['common_name'] = name
            secondary_common_name = common_name_list

        #Load aliases
        obj_json['aliases'] = load_aliases(bud_obj, bud_session, secondary_common_name)
        
        #Load children
        obj_json['children'] = load_relations(bud_obj, bud_session)

        obj_json['urls'] = [{"display_name": 'NCBI Taxonomy',
                             "url_type": 'NCBI Taxonomy',
                             "source": {'display_name': 'NCBI'},
                             "link": "http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id="+str(bud_obj.id)}]

        yield obj_json

    bud_session.close()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, taxonomy_starter, 'taxonomy', lambda x: x['display_name'])



