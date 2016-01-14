from sqlalchemy.orm import joinedload
from src.sgd.convert import basic_convert
from src.sgd.convert.sequence_files import new_sequence_files
from src.sgd.convert.util import make_fasta_file_starter, number_to_roman, \
    get_dna_sequence_library, get_sequence, get_ref_sequence_library_fsa, \
    get_sequence_library_fsa, reverse_complement, get_strain_taxid_mapping

__author__ = 'sweng66'

S288C_TAXON = "TAX:559292"

def dnasubsequence_starter(bud_session_maker):
    from src.sgd.model.nex.so import So
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.strain import Strain
    from src.sgd.model.nex.contig import Contig
    from src.sgd.model.nex.dnasequenceannotation import Dnasequenceannotation
    # from src.sgd.model.nex.genomerelease import Genomerelease
    
    nex_session = get_nex_session()
    bud_session = bud_session_maker()

    contig_name_to_contig = dict([(x.format_name, x) for x in nex_session.query(Contig).all()])    
    type_to_so_id = dict([(x.display_name, x.id) for x in nex_session.query(So).all()]) 
    feature_bud_id_to_dbentity = dict([(x.bud_id, x) for x in nex_session.query(Locus).all()])
    name_to_dbentity_id = dict([(x.systematic_name, x.id) for x in nex_session.query(Locus).all()])

    S288C_taxonomy_obj = nex_session.query(Taxonomy).filter_by(taxid=S288C_TAXON).first()
    S288C_taxonomy_id = S288C_taxonomy_obj.id

    ### load sub features from BUD for S288C

    from src.sgd.model.bud.feature import FeatRel
    from src.sgd.model.bud.sequence import Sequence, Feat_Location, FeatLocation_Rel
    
    feature_id_to_parent = dict([(x.child_id, x.parent_id) for x in bud_session.query(FeatRel).all()])  

    dbentity_id_to_dnasequenceannotation = dict([(x.dbentity_id, x) for x in nex_session.query(Dnasequenceannotation).filter_by(dna_type='GENOMIC').filter_by(taxonomy_id=S288C_taxonomy_id).all()])

    feature_types = get_feature_type_list()

    for bud_location in bud_session.query(Feat_Location).filter(Feat_Location.is_current == 'Y').options(joinedload('sequence'), joinedload('feature')).all():

        if bud_location.feature.type not in feature_types:
            continue
        if bud_location.sequence.is_current == 'N' or bud_location.feature.status != 'Active':
            continue
        ## it is an active, current subfeature; ID from BUD  
        parent_dbentity_id = None
        parent_name = None
        parent_gene = None
        if 'uORF' in bud_location.feature.name:
            name = bud_location.feature.name
            parent_name = name.split('-')[0]
            parent_gene = parent_name
            parent_dbentity_id = name_to_dbentity_id.get(parent_name)
        else:    
            child_id = bud_location.feature_id
            parent_id = feature_id_to_parent.get(child_id)
            if parent_id is None:
                print "The subfeature BUD feature_no:", child_id, " does not have a parent in FEAT_RELATIONSHIP table."
                continue
            ## ID from NEX for main feature (eg. YFL039C)
            parent_dbentity_obj = feature_bud_id_to_dbentity.get(parent_id)
            if parent_dbentity_obj is None:
                print "The BUD feature_no:", parent_id, " is not in DBENTITY table."
                continue
            parent_dbentity_id = parent_dbentity_obj.id
            parent_name = parent_dbentity_obj.systematic_name
            parent_gene = parent_name
            if parent_dbentity_obj.gene_name is not None:
                parent_gene = parent_dbentity_obj.gene_name
        annotation_obj = dbentity_id_to_dnasequenceannotation.get(parent_dbentity_id)
        if annotation_obj is None:
            print "The genomic sequence for BUD feature_no:", parent_id, " is not in DNASEQUENCEANNOTATION table."
            continue
        so_id = type_to_so_id.get(bud_location.feature.type)
        if so_id is None:
            print "The feature_type:", bud_location.feature.type, " is not in SO table."
            continue
        residues = bud_location.sequence.residues        
        start = bud_location.min_coord
        end = bud_location.max_coord
        display_name = bud_location.feature.type
        relative_start_index = start - annotation_obj.start_index + 1
        relative_end_index = end - annotation_obj.start_index + 1
        contig_start_index = start
        contig_end_index = end

        file_header = ">" + parent_name + " " + parent_gene + " " + bud_location.feature.type + ":" + str(start) + ".." + str(end) 
        download_filename = parent_name + "_" + bud_location.feature.type + ".fsa"

        yield { 'annotation_id': annotation_obj.id,
                'dbentity_id': parent_dbentity_obj.id,
                'display_name': display_name,
                'bud_id': bud_location.sequence.id,
                'so_id': so_id,
                'relative_start_index': relative_start_index,
                'relative_end_index': relative_end_index,
                'contig_start_index': contig_start_index,
                'contig_end_index': contig_end_index,
                'seq_version': str(bud_location.sequence.seq_version),
                'coord_version': str(bud_location.coord_version),  
                'residues': residues,
                'file_header': file_header,
                'download_filename': download_filename,
                'date_created': str(bud_location.sequence.date_created),
                'created_by': str(bud_location.sequence.created_by) }


    #Five prime UTR introns: 

    for feat_rel in bud_session.query(FeatRel).filter_by(relationship_type='adjacent_to').all():
        feat_location = bud_session.query(Feat_Location).filter_by(feature_id=feat_rel.child_id).filter_by(is_current='Y').first()
        parent_dbentity_obj = feature_bud_id_to_dbentity.get(feat_rel.parent_id)
        if parent_dbentity_obj is None:
            print "The BUD feature_no:", parent_id, " is not in DBENTITY table."
            continue
        annotation_obj = dbentity_id_to_dnasequenceannotation.get(parent_dbentity_obj.id)
        if annotation_obj is None:
            print "The genomic sequence for BUD feature_no:", parent_id, " is not in DNASEQUENCEANNOTATION table."
            continue
        so_id = type_to_so_id.get(feat_location.feature.type)
        if so_id is None:
            print "The feature_type:", feat_location.feature.type, " is not in SO table."
            continue
        residues = feat_location.sequence.residues
        start = feat_location.min_coord
        end = feat_location.max_coord
        display_name =feat_location.feature.type
        relative_start_index = start - annotation_obj.start_index + 1
        relative_end_index = end - annotation_obj.start_index + 1
        contig_start_index = start
        contig_end_index = end
        name = parent_dbentity_obj.systematic_name
        gene = name
        if parent_dbentity_obj.gene_name is not None:
            gene = parent_dbentity_obj.gene_name
        file_header = ">" + name + " " + gene + " " + feat_location.feature.type + ":" + str(start) + ".." + str(end)
        download_filename = name + "_" + feat_location.feature.type + ".fsa"
        
        yield { 'annotation_id': annotation_obj.id,
                'dbentity_id': parent_dbentity_obj.id,
                'display_name': display_name,
                'bud_id': bud_location.sequence.id,
                'so_id': so_id,
                'relative_start_index': relative_start_index,
                'relative_end_index': relative_end_index,
                'contig_start_index': contig_start_index,
                'contig_end_index': contig_end_index,
                'seq_version': str(bud_location.sequence.seq_version),
                'coord_version': str(bud_location.coord_version),
                'residues': residues,
                'file_header': file_header,
                'download_filename': download_filename,
                'date_created': str(bud_location.sequence.date_created),
                'created_by': str(bud_location.sequence.created_by) }
                    
    # Other strains                                                                                 
    contig_name_to_contig = dict([(x.format_name, x) for x in nex_session.query(Contig).all()])
    strain_to_strain_id =  dict([(x.format_name, x.id) for x in nex_session.query(Strain).all()])
    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    strain_to_taxid_mapping = get_strain_taxid_mapping()
    
    for seq_file, coding_file, strain in new_sequence_files:
        strain_id = strain_to_strain_id.get(strain.replace('.', ''))
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
        
        dbentity_contig_to_dnasequenceannotation = dict([((x.dbentity_id, x.contig_id), x) for x in nex_session.query(Dnasequenceannotation).filter_by(dna_type='GENOMIC').filter_by(taxonomy_id=taxonomy_id).all()])                                                   
        f = open(seq_file, 'r')
        sequence_library = get_dna_sequence_library(f, remove_spaces=True)
        f.close()

        f = open(seq_file, 'r')
        for row in f:
            if row.startswith('>'):
                break
            pieces = row.split(' ')
            if len(pieces) >= 9:
                class_type = pieces[2]
                parent_id = pieces[0]
                contig_name = parent_id.split('|')[3]
                if (class_type == 'CDS' or class_type == 'intron') and contig_name in contig_name_to_contig:
                    start = int(pieces[3])
                    end = int(pieces[4])
                    strand = pieces[6]
                    infos = pieces[8].split(',')
                    residues = get_sequence(parent_id, start, end, strand, sequence_library)
                    contig_obj = contig_name_to_contig[contig_name]
                    contig_id = contig_obj.id
                    name = infos[0].strip()
                    gene = name
                    if len(infos) > 5:
                        gene = infos[5].strip()
                    dbentity_id = name_to_dbentity_id.get(name)
                    if dbentity_id is None:
                        print "The feature:", name, " is not in the DBENTITY table."
                        continue
                    annotation_obj = dbentity_contig_to_dnasequenceannotation.get((dbentity_id, contig_id))
                    if annotation_obj is None:
                        print "The name=", name, " and contig=", contig_name, " is not in DNASEQUENCEANNOTATION table."
                        continue
                    so_id = type_to_so_id.get(class_type)
                    if so_id is None:
                        print "The subfeature type:", class_type, " is not in SO table."
                        continue
                    file_header = ">" + name + " " + gene + " " + class_type + ":" + str(start) + ".." + str(end)
                    download_filename = name + "_" + strain + "_" + class_type + ".fsa"

                    yield { 'annotation_id': annotation_obj.id,
                            'dbentity_id': dbentity_id,
                            'display_name': class_type,
                            'so_id': so_id,
                            'relative_start_index': start - annotation_obj.start_index + 1,
                            'relative_end_index': end - annotation_obj.start_index + 1,
                            'contig_start_index': start,
                            'contig_end_index': end,
                            'residues': residues,
                            'file_header': file_header,
                            'download_filename': download_filename } 
        f.close()

    nex_session.close()
    bud_session.close()


def get_feature_type_list():

    return [ "ARS_consensus_sequence",
             "CDS",
             "W_region",
             "X_element",
             "X_element_combinatorial_repeat",
             "X_region",
             "Y_prime_element",
             "Y_region",
             "Z1_region",
             "Z2_region",
             "binding_site",
             "centromere_DNA_Element_I",
             "centromere_DNA_Element_II",
             "centromere_DNA_Element_III",
             "external_transcribed_spacer_region",
             "five_prime_UTR_intron",
             "insertion",
             "intein_encoding_region",
             "internal_transcribed_spacer_region",
             "intron",
             "mRNA",
             "non_transcribed_region",
             "noncoding_exon",
             "plus_1_translational_frameshift",
             "telomeric_repeat",
             "uORF" ]

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, dnasubsequence_starter, 'dnasubsequence', lambda x: (x['annotation_id'], x['dbentity_id'], x['so_id'], x['residues'], x['relative_start_index'], x['relative_end_index']))
