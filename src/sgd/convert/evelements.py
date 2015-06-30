from sqlalchemy.orm import joinedload

from src.sgd.convert.transformers import make_file_starter, \
    make_obo_file_starter
from src.sgd.convert import create_format_name
from src.sgd.model.nex.misc import Source


__author__ = 'kpaskov'

#Recorded times: 
#Maitenance (cherry-vm08): 0:01, 
#First Load (sgd-ng1): :09, :10
#1.23.14 Maitenance (sgd-dev): :06


# --------------------- Convert Alias Reference ---------------------
def make_alias_reference_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Bioentityalias
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.reference import Reflink as OldReflink
    from src.sgd.model.bud.feature import AliasFeature as OldAliasFeature
    from src.sgd.model.bud.general import DbxrefFeat as OldDbxrefFeat
    def alias_reference_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_alias = dict([(x.unique_key(), x) for x in nex_session.query(Bioentityalias).all()])

        feat_alias_id_to_reflinks = dict()
        for reflink in bud_session.query(OldReflink).filter_by(tab_name='FEAT_ALIAS').all():
            if reflink.primary_key in feat_alias_id_to_reflinks:
                feat_alias_id_to_reflinks[reflink.primary_key].append(reflink)
            else:
                feat_alias_id_to_reflinks[reflink.primary_key] = [reflink]

        dbxref_feat_id_to_reflinks = dict()
        for reflink in bud_session.query(OldReflink).filter_by(tab_name='DBXREF_FEAT').all():
            if reflink.primary_key in dbxref_feat_id_to_reflinks:
                dbxref_feat_id_to_reflinks[reflink.primary_key].append(reflink)
            else:
                dbxref_feat_id_to_reflinks[reflink.primary_key] = [reflink]

        for old_alias in bud_session.query(OldAliasFeature).options(joinedload('alias')).all():
            bioentity_id = old_alias.feature_id
            alias_key = 'BIOENTITY', old_alias.alias_name, str(bioentity_id), 'Alias' if old_alias.alias_type == 'Uniform' or old_alias.alias_type == 'Non-uniform' else old_alias.alias_type

            if old_alias.id in feat_alias_id_to_reflinks:
                for reflink in feat_alias_id_to_reflinks[old_alias.id]:
                    reference_id = reflink.reference_id
                    if alias_key in key_to_alias and reference_id in id_to_reference:
                        yield {
                            'alias_id': key_to_alias[alias_key].id,
                            'reference_id': id_to_reference[reference_id].id,
                        }
                    else:
                        print 'Reference or alias not found: ' + str(reference_id) + ' ' + str(alias_key)

        for old_dbxref_feat in bud_session.query(OldDbxrefFeat).options(joinedload(OldDbxrefFeat.dbxref), joinedload('dbxref.dbxref_urls')).all():
            if old_dbxref_feat.dbxref.dbxref_type != 'DBID Primary':
                bioentity_id = old_dbxref_feat.feature_id
                alias_key = 'BIOENTITY', old_dbxref_feat.dbxref.dbxref_id, str(bioentity_id), old_dbxref_feat.dbxref.dbxref_type

                if old_dbxref_feat.id in dbxref_feat_id_to_reflinks:
                    for reflink in dbxref_feat_id_to_reflinks[old_dbxref_feat.id]:
                        reference_id = reflink.reference_id
                        if alias_key in key_to_alias and reference_id in id_to_reference:
                            yield {
                                'alias_id': key_to_alias[alias_key].id,
                                'reference_id': id_to_reference[reference_id].id,
                            }
                        else:
                            print 'Reference or alias not found: ' + str(reference_id) + ' ' + str(alias_key)

        bud_session.close()
        nex_session.close()
    return alias_reference_starter

