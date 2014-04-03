import logging
import sys

from mpmath import ceil
from sqlalchemy.orm import joinedload

from src.sgd.convert import OutputCreator, create_or_update, create_format_name


__author__ = 'kpaskov'

#Recorded times: 
#Maitenance (cherry-vm08): 2:56, 2:59 
#First Load (sgd-ng1): 4:08, 3:49
#Maitenance (sgd-ng1): 4:17

# --------------------- Convert Bioentity Tabs ---------------------
def create_bioentitytabs(locus):
    from src.sgd.model.nex.auxiliary import Locustabs
    
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
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.auxiliary import Locustabs

    new_session = None
    old_session = None
    log = logging.getLogger('convert.bioentity_in_depth.bioentitytabs')
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

# --------------------- Convert Alias ---------------------
def create_alias(old_alias, id_to_bioentity, key_to_source):
    from src.sgd.model.nex.bioentity import Bioentityalias

    new_aliases = []

    bioentity_id = old_alias.feature_id
    bioentity = None if bioentity_id not in id_to_bioentity else id_to_bioentity[bioentity_id]

    display_name = old_alias.alias_name
    source = key_to_source['SGD']

    new_aliases.append(Bioentityalias(display_name, None, source, old_alias.alias_type, bioentity, 0,
                               old_alias.date_created, old_alias.created_by))
    return new_aliases

def create_alias_from_dbxref(old_dbxref_feat, id_to_bioentity, key_to_source):
    from src.sgd.model.nex.bioentity import Bioentityalias

    new_aliases = []

    if old_dbxref_feat.dbxref.dbxref_type != 'DBID Primary':
        source = key_to_source[old_dbxref_feat.dbxref.source.replace('/', '-')]
        bioentity_id = old_dbxref_feat.feature_id
        bioentity = None if bioentity_id not in id_to_bioentity else id_to_bioentity[bioentity_id]
        display_name = old_dbxref_feat.dbxref.dbxref_id
        link = None
        if len(old_dbxref_feat.dbxref.urls) > 0:
            link = old_dbxref_feat.dbxref.urls[0].url.replace('_SUBSTITUTE_THIS_', display_name)

        new_aliases.append(Bioentityalias(display_name, link, source, old_dbxref_feat.dbxref.dbxref_type, bioentity, 1,
                               old_dbxref_feat.dbxref.date_created, old_dbxref_feat.dbxref.created_by))
    return new_aliases

def create_alias_from_complex(complex):
    from src.sgd.model.nex.bioentity import Bioentityalias

    new_aliases = []

    for alias in complex.go.aliases:
        new_aliases.append(Bioentityalias(alias.display_name, alias.link, alias.source, None, alias.bioentity, 1,
                               alias.date_created, alias.created_by))

    return new_aliases

def convert_alias(old_session_maker, new_session_maker):
    from src.sgd.model.nex.bioentity import Bioentity as NewBioentity, Bioentityalias as NewBioentityalias, Complex
    from src.sgd.model.nex.misc import Source as NewSource
    from src.sgd.model.bud.feature import AliasFeature as OldAliasFeature
    from src.sgd.model.bud.general import DbxrefFeat as OldDbxrefFeat

    new_session = None
    old_session = None
    log = logging.getLogger('convert.bioentity_in_depth.bioentity_alias')
    output_creator = OutputCreator(log)
    
    try:
        new_session = new_session_maker()
        old_session = old_session_maker()

        #Grab all current objects
        current_objs = new_session.query(NewBioentityalias).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])
        
        #Values to check
        values_to_check = ['source_id', 'category', 'created_by', 'date_created', 'subclass_type', 'link', 'is_external_id']
        
        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen_obj = set()
        
        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])

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
                else:
                    print newly_created_obj.unique_key()
                already_seen_obj.add(newly_created_obj.unique_key())

        #Commit
        output_creator.finished()
        new_session.commit()

        #Grab old objects
        old_objs = old_session.query(OldDbxrefFeat).options(joinedload(OldDbxrefFeat.dbxref), joinedload('dbxref.dbxref_urls')).all()

        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_alias_from_dbxref(old_obj, id_to_bioentity, key_to_source)

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
                else:
                    print newly_created_obj.unique_key()
                already_seen_obj.add(newly_created_obj.unique_key())

        #Grab old objects
        new_complex = new_session.query(Complex).all()

        for old_obj in new_complex:
            #Convert old objects into new ones
            newly_created_objs = create_alias_from_complex(old_obj)

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
                else:
                    print newly_created_obj.unique_key()
                already_seen_obj.add(newly_created_obj.unique_key())
                        
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

