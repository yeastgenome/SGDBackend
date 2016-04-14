from src.sgd.convert import basic_convert
from src.sgd.convert.util import number_to_roman

__author__ = 'sweng66'

def arch_contigchange_starter(bud_session_maker):

    from src.sgd.model.nex.genomerelease import Genomerelease
    from src.sgd.model.nex.arch_contig import ArchContig

    nex_session = get_nex_session()
    bud_session = bud_session_maker()

    release_to_genomerelease_id =  dict([(x.display_name, x.id) for x in nex_session.query(Genomerelease).all()])
    
    key_to_arch_contig_id = {}
    for x in nex_session.query(ArchContig).all():
        pieces = x.format_name.split('_')
        chr = pieces[1]
        version = pieces[2].replace("R", "")
        key = (chr, version)
        key_to_arch_contig_id[key] = x.id
    
    from src.sgd.model.bud.sequence import Sequence, Seq_Change_Archive

    seq_id_to_chr = {}
    for x in bud_session.query(Sequence).all():
        if x.feature.name in number_to_roman:
            seq_id_to_chr[x.id] = number_to_roman[x.feature.name]

    for x in bud_session.query(Seq_Change_Archive).all():

        chr = seq_id_to_chr.get(x.sequence_id)
        if chr is None:
            print "No chr found for seq_no = ", x.sequence_id
            continue
        key = (chr, x.genome_release)
        arch_contig_id = key_to_arch_contig_id.get(key)
        if arch_contig_id is None:
            print "The key: ", key, " is not found in ARCH_CONTIG table."
            continue
        genomerelease_id = release_to_genomerelease_id.get(x.genome_release)
        if genomerelease_id is None:
            print "The genome_release: ", x.genome_release, " is not in GENOMERELEASE table."
            continue

        data = { 'contig_id': arch_contig_id,
                 'source': { "display_name": 'SGD'},
                 'bud_id': x.id,
                 'genomerelease_id': genomerelease_id,
                 'change_type': x.seq_change_type,
                 'change_min_coord': x.change_min_coord,
                 'change_max_coord': x.change_max_coord,
                 'date_changed': str(x.date_created),
                 'changed_by': x.created_by,
                 'date_archived': str(x.date_created) }
    
        if x.old_seq:
            data['old_value'] = x.old_seq
        if x.new_seq:
            data['new_value'] = x.new_seq

        yield data

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
    basic_convert(config.BUD_HOST, config.NEX_HOST, arch_contigchange_starter, 'arch_contigchange', lambda x: (x['contig_id'], x['change_type'], x['change_min_coord'], x['change_max_coord'], x.get('old_value'), x.get('new_value'), x['genomerelease_id']))
