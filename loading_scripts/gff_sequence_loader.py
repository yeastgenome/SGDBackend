'''
Created on Apr 10, 2013

@author: kpaskov
'''


from model_new_schema import config as new_config

from schema_conversion import add_or_check, cache, check_values
from schema_conversion.convert import prepare_schema_connection
from schema_conversion.old_to_new_bioentity import create_gene_type
from schema_conversion.output_manager import OutputCreator
import model_new_schema

new_session_maker = prepare_schema_connection(model_new_schema, new_config)
from model_new_schema.bioentity import Contig, Gene
from model_new_schema.sequence import Assembly, Seqtag, Sequence, Strain
id_to_contig = {}
tuple_to_sequence = {}
tuple_to_seqtag = {}

def load_gff(assembly, filename, new_session):
    f = open(filename)
    
    #Cache genes
    gene_output_creator = OutputCreator('gene')
    name_to_gene = {}
    cache(Gene, name_to_gene, lambda x: x.official_name, new_session, gene_output_creator)
    
    #Cache contigs
    contig_output_creator = OutputCreator('contig')
    cache(Contig, id_to_contig, lambda x: x.id, new_session, contig_output_creator)
    
    #Cache sequences
    seq_output_creator = OutputCreator('sequence')
    cache(Sequence, tuple_to_sequence, lambda x: (x.bioent_id, x.rootseq_id, x.strain_id), new_session, seq_output_creator)
    
    #Cache seqtags
    seqtag_output_creator = OutputCreator('seqtag')
    cache(Seqtag, tuple_to_seqtag, lambda x: (x.seq_id, x.seqtag_type, x.chrom_coord, x.length, x.strand), new_session, seqtag_output_creator)
    
    #Pull out contigs and sequences
    assemb_id_to_contig = {}
    assemb_id_to_seq = {}
    contig_to_residues = {}
        
    full_sequence_id = None
    full_sequence = []
    for line in f:
        pieces = line.strip().split('\t')

        if len(pieces) == 9:            
            contig_id = pieces[0]
            source = pieces[1]
            feature_type = pieces[2]
            start = int(pieces[3])
            end = int(pieces[4])
            score = pieces[5]
            strand = pieces[6]
            frame = pieces[7]
            attrs = pieces[8]
            attr_dict = attrs_to_dict(attrs)
            
            if feature_type == 'contig':
                bioent_id = int(contig_id[3:12])
                contig = Contig(attr_dict['Name'], source, attr_dict['dbxref'], assembly.id, contig_id, end, None, bioent_id=bioent_id)
                assemb_id_to_contig[contig_id] = contig
                values_to_check = ['assembly_id', 'internal_id', 'length', 'chromosome_id']
                add_or_check(contig, id_to_contig, contig.id, values_to_check, new_session, contig_output_creator)

            else:
                dbxref_id = attr_dict['dbxref'] if 'dbxref' in attr_dict else None
                name = attr_dict['Name']
                if 'Parent' not in attr_dict:
                    note = attr_dict['Note'] if 'Note' in attr_dict else None
                    gene = Gene(name, create_gene_type(feature_type), dbxref_id, None, name, None, None, None, None, note, None)
                    add_or_check(gene, name_to_gene, gene.official_name, [], new_session, gene_output_creator)
                    if name in name_to_gene:
                        gene = name_to_gene[name]
                    contig = assemb_id_to_contig[contig_id]
                    seq = Sequence(gene.id, None, None, start, end, strand, end-start+1, None, None, 'DNA', source, contig.id, assembly.strain_id)
                    values_to_check = ['bioent_id', 'seq_version', 'coord_version', 'min_coord', 'max_coord', 'strand', 'is_current', 'length', 'ftp_file',
                                       'residues', 'seq_type', 'source', 'rootseq_id', 'strain_id', 'date_created', 'created_by']
                    add_or_check(seq, tuple_to_sequence, (seq.bioent_id, seq.rootseq_id, seq.strain_id), values_to_check, new_session, seq_output_creator)
                    assemb_id_to_seq[attr_dict['ID']] = tuple_to_sequence[(seq.bioent_id, seq.rootseq_id, seq.strain_id)]
                else:
                    seq = assemb_id_to_seq[attr_dict['Parent']]
                    orf_classification = attr_dict['orf_classification'] if 'orf_classification' in attr_dict else None
                    if seq.strand == '+':
                        relative_coord = start-seq.min_coord
                    else:
                        relative_coord = seq.max_coord-end
                    seqtag = Seqtag(seq.id, attr_dict['Name'], feature_type, dbxref_id, source, None, relative_coord, start, end-start+1, score, strand, frame, orf_classification)
                    if 'ID' in attr_dict:
                        assemb_id_to_seq[attr_dict['ID']] = seq
                        
                    already_has = None
                    for childtag in seq.seq_tags:
                        if seqtag.seqtag_type == childtag.seqtag_type and seqtag.chrom_coord == childtag.chrom_coord and seqtag.length == childtag.length and seqtag.strand == childtag.strand:
                            already_has = childtag
                    if already_has is None:
                        seq.seq_tags.append(seqtag)
                        seqtag_output_creator.added()
                    else:
                        values_to_check = ['seq_id', 'name', 'seqtag_type', 'dbxref_id', 'source', 'secondary_name', 'relative_coord', 'length', 'orf_classification',
                                           'score', 'strand', 'frame', 'date_created', 'created_by']
                        check_values(seqtag, already_has, values_to_check, seqtag_output_creator, seqtag.id)
        else:
            if line.startswith('#'):
                print 'comment'
            elif line.startswith('>'):
                if full_sequence_id is not None:
                    contig = assemb_id_to_contig[full_sequence_id]
                    residues = ''.join(full_sequence)
                    contig_to_residues[contig.id] = residues
                    seq = Sequence(contig.id, None, None, 1, contig.length, strand, contig.length, None, residues, 'DNA', source, None, assembly.strain_id)
                    values_to_check = ['bioent_id', 'seq_version', 'coord_version', 'min_coord', 'max_coord', 'strand', 'is_current', 'length', 'ftp_file',
                                       'residues', 'seq_type', 'source', 'rootseq_id', 'strain_id', 'date_created', 'created_by']
                    add_or_check(seq, tuple_to_sequence, (seq.bioent_id, seq.rootseq_id, seq.strain_id), values_to_check, new_session, seq_output_creator)
                full_sequence_id = pieces[0][1:]
                full_sequence = []
            else:
                full_sequence.append(pieces[0])
    contig = assemb_id_to_contig[full_sequence_id]
    residues = ''.join(full_sequence)
    contig_to_residues[contig.id] = residues
    seq = Sequence(contig.id, None, None, 1, contig.length, strand, contig.length, None, residues, 'DNA', source, None, assembly.strain_id)
    values_to_check = ['bioent_id', 'seq_version', 'coord_version', 'min_coord', 'max_coord', 'strand', 'is_current', 'length', 'ftp_file',
                                       'residues', 'seq_type', 'source', 'rootseq_id', 'strain_id', 'date_created', 'created_by']
    add_or_check(seq, tuple_to_sequence, (seq.bioent_id, seq.rootseq_id, seq.strain_id), values_to_check, new_session, seq_output_creator)
                
     
    for seq in assemb_id_to_seq.values():        
        seq.residues = contig_to_residues[seq.rootseq_id][seq.min_coord-1:seq.max_coord]
        if seq.strand == '-':
            seq.residues = reverse_complement(seq.residues)
    
    gene_output_creator.finished()
    contig_output_creator.finished()
    seq_output_creator.finished()
    seqtag_output_creator.finished()
    
