'''
Created on Mar 22, 2013

@author: kpaskov
'''
from model_old_schema.config import DBUSER as OLD_DBUSER
from schema_conversion import cache, create_or_update, add_or_check, \
    create_or_update_and_remove
from schema_conversion.old_to_new_bioentity import id_to_bioent, \
    create_protein_id, create_transcript_id
from schema_conversion.output_manager import OutputCreator
import model_old_schema


id_to_bioent_bioent = {}
id_to_sequence = {}
id_to_seqtag = {}


"""
---------------------Create------------------------------
"""

def create_sequence(old_seq):
    from model_new_schema.sequence import Sequence as NewSequence  
    old_feat_location = old_seq.current_feat_location
    feature_id = old_seq.feature_id if old_seq.seq_type == 'genomic' else create_protein_id(old_seq.feature_id)  
      
    if feature_id in id_to_bioent and old_seq.is_current == 'Y':
        if old_feat_location is not None:
            return NewSequence(feature_id, old_seq.seq_version, old_feat_location.coord_version, old_feat_location.min_coord, 
                       old_feat_location.max_coord, old_feat_location.strand, old_seq.is_current, old_seq.seq_length, old_seq.ftp_file, 
                       old_seq.residues, old_seq.seq_type, old_seq.source, old_feat_location.rootseq_id, 'S288C',
                       sequence_id=old_seq.id, 
                       date_created=old_seq.date_created, created_by=old_seq.created_by)
        else:
            return NewSequence(feature_id, old_seq.seq_version, None, None, None, None, old_seq.is_current, old_seq.seq_length, old_seq.ftp_file, 
                       old_seq.residues, old_seq.seq_type, old_seq.source, None, 'S288C',
                       sequence_id=old_seq.id, 
                       date_created=old_seq.date_created, created_by=old_seq.created_by)
    else:
        return None
    
def create_transcript(old_seq):
    from model_new_schema.bioentity import Transcript as NewTranscript
    gene_id = old_seq.feature_id
    if old_seq.seq_type == 'genomic' and old_seq.is_current == 'Y' and gene_id in id_to_bioent:
        return NewTranscript(gene_id, 'Active', bioent_id=create_transcript_id(old_seq.feature_id))
    else:
        return None
    
def create_protein(old_seq):
    from model_new_schema.bioentity import Protein as NewProtein
    transcript_id = create_transcript_id(old_seq.feature_id)
    if old_seq.seq_type == 'protein' and old_seq.is_current == 'Y' and transcript_id in id_to_bioent:
        return NewProtein(None, None, transcript_id, None, None, None, None, None, None, 
                          None, None, None, None, 
                          None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 
                          None, None, None, None, None, None, 
                          None, None, None, 
                          None, None, None, None, 
                          None, None, bioent_id=create_protein_id(old_seq.feature_id), 
                          date_created=old_seq.date_created, created_by=old_seq.created_by)
    else:
        return None
    
def create_seqtag(old_seq, old_feature, parent_seq_id, parent_seq_min_coord):
    from model_new_schema.sequence import Seqtag as NewSeqtag
    return NewSeqtag(parent_seq_id, old_feature.name, old_feature.type, old_feature.dbxref_id, old_feature.source, 
                     old_feature.status, old_feature.secondary_name, 
                     old_seq.min_coord-parent_seq_min_coord, old_seq.min_coord, old_seq.length, 
                     seqtag_id=old_seq.id, date_created=old_seq.date_created, created_by=old_seq.created_by)
    
    
"""
---------------------Convert------------------------------
"""  

def convert_sequence(old_session, new_session):
    from model_old_schema.sequence import Sequence as OldSequence
    from model_old_schema.feature import FeatRel as OldFeatRel, Feature as OldFeature

    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.sequence import Sequence as NewSequence, Seqtag as NewSeqtag
      
    #Cache bioents
    output_creator = OutputCreator('bioent')
    key_maker = lambda x: x.id
    cache(NewBioentity, id_to_bioent, key_maker, new_session, output_creator)

    #Create new transcripts if they don't exist, or update the database if they do.
    #Remove any transcripts that don't match.
    output_creator = OutputCreator('transcript')
    old_seqs = old_session.query(OldSequence).all()
    output_creator.pulled('sequence', len(old_seqs))
    values_to_check = ['gene_id']
    create_or_update_and_remove(old_seqs, id_to_bioent, create_transcript, key_maker, values_to_check, new_session, output_creator)
    
    #Create new proteins if they don't exist, or update the database if they do.
    #Remove any proteins that don't match.
    output_creator = OutputCreator('protein')
    output_creator.pulled('sequence', len(old_seqs))
    values_to_check = ['transcript_id']
    create_or_update_and_remove(old_seqs, id_to_bioent, create_protein, key_maker, values_to_check, new_session, output_creator)

    #Cache sequences
    output_creator = OutputCreator('sequence')
    output_creator.pulled('sequence', len(old_seqs))
    key_maker = lambda x: x.id
    cache(NewSequence, id_to_sequence, key_maker, new_session, output_creator)
    
    #Create new sequences if they don't exist, or update the database if they do.
    #Remove any sequences that don't match.
    values_to_check = ['bioent_id', 'seq_version', 'coord_version', 'min_coord', 'max_coord', 'strand', 'is_current', 'length', 'ftp_file', 
                       'residues', 'seq_type', 'rootseq_id', 'date_created', 'created_by']
    create_or_update_and_remove(old_seqs, id_to_sequence, create_sequence, key_maker, values_to_check, new_session, output_creator)
    
    #Cache seqtags
    output_creator = OutputCreator('seqtag')
    key_maker = lambda x: x.old_feat_id
    cache(NewSeqtag, id_to_seqtag, key_maker, new_session, output_creator)

    #Create new seqtags if they don't exist or update the database if they do.
    #Remove any seqtags that don't match.
    parent_to_children = {}
    feat_id_to_seq = {}
    
    old_feat_rels = old_session.query(OldFeatRel).filter(OldFeatRel.relationship_type=='part of').all()
    output_creator.pulled('feat_rels', len(old_feat_rels))
    feat_id_to_feat = dict([(feat.id, feat) for feat in old_session.query(OldFeature).all()])
    for old_feat_rel in old_feat_rels:
        if old_feat_rel.parent_id not in parent_to_children:
            parent_to_children[old_feat_rel.parent_id] = []
        parent_to_children[old_feat_rel.parent_id].append(old_feat_rel.child_id)        
    for old_seq in old_seqs:
        if old_seq.is_current == 'Y':
            feat_id_to_seq[old_seq.feature_id] = old_seq
    
    check_values = ['seq_id', 'name', 'seqtag_type', 'dbxref', 'source', 'status', 'secondary_name', 'relative_coord',
                    'chrom_coord', 'length', 'date_created', 'created_by']
    for bioent in id_to_bioent.values():
        children = parent_to_children[bioent.id]
        parent_seq = feat_id_to_seq[bioent.id]
        while len(children) > 0:
            child_id = children.pop(0)
            child = feat_id_to_feat[child_id]
            old_seq = feat_id_to_seq[child_id]
            seqtag = create_seqtag(old_seq, child, parent_seq.id, parent_seq.min_coord)
            add_or_check(seqtag, id_to_seqtag, child_id, check_values, new_session, output_creator)
            if child_id in parent_to_children:
                children.append(parent_to_children[child_id])
            
            
            
    output_creator.finished()
    
    