# --------------------- Convert Relation Reference ---------------------
def make_relation_reference_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Bioentityrelation
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.reference import Reflink as OldReflink
    from src.sgd.model.bud.feature import FeatRel
    def alias_reference_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_relation = dict([(x.unique_key(), x) for x in nex_session.query(Bioentityrelation).all()])

        relation_id_to_reflinks = dict()
        for reflink in bud_session.query(OldReflink).filter_by(tab_name='FEAT_RELATIONSHIP').all():
            if reflink.primary_key in relation_id_to_reflinks:
                relation_id_to_reflinks[reflink.primary_key].append(reflink)
            else:
                relation_id_to_reflinks[reflink.primary_key] = [reflink]

        for old_relation in bud_session.query(FeatRel).filter_by(relationship_type='pair').all():
             relation1_key = (str(old_relation.parent_id) + ' - ' + str(old_relation.child_id), 'BIOENTITY', 'paralog')
             relation2_key = (str(old_relation.child_id) + ' - ' + str(old_relation.parent_id), 'BIOENTITY', 'paralog')

             if old_relation.id in relation_id_to_reflinks:
                for reflink in relation_id_to_reflinks[old_relation.id]:
                    reference_id = reflink.reference_id
                    if relation1_key in key_to_relation and reference_id in id_to_reference:
                        yield {
                            'relation_id': key_to_relation[relation1_key].id,
                            'reference_id': id_to_reference[reference_id].id,
                        }
                    else:
                        print 'Reference or relation not found: ' + str(reference_id) + ' ' + str(relation1_key)

                    if relation2_key in key_to_relation and reference_id in id_to_reference:
                        yield {
                            'relation_id': key_to_relation[relation2_key].id,
                            'reference_id': id_to_reference[reference_id].id,
                        }
                    else:
                        print 'Reference or relation not found: ' + str(reference_id) + ' ' + str(relation2_key)

        bud_session.close()
        nex_session.close()
    return alias_reference_starter

bad_quality_references = {37408}
def make_quality_reference_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source, Strain, Quality
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.reference import Reflink as OldReflink
    from src.sgd.model.bud.feature import Annotation as OldAnnotation, FeatureProperty as OldFeatureProperty
    def quality_reference_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Bioentity).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_quality = dict([(x.unique_key(), x) for x in nex_session.query(Quality).all()])

        for reflink in bud_session.query(OldReflink).filter_by(tab_name='FEAT_ANNOTATION').all():
            if reflink.col_name != 'DNA binding motif':
                if reflink.primary_key in id_to_bioentity:
                    reference_id = reflink.reference_id
                    if reference_id not in bad_quality_references:
                        quality_key = None
                        if reflink.col_name == 'QUALIFIER':
                            quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Qualifier')
                        elif reflink.col_name == 'NAME_DESCRIPTION':
                            quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Name Description')
                        elif reflink.col_name == 'DESCRIPTION':
                            quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Description')
                        elif reflink.col_name == 'GENETIC_POSITION':
                            quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Genetic Position')
                        elif reflink.col_name == 'HEADLINE':
                            quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Headline')

                        if quality_key is None:
                            print 'Column not found: ' + reflink.col_name
                        elif quality_key in key_to_quality and reference_id in id_to_reference:
                            yield {
                                    'quality_id': key_to_quality[quality_key].id,
                                    'reference_id': id_to_reference[reference_id].id,
                                 }
                        else:
                            print 'Quality or reference not found: ' + str(quality_key) + ' ' + str(reference_id)
                else:
                    #print 'Bioentity not found: ' + str(reflink.primary_key)
                    yield None

        id_to_feat_property = dict([(x.id, x) for x in bud_session.query(OldFeatureProperty).all()])
        for reflink in bud_session.query(OldReflink).filter_by(tab_name='FEAT_PROPERTY').all():
            if reflink.primary_key in id_to_feat_property:
                feat_property = id_to_feat_property[reflink.primary_key]
                reference_id = reflink.reference_id
                if reference_id not in bad_quality_references:
                    quality_key = (str(feat_property.feature_id), 'BIOENTITY', feat_property.property_type)

                    if quality_key in key_to_quality and reference_id in id_to_reference:
                        yield {
                                'quality_id': key_to_quality[quality_key].id,
                                'reference_id': id_to_reference[reference_id].id,
                             }
                    else:
                        print 'Quality or reference not found: ' + str(quality_key) + ' ' + str(reference_id)
            else:
                print 'Feature property not found: ' + str(reflink.primary_key)

        for reflink in bud_session.query(OldReflink).filter_by(tab_name='FEATURE').all():
            if reflink.primary_key in id_to_bioentity:
                quality_key = None
                reference_id = reflink.reference_id
                if reference_id not in bad_quality_references:
                    if reflink.col_name == 'GENE_NAME':
                        quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Gene Name')
                    elif reflink.col_name == 'FEATURE_TYPE':
                        quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Feature Type')
                    elif reflink.col_name == 'FEATURE_NO':
                        quality_key = (str(reflink.primary_key), 'BIOENTITY', 'ID')

                    if quality_key is None:
                        print 'Column not found : ' + reflink.col_name
                    elif quality_key in key_to_quality and reference_id in id_to_reference:
                        yield {
                                'quality_id': key_to_quality[quality_key].id,
                                'reference_id': id_to_reference[reference_id].id,
                             }
                    else:
                        print 'Quality or reference not found: ' + str(quality_key) + ' ' + str(reference_id)
            else:
                #print 'Bioentity not found: ' + str(reflink.primary_key)
                yield None

        bud_session.close()
        nex_session.close()
    return quality_reference_starter