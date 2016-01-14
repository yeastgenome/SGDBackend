from src.sgd.convert import basic_convert
from src.sgd.convert.sequence_files import protein_sequence_files_for_alt_strains
from src.sgd.convert.util import get_protein_sequence_library_fsa, \
     get_strain_taxid_mapping, number_to_roman

__author__ = 'sweng66'

def proteinsequenceannotation_starter(bud_session_maker):

    from src.sgd.model.nex.strain import Strain
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.contig import Contig
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.genomerelease import Genomerelease
    
    nex_session = get_nex_session()
    bud_session = bud_session_maker()

    strain_to_strain_id =  dict([(x.format_name, x.id) for x in nex_session.query(Strain).all()])
    contig_name_to_contig = dict([(x.format_name, x) for x in nex_session.query(Contig).all()])
    contig_id_to_contig_name = dict([(x.id, x.format_name) for x in nex_session.query(Contig).all()])
    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    bud_id_to_genomerelease_id =  dict([(x.bud_id, x.id) for x in nex_session.query(Genomerelease).all()])
    locus_to_dbentity_id = dict([(x.systematic_name, x.id) for x in nex_session.query(Locus).all()])
    strain_to_taxid_mapping = get_strain_taxid_mapping()
    
    ########### load protein sequences for S288C
    
    from src.sgd.model.bud.sequence import Sequence, SeqRel, Feat_Location
    from src.sgd.model.bud.feature import Feature, FeatRel

    taxid = strain_to_taxid_mapping['S288C']
    taxonomy_id = taxid_to_taxonomy_id[taxid]

    bud_id_to_contig_id = dict()
    bud_id_to_chr = dict()

    bud_id_to_locus_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    child_id_to_parent_id = dict([(x.child_id, x.parent_id) for x in bud_session.query(FeatRel).filter_by(rank=1).all()])
    id_to_feature = dict([(x.id, x) for x in bud_session.query(Feature).all()])
    seq_id_to_release_bud_id = dict([(x.seq_id, x.release_id) for x in bud_session.query(SeqRel).all()])

    for bud_id in child_id_to_parent_id:
        chr_id = child_id_to_parent_id[bud_id]
        if id_to_feature[chr_id].name in number_to_roman:
            chr_name = 'Chromosome_' + number_to_roman[id_to_feature[chr_id].name]
            bud_id_to_chr[bud_id] = number_to_roman[id_to_feature[chr_id].name]
        else:
            chr_name = 'Chromosome_' + id_to_feature[bud_id].name
            bud_id_to_chr[bud_id] = id_to_feature[bud_id].name
        if chr_name in contig_name_to_contig:
            bud_id_to_contig_id[bud_id] = contig_name_to_contig[chr_name].id
    
    plasmid_x = nex_session.query(Contig).filter_by(format_name="2-micron_plasmid").first()
    plasmid_contig_id = plasmid_x.id

    name_to_coords = {}
    for bud_location in bud_session.query(Feat_Location).all():
        bud_id = bud_location.feature_id
        if bud_location.is_current == 'Y':
            name = id_to_feature[bud_id].name
            name_to_coords[name] = str(bud_location.min_coord) + ".." + str(bud_location.max_coord) 
    name_to_release_bud_id = {}
    for bud_seq in bud_session.query(Sequence).filter_by(is_current='Y').filter_by(seq_type='genomic').all():
        bud_id = bud_seq.feature_id
        name = id_to_feature[bud_id].name
        name_to_release_bud_id[name] = seq_id_to_release_bud_id.get(bud_seq.id)

    for bud_seq in bud_session.query(Sequence).filter_by(is_current='Y').filter_by(seq_type='protein').all():
        bud_id = bud_seq.feature_id
        name = id_to_feature[bud_id].name
        gene_name = id_to_feature[bud_id].gene_name
        sgdid = id_to_feature[bud_id].dbxref_id
        chr = bud_id_to_chr[bud_id]
        
        dbentity_id = locus_to_dbentity_id.get(name)
        if dbentity_id is None:
            print "The feature ", name, " is not in DBENTITY table."
            continue
        contig_id = bud_id_to_contig_id.get(bud_id)
        if name.startswith('R00'):
            contig_id = plasmid_contig_id
        if contig_id is None:
            print "The feature ", name, " is not mapped to a chromosome."
            continue

        release_bud_id = name_to_release_bud_id.get(name) 
        if release_bud_id is None:
            print "The seq for feature:", bud_seq.id, " is not mapped to the BUD.SEQ_REL table."
            continue
        release_id = bud_id_to_genomerelease_id.get(release_bud_id)
        if release_id is None:
            print "The BUD release_no:", release_bud_id, " is not in GENOMERELEASE table."
            continue
        if gene_name is None:
            gene_name = name
        file_header = ">" + name + " " + gene_name + " SGDID:" + sgdid + " chr" + chr + ":" + name_to_coords[name] + " [Genome Release 64-2-1]"
        download_filename = name + "-protein.fsa"
        
        yield { 'source': { "display_name": 'SGD'},
                'taxonomy_id': taxonomy_id,
                'dbentity_id': dbentity_id,
                'residues': bud_seq.residues,
                'seq_version': str(bud_seq.seq_version),
                'bud_id': bud_seq.id,
                'contig_id': contig_id,
                'file_header': file_header,
                'genomerelease_id': release_id,
                'download_filename': download_filename,
                'date_created': str(bud_seq.date_created),
                'created_by': bud_seq.created_by }


    ########### load protein sequences for the alternative strains
        
    for sequence_filename, strain in protein_sequence_files_for_alt_strains:
        strain = strain.replace('.', '')
        strain_id = strain_to_strain_id.get(strain)
        if strain_id is None:
            print "The strain ", strain, " is not in STRAIN table."
            continue
        taxid = strain_to_taxid_mapping.get(strain)
        if taxid is None:
            print "The strain: ", strain, " is not mapped to a TAXON ID."
            continue

        taxonomy_id = taxid_to_taxonomy_id.get(taxid)
        if taxonomy_id is None:
            print "The strain ", strain, " is not in TAXONOMY table."
            continue

        f = open(sequence_filename, 'r')
        for (name_strain, header), residues in get_protein_sequence_library_fsa(f).iteritems():
            name = name_strain.split('_')[0]
            items = header.split(' ')
            if items[0].startswith('>UNDEF'):
                continue
            gene = items[1]
            if "|" in gene:
                items[2] = gene
                gene = name
            dbentity_id = locus_to_dbentity_id.get(name)
            if dbentity_id is None:
                print "The feature name:", name, " is not in DBENTITY table."
                continue

            if gene_name is None:
                gene_name = name

            contig_name = items[2].split("|")[3]
            coords = items[3].replace("-", "..")
            contig_obj = contig_name_to_contig.get(contig_name)
            if contig_obj is None:
                print "The contig name: ", contig_name, " is not in the Contig table."
                continue
            contig_id = contig_obj.id

            file_header = ">" + name + " " + gene_name + " " + contig_name + ":" + coords 
            download_filename = name_strain + "-protein.fsa"
        
            yield { 'source': { "display_name": 'SGD'},
                    'taxonomy_id': taxonomy_id,
                    'dbentity_id': dbentity_id,
                    'residues': residues,
                    'contig_id': contig_id,
                    'file_header': file_header,
                    'download_filename': download_filename }
                               
    nex_session.close()
    bud_session.close()

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, proteinsequenceannotation_starter, 'proteinsequenceannotation', lambda x: (x['dbentity_id'], x['taxonomy_id'], x['contig_id']))
