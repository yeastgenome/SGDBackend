'''
Created on May 31, 2013

@author: kpaskov
'''
import logging
import sys

from convert_utils import create_or_update, create_format_name
from convert_utils.output_manager import OutputCreator
from mpmath import ceil
from sqlalchemy.orm import joinedload


#Recorded times: 
#Maitenance (cherry-vm08): 2:56, 2:59 
#First Load (sgd-ng1): 4:08, 3:49
#Maitenance (sgd-ng1): 4:17
    
"""
--------------------- Convert Bioentity Tabs ---------------------
"""

def create_bioentitytabs(locus):
    from model_new_schema.auxiliary import Locustabs
    
    show_summary = 1
    show_history = 1
    show_sequence = 1
    show_wiki = 1
    
    if locus.bioent_status != 'Active':
        return [Locustabs(locus.id, show_summary, show_sequence, show_history, 0,
                          0, 0, 0, 0, 0, 0, show_wiki)]
    
    show_literature = 1
    
    no_go = {'ARS', 'ARS_CONSENSUS_SEQUENCE', 'MATING_LOCUS', 'X_ELEMENT_COMBINATORIAL_REPEATS',
             'X_ELEMENT_CORE_SEQUENCE', "Y'_ELEMENT", 'CENTROMERE', 'LONG_TERMINAL_REPEAT',
             'TELOMERE', 'TELOMERIC_REPEAT', 'RETROTRANSPOSON', 'GENE_CASSETTE', 'MULTIGENE_LOCUS'}
    show_go = 0 if locus.locus_type in no_go else 1
    
    no_phenotype = {'ARS', 'ARS_CONSENSUS_SEQUENCE', 'MATING_LOCUS', 'X_ELEMENT_COMBINATORIAL_REPEATS',
             'X_ELEMENT_CORE_SEQUENCE', "Y'_ELEMENT", 'CENTROMERE', 'LONG_TERMINAL_REPEAT',
             'TELOMERE', 'TELOMERIC_REPEAT', 'RETROTRANSPOSON', 'GENE_CASSETTE'}
    show_phenotype = 0 if locus.locus_type in no_phenotype else 1
    
    no_interactions = {'ARS', 'ARS_CONSENSUS_SEQUENCE', 'MATING_LOCUS', 'X_ELEMENT_COMBINATORIAL_REPEATS',
             'X_ELEMENT_CORE_SEQUENCE', "Y'_ELEMENT", 'CENTROMERE', 'LONG_TERMINAL_REPEAT',
             'TELOMERE', 'TELOMERIC_REPEAT', 'RETROTRANSPOSON', 'GENE_CASSETTE', 'MULTIGENE_LOCUS',
             'NOT_IN_SYSTEMATIC_SEQUENCE_OF_S288C', 'NOT_PHYSICALLY_MAPPED'}
    show_interactions = 0 if locus.locus_type in no_interactions else 1
    
    no_expression = {'ARS', 'ARS_CONSENSUS_SEQUENCE', 'MATING_LOCUS', 'X_ELEMENT_COMBINATORIAL_REPEATS',
             'X_ELEMENT_CORE_SEQUENCE', "Y'_ELEMENT", 'CENTROMERE', 'LONG_TERMINAL_REPEAT',
             'TELOMERE', 'TELOMERIC_REPEAT', 'RETROTRANSPOSON', 'GENE_CASSETTE', 'MULTIGENE_LOCUS',
             'NOT_IN_SYSTEMATIC_SEQUENCE_OF_S288C', 'NOT_PHYSICALLY_MAPPED', 'TRANSPOSABLE_ELEMENT_GENE',
             'PSEUDOGENE', 'NCRNA', 'SNORNA', 'TRNA', 'RRNA', 'SNRNA'}
    show_expression = 0 if locus.locus_type in no_expression else 1
    
    no_regulation = {'ARS', 'ARS_CONSENSUS_SEQUENCE', 'MATING_LOCUS', 'X_ELEMENT_COMBINATORIAL_REPEATS',
             'X_ELEMENT_CORE_SEQUENCE', "Y'_ELEMENT", 'CENTROMERE', 'LONG_TERMINAL_REPEAT',
             'TELOMERE', 'TELOMERIC_REPEAT', 'RETROTRANSPOSON', 'GENE_CASSETTE', 'MULTIGENE_LOCUS',
             'NOT_IN_SYSTEMATIC_SEQUENCE_OF_S288C', 'NOT_PHYSICALLY_MAPPED'}
    show_regulation = 0 if locus.locus_type in no_regulation else 1
    
    no_protein = {'ARS', 'ARS_CONSENSUS_SEQUENCE', 'MATING_LOCUS', 'X_ELEMENT_COMBINATORIAL_REPEATS',
             'X_ELEMENT_CORE_SEQUENCE', "Y'_ELEMENT", 'CENTROMERE', 'LONG_TERMINAL_REPEAT',
             'TELOMERE', 'TELOMERIC_REPEAT', 'RETROTRANSPOSON', 'GENE_CASSETTE', 'MULTIGENE_LOCUS',
             'NOT_IN_SYSTEMATIC_SEQUENCE_OF_S288C', 'NOT_PHYSICALLY_MAPPED',
             'NCRNA', 'SNORNA', 'TRNA', 'RRNA', 'SNRNA'}
    show_protein = 0 if locus.locus_type in no_protein else 1
    
    
    return [Locustabs(locus.id, show_summary, show_sequence, show_history, show_literature,
                          show_go, show_phenotype, show_interactions, show_expression, 
                          show_regulation, show_protein, show_wiki)]

