import logging
import sys

from src.sgd.convert import OutputCreator, create_format_name, create_or_update, break_up_file


__author__ = 'kpaskov'



# --------------------- Convert Paragraph ---------------------
def create_paragraph(gofeature, key_to_bioentity, key_to_source):
    from src.sgd.model.nex.paragraph import Paragraph

    format_name = create_format_name(gofeature.feature.name)
    bioentity_key = (format_name, 'LOCUS')

    bioentity = None if bioentity_key not in key_to_bioentity else key_to_bioentity[bioentity_key]
    source = key_to_source[gofeature.source]
    date_last_reviewed = gofeature.date_last_reviewed

    if bioentity is not None and source is not None:
        paragraph = Paragraph('GO', source, bioentity, str(date_last_reviewed), gofeature.date_created, gofeature.created_by)
        return [paragraph]
    else:
        return []

def convert_paragraph(old_session_maker, new_session_maker):
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.paragraph import Paragraph
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.go import GoFeature as OldGoFeature

    new_session = None
    old_session = None
    log = logging.getLogger('convert.go.paragraph')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()
        old_session = old_session_maker()

        #Values to check
        values_to_check = ['text', 'source_id', 'date_created', 'created_by', 'display_name']

        #Grab cached dictionaries
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])

        #Grab all current objects
        current_objs = new_session.query(Paragraph).filter(Paragraph.class_type == 'GO').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())

        already_seen = set()

        old_objs = old_session.query(OldGoFeature).all()
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_paragraph(old_obj, key_to_bioentity, key_to_source)

            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    if unique_key not in already_seen:
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                        already_seen.add(unique_key)

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

# --------------------- Convert Paragraph ---------------------
def create_paragraph(row, key_to_bioentity, key_to_source):
    from src.sgd.model.nex.paragraph import Paragraph

    bioent_format_name = row[0]
    bioent_key = (bioent_format_name, 'LOCUS')
    bioent = None if bioent_key not in key_to_bioentity else key_to_bioentity[bioent_key]
    source = key_to_source['SGD']

    text = row[2]

    paragraph = Paragraph('REGULATION', source, bioent, text, None, None)
    return [paragraph]

def convert_paragraph(new_session_maker):
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.paragraph import Paragraph
    from src.sgd.model.nex.misc import Source

    new_session = None
    log = logging.getLogger('convert.regulation.paragraph')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = ['text']

        #Grab cached dictionaries
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])

        #Grab all current objects
        current_objs = new_session.query(Paragraph).filter(Paragraph.class_type == 'REGULATION').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())

        old_objs = break_up_file('src/sgd/convert/data/Reg_Summary_Paragraphs04282013.txt')
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_paragraph(old_obj, key_to_bioentity, key_to_source)

            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)

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

# --------------------- Convert ParagraphReference ---------------------
def create_paragraph_reference(row, key_to_bioentity, key_to_paragraph, pubmed_id_to_reference, key_to_source):
    from src.sgd.model.nex.paragraph import ParagraphReference

    bioent_format_name = row[0]
    bioent_key = (bioent_format_name, 'LOCUS')
    if bioent_key not in key_to_bioentity:
        bioent_key = (bioent_format_name, 'BIOENTITY')
        if bioent_key not in key_to_bioentity:
            print 'Bioentity does not exist. ' + str(bioent_format_name)
            return None
    bioent = key_to_bioentity[bioent_key]

    paragraph_key = (bioent.format_name, 'REGULATION')
    if paragraph_key not in key_to_paragraph:
        print 'Paragraph does not exist. ' + str(paragraph_key)
        return None
    paragraph = key_to_paragraph[paragraph_key]

    paragraph_references = []

    if len(row) == 4:
        pubmed_ids = row[3].split('|')
        for pubmed_id in pubmed_ids:
            num_pubmed_id = ''
            if pubmed_id != '':
                num_pubmed_id = int(pubmed_id.strip())
            if num_pubmed_id not in pubmed_id_to_reference:
                print 'Reference does not exist. ' + str(num_pubmed_id)
                return None
            reference = pubmed_id_to_reference[num_pubmed_id]
            source = key_to_source['SGD']
            paragraph_references.append(ParagraphReference(source, paragraph, reference, 'REGULATION', None, None))


    return paragraph_references

def convert_paragraph_reference(new_session_maker):
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.paragraph import Paragraph, ParagraphReference
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.reference import Reference

    new_session = None
    log = logging.getLogger('convert.regulation.paragraph_reference')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = []

        #Grab cached dictionaries
        key_to_bioentity = dict([(x.unique_key(), x) for x in new_session.query(Bioentity).all()])
        key_to_paragraph = dict([(x.unique_key(), x) for x in new_session.query(Paragraph).filter(Paragraph.class_type == 'REGULATION').all()])
        pubmed_id_to_reference = dict([(x.pubmed_id, x) for x in new_session.query(Reference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])

        #Grab all current objects
        current_objs = new_session.query(ParagraphReference).filter(ParagraphReference.class_type == 'REGULATION').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        untouched_obj_ids = set(id_to_current_obj.keys())

        used_unique_keys = set()

        old_objs = break_up_file('src/sgd/convert/data/Reg_Summary_Paragraphs04282013.txt')
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_paragraph_reference(old_obj, key_to_bioentity, key_to_paragraph, pubmed_id_to_reference, key_to_source)

            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    unique_key = newly_created_obj.unique_key()
                    if unique_key not in used_unique_keys:
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        used_unique_keys.add(unique_key)

                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)

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

# ---------------------Convert------------------------------
def convert(old_session_maker, new_session_maker):
    convert_evidence(old_session_maker, new_session_maker, 100)

    #convert_paragraph(old_session_maker, new_session_maker)
    
    #from src.sgd.model.nex.bioconcept import Go
    #from src.sgd.model.nex.evidence import Goevidence
    #get_bioent_ids_f = lambda x: [x.bioentity_id]
    #convert_bioentity_reference(new_session_maker, Goevidence, 'GO', 'convert.go.bioentity_reference', 10000, get_bioent_ids_f)

    #convert_biofact(new_session_maker, Goevidence, Go, 'GO', 'convert.go.biofact', 10000)