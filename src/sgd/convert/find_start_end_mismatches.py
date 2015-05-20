__author__ = 'kpaskov'


new_sequence_files = [("data/strains/Sigma1278b-10560-6B_JRIQ00000000.gff", 'src/sgd/convert/data/strains/Sigma1278b-10560-6B_JRIQ00000000_cds.fsa', 'Sigma1278b'),
                      ("data/strains/BC187_JRII00000000.gff", "src/sgd/convert/data/strains/BC187_JRII00000000_cds.fsa", 'BC187'),
                      ("data/strains/BY4741_JRIS00000000.gff", "src/sgd/convert/data/strains/BY4741_JRIS00000000_cds.fsa", 'BY4741'),
                      ("data/strains/BY4742_JRIR00000000.gff", "src/sgd/convert/data/strains/BY4742_JRIR00000000_cds.fsa", 'BY4742'),
                      ("data/strains/CEN.PK2-1Ca_JRIV01000000.gff", "src/sgd/convert/data/strains/CEN.PK2-1Ca_JRIV01000000_cds.fsa", 'CENPK'),
                      ("data/strains/D273-10B_JRIY00000000.gff", "src/sgd/convert/data/strains/D273-10B_JRIY00000000_cds.fsa", 'D273-10B'),
                      ("data/strains/DBVPG6044_JRIG00000000.gff", "src/sgd/convert/data/strains/DBVPG6044_JRIG00000000_cds.fsa", 'DBVPG6044'),
                      ("data/strains/FL100_JRIT00000000.gff", "src/sgd/convert/data/strains/FL100_JRIT00000000_cds.fsa", 'FL100'),
                      ("data/strains/FY1679_JRIN00000000.gff", "src/sgd/convert/data/strains/FY1679_JRIN00000000_cds.fsa", 'FY1679'),
                      ("data/strains/JK9-3d_JRIZ00000000.gff", "src/sgd/convert/data/strains/JK9-3d_JRIZ00000000_cds.fsa", 'JK9-3d'),
                      ("data/strains/K11_JRIJ00000000.gff", "src/sgd/convert/data/strains/K11_JRIJ00000000_cds.fsa", 'K11'),
                      ("data/strains/L1528_JRIK00000000.gff", "src/sgd/convert/data/strains/L1528_JRIK00000000_cds.fsa", 'L1528'),
                      ("data/strains/RedStar_JRIL00000000.gff", "src/sgd/convert/data/strains/RedStar_JRIL00000000_cds.fsa", 'RedStar'),
                      ("data/strains/RM11-1A_JRIP00000000.gff", "src/sgd/convert/data/strains/RM11-1A_JRIP00000000_cds.fsa", 'RM11-1a'),
                      ("data/strains/SEY6210_JRIW00000000.gff", "src/sgd/convert/data/strains/SEY6210_JRIW00000000_cds.fsa", 'SEY6210'),
                      ("data/strains/SK1_JRIH00000000.gff", "src/sgd/convert/data/strains/SK1_JRIH00000000_cds.fsa", 'SK1'),
                      ("data/strains/UWOPS05-217-3_JRIM00000000.gff", "src/sgd/convert/data/strains/UWOPS05-217-3_JRIM00000000_cds.fsa", 'UWOPSS'),
                      ("data/strains/W303_JRIU00000000.gff", "src/sgd/convert/data/strains/W303_JRIU00000000_cds.fsa", 'W303'),
                      ("data/strains/X2180-1A_JRIX00000000.gff", "src/sgd/convert/data/strains/X2180-1A_JRIX00000000_cds.fsa", 'X2180-1A'),
                      ("data/strains/Y55_JRIF00000000.gff", "src/sgd/convert/data/strains/Y55_JRIF00000000_cds.fsa", 'Y55'),
                      ("data/strains/YJM339_JRIE00000000.gff", "src/sgd/convert/data/strains/YJM339_JRIE00000000_cds.fsa", 'YJM339'),
                      ("data/strains/YPH499_JRIO00000000.gff", "src/sgd/convert/data/strains/YPH499_JRIO00000000_cds.fsa", 'YPH499'),
                      ("data/strains/YPS128_JRID00000000.gff", "src/sgd/convert/data/strains/YPS128_JRID00000000_cds.fsa", 'YPS128'),
                      ("data/strains/YPS163_JRIC00000000.gff", "src/sgd/convert/data/strains/YPS163_JRIC00000000_cds.fsa", 'YPS163'),
                      ("data/strains/YS9_JRIB00000000.gff", "src/sgd/convert/data/strains/YS9_JRIB00000000_cds.fsa", 'YS9')]

def find_mismatches():
    output_file = open('start_end_mismatches.txt', 'w+')
    for sequence_file, _, strain in new_sequence_files:
        gene_to_CDS_start = dict()
        gene_to_CDS_end = dict()
        gene_start_end = dict()
        gene_count = dict()
        f = open(sequence_file, 'r')
        for row in f:
            pieces = row.split(' ')
            if len(pieces) >= 9 and not row.startswith('>'):
                class_type = pieces[2]
                start = int(pieces[3])
                end = int(pieces[4])
                gene_name = pieces[8].split(',')[0]

                if class_type == 'CDS':
                    if gene_name not in gene_to_CDS_start:
                        gene_to_CDS_start[gene_name] = []
                        gene_to_CDS_end[gene_name] = []
                    gene_to_CDS_start[gene_name].append(start)
                    gene_to_CDS_end[gene_name].append(end)
                elif class_type == 'gene':
                    gene_start_end[gene_name] = (start, end)
                    if gene_name not in gene_count:
                        gene_count[gene_name] = 0
                    gene_count[gene_name] += 1

        f.close()

        for gene_name, (start, end) in gene_start_end.iteritems():
            min_CDS_start = None if gene_name not in gene_to_CDS_start else min(gene_to_CDS_start[gene_name])
            max_CDS_end = None if gene_name not in gene_to_CDS_end else max(gene_to_CDS_end[gene_name])
            if min_CDS_start is not None and max_CDS_end is not None and gene_name != 'UNDEF':
                has_intron = 'Has Intron' if len(gene_to_CDS_start[gene_name]) > 1 else ''
                if min_CDS_start != start and max_CDS_end != end:
                    output_file.write('\t'.join([gene_name, strain, 'Both', has_intron, str(gene_count[gene_name])]) + '\n')
                elif min_CDS_start != start:
                    output_file.write('\t'.join([gene_name, strain, 'Start', has_intron, str(gene_count[gene_name])]) + '\n')
                elif max_CDS_end != end:
                    output_file.write('\t'.join([gene_name, strain, 'End', has_intron, str(gene_count[gene_name])]) + '\n')

    output_file.close()

if __name__ == "__main__":
    find_mismatches()