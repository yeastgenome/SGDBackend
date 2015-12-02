from src.sgd.convert import basic_convert
from src.sgd.convert.sequence_files import sequence_files, new_sequence_files
from src.sgd.convert.util import make_fasta_file_starter, number_to_roman, get_strain_taxid_mapping

__author__ = 'sweng66'

DEFAULT_TAXON_ID = "TAX:4932"

def contig_starter(bud_session_maker):

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

    ## load contigs from old strains
    for sequence_filename, coding_sequence_filename, strain in sequence_files:
        strain_id = strain_to_strain_id.get(strain.replace('.', ''))
        if strain_id is None:
            print "The strain ", strain, " is not in STRAIN table."
            continue
        taxid = DEFAULT_TAXON_ID
        if strain in strain_to_taxid_mapping:
            taxid = strain_to_taxid_mapping[strain]
            print "STRAIN_WITH_TAXON_ID: ", strain, taxid
        else:
            print "STRAIN_WITH_NO_TAXON_ID: ", strain

        taxonomy_id = taxid_to_taxonomy_id.get(taxid)
        if taxonomy_id is None:
            print "The strain ", strain, " is not in TAXONOMY table."
            continue
        so_id = type_to_so_id['contig']
        filenames = []
        if isinstance(sequence_filename, list):
            filenames = sequence_filename
        elif sequence_filename is not None:
            filenames.append(sequence_filename)
        for filename in filenames:
            for sequence_id, fasta_header, residues in make_fasta_file_starter(filename)():
                gi_number = sequence_id.split('|')[1]
                genbank_accession = sequence_id.split('|')[3]
                download_filename = strain + "_" + genbank_accession + ".fsa"
                obj_json = {'source': { 'display_name': 'SGD'},
                            'strain_id': strain_id, 
                            'display_name': genbank_accession,
                            'format_name': genbank_accession,
                            'taxonomy_id': taxonomy_id,
                            'residues': residues,
                            'so_id': so_id,
                            'genbank_accession': genbank_accession,
                            'gi_number': gi_number,
                            'file_header': fasta_header,
                            'download_filename': download_filename}
                obj_json['urls'] = load_contig_urls(obj_json)
                print obj_json 
                yield obj_json
                
    ## load contigs for the new 25 stanford strains
    for sequence_filename, coding_sequence_filename, strain in new_sequence_files:
        filenames = []
        strain_id = strain_to_strain_id.get(strain.replace('.', ''))
        if strain_id is None:
            print "The strain ", strain, " is not in STRAIN table."
            continue
        taxid = DEFAULT_TAXON_ID
        if strain in strain_to_taxid_mapping:
            taxid = strain_to_taxid_mapping[strain]
            print "STRAIN_WITH_TAXON_ID: ", strain, taxid
        else:
            print "STRAIN_WITH_NO_TAXON_ID: ", strain

        taxonomy_id = taxid_to_taxonomy_id.get(taxid)
        if taxonomy_id is None:
            print "The strain ", strain, " is not in TAXONOMY table."
            continue
        so_id = type_to_so_id['contig']
        if isinstance(sequence_filename, list):
            filenames = sequence_filename
        elif sequence_filename is not None:
            filenames.append(sequence_filename)
        for filename in filenames:
            for sequence_id, fasta_header, residues in make_fasta_file_starter(filename)():
                name = sequence_id.split(' ')[0]
                gi_number = name.split('|')[1]
                genbank_accession = name.split('|')[3]
                download_filename = strain + "_" + genbank_accession + ".fsa"
                if genbank_accession != '.':
                    obj_json = {'source': { 'display_name' : 'SGD' }, 
                                'strain_id': strain_id,
                                'display_name': genbank_accession,
                                'format_name': genbank_accession,
                                'taxonomy_id': taxonomy_id,
                                'residues': residues,
                                'so_id': so_id,
                                'genbank_accession': genbank_accession,
                                'gi_number': gi_number,
                                'file_header': fasta_header,
                                'download_filename': download_filename }
                    obj_json['urls'] = load_contig_urls(obj_json)
                    yield obj_json
                    # print obj_json


        #load chromosomes for S288C  

        S288C_chr_to_genbank_refseq_mapping = get_S288C_chr_to_genbank_refseq_mapping()

        version = "[note=R64-1-1]"
        chr_header = "[organism=Saccharomyces cerevisiae S288c] [strain=S288c] [moltype=genomic]"
        mito_header = ">ref|NC_001224| [org=Saccharomyces cerevisiae] [strain=S288C] [moltype=genomic] [location=mitochondrion] [top=circular] [note=R10-1-1]"
        plasmid_header = ">NC_001398.1 Saccharomyces cerevisiae A364A 2 micron circle plasmid, complete sequence"

        from sqlalchemy.sql.expression import or_
        from src.sgd.model.bud.feature import Feature
        from src.sgd.model.bud.sequence import Sequence

        taxid = strain_to_taxid_mapping['S288C']
        taxonomy_id = taxid_to_taxonomy_id[taxid]

        for feature in bud_session.query(Feature).filter(or_(Feature.type == 'chromosome', Feature.type == 'plasmid')).all():
            so_id = type_to_so_id[feature.type]
            for sequence in feature.sequences:
                if sequence.is_current == 'Y':
                    display_name = None
                    if feature.type == 'plasmid':
                        display_name = '2-micron plasmid'
                    else:
                        display_name = 'Chromosome ' + (feature.name if feature.name not in number_to_roman else number_to_roman[feature.name])
                    genbank_accession = ''
                    refseq_id = ''
                    if display_name in S288C_chr_to_genbank_refseq_mapping:
                        genbank_accession, refseq_id = S288C_chr_to_genbank_refseq_mapping[display_name]

                    file_header = None
                    download_filename = None
                    if feature.type == 'plasmid':
                        file_header = plasmid_header
                        download_filename = "S288C_2-micron_plasmid.fsa"
                    elif feature.name == '17':
                        file_header = mito_header
                        download_filename = "S288C_chrmito_NC_001224.fsa" 
                    else:
                        file_header = ">tpg|" + genbank_accession + "| " + chr_header + " [chromosome=" + number_to_roman[feature.name] + "] " + version
                        download_filename = "S288C_chr" + number_to_roman[feature.name] + "_" + genbank_accession + ".fsa"
                    releases = [] if len(sequence.feat_locations) == 0 else [x.release for x in sequence.feat_locations[0].featlocation_rels]

                    genomerelease_id = None
                    if len(releases) > 0:
                         genomerelease_id = genomerelease_to_genomerelease_id.get(releases[0].genome_release)
     
                    obj_json = {'display_name': display_name,
                                'format_name': display_name.replace(' ', '_'),
                                'source': { 'display_name': 'SGD' } ,
                                'strain_id': strain_to_strain_id['S288C'],
                                'taxonomy_id': taxonomy_id,
                                'genomerelease_id': genomerelease_id,
                                'residues': sequence.residues,
                                'so_id': so_id,
                                'genbank_accession': genbank_accession,
                                'refseq_id': refseq_id,
                                'seq_version': str(sequence.seq_version),
                                'file_header': file_header,
                                'download_filename': download_filename,
                                'date_created': str(feature.date_created),
                                'created_by': feature.created_by }

                    if genomerelease_id is not None:
                        obj_json['genomerelease_id'] = genomerelease_id

                    centromeres = [x.child for x in feature.children if x.child.type == 'centromere']
                    feat_locations = sequence.feat_locations
                    if len(feat_locations) > 0:
                        obj_json['coord_version'] = str(feat_locations[0].coord_version)

                    if len(centromeres) > 0:
                        feat_location = [x for x in centromeres[0].feat_locations if x.is_current == 'Y'][0]
                        obj_json['centromere_start'] = feat_location.min_coord
                        obj_json['centromere_end'] = feat_location.max_coord

                    obj_json['urls'] = load_contig_urls(obj_json)

                    yield obj_json

                    # print obj_json

    nex_session.close()
    bud_session.close()
    
    