# --------------------- Convert Alias Evidence ---------------------
def create_alias_evidence(old_alias, id_to_bioentity, key_to_source, key_to_alias, id_to_reference, feat_alias_id_to_reflinks):
    from src.sgd.model.nex.bioentity import Bioentityalias
    from src.sgd.model.nex.evidence import Aliasevidence

    new_alias_evidences = []

    bioentity_id = old_alias.feature_id
    bioentity = None if bioentity_id not in id_to_bioentity else id_to_bioentity[bioentity_id]

    display_name = old_alias.alias_name
    source = key_to_source['SGD']

    alias_key = Bioentityalias(display_name, None, source, old_alias.alias_type, bioentity, 0, old_alias.date_created, old_alias.created_by).unique_key()
    if alias_key not in key_to_alias:
        print 'Alias not found: ' + str(alias_key)
        return []

    alias = key_to_alias[alias_key]

    if old_alias.id in feat_alias_id_to_reflinks:
        reflinks = feat_alias_id_to_reflinks[old_alias.id]
        for reflink in reflinks:
            reference_id = reflink.reference_id
            reference = None if reference_id not in id_to_reference else id_to_reference[reference_id]
            new_alias_evidences.append(Aliasevidence(source, reference, alias, reflink.date_created, reflink.created_by))

    return new_alias_evidences

def create_alias_evidence_from_dbxref(old_dbxref_feat, id_to_bioentity, key_to_source, key_to_alias, id_to_reference, dbxref_feat_id_to_reflinks):
    from src.sgd.model.nex.bioentity import Bioentityalias
    from src.sgd.model.nex.evidence import Aliasevidence

    new_alias_evidences = []

    if old_dbxref_feat.dbxref.dbxref_type != 'DBID Primary':
        source = key_to_source[old_dbxref_feat.dbxref.source.replace('/', '-')]
        bioentity_id = old_dbxref_feat.feature_id
        bioentity = None if bioentity_id not in id_to_bioentity else id_to_bioentity[bioentity_id]
        display_name = old_dbxref_feat.dbxref.dbxref_id
        link = None
        if len(old_dbxref_feat.dbxref.urls) > 0:
            link = old_dbxref_feat.dbxref.urls[0].url.replace('_SUBSTITUTE_THIS_', display_name)

        alias_key = Bioentityalias(display_name, link, source, old_dbxref_feat.dbxref.dbxref_type, bioentity, 1,
                               old_dbxref_feat.dbxref.date_created, old_dbxref_feat.dbxref.created_by).unique_key()
        if alias_key not in key_to_alias:
            print 'Alias not found: ' + str(alias_key)
            return []

        alias = key_to_alias[alias_key]

        if old_dbxref_feat.id in dbxref_feat_id_to_reflinks:
            reflinks = dbxref_feat_id_to_reflinks[old_dbxref_feat.id]
            for reflink in reflinks:
                reference_id = reflink.reference_id
                reference = None if reference_id not in id_to_reference else id_to_reference[reference_id]
                new_alias_evidences.append(Aliasevidence(source, reference, alias, reflink.date_created, reflink.created_by))

    return new_alias_evidences

