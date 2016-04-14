from sqlalchemy.orm import joinedload
from src.sgd.convert import basic_convert
from src.sgd.convert.util import number_to_roman

__author__ = 'sweng66'

TAXON = "TAX:559292"

def arch_proteinseqannotation_starter(bud_session_maker):
    from src.sgd.model.nex.so import So
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.arch_contig import ArchContig
    from src.sgd.model.nex.arch_dnaseqannotation import ArchDnaseqannotation
    from src.sgd.model.nex.genomerelease import Genomerelease

    nex_session = get_nex_session()

    print "populating dictionaries..."

    format_name_to_contig_id = dict([(x.format_name, x.id) for x in nex_session.query(ArchContig).all()])
    contig_id_dbentity_id_to_annotation = dict([((x.contig_id, x.dbentity_id), x) for x in nex_session.query(ArchDnaseqannotation).all()])
    feature_bud_id_to_dbentity = dict([(x.bud_id, x) for x in nex_session.query(Locus).all()])
    genomerelease_to_id = dict([(x.format_name, x.id) for x in nex_session.query(Genomerelease).all()])
                                    
    taxonomy_obj = nex_session.query(Taxonomy).filter_by(taxid=TAXON).first()
    taxonomy_id = taxonomy_obj.id

    # 1.  Version = 64-1-1
    # 2.  Chromosome = VI
    # 3.  feature_name = YFL039C
    # 4.  feature_no = 4430
    # 5.  gene_name = ACT1
    # 6.  seq_version
    # 7.  created_by
    # 8.  date_created
    # 9.  residues

    print "Start loading..."
    
    f = open("src/sgd/convert/data/arch_proteinseqannotation.txt")
    for line in f:
        pieces = line.strip().split("\t")
        if len(pieces) < 9:
            print "bad row: ", line 
            continue
        if pieces[0] == '64-2-1':
            continue
        if pieces[5] is None:
            continue
        genome_release = pieces[0]
        arch_contig_format_name = None
        if pieces[1] == 17:
            arch_contig_format_name = "Chromosome_Mito_R" + genome_release
        elif pieces[1] == '2-micron':
            arch_contig_format_name = "2-micron_plasmid_R" + genome_release
        else:
            arch_contig_format_name = "Chromosome_" + number_to_roman[pieces[1]]+ "_R" + genome_release
        arch_contig_id = format_name_to_contig_id.get(arch_contig_format_name)
        if arch_contig_id is None:
            print "The contig format_name: ", arch_contig_format_name, " is not in ARCH_CONTIG table."
            continue
        genomerelease_id = genomerelease_to_id.get(genome_release)
        if genomerelease_id is None:
            print "The genomerelease: ", genome_release, " is not in GENOMERELEASE table."
            continue
        dbentity = feature_bud_id_to_dbentity.get(int(pieces[3]))                           
        if dbentity is None:
            print "The BUD_ID = feature_no =", pieces[3], " is not in LOCUSDBENTITY table."
            continue
        dbentity_id = dbentity.id
        sgdid = dbentity.sgdid
        annotation = contig_id_dbentity_id_to_annotation.get((arch_contig_id, dbentity_id))
        name = pieces[2]
        gene_name = pieces[4]
        if gene_name == "":
            gene_name = name
 
        file_header = ">" + name + " " + gene_name + " SGDID:" + sgdid + " chr" + pieces[1] + ":"
        if annotation.strand == '-':
            file_header = file_header + str(annotation.end_index) + ".." + str(annotation.start_index)
        else:
            file_header = file_header + str(annotation.start_index) + ".." + str(annotation.end_index)
        file_header = file_header + " [Genome Release " + genome_release + "]"
        download_filename = name + "-protein.fsa"
 
        yield { 'dbentity_id': dbentity_id,
                'source': { 'display_name': 'SGD' },
                'taxonomy_id': taxonomy_id,
                'contig_id': arch_contig_id,
                'seq_version': str(pieces[5]),
                'created_by': pieces[6],
                'date_created': str(pieces[7]),
                'residues': pieces[8],
                'file_header': file_header,
                'download_filename': download_filename }
    
    f.close()
    nex_session.close()    

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, arch_proteinseqannotation_starter, 'arch_proteinseqannotation', lambda x: (x['dbentity_id'], x['contig_id'], x['residues']))