def reverse_complement(residues):
    code = {'G':'C', 'C':'G', 'A':'T', 'T':'A', 'R':'Y', 'Y':'R', 'W':'S', 'S':'W', 'M':'K', 'K':'M', 'V':'B', 'B':'V',
            'H':'D', 'D':'H', 'N':'N', 'X':'X', 'U':'U'}
    reverse_complement = ''.join([code[letter] for letter in reversed(residues)])
    return reverse_complement
                    
def attrs_to_dict(attrs):
    attr_dict = {}
    for attr in attrs.split(';'):
        eq_index = attr.index('=')
        key = attr[0:eq_index]
        value = attr[eq_index+1:]
        attr_dict[key] = value
    return attr_dict
            
    
    
if __name__ == "__main__":

    commit = True
    try:
        new_session = new_session_maker()
        
#        strain_name = 'Sigma1278b'
#        strain_description = 'Laboratory strain.'
#        
#        assembly_name = 'Sigma1278b_MIT'
#        assembly_description = "Assembly of the genome of S. cerevisiae strain Sigma1278b (WGS ID: ACVY00000000). Feature definitions (for coding sequences and features in the gff file) were assigned using Jim Kent's liftOver program with a blat alignment vs. the R64 (current) S288C reference sequence. This assembly contains 67 contigs (coverage: 45X, mean contig size: 177702, N50: 365700). Using liftOver, 6419 SGD gene features were found in the assembly. This data is preliminary and is subject to change without notice."
#        filename = 'Sigma1278b_ACVY01000000.gff'
#        coverage = '45X'
#        mean_contig_size = 177702
#        n50 = 365700
#        num_gene_features = 6419
#        software = 'liftOver'
#        background_strain_id = 1
#        file_location = '/Users/kpaskov/Downloads/' + filename