def convert_alias_evidence(old_session_maker, new_session_maker):
    from src.sgd.model.nex.bioentity import Bioentity as NewBioentity, Bioentityalias as NewBioentityalias
    from src.sgd.model.nex.reference import Reference as NewReference
    from src.sgd.model.nex.misc import Source as NewSource
    from src.sgd.model.nex.evidence import Aliasevidence as NewAliasevidence
    from src.sgd.model.bud.feature import AliasFeature as OldAliasFeature
    from src.sgd.model.bud.general import DbxrefFeat as OldDbxrefFeat
    from src.sgd.model.bud.reference import Reflink as OldReflink

    new_session = None
    old_session = None
    log = logging.getLogger('convert.bioentity_in_depth.bioentity_alias')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()
        old_session = old_session_maker()

        #Grab all current objects
        current_objs = new_session.query(NewAliasevidence).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        #Values to check
        values_to_check = ['source_id', 'reference_id', 'alias_id', 'created_by', 'date_created']

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen_obj = set()

        #Grab cached dictionaries
        id_to_bioentity = dict([(x.id, x) for x in new_session.query(NewBioentity).all()])
        id_to_reference = dict([(x.id, x) for x in new_session.query(NewReference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(NewSource).all()])
        key_to_alias = dict([(x.unique_key(), x) for x in new_session.query(NewBioentityalias).all()])

        feat_alias_id_to_reflinks = dict()
        for reflink in old_session.query(OldReflink).filter_by(tab_name='FEAT_ALIAS').all():
            if reflink.primary_key in feat_alias_id_to_reflinks:
                feat_alias_id_to_reflinks[reflink.primary_key].append(reflink)
            else:
                feat_alias_id_to_reflinks[reflink.primary_key] = [reflink]

        dbxref_feat_id_to_reflinks = dict()
        for reflink in old_session.query(OldReflink).filter_by(tab_name='DBXREF_FEAT').all():
            if reflink.primary_key in dbxref_feat_id_to_reflinks:
                dbxref_feat_id_to_reflinks[reflink.primary_key].append(reflink)
            else:
                dbxref_feat_id_to_reflinks[reflink.primary_key] = [reflink]

        #Grab old objects
        old_objs = old_session.query(OldAliasFeature).options(joinedload('alias')).all()

        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_alias_evidence(old_obj, id_to_bioentity, key_to_source, key_to_alias, id_to_reference, feat_alias_id_to_reflinks)

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
                else:
                    print newly_created_obj.unique_key()
                already_seen_obj.add(newly_created_obj.unique_key())

        #Commit
        output_creator.finished()
        new_session.commit()

        #Grab old objects
        old_objs = old_session.query(OldDbxrefFeat).options(joinedload(OldDbxrefFeat.dbxref), joinedload('dbxref.dbxref_urls')).all()

        for old_obj in old_objs:
            #Convert old objects into new ones
            newly_created_objs = create_alias_evidence_from_dbxref(old_obj, id_to_bioentity, key_to_source, key_to_alias, id_to_reference, dbxref_feat_id_to_reflinks)

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
                else:
                    print newly_created_obj.unique_key()
                already_seen_obj.add(newly_created_obj.unique_key())

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

# --------------------- Convert Relation ---------------------
def create_relation_from_complex(complex, key_to_source, go_id_to_complex):
    from src.sgd.model.nex.bioentity import Bioentityrelation

    new_relations = []
    for child in complex.go.children:
        if child.child.id in go_id_to_complex:
            child = go_id_to_complex[child.child.id]
            new_relations.append(Bioentityrelation(key_to_source['SGD'], 'is a', complex, child, None, None))
    return new_relations

def convert_relation(new_session_maker):
    from src.sgd.model.nex.bioentity import Bioentityrelation, Complex
    from src.sgd.model.nex.misc import Source as Source

    new_session = None
    log = logging.getLogger('convert.bioentity_in_depth.relations')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Grab all current objects
        current_objs = new_session.query(Bioentityrelation).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        #Values to check
        values_to_check = ['source_id', 'relation_type', 'parent_id', 'child_id']

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen_obj = set()

        #Grab cached dictionaries
        complexes = new_session.query(Complex).all()
        go_id_to_complex = dict([(x.go.id, x) for x in complexes])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])

        for old_obj in complexes:
            #Convert old objects into new ones
            newly_created_objs = create_relation_from_complex(old_obj, key_to_source, go_id_to_complex)

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
                else:
                    print newly_created_obj.unique_key()
                already_seen_obj.add(newly_created_obj.unique_key())

        #Commit
        output_creator.finished()
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

# --------------------- Convert Url ---------------------
def create_url(old_feat_url, old_webdisplay, id_to_bioentity, key_to_source):
    from src.sgd.model.nex.bioentity import Bioentityurl
        
    old_url = old_webdisplay.url
    url_type = old_url.url_type
    link = old_url.url
    
    feature = old_feat_url.feature
    if feature.id not in id_to_bioentity:
        return []
    
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
        return []
        
    url = Bioentityurl(display_name, link, source, category, bioentity, 
                                 old_url.date_created, old_url.created_by)
    return [url]

def create_url_from_dbxref(old_dbxref_feat, url_to_display, id_to_bioentity, key_to_source):
    from src.sgd.model.nex.bioentity import Bioentityurl
    
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
                elif url_type == 'query by SGDID':
                    link = link.replace('_SUBSTITUTE_THIS_', id_to_bioentity[feature_id].sgdid)
                else:
                    print "Can't handle this url. " + str(old_url.url_type)

                source_key = create_format_name(old_url.source)
                source = None if source_key not in key_to_source else key_to_source[source_key]
                    
                urls.append(Bioentityurl(old_webdisplay.label_name, link, source, old_webdisplay.label_location, bioentity, 
                                             old_url.date_created, old_url.created_by))
    return urls

