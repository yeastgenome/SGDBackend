from src.sgd.convert import basic_convert
from src.sgd.convert.util import number_to_roman, get_strain_taxid_mapping

__author__ = 'sweng66'

def arch_dnaseqannotation_starter(bud_session_maker):

    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.so import So
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.genomerelease import Genomerelease
    from src.sgd.model.nex.arch_contig import ArchContig

    nex_session = get_nex_session()
    bud_session = bud_session_maker()

    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    bud_id_to_genomerelease_id =  dict([(x.bud_id, x.id) for x in nex_session.query(Genomerelease).all()])
    type_to_so_id = dict([(x.display_name, x.id) for x in nex_session.query(So).all()]) 
    locus_to_dbentity_id = dict([(x.systematic_name, x.id) for x in nex_session.query(Locus).all()])
    
    strain_to_taxid_mapping = get_strain_taxid_mapping()

    from sqlalchemy.sql.expression import or_
    from src.sgd.model.bud.feature import Feature, FeatRel
    from src.sgd.model.bud.sequence import Sequence, Feat_Location, FeatLocation_Rel
    
    feature_types = get_feature_type_list()

    taxid = strain_to_taxid_mapping['S288C']
    taxonomy_id = taxid_to_taxonomy_id[taxid]

    bud_id_to_chr = dict()

    bud_id_to_locus_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    child_id_to_parent_id = dict([(x.child_id, x.parent_id) for x in bud_session.query(FeatRel).filter_by(rank=1).all()])
    id_to_feature = dict([(x.id, x) for x in bud_session.query(Feature).all()])
    # feature_location_id_to_release_bud_id = dict([(x.feature_location_id, x.release_id) for x in bud_session.query(FeatLocation_Rel).all()])

    feature_location_id_to_release_bud_id = {}
    for x in bud_session.query(FeatLocation_Rel).all():
        ids = []
        if x.feature_location_id in feature_location_id_to_release_bud_id:
            ids = feature_location_id_to_release_bud_id.get(x.feature_location_id)
        ids.append(x.release_id)
        feature_location_id_to_release_bud_id[x.feature_location_id] = ids

    for bud_id in child_id_to_parent_id:
        chr_id = child_id_to_parent_id[bud_id]
        if id_to_feature[chr_id].name in number_to_roman:
            bud_id_to_chr[bud_id] = number_to_roman[id_to_feature[chr_id].name]
        else:
            bud_id_to_chr[bud_id] = id_to_feature[bud_id].name

    key_to_arch_contig_id = {}
    genomerelease_id_to_version = {}
    for x in nex_session.query(ArchContig).all():
        pieces = x.format_name.split('_')
        chr = pieces[1]
        version = pieces[2]
        key = (chr, x.genomerelease_id)
        key_to_arch_contig_id[key] = x.id
        genomerelease_id_to_version[x.genomerelease_id] = version.replace("R", "")

    for bud_location in bud_session.query(Feat_Location).all():
        bud_id = bud_location.feature_id

        type = id_to_feature[bud_id].type
        # if type in feature_types and bud_location.is_current == 'N':
        if type in feature_types:
            name = id_to_feature[bud_id].name
            gene_name = id_to_feature[bud_id].gene_name
            if gene_name is None:
                gene_name = name
            sgdid = id_to_feature[bud_id].dbxref_id
            chr = bud_id_to_chr[bud_id]

            dbentity_id = bud_id_to_locus_id.get(bud_id)
            if dbentity_id is None:
                print "The feature ", name, " is not in DBENTITY table."
                continue
            so_id = type_to_so_id.get(type)
            if name.startswith('R00'):
                so_id = type_to_so_id.get('ORF')
            if so_id is None:
                print "The feature_type ", type, " is not in SO table."
                continue

            chrname = number_to_roman.get(chr)
            if chrname is None:
                chrname = chr

            release_bud_ids = feature_location_id_to_release_bud_id.get(bud_location.id)
            if release_bud_ids is None:
                continue
            for release_bud_id in release_bud_ids:
                release_id = bud_id_to_genomerelease_id.get(release_bud_id)
                release_version = genomerelease_id_to_version.get(release_id)
                if release_version == '64-2-1':
                    continue
                if release_version is None:
                    print "The genomerelease_id: ", release_id, " is not in the ARCH_CONTIG table."
                    continue
                arch_contig_id = key_to_arch_contig_id.get((chrname, release_id))
                if arch_contig_id is None:
                    print "The genomerelease_id: ", release_id, " is not in the ARCH_CONTIG table."
                    continue
            
                file_header = ">" + name + " " + gene_name + " SGDID:" + sgdid + " chr" + chr + ":"
                if bud_location.strand == '-':
                    file_header = file_header + str(bud_location.max_coord) + ".." + str(bud_location.min_coord)
                else:
                    file_header = file_header + str(bud_location.min_coord) + ".." + str(bud_location.max_coord)
                file_header = file_header + " [Genome Release " + release_version + "]"
                download_filename = name + "-genomic.fsa"

                yield { 'source': { "display_name": 'SGD'},
                        'taxonomy_id': taxonomy_id,
                        'dbentity_id': bud_id_to_locus_id[bud_id],
                        'dna_type': 'GENOMIC',
                        'so_id': so_id,
                        'residues': bud_location.sequence.residues,
                        'seq_version': str(bud_location.sequence.seq_version),
                        'coord_version': str(bud_location.coord_version),
                        'bud_id': bud_location.sequence.id,
                        'contig_id': arch_contig_id,
                        'start_index': bud_location.min_coord,
                        'end_index': bud_location.max_coord,
                        'strand': bud_location.strand,
                        'file_header': file_header,
                        'genomerelease_id': release_id,
                        'download_filename': download_filename,
                        'date_created': str(bud_location.sequence.date_created),
                        'created_by': bud_location.sequence.created_by }
    
    nex_session.close()
    bud_session.close()

def get_feature_type_list():

    return [ "ARS", 
             "LTR_retrotransposon", 
             "ORF", 
             "blocked_reading_frame", 
             "disabled_reading_frame", 
             "centromere", 
             "gene_group", 
             "long_terminal_repeat",
             "mating_type_region",
             "matrix_attachment_site", 
             "ncRNA_gene",
             "origin_of_replication",
             "pseudogene",
             "rRNA_gene",
             "silent_mating_type_cassette_array",
             "snRNA_gene", 
             "snoRNA_gene", 
             "tRNA_gene",
             "telomerase_RNA_gene",
             "telomere",
             "transposable_element_gene" ]

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, arch_dnaseqannotation_starter, 'arch_dnaseqannotation', lambda x: (x['dbentity_id'], x['taxonomy_id'], x['so_id'], x['dna_type'], x['contig_id']))
