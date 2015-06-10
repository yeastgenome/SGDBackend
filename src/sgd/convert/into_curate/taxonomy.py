from src.sgd.convert.into_curate import basic_convert, remove_nones
from sqlalchemy.orm import joinedload


__author__ = 'kpaskov'


def load_aliases(bud_obj, bud_session):
    from src.sgd.model.bud.taxonomy import TaxonomyAlias

    aliases = []
    for bud_obj in bud_session.query(TaxonomyAlias).filter_by(taxon_id=bud_obj.id).all():
        aliases.append(remove_nones({
            "name": bud_obj.synonym,
            "alias_type": 'Synonym',
            'source': {'name': '-'}
        }))
    return aliases

def load_relations(bud_obj, bud_session):
    from src.sgd.model.bud.taxonomy import TaxonomyRelation

    relations = []
    for bud_obj in bud_session.query(TaxonomyRelation).filter_by(parent_id=bud_obj.id).filter_by(generation=1).all():
        relations.append(remove_nones({
            "name": bud_obj.child.name,
            'source': {'name': '-'},
            "relation_type": 'is a'
        }))
    return relations


def taxonomy_starter(bud_session_maker):
    from src.sgd.model.bud.taxonomy import TaxonomyRelation
    bud_session = bud_session_maker()

    for relation in bud_session.query(TaxonomyRelation).options(joinedload(TaxonomyRelation.child)).filter_by(parent_id=4893).all():
        bud_obj = relation.child
        obj_json = remove_nones({'name': bud_obj.name,
                                 'bud_id': bud_obj.id,
                                 'ncbi_taxon_id': bud_obj.id,
                                 'common_name': bud_obj.common_name,
                                 'description': bud_obj.common_name,
                                 'rank': bud_obj.rank,
                                 'source': {'name': '-'},
                                 'date_created': str(bud_obj.date_created),
                                 'created_by': bud_obj.created_by})

        #Load aliases
        obj_json['aliases'] = load_aliases(bud_obj, bud_session)

        #Load children
        obj_json['children'] = load_relations(bud_obj, bud_session)

        yield obj_json

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, taxonomy_starter, 'taxonomy', lambda x: x['name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')

