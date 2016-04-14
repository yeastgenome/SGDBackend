from src.sgd.convert import basic_convert
from src.sgd.convert.sequence_files import sequence_files, new_sequence_files
from src.sgd.convert.util import make_fasta_file_starter, number_to_roman, get_strain_taxid_mapping

__author__ = 'sweng66'

def arch_contig_starter(bud_session_maker):

    from src.sgd.model.nex.strain import Strain
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.so import So
    from src.sgd.model.nex.genomerelease import Genomerelease

    nex_session = get_nex_session()
    bud_session = bud_session_maker()

    strain_to_strain_id =  dict([(x.format_name, x.id) for x in nex_session.query(Strain).all()])
    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    genomerelease_to_genomerelease_id =  dict([(x.display_name, x.id) for x in nex_session.query(Genomerelease).all()])
    type_to_so_id = dict([(x.display_name, x.id) for x in nex_session.query(So).all()]) 

    strains_with_chromosomes = set(['S288C'])
    strain_to_taxid_mapping = get_strain_taxid_mapping()

    #load chromosomes for S288C  

    from sqlalchemy.sql.expression import or_
    from src.sgd.model.bud.feature import Feature
    from src.sgd.model.bud.sequence import Sequence

    taxid = strain_to_taxid_mapping['S288C']
    taxonomy_id = taxid_to_taxonomy_id[taxid]

    for feature in bud_session.query(Feature).filter(or_(Feature.type == 'chromosome', Feature.type == 'plasmid')).all():
        so_id = type_to_so_id[feature.type]
        for sequence in feature.sequences:
            # if sequence.is_current == 'N':
            if sequence.ftp_file == '':
                continue
            name = None
            if feature.type == 'plasmid':
                name = '2-micron plasmid'
            else:
                name = 'Chromosome ' + (feature.name if feature.name not in number_to_roman else number_to_roman[feature.name])
        
            if len(sequence.seq_rels) < 1:
                continue

            for seqrel in sequence.seq_rels:

                if seqrel.release.genome_release == "64-2-1":
                    continue

                genomerelease_id = genomerelease_to_genomerelease_id.get(seqrel.release.genome_release)
                if genomerelease_id is None:
                    print "The genome release: ", seqrel.release.genome_release, " is not in the genomerelease table."
                    continue
                version = "[note=R" + seqrel.release.genome_release + "]" 

                file_header = None
                download_filename = None
                if feature.type == 'plasmid':
                    file_header = ">S288C_2-micron_plasmid " + version
                    download_filename = "S288C_2-micron_plasmid_R" + seqrel.release.genome_release + ".fsa"
                elif feature.name == '17':
                    file_header = ">S288C_chrmito " + version
                    download_filename = "S288C_chrmito_R" + seqrel.release.genome_release + ".fsa"  
                else:
                    file_header = ">S288C_chr" + number_to_roman[feature.name] + " " + version
                    download_filename = "S288C_chr" + number_to_roman[feature.name] + "_R" + seqrel.release.genome_release + ".fsa"
                display_name = name + " R" + seqrel.release.genome_release
                format_name = display_name.replace(' ', '_')

                ## 'display_name': display_name,
                obj_json = {'display_name': display_name,
                            'format_name': format_name,
                            'source': { 'display_name': 'SGD' } ,
                            'bud_id': seqrel.id,
                            'obj_url': '/archcontig/' + format_name,
                            'residues': sequence.residues, 
                            'taxonomy_id': taxonomy_id,
                            'genomerelease_id': genomerelease_id,
                            'so_id': so_id,
                            'seq_version': str(sequence.seq_version),
                            'file_header': file_header,
                            'download_filename': download_filename,
                            'date_created': str(feature.date_created),
                            'created_by': feature.created_by }

                centromeres = [x.child for x in feature.children if x.child.type == 'centromere']
                feat_locations = sequence.feat_locations
                if len(feat_locations) > 0:
                    obj_json['coord_version'] = str(feat_locations[0].coord_version)

                if len(centromeres) > 0:
                    feat_location = [x for x in centromeres[0].feat_locations if x.is_current == 'N'][0]
                    obj_json['centromere_start'] = feat_location.min_coord
                    obj_json['centromere_end'] = feat_location.max_coord


                # print obj_json, "\n"

                yield obj_json


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
    basic_convert(config.BUD_HOST, config.NEX_HOST, arch_contig_starter, 'arch_contig', lambda x: (x['display_name'], x['so_id'], x['residues'], x['taxonomy_id'], x['seq_version'], x['genomerelease_id']))
