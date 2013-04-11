'''
Created on Apr 10, 2013

@author: kpaskov
'''

from model_new_schema import config as new_config
from model_new_schema.bioentity import Contig, Gene
from model_new_schema.sequence import Assembly, Seqtag, Sequence
from schema_conversion import add_or_check, cache
from schema_conversion.convert import prepare_schema_connection
from schema_conversion.output_manager import OutputCreator
import model_new_schema

def load_gff(assembly, filename, new_session):
    f = open(filename)
    
    output_creator = OutputCreator('assembly')
    values_to_check = ['name', 'description', 'filename', 'coverage', 'mean_contig_size', 'n50', 'num_gene_features',
                       'software', 'strain_id', 'background_strain_id']
    mapping = {assembly.id: new_session.query(Assembly).filter(Assembly.id == assembly.id).first()}
    add_or_check(assembly, mapping, assembly.id, values_to_check, new_session, output_creator)
    
    #Cache genes
    output_creator = OutputCreator('gene')
    name_to_gene = {}
    cache(Gene, name_to_gene, lambda x: x.secondary_name, new_session, output_creator)
    
    #Pull out contigs and sequences
    assemb_id_to_contig = {}
    id_to_contig = {}
    assemb_id_to_seq = {}
        
    full_sequence_id = None
    full_sequence = []
    for line in f:
        pieces = line.strip().split('\t')

        if len(pieces) == 9:            
            contig_id = pieces[0]
            source = pieces[1]
            feature_type = pieces[2]
            start = pieces[3]
            end = pieces[4]
            score = pieces[5]
            strand = pieces[6]
            frame = pieces[7]
            attrs = pieces[8]
            attr_dict = attrs_to_dict(attrs)
            
            if feature_type == 'contig':
                contig = Contig(attr_dict['Name'], source, attr_dict['dbxref'], assembly.id, contig_id, end, None)
                assemb_id_to_contig[pieces[0]] = contig
            else:
                dbxref_id = attr_dict['dbxref'] if 'dbxref' in attr_dict else None
                
                if 'gene' in attr_dict:
                    gene = new_session.query(Gene).filter(Gene.secondary_name==attr_dict['gene'])
                    contig = assemb_id_to_contig[contig_id]
                    seq = Sequence(gene.id, None, None, start, end, strand, end-start, None, None, 'DNA', source, contig.id, assembly.strain_id)
                    assemb_id_to_seq[attr_dict['ID']] = seq
                else:
                    seq = assemb_id_to_seq['Parent']
                    seqtag = Seqtag(seq.id, attr_dict['Name'], feature_type, dbxref_id, source, None, seq.min_coord-start, start, end-start+1, score, strand, frame, attr_dict['orf_classification'])
                    new_session.add(seqtag)
        else:
            if line.startswith('#'):
                print 'comment'
            elif line.startswith('>'):
                full_sequence_id = pieces[0][1:]
                contig = assemb_id_to_contig[full_sequence_id]
                residues = ''.join(full_sequence)
                seq = Sequence(contig.id, None, None, 1, contig.length, strand, contig.length, None, residues, 'DNA', source, None, assembly.strain_id)
                new_session.add(seq)
                full_sequence = []
            else:
                full_sequence.append(pieces[0])
                
    #Add residues to all sequences
    for seq in assemb_id_to_seq.values:
        seq.rootseq_id
                    
def attrs_to_dict(attrs):
    attr_dict = {}
    for attr in attrs.split(';'):
        eq_index = attr.index('=')
        key = attr[0:eq_index]
        value = attr[eq_index+1:]
        attr_dict[key] = value
    return attr_dict
            
    
    
if __name__ == "__main__":
    new_session_maker = prepare_schema_connection(model_new_schema, new_config)
    description = "Assembly of the genome of S. cerevisiae strain Sigma1278b (WGS ID: ACVY00000000). Feature definitions (for coding sequences and features in the gff file) were assigned using Jim Kent's liftOver program with a blat alignment vs. the R64 (current) S288C reference sequence. This assembly contains 67 contigs (coverage: 45X, mean contig size: 177702, N50: 365700). Using liftOver, 6419 SGD gene features were found in the assembly. This data is preliminary and is subject to change without notice."
    assembly = Assembly('Sigma1278b_MIT', description, 'Sigma1278b_ACVY01000000.gff', '45X', 177702, 365700, 6419, 'liftOver', 'Sigma1278b', 'S288C')
    
    commit = False
    try:
        new_session = new_session_maker()
        load_gff(assembly, '/Users/kpaskov/Downloads/Sigma1278b_ACVY01000000.gff', new_session)
      
        if commit:
            new_session.commit()
    finally:
        new_session.close()
    

    
    