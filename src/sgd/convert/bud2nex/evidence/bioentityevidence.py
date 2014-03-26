import logging
import sys

from src.sgd.convert import OutputCreator, create_or_update


__author__ = 'kpaskov'

# --------------------- Convert Qualifier Evidence ---------------------
def create_bioentity_evidence(old_annotation, id_to_bioentity, key_to_strain, key_to_source, id_to_reference, annotation_id_to_reflinks):
    from src.sgd.model.nex.evidence import Bioentityevidence

    bioentity_evidences = []

    bioentity = None if old_annotation.feature_id not in id_to_bioentity else id_to_bioentity[old_annotation.feature_id]
    strain = key_to_strain['S288C']
    source = key_to_source['SGD']

    qualifier = str(old_annotation.qualifier)
    name_description = str(old_annotation.name_description)
    description = str(old_annotation.description)
    genetic_position = str(old_annotation.genetic_position)
    headline = str(old_annotation.headline)
    feat_attribute = str(old_annotation.attribute)

    qualifier_ref = None
    name_description_ref = None
    description_ref = None
    genetic_position_ref = None
    headline_ref = None
    feat_attribute_ref = None
    reflinks = [] if old_annotation.feature_id not in annotation_id_to_reflinks else annotation_id_to_reflinks[old_annotation.feature_id]
    for reflink in reflinks:
        if reflink.col_name == 'QUALIFIER':
            qualifier_ref = None if reflink.reference_id not in id_to_reference else id_to_reference[reflink.reference_id]
        if reflink.col_name == 'NAME_DESCRIPTION':
            name_description_ref = None if reflink.reference_id not in id_to_reference else id_to_reference[reflink.reference_id]
        if reflink.col_name == 'DESCRIPTION':
            description_ref = None if reflink.reference_id not in id_to_reference else id_to_reference[reflink.reference_id]
        if reflink.col_name == 'GENETIC_POSITION':
            genetic_position_ref = None if reflink.reference_id not in id_to_reference else id_to_reference[reflink.reference_id]
        if reflink.col_name == 'HEADLINE':
            headline_ref = None if reflink.reference_id not in id_to_reference else id_to_reference[reflink.reference_id]
        if reflink.col_name == 'FEAT_ATTRIBUTE':
            feat_attribute_ref = None if reflink.reference_id not in id_to_reference else id_to_reference[reflink.reference_id]

    if qualifier is not None:
        bioentity_evidences.append(Bioentityevidence(source, qualifier_ref, strain, bioentity, "Qualifier", qualifier, old_annotation.date_created, old_annotation.created_by))
    if name_description is not None:
        bioentity_evidences.append(Bioentityevidence(source, name_description_ref, None, bioentity, "Name Description", name_description, old_annotation.date_created, old_annotation.created_by))
    if description is not None:
        bioentity_evidences.append(Bioentityevidence(source, description_ref, None, bioentity, "Description", description, old_annotation.date_created, old_annotation.created_by))
    if genetic_position is not None:
        bioentity_evidences.append(Bioentityevidence(source, genetic_position_ref, strain, bioentity, "Genetic Position", genetic_position, old_annotation.date_created, old_annotation.created_by))
    if headline is not None:
        bioentity_evidences.append(Bioentityevidence(source, headline_ref, None, bioentity, "Headline", headline, old_annotation.date_created, old_annotation.created_by))
    if feat_attribute is not None:
        bioentity_evidences.append(Bioentityevidence(source, feat_attribute_ref, strain, bioentity, "Silenced Gene", 'True', old_annotation.date_created, old_annotation.created_by))

    return bioentity_evidences

def create_bioentity_evidence_from_reflink(reflink, id_to_bioentity, key_to_strain, key_to_source, id_to_reference):
    from src.sgd.model.nex.evidence import Bioentityevidence

    bioentity_evidences = []

    bioentity = None if reflink.primary_key not in id_to_bioentity else id_to_bioentity[reflink.primary_key]
    strain = key_to_strain['S288C']
    source = key_to_source['SGD']
    reference = None if reflink.reference_id not in id_to_reference else id_to_reference[reflink.reference_id]

    if reflink.col_name == 'GENE_NAME':
        bioentity_evidences.append(Bioentityevidence(source, reference, strain, bioentity, "Gene Name", bioentity.gene_name, reflink.date_created, reflink.created_by))
    if reflink.col_name == 'FEATURE_NO':
        bioentity_evidences.append(Bioentityevidence(source, reference, strain, bioentity, '-', '-', reflink.date_created, reflink.created_by))
    if reflink.col_name == 'FEATURE_TYPE':
        bioentity_evidences.append(Bioentityevidence(source, reference, strain, bioentity, "Feature Type", bioentity.locus_type, reflink.date_created, reflink.created_by))

    return bioentity_evidences

