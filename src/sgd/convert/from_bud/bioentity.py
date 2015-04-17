from sqlalchemy.orm import joinedload

from src.sgd.convert import break_up_file
from src.sgd.convert.transformers import make_db_starter, make_file_starter

__author__ = 'kpaskov'


# --------------------- Convert Bioentity Quality ---------------------
def make_bioentity_quality_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.bud.feature import Annotation as OldAnnotation, FeatureProperty as OldFeatureProperty
    def bioentity_quality_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for old_annotation in bud_session.query(OldAnnotation).all():
            bioentity_id = old_annotation.feature_id

            if bioentity_id in id_to_bioentity:

                if old_annotation.qualifier is not None:
                    yield {'source': key_to_source['SGD'],
                                   'bioentity': id_to_bioentity[bioentity_id],
                                   'display_name': 'Qualifier',
                                   'value': old_annotation.qualifier,
                                   'date_created': old_annotation.date_created,
                                   'created_by': old_annotation.created_by}

                if old_annotation.name_description is not None:
                    yield {'source': key_to_source['SGD'],
                                   'bioentity': id_to_bioentity[bioentity_id],
                                   'display_name': 'Name Description',
                                   'value': old_annotation.name_description,
                                   'date_created': old_annotation.date_created,
                                   'created_by': old_annotation.created_by}

                if old_annotation.description is not None:
                    yield {'source': key_to_source['SGD'],
                                   'bioentity': id_to_bioentity[bioentity_id],
                                   'display_name': 'Description',
                                   'value': old_annotation.description,
                                   'date_created': old_annotation.date_created,
                                   'created_by': old_annotation.created_by}

                if old_annotation.genetic_position is not None:
                    yield {'source': key_to_source['SGD'],
                                   'bioentity': id_to_bioentity[bioentity_id],
                                   'display_name': 'Genetic Position',
                                   'value': old_annotation.genetic_position,
                                   'date_created': old_annotation.date_created,
                                   'created_by': old_annotation.created_by}

                if old_annotation.headline is not None:
                    yield {'source': key_to_source['SGD'],
                                   'bioentity': id_to_bioentity[bioentity_id],
                                   'display_name': 'Headline',
                                   'value': old_annotation.headline,
                                   'date_created': old_annotation.date_created,
                                   'created_by': old_annotation.created_by}
            else:
                #print 'Could not find  bioentity: ' + str(bioentity_id)
                yield None

        for bioentity in id_to_bioentity.values():
            yield {'source': key_to_source['SGD'],
                               'bioentity': bioentity,
                               'display_name': 'Gene Name',
                               'value': bioentity.gene_name}

            yield {'source': key_to_source['SGD'],
                               'bioentity': bioentity,
                               'display_name': 'Feature Type',
                               'value': bioentity.locus_type}

            yield {'source': key_to_source['SGD'],
                               'bioentity': bioentity,
                               'display_name': 'ID',
                               'value': bioentity.id}

        for feature_property in bud_session.query(OldFeatureProperty).all():
            bioentity_id = feature_property.feature_id
            if bioentity_id in id_to_bioentity:
                yield {'source': key_to_source['SGD'],
                               'bioentity': id_to_bioentity[bioentity_id],
                               'display_name': feature_property.property_type,
                               'value': feature_property.property_value}
            else:
                #print 'Could not find bioentity: ' + str(bioentity_id)
                yield None

        bud_session.close()
        nex_session.close()
    return bioentity_quality_starter


# --------------------- Convert Relation ---------------------
def make_bioentity_relation_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.feature import FeatRel

    def bioentity_relation_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for relation in bud_session.query(FeatRel).filter_by(relationship_type='pair').all():
            yield {'source': key_to_source['SGD'],
                           'relation_type': 'paralog',
                           'parent_id': relation.parent_id,
                           'child_id': relation.child_id}

            yield {'source': key_to_source['SGD'],
                           'relation_type': 'paralog',
                           'parent_id': relation.child_id,
                           'child_id': relation.parent_id}

        bud_session.close()
        nex_session.close()
    return bioentity_relation_starter