def convert_bioentitytabs(new_session_maker):
    from model_new_schema.bioentity import Locus
    from model_new_schema.auxiliary import Locustabs
    
    log = logging.getLogger('convert.bioentity_in_depth.bioentitytabs')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(Locustabs).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
                
        #Values to check
        values_to_check = ['summary', 'history', 'literature', 'go', 'phenotype', 'interactions', 'expression',
                           'regulation', 'protein', 'sequence', 'wiki']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        
        #Grab old objects
        new_session = new_session_maker()
        old_objs = new_session.query(Locus).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_bioentitytabs(old_obj)
                
            if newly_created_objs is not None:
                #Edit or add new objects
                for newly_created_obj in newly_created_objs:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    print current_obj_by_key.sequence
                    
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
        
    log.info('complete')


"""
--------------------- Convert Alias ---------------------
"""

def create_alias(old_alias, id_to_bioentity, key_to_source):
    from model_new_schema.bioentity import Bioentityalias

    bioentity_id = old_alias.feature_id
    bioentity = None if bioentity_id not in id_to_bioentity else id_to_bioentity[bioentity_id]

    display_name = old_alias.alias_name
    source = key_to_source['SGD']
    
    new_alias = Bioentityalias(display_name, source, old_alias.alias_type, bioentity,
                               old_alias.date_created, old_alias.created_by)
    return [new_alias] 

def convert_alias(old_session_maker, new_session_maker):
    from model_new_schema.bioentity import Bioentity as NewBioentity, Bioentityalias as NewBioentityalias
    from model_new_schema.evelements import Source as NewSource
    from model_old_schema.feature import AliasFeature as OldAliasFeature
    
    log = logging.getLogger('convert.bioentity_in_depth.bioentity_alias')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        #Grab all current objects
        new_session = new_session_maker()
        current_objs = new_session.query(NewBioentityalias).filter(NewBioentityalias.subclass_type == 'LOCUS').all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
        #Values to check
        values_to_check = ['source_id', 'category', 'created_by', 'date_created', 'subclass_type']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen_obj = set()
        
        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])

        #Grab old objects
        old_session = old_session_maker()
        
        #Grab old objects
        old_objs = old_session.query(OldAliasFeature).options(joinedload('alias')).all()
        
        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_alias(old_obj, id_to_bioentity, key_to_source)
                
            #Edit or add new objects
            for newly_created_obj in newly_created_objs:
                if newly_created_obj.unique_key() not in already_seen_obj:
                    current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                    current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                    create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    
                    if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_id.id)
                    if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                        untouched_obj_ids.remove(current_obj_by_key.id)
                already_seen_obj.add(newly_created_obj.unique_key())
                        
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
        
    log.info('complete')
    