#        strain_name = 'AWRI1631'
#        strain_description = 'Haploid derivative of South African commercial wine strain N96.'
#        
#        assembly_name = 'AWRI1631'
#        assembly_description = "This data is preliminary and is subject to change without notice."
#        filename = 'AWRI1631_ABSV01000000.gff'
#        coverage = '7X'
#        mean_contig_size = 4500
#        n50 = 7704
#        num_gene_features = 4747
#        software = 'liftOver'
#        background_strain_id = 1
#        file_location = '/Users/kpaskov/Downloads/' + filename
        
#        strain_name = 'AWRI796'
#        strain_description = 'South African red wine strain.'
#        
#        assembly_name = 'AWR1796'
#        assembly_description = "This data is preliminary and is subject to change without notice."
#        filename = 'AWRI796_ADVS01000000.gff'
#        coverage = '20X'
#        mean_contig_size = 111795
#        n50 = 403341
#        num_gene_features = 6295
#        software = 'liftOver'
#        background_strain_id = 1
#        file_location = '/Users/kpaskov/Downloads/' + filename
#        
#        strain_name = 'BY4741'
#        strain_description = 'S288C-derivative laboratory strain.'
#        
#        assembly_name = 'BY4741'
#        assembly_description = "These data are preliminary and will be updated.  The genome fasta file does not currently include chr03, chr05, or chr12.  The gff file does not currently include the following features: YCR039C, YCR040W, YCR038W-A, YCR041W, YCL066W, YCR067C, ARS301, YCL068C, YCL065W, ARS302, YCR096C, YCR097W, ARS317, ARS318, and YCR097W-A.  The pep.fsa and cds.fsa files do not currently include the following ORFs: YCR039C, YCR040W, YCR038W-A, YCR041W, YCL066W, YCR067C, YCL068C, YCL065W, YCR096C, YCR097W, and YCR097W-A."
#        filename = 'BY4741_Toronto_2012.gff'
#        coverage = None
#        mean_contig_size = None
#        n50 = None
#        num_gene_features = 6692
#        software = 'liftOver'
#        background_strain_id = 1
#        file_location = '/Users/kpaskov/Downloads/' + filename
        