def create_url_from_protein_sequence(locus, key_to_source):
    from src.sgd.model.nex.bioentity import Bioentityurl
    return [Bioentityurl('NCBI Dart', 'http://www.ncbi.nlm.nih.gov/Structure/lexington/lexington.cgi?FILTER=on&EXPECT=0.01&cmd=seq&fasta=_SUBSTITUTE_SEQUENCE_', key_to_source['NCBI'], 'Domain', locus, None, None),
                Bioentityurl('SMART domain', 'http://smart.embl-heidelberg.de/smart/show_motifs.pl?SEQUENCE=_SUBSTITUTE_SEQUENCE_', key_to_source['SMART'], 'Domain', locus, None, None),
                Bioentityurl('PFAM domain', 'http://pfam.sanger.ac.uk/search/sequence?seqOpts=both&ga=0&evalue=1.0&seq=_SUBSTITUTE_SEQUENCE_', key_to_source['Pfam'], 'Domain', locus, None, None),
                Bioentityurl('PROSITE Pattern', 'http://us.expasy.org/cgi-bin/prosite/PSScan.cgi?seq=_SUBSTITUTE_SEQUENCE_', key_to_source['Prosite'], 'Domain', locus, None, None),
                Bioentityurl('SCOP', 'http://supfam.org/SUPERFAMILY/cgi-bin/gene.cgi?genome=sc&seqid=' + locus.format_name, key_to_source['NCBI'], 'Domain', locus, None, None)]

def convert_url(old_session_maker, new_session_maker, chunk_size):
    from src.sgd.model.nex.bioentity import Bioentity as NewBioentity, Bioentityurl as NewBioentityurl
    from src.sgd.model.nex.misc import Source as NewSource
    from src.sgd.model.bud.general import WebDisplay as OldWebDisplay, FeatUrl as OldFeatUrl, DbxrefFeat as OldDbxrefFeat
    from src.sgd.model.nex.bioentity import Protein

    new_session = None
    old_session = None
    log = logging.getLogger('convert.bioentity_in_depth.bioentity_url')
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
        #Interaction Resources
        old_web_displays = old_session.query(OldWebDisplay).filter(OldWebDisplay.label_location == 'Interaction Resources').all()
        #Phenotype Resources
        old_web_displays.extend(old_session.query(OldWebDisplay).filter(OldWebDisplay.label_location == 'Phenotype Resources').filter(OldWebDisplay.web_page_name == 'Locus').all())
        old_web_displays.extend(old_session.query(OldWebDisplay).filter(OldWebDisplay.label_location == 'Mutant Strains').filter(OldWebDisplay.web_page_name == 'Phenotype').all())
        #Protein Resources
        old_web_displays.extend(old_session.query(OldWebDisplay).filter(OldWebDisplay.label_location == 'Post-translational modifications').filter(OldWebDisplay.web_page_name == 'Protein').all())
        old_web_displays.extend(old_session.query(OldWebDisplay).filter(OldWebDisplay.label_location == 'Protein Information Homologs').filter(OldWebDisplay.web_page_name == 'Locus').all())
        old_web_displays.extend(old_session.query(OldWebDisplay).filter(OldWebDisplay.label_location == 'Analyze Sequence S288C vs. other species').filter(OldWebDisplay.web_page_name == 'Locus').all())
        old_web_displays.extend(old_session.query(OldWebDisplay).filter(OldWebDisplay.label_location == 'Protein databases/Other').filter(OldWebDisplay.web_page_name == 'Protein').all())
        old_web_displays.extend(old_session.query(OldWebDisplay).filter(OldWebDisplay.label_location == 'Localization Resources').filter(OldWebDisplay.web_page_name == 'Protein').all())

        url_to_display = dict([(x.url_id, x) for x in old_web_displays])

        locus_ids_with_protein = set([x.locus_id for x in new_session.query(Protein).all()])
                
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
                                            OldDbxrefFeat.feature_id < max_id).options(
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



            for locus_id in locus_ids_with_protein:
                if locus_id > min_id and (i == num_chunks-1 or locus_id < max_id):
                    newly_created_objs = create_url_from_protein_sequence(id_to_bioentity[locus_id], key_to_source)

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

# ---------------------Convert------------------------------
def convert(old_session_maker, new_session_maker):

    convert_alias(old_session_maker, new_session_maker)

    #convert_relation(new_session_maker)

    #convert_alias_evidence(old_session_maker, new_session_maker)
    
    #convert_url(old_session_maker, new_session_maker, 1000)
        
    #convert_bioentitytabs(new_session_maker)

    #convert_disambigs(new_session_maker, Locus, ['id', 'format_name', 'display_name', 'sgdid'], 'BIOENTITY', 'LOCUS', 'convert.bioentity_in_depth.locus_disambigs', 1000)

    #convert_disambigs(new_session_maker, Protein, ['id', 'format_name', 'display_name', 'sgdid'], 'BIOENTITY', 'PROTEIN', 'convert.bioentity_in_depth.protein_disambigs', 10000)

    #convert_disambigs(new_session_maker, Complex, ['id', 'format_name'], 'BIOCONCEPT', 'COMPLEX', 'convert.complex.disambigs', 1000)