"""
--------------------- Convert Url ---------------------
"""

def create_url(old_feat_url, old_webdisplay, id_to_bioentity, key_to_source):
    from model_new_schema.bioentity import Bioentityurl
        
    old_url = old_webdisplay.url
    url_type = old_url.url_type
    link = old_url.url
    
    feature = old_feat_url.feature
    if feature.id not in id_to_bioentity:
        return None
    
    bioentity_id = feature.id
    bioentity = None if bioentity_id not in id_to_bioentity else id_to_bioentity[bioentity_id]
    display_name = old_webdisplay.label_name
    source_key = old_url.source
    category = old_webdisplay.label_location
    
    source_key = create_format_name(source_key)
    source = None if source_key not in key_to_source else key_to_source[source_key]
    
    if url_type == 'query by SGDID':
        link = link.replace('_SUBSTITUTE_THIS_', str(feature.dbxref_id))
    elif url_type == 'query by SGD ORF name with anchor' or url_type == 'query by SGD ORF name' or url_type == 'query by ID assigned by database':
        link = link.replace('_SUBSTITUTE_THIS_', str(feature.name))
    else:
        print "Can't handle this url. " + str(old_url.url_type)
        return None
        
    url = Bioentityurl(display_name, link, source, category, bioentity, 
                                 old_url.date_created, old_url.created_by)
    return [url]

def create_url_from_dbxref(old_dbxref_feat, url_to_display, id_to_bioentity, key_to_source):
    from model_new_schema.bioentity import Bioentityurl
    
    urls = []
    
    old_urls = old_dbxref_feat.dbxref.urls
    feature_id = old_dbxref_feat.feature_id
    dbxref_id = old_dbxref_feat.dbxref.dbxref_id
    
    if feature_id in id_to_bioentity:
        bioentity = id_to_bioentity[feature_id]
        for old_url in old_urls:
            if old_url.id in url_to_display:
                old_webdisplay = url_to_display[old_url.id]
                url_type = old_url.url_type
                link = old_url.url
                
                if url_type == 'query by SGD ORF name with anchor' or url_type == 'query by SGD ORF name':
                    link = link.replace('_SUBSTITUTE_THIS_', id_to_bioentity[feature_id].format_name)
                elif url_type == 'query by ID assigned by database':
                    link = link.replace('_SUBSTITUTE_THIS_', str(dbxref_id))
                else:
                    print "Can't handle this url. " + str(old_url.url_type)
                    return None
                
                source_key = create_format_name(old_url.source)
                source = None if source_key not in key_to_source else key_to_source[source_key]
                    
                urls.append(Bioentityurl(old_webdisplay.label_name, link, source, old_webdisplay.label_location, bioentity, 
                                             old_url.date_created, old_url.created_by))
    return urls

