import logging
import sys

from sqlalchemy.orm import joinedload

from src.sgd.convert import OutputCreator, create_or_update, page_query


__author__ = 'kpaskov'

#1.23.14 Maitenance (sgd-dev): 1:15:15

# --------------------- Convert Literature Evidence ---------------------
def create_litevidence(litguide, id_to_reference, id_to_bioentity, key_to_source):
    from src.sgd.model.nex.evidence import Literatureevidence
    from src.sgd.model.nex.archive import ArchiveLiteratureevidence

    reference_id = litguide.reference_id
    reference = None if reference_id not in id_to_reference else id_to_reference[reference_id]
    if reference is None:
        print 'Reference not found: ' + str(reference_id)
        return []
    source = key_to_source['SGD']
    topic = litguide.topic

    literature_evidences = []
    if len(litguide.litguide_features) > 0:
        for litguide_feature in litguide.litguide_features:
            bioentity_id = litguide_feature.feature_id
            bioentity = None if bioentity_id not in id_to_bioentity else id_to_bioentity[bioentity_id]
            if bioentity is None:
                print 'Bioentity not found: ' + str(bioentity_id)
            else:
                if topic in {'Additional Literature', 'Primary Literature', 'Omics', 'Reviews'}:
                    literature_evidences.append(Literatureevidence(source, reference, bioentity, topic,
                                                       litguide_feature.date_created, litguide_feature.created_by))
                else:
                    literature_evidences.append(ArchiveLiteratureevidence(source, reference, bioentity, topic,
                                                       litguide_feature.date_created, litguide_feature.created_by))
    else:
        if topic in {'Additional Literature', 'Primary Literature', 'Omics', 'Reviews'}:
            literature_evidences.append(Literatureevidence(source, reference, None, topic,
                                                       litguide.date_created, litguide.created_by))
        else:
            literature_evidences.append(ArchiveLiteratureevidence(source, reference, None, topic,
                                                       litguide.date_created, litguide.created_by))
    return literature_evidences

def convert_litevidence(old_session_maker, new_session_maker, chunk_size):
    from src.sgd.model.nex.evidence import Literatureevidence as NewLiteratureevidence
    from src.sgd.model.nex.archive import ArchiveLiteratureevidence as NewArchiveLiteratureevidence
    from src.sgd.model.nex.reference import Reference as NewReference
    from src.sgd.model.nex.misc import Source as NewSource
    from src.sgd.model.nex.bioentity import Bioentity as NewBioentity
    from src.sgd.model.bud.reference import Litguide as OldLitguide

    old_session = None
    new_session = None
    log = logging.getLogger('convert.literature.evidence')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()      
                  
        #Values to check
        values_to_check = ['experiment_id', 'reference_id', 'class_type', 'strain_id',
                       'source_id', 'topic', 'bioentity_id']

        current_objs = new_session.query(NewLiteratureevidence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        current_arch_objs = new_session.query(NewArchiveLiteratureevidence).all()
        id_to_current_obj.update([(x.id, x) for x in current_arch_objs])
        key_to_current_obj.update([(x.unique_key(), x) for x in current_arch_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())

        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])

        count = 0
        for old_obj in page_query(old_session.query(OldLitguide).options(joinedload(OldLitguide.litguide_features)), chunk_size):
            #Convert old objects into new ones
            newly_created_objs = create_litevidence(old_obj, id_to_reference, id_to_bioentity, key_to_source)
                    
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    
                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)

            count += 1
            if count % chunk_size == 0:
                #Commit
                output_creator.finished(str(1.0*count/chunk_size))
                new_session.commit()
                            
        #Delete untouched objs
        for untouched_obj_id in untouched_obj_ids:
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

def convert(old_session_maker, new_session_maker):
    convert_litevidence(old_session_maker, new_session_maker, 1000)
    
    #from src.sgd.model.nex.evidence import Literatureevidence
    #get_bioent_ids_f = lambda x: [x.bioentity_id]
    #convert_bioentity_reference(new_session_maker, Literatureevidence, 'PRIMARY_LITERATURE', 'convert.literature.primary_bioentity_reference',
    #                            100000, get_bioent_ids_f, filter_f = lambda x: x.topic=='Primary Literature')
    #convert_bioentity_reference(new_session_maker, Literatureevidence, 'ADDITIONAL_LITERATURE', 'convert.literature.additional_bioentity_reference',
    #                            100000, get_bioent_ids_f, filter_f = lambda x: x.topic=='Additional Literature')
    #convert_bioentity_reference(new_session_maker, Literatureevidence, 'OMICS_LITERATURE', 'convert.literature.omics_bioentity_reference',
    #                            100000, get_bioent_ids_f, filter_f = lambda x: x.topic=='Omics')
    #convert_bioentity_reference(new_session_maker, Literatureevidence, 'REVIEW_LITERATURE', 'convert.literature.review_bioentity_reference',
    #                            100000, get_bioent_ids_f, filter_f = lambda x: x.topic=='Reviews')