def load_contig_urls(obj_json):
    urls = []
    if 'genbank_accession' in obj_json:
        urls.append({'display_name': obj_json['genbank_accession'],
                     'link': 'http://www.ncbi.nlm.nih.gov/nuccore/' + obj_json['genbank_accession'],
                     'source': {'display_name': 'GenBank-EMBL-DDBJ'},
                     'url_type': 'GenBank'})
    return urls

def get_S288C_chr_to_genbank_refseq_mapping():        

    return { 'Chromosome I': ('BK006935.2', 'NC_001133.9'),
             'Chromosome II': ('BK006936.2', 'NC_001134.8'),
             'Chromosome III': ('BK006937.2', 'NC_001135.5'),
             'Chromosome IV': ('BK006938.2', 'NC_001136.10'),
             'Chromosome V': ('BK006939.2', 'NC_001137.3'),
             'Chromosome VI': ('BK006940.2', 'NC_001138.5'),
             'Chromosome VII': ('BK006941.2', 'NC_001139.9'),
             'Chromosome VIII': ('BK006934.2', 'NC_001140.6'),
             'Chromosome IX': ('BK006942.2', 'NC_001141.2'),
             'Chromosome X': ('BK006943.2', 'NC_001142.9'),
             'Chromosome XI': ('BK006944.2', 'NC_001143.9'),
             'Chromosome XII': ('BK006945.2', 'NC_001144.5'),
             'Chromosome XIII': ('BK006946.2', 'NC_001145.3'),
             'Chromosome XIV': ('BK006947.3', 'NC_001146.8'),
             'Chromosome XV': ('BK006948.2', 'NC_001147.6'),
             'Chromosome XVI': ('BK006949.2', 'NC_001148.4'),
             'Chromosome Mito': ('AJ011856.1', 'NC_001224.1'),
             '2-micron plasmid': ('NC_001398.1', '') }

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, contig_starter, 'contig', lambda x: (x['display_name'], x['genbank_accession'], x['so_id'], x['residues'], x['taxonomy_id']))