def convert_url(old_session_maker, new_session_maker, chunk_size):
    from model_new_schema.bioentity import Bioentity as NewBioentity, Bioentityurl as NewBioentityurl
    from model_new_schema.evelements import Source as NewSource
    from model_old_schema.general import WebDisplay as OldWebDisplay, FeatUrl as OldFeatUrl, DbxrefFeat as OldDbxrefFeat
    
    log = logging.getLogger('convert.bioentity_in_depth.bioentity_url')
    log.info('begin')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()
        
        #Values to check
        values_to_check = ['display_name', 'source_id']
        
        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        
        #Urls of interest
        old_web_displays = old_session.query(OldWebDisplay).filter(OldWebDisplay.label_location == 'Interaction Resources').all()
        old_web_displays.extend(old_session.query(OldWebDisplay).filter(OldWebDisplay.label_location == 'Phenotype Resources').filter(OldWebDisplay.web_page_name == 'Locus').all())
        old_web_displays.extend(old_session.query(OldWebDisplay).filter(OldWebDisplay.label_location == 'Mutant Strains').filter(OldWebDisplay.web_page_name == 'Phenotype').all())

        url_to_display = dict([(x.url_id, x) for x in old_web_displays])
                
        min_bioent_id = 0
        max_bioent_id = 10000
        num_chunks = ceil(1.0*(max_bioent_id-min_bioent_id)/chunk_size)
        
        for i in range(0, num_chunks):
            min_id = min_bioent_id + i*chunk_size
            max_id = min_bioent_id + (i+1)*chunk_size
            
            #Grab all current/old objects
            if i < num_chunks-1:
                current_objs = new_session.query(NewBioentityurl).filter(NewBioentityurl.subclass_type == 'LOCUS').filter(NewBioentityurl.bioentity_id >= min_id).filter(NewBioentityurl.bioentity_id < max_id).all()
                old_objs = old_session.query(OldFeatUrl).filter(OldFeatUrl.feature_id >= min_id).filter(OldFeatUrl.feature_id < max_id).options(joinedload('url')).all()
            else:
                current_objs = new_session.query(NewBioentityurl).filter(NewBioentityurl.subclass_type == 'LOCUS').filter(NewBioentityurl.bioentity_id >= min_id).all()
                old_objs = old_session.query(OldFeatUrl).filter(OldFeatUrl.feature_id >= min_id).options(joinedload('url')).all()
                
            id_to_current_obj = dict([(x.id, x) for x in current_objs])
            key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
            untouched_obj_ids = set(id_to_current_obj.keys())
            already_seen = set()
        
            #Grab old objects
            
            for old_obj in old_objs:
                #Convert old objects into new ones
                if old_obj.url_id in url_to_display:
                    newly_created_objs = create_url(old_obj, url_to_display[old_obj.url_id], id_to_bioentity, key_to_source)
                    
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        if newly_created_obj.unique_key() not in already_seen:
                            current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                            current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                            create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                        
                            if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_id.id)
                            if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                                untouched_obj_ids.remove(current_obj_by_key.id)
                        else:
                            print newly_created_obj.unique_key()
                                
            #Grab old objects (dbxref)
            old_objs = old_session.query(OldDbxrefFeat).filter(
                                            OldDbxrefFeat.feature_id >= min_id).filter(
                                            OldDbxrefFeat.feature_id < min_id+chunk_size).options(
                                                            joinedload('dbxref'), joinedload('dbxref.dbxref_urls')).all()
            
            for old_obj in old_objs:
                #Convert old objects into new ones
                newly_created_objs = create_url_from_dbxref(old_obj, url_to_display, id_to_bioentity, key_to_source)
                
                if newly_created_objs is not None:
                    #Edit or add new objects
                    for newly_created_obj in newly_created_objs:
                        current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                        current_obj_by_key = None if newly_created_obj.unique_key() not in key_to_current_obj else key_to_current_obj[newly_created_obj.unique_key()]
                        create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)
                    
                        if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_id.id)
                        if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                            untouched_obj_ids.remove(current_obj_by_key.id)
                                
            #Delete untouched objs
            for untouched_obj_id  in untouched_obj_ids:
                new_session.delete(id_to_current_obj[untouched_obj_id])
                output_creator.removed()
                        
            output_creator.finished(str(i+1) + "/" + str(int(num_chunks)))
            new_session.commit()
        
    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
        old_session.close()
        
    log.info('complete')

"""
---------------------Convert------------------------------
"""   

def convert(old_session_maker, new_session_maker):

    #convert_alias(old_session_maker, new_session_maker)
    
    #convert_url(old_session_maker, new_session_maker, 1000)
        
    #convert_bioentitytabs(new_session_maker)

    #convert_disambigs(new_session_maker, Locus, ['id', 'format_name', 'display_name', 'sgdid'], 'BIOENTITY', 'LOCUS', 'convert.bioentity_in_depth.locus_disambigs', 1000)

    #convert_disambigs(new_session_maker, Protein, ['id', 'format_name', 'display_name', 'sgdid'], 'BIOENTITY', 'PROTEIN', 'convert.bioentity_in_depth.protein_disambigs', 10000)

    #convert_disambigs(new_session_maker, Complex, ['id', 'format_name'], 'BIOCONCEPT', 'COMPLEX', 'convert.complex.disambigs', 1000)
    pass