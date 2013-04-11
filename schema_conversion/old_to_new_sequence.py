'''
Created on Mar 22, 2013

@author: kpaskov
'''
from schema_conversion import cache, create_or_update, add_or_check
from schema_conversion.old_to_new_bioentity import create_protein_id, \
    create_transcript_id
from schema_conversion.output_manager import OutputCreator
from sqlalchemy.orm import joinedload


id_to_dna_sequence = {}
id_to_seqtag = {}
id_to_gene = {}
id_to_transcript = {}
id_to_protein = {}


"""
---------------------Create------------------------------
"""

def create_dna_sequence(old_seq):
    from model_new_schema.sequence import Sequence as NewSequence  
    old_feat_location = old_seq.current_feat_location
    feature_id = old_seq.feature_id 
      
    if feature_id in id_to_gene and old_seq.is_current == 'Y' and old_seq.seq_type=='genomic':
        return NewSequence(feature_id, old_seq.seq_version, old_feat_location.coord_version, old_feat_location.min_coord, 
                    old_feat_location.max_coord, old_feat_location.strand, old_seq.seq_length, old_seq.ftp_file, 
                    old_seq.residues, 'DNA', old_seq.source, old_feat_location.rootseq_id, 'S288C',
                    sequence_id=old_seq.id, 
                    date_created=old_seq.date_created, created_by=old_seq.created_by)
    else:
        return None
    
def create_seqtag(old_seq, old_feature, parent_seq_id, parent_seq_min_coord):
    from model_new_schema.sequence import Seqtag as NewSeqtag
    old_feat_location = old_seq.current_feat_location
    
    return NewSeqtag(parent_seq_id, old_feature.name, old_feature.type, old_feature.dbxref_id, old_feature.source, 
                     old_feature.gene_name, 
                     old_feat_location.min_coord-parent_seq_min_coord, old_feat_location.min_coord, old_seq.seq_length, 
                     seqtag_id=old_seq.id, date_created=old_seq.date_created, created_by=old_seq.created_by)
    
    
"""
---------------------Convert------------------------------
"""  

def convert_dna_sequence(old_session, new_session):
    from model_old_schema.sequence import Sequence as OldSequence
    from model_old_schema.feature import FeatRel as OldFeatRel, Feature as OldFeature

    from model_new_schema.bioentity import Gene as NewGene
    from model_new_schema.sequence import Sequence as NewSequence, Seqtag as NewSeqtag
    
    #Cache genes
    gene_output_creator = OutputCreator('gene')
    key_maker = lambda x: x.id
    cache(NewGene, id_to_gene, key_maker, new_session, gene_output_creator)
        
    #Cache sequences
    seq_output_creator = OutputCreator('sequence')
    key_maker = lambda x: x.id
    id_to_dna_sequence.update(dict([(key_maker(x), x) for x in new_session.query(NewSequence).filter(NewSequence.seq_type=='DNA').all()]))
    seq_output_creator.cached()
    
    #Cache seqtags
    seqtag_output_creator = OutputCreator('seqtag')

    key_maker = lambda x: x.id
    cache(NewSeqtag, id_to_seqtag, key_maker, new_session, seqtag_output_creator)
    
    #Create new dna sequences if they don't exist, or update the database if they do.
    #Remove any dna sequences that don't match.
    values_to_check_seq = ['bioent_id', 'seq_version', 'coord_version', 'min_coord', 'max_coord', 'strand', 'length', 'ftp_file', 
                       'residues', 'seq_type', 'rootseq_id', 'date_created', 'created_by']
    values_to_check_seqtag = ['seq_id', 'name', 'seqtag_type', 'dbxref_id', 'source', 'secondary_name', 'relative_coord',
                    'chrom_coord', 'length', 'date_created', 'created_by']    
    
    feat_id_to_feat = dict([(x.id, x) for x in old_session.query(OldFeature).all()])
    no_sequences = []
    multiple_sequences = []
    no_sequence_seqtags = set()
    i = 0
    for gene_id in id_to_gene.keys():
        #Create sequence
        old_seqs = old_session.query(OldSequence).options(joinedload('feat_locations')).filter(OldSequence.feature_id == gene_id).filter(OldSequence.is_current == 'Y').filter(OldSequence.seq_type == 'genomic').all()
        if len(old_seqs) == 0:
            no_sequences.append(id_to_gene[gene_id].name)
        elif len(old_seqs) > 1:
            multiple_sequences.append(id_to_gene[gene_id].name)
        else:
            new_seq = create_dna_sequence(old_seqs[0])
            if new_seq != None:
                add_or_check(new_seq, id_to_dna_sequence, key_maker(new_seq), values_to_check_seq, new_session, seq_output_creator)
                
            #Create seqtags
            children = [gene_id]
            while len(children) > 0:
                first_id = children.pop(0)
                child = feat_id_to_feat[first_id]
                child_seq = old_session.query(OldSequence).options(joinedload('feat_locations')).filter(OldSequence.feature_id == first_id).filter(OldSequence.is_current == 'Y').filter(OldSequence.seq_type == 'genomic').first()
                if child_seq is None:
                    no_sequence_seqtags.add(child.name)
                else:
                    new_seqtag = create_seqtag(child_seq, child, new_seq.id, new_seq.min_coord)
                    add_or_check(new_seqtag, id_to_seqtag, new_seqtag.id, values_to_check_seqtag, new_session, seqtag_output_creator)
                children.extend([x.child_id for x in old_session.query(OldFeatRel).filter(OldFeatRel.relationship_type=='part of').filter(OldFeatRel.parent_id==first_id).all()])    
        
        i = i+1
        if i%1000==0:
            print str(i) + '/' + str(len(id_to_gene))
    seq_output_creator.finished()
    print 'The following genes did not have dna sequences: ' + str(no_sequences)
    print 'The following genes had multiple dna sequences: ' + str(multiple_sequences)
    seqtag_output_creator.finished()
    print 'The following seqtags did not have dna sequences: ' + str(no_sequence_seqtags)
   


    
    