def create_bioentity_evidence_from_feature_property(feature_property, id_to_bioentity, key_to_strain, key_to_source, id_to_reference, feature_property_id_to_reflinks):
    from src.sgd.model.nex.evidence import Bioentityevidence

    bioentity_evidences = []

    bioentity = None if feature_property.feature_id not in id_to_bioentity else id_to_bioentity[feature_property.feature_id]
    strain = key_to_strain['S288C']
    source = key_to_source[feature_property.source]

    if feature_property.id in feature_property_id_to_reflinks:
        reflinks = feature_property_id_to_reflinks[feature_property.id]
        for reflink in reflinks:
            reference = None if reflink.reference_id not in id_to_reference else id_to_reference[reflink.reference_id]
            bioentity_evidences.append(Bioentityevidence(source, reference, strain, bioentity, feature_property.property_type, feature_property.property_value, feature_property.date_created, feature_property.created_by))
    else:
        bioentity_evidences.append(Bioentityevidence(source, None, strain, bioentity, feature_property.property_type, feature_property.property_value, feature_property.date_created, feature_property.created_by))
    return bioentity_evidences

def convert_bioentity_evidence(old_session_maker, new_session_maker):
    from src.sgd.model.nex.bioentity import Bioentity as NewBioentity
    from src.sgd.model.nex.evidence import Bioentityevidence as NewBioentityevidence
    from src.sgd.model.nex.misc import Strain as NewStrain, Source as NewSource
    from src.sgd.model.nex.reference import Reference as NewReference
    from src.sgd.model.bud.feature import Annotation as OldAnnotation, FeatureProperty as OldFeatureProperty
    from src.sgd.model.bud.reference import Reflink as OldReflink

    old_session = None
    new_session = None
    log = logging.getLogger('convert.bioentity.evidence')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewBioentityevidence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['reference_id', 'experiment_id', 'strain_id', 'source_id',
                           'bioentity_id', 'info_key', 'info_value']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(NewStrain).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        
        #Grab old objects
        old_session = old_session_maker()
        old_objs = old_session.query(OldAnnotation).all()

        old_reflinks = old_session.query(OldReflink).filter_by(tab_name='FEAT_ANNOTATION').all()
        annotation_id_to_reflinks = dict()
        for reflink in old_reflinks:
            if reflink.primary_key in annotation_id_to_reflinks:
                annotation_id_to_reflinks[reflink.primary_key].append(reflink)
            else:
                annotation_id_to_reflinks[reflink.primary_key] = [reflink]
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_bioentity_evidence(old_obj, id_to_bioentity, key_to_strain, key_to_source, id_to_reference, annotation_id_to_reflinks)
                
            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    obj_key = newly_created_obj.unique_key()
                    obj_id = newly_created_obj.id
                    current_obj_by_id = None if obj_id not in id_to_current_obj else id_to_current_obj[obj_id]
                    current_obj_by_key = None if obj_key not in key_to_current_obj else key_to_current_obj[obj_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)

        output_creator.finished('1/3')
        new_session.commit()

        old_objs = old_session.query(OldReflink).filter_by(tab_name='FEATURE').all()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_bioentity_evidence_from_reflink(old_obj, id_to_bioentity, key_to_strain, key_to_source, id_to_reference)

            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    obj_key = newly_created_obj.unique_key()
                    obj_id = newly_created_obj.id
                    current_obj_by_id = None if obj_id not in id_to_current_obj else id_to_current_obj[obj_id]
                    current_obj_by_key = None if obj_key not in key_to_current_obj else key_to_current_obj[obj_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)

        output_creator.finished('2/3')
        new_session.commit()

        feature_property_id_to_reflinks = dict()
        for reflink in old_session.query(OldReflink).filter_by(tab_name='FEAT_PROPERTY').all():
            if reflink.primary_key in feature_property_id_to_reflinks:
                feature_property_id_to_reflinks[reflink.primary_key].append(reflink)
            else:
                feature_property_id_to_reflinks[reflink.primary_key] = [reflink]

        old_objs = old_session.query(OldFeatureProperty).all()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_bioentity_evidence_from_feature_property(old_obj, id_to_bioentity, key_to_strain, key_to_source, id_to_reference, feature_property_id_to_reflinks)

            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    obj_key = newly_created_obj.unique_key()
                    obj_id = newly_created_obj.id
                    current_obj_by_id = None if obj_id not in id_to_current_obj else id_to_current_obj[obj_id]
                    current_obj_by_key = None if obj_key not in key_to_current_obj else key_to_current_obj[obj_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)

        output_creator.finished('3/3')
        new_session.commit()
                        
        #Delete untouched objs
        for untouched_obj_id  in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()
        
        #Commit
        output_creator.finished()
        new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()

# ---------------------Convert------------------------------
def convert(old_session_maker, new_session_maker):
    convert_bioentity_evidence(old_session_maker, new_session_maker)