#        strain_name = 'BY4742'
#        strain_description = 'S288C-derivative laboratory strain.'
#        
#        assembly_name = 'BY4742'
#        assembly_description = "NOTE: These data are preliminary and will be updated. The genome fasta file does not currently contain chr02, chr03, or chr05."
#        filename = 'BY4742_Toronto_2012.gff'
#        coverage = None
#        mean_contig_size = None
#        n50 = None
#        num_gene_features = 6692
#        software = 'liftOver'
#        background_strain_id = 1
#        file_location = '/Users/kpaskov/Downloads/' + filename

#        strain_name = 'CBS7960'
#        strain_description = 'Brazilian bioethanol factory isolate.'
#        
#        assembly_name = strain_name
#        assembly_description = "This data is preliminary and is subject to change without notice."
#        filename = 'CBS7960_AEWL01000000.gff'
#        coverage = '17X'
#        mean_contig_size = 5161
#        n50 = 18761
#        num_gene_features = 5333
#        software = 'liftOver'
#        background_strain_id = 1
#        file_location = '/Users/kpaskov/Downloads/' + filename
#        
#        strain_name = 'CEN.PK'
#        strain_description = 'Laboratory strain.'
#        
#        assembly_name = strain_name
#        assembly_description = "This data is preliminary and is subject to change without notice."
#        filename = 'CEN.PK113-7D_AEHG00000000.gff'
#        coverage = '18X'
#        mean_contig_size = 19694
#        n50 = 61000
#        num_gene_features = 62528
#        software = 'liftOver'
#        background_strain_id = 1
#        file_location = '/Users/kpaskov/Downloads/' + filename
        
#        strain_name = 'CLIB215'
#        strain_description = 'New Zealand bakery isolate.'
#        
#        assembly_name = strain_name
#        assembly_description = "This data is preliminary and is subject to change without notice."
#        filename = 'CLIB215_AEWP01000000.gff'
#        coverage = '16.9X'
#        mean_contig_size = 7268
#        n50 = 16813
#        num_gene_features = 5051
#        software = 'liftOver'
#        background_strain_id = 1
#        file_location = '/Users/kpaskov/Downloads/' + filename
        
#        strain_name = 'CLIB324'
#        strain_description = 'Vietnamese bakery isolate.'
#        
#        assembly_name = strain_name
#        assembly_description = "This data is preliminary and is subject to change without notice."
#        filename = 'CLIB324_AEWM01000000.gff'
#        coverage = '7.1X'
#        mean_contig_size = 3079
#        n50 = 4260
#        num_gene_features = 3733
#        software = 'liftOver'
#        background_strain_id = 1
#        file_location = '/Users/kpaskov/Downloads/' + filename
        
        strain_name = 'CLIB382'
        strain_description = 'Irish beer isolate.'
        
        assembly_name = strain_name
        assembly_description = "This data is preliminary and is subject to change without notice."
        filename = 'CLIB382_AFDG01000000.gff'
        coverage = '5.96X'
        mean_contig_size = 683
        n50 = 840
        num_gene_features = 937
        software = 'liftOver'
        background_strain_id = 1
        file_location = '/Users/kpaskov/Downloads/' + filename
        
        
        
        strain = new_session.query(Strain).filter(Strain.name == strain_name).first()
        if strain is None:
            strain = Strain(strain_name, strain_description)
            new_session.add(strain)
            new_session.commit()
        print strain.id
        
        assembly = new_session.query(Assembly).filter(Assembly.filename == filename).first()
        if assembly is None:
            assembly = Assembly(assembly_name, assembly_description, filename, coverage, mean_contig_size, n50, num_gene_features, software, strain.id, background_strain_id)
            new_session.add(assembly)
            new_session.commit()
        print assembly.id
        
        load_gff(assembly, file_location, new_session)
        
        
      
        if commit:
            new_session.commit()
    finally:
        new_session.close()
    

    
    