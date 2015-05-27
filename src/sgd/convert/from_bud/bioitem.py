from sqlalchemy.sql.expression import or_
from sqlalchemy.orm import joinedload

from src.sgd.convert import create_format_name, number_to_roman
from src.sgd.convert.transformers import make_db_starter, \
    make_file_starter, make_fasta_file_starter
import os
from decimal import Decimal

__author__ = 'kpaskov'


# --------------------- Convert Reservedname ---------------------
def make_reservedname_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.feature import GeneReservation
    from src.sgd.model.bud.reference import Reflink

    def reservedname_starter():
        nex_session = nex_session_maker()
        bud_session = bud_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])

        locus_id_to_reference = dict([(x.primary_key, x.reference_id) for x in bud_session.query(Reflink).filter_by(tab_name='GENE_RESERVATION')])

        for gene_reservation in bud_session.query(GeneReservation).filter_by(date_standardized=None).all():
            yield {
                'display_name': gene_reservation.reserved_gene_name,
                'locus': None if gene_reservation.id not in id_to_bioentity else id_to_bioentity[gene_reservation.id],
                'reference': None if gene_reservation.id not in locus_id_to_reference else id_to_reference[locus_id_to_reference[gene_reservation.id]],
                'reservation_date': gene_reservation.reservation_date,
                'expiration_date': gene_reservation.expiration_date,
                'source': key_to_source['SGD'],
                'date_created': gene_reservation.date_created,
                'created_by': gene_reservation.created_by
            }

        nex_session.close()
        bud_session.close()
    return reservedname_starter

# --------------------- Convert Pathway ---------------------
def make_pathway_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.general import Dbxref

    def pathway_starter():
        nex_session = nex_session_maker()
        bud_session = bud_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for dbxref in bud_session.query(Dbxref).filter_by(dbxref_type='Pathway ID').all():
            yield {
                'format_name': dbxref.dbxref_id,
                'display_name': dbxref.dbxref_name,
                'source': key_to_source[dbxref.source],
                'link': 'http://pathway.yeastgenome.org/YEAST/new-image?type=PATHWAY&object=' + dbxref.dbxref_id + '&detail-level=2',
                'date_created': dbxref.date_created,
                'created_by': dbxref.created_by
            }

        nex_session.close()
        bud_session.close()
    return pathway_starter

# --------------------- Convert Dataset ---------------------
def make_dataset_starter(nex_session_maker, expression_dir):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.reference import Reference
    def dataset_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        pubmed_id_to_reference = dict([(x.pubmed_id, x) for x in nex_session.query(Reference).all()])

        filename_to_channel_count = dict([(x[0], x[1].strip()) for x in make_file_starter(expression_dir + '/channel_count.txt')()])

        for path in os.listdir(expression_dir):
            if os.path.isdir(expression_dir + '/' + path):
                full_description = None
                geo_id = None
                pcl_filename_to_info = {}
                pubmed_id = None

                state = 'BEGIN'
                try:
                    for row in make_file_starter(expression_dir + '/' + path + '/README')():
                        if row[0].startswith('Full Description'):
                            state = 'FULL_DESCRIPTION:'
                            full_description = row[0][18:].strip()
                        elif row[0].startswith('PMID:'):
                            pubmed_id = int(row[0][6:].strip())
                        elif row[0].startswith('GEO ID:'):
                            geo_id = row[0][8:].strip().split('.')[0].split('GPL')[0]
                        elif row[0].startswith('PCL filename'):
                            state = 'OTHER'
                        elif state == 'FULL_DESCRIPTION':
                            full_description = full_description + row[0].strip()
                        elif state == 'OTHER':
                            pcl_filename = row[0].strip()
                            short_description = row[1].strip()
                            tag = row[3].strip()
                            pcl_filename_to_info[pcl_filename] = (short_description, tag)

                    if geo_id == 'N/A':
                        geo_id = None

                    for file in os.listdir(expression_dir + '/' + path):
                        if file != 'README':
                            f = open(expression_dir + '/' + path + '/' + file, 'r')
                            pieces = f.next().split('\t')
                            f.close()

                            if pubmed_id not in pubmed_id_to_reference:
                                print 'Warning: pubmed_id not found ' + str(pubmed_id)

                            if file in pcl_filename_to_info:
                                yield {
                                    'description': full_description,
                                    'geo_id': geo_id,
                                    'pcl_filename': file,
                                    'short_description': pcl_filename_to_info[file][0],
                                    'tags': pcl_filename_to_info[file][1],
                                    'reference': None if pubmed_id is None or pubmed_id not in pubmed_id_to_reference else pubmed_id_to_reference[pubmed_id],
                                    'source': key_to_source['SGD'],
                                    'channel_count': 1 if file not in filename_to_channel_count else int(filename_to_channel_count[file]),
                                    'condition_count': len(pieces)-3
                                }
                            else:
                                print 'Filename not in readme: ' + file
                except:
                    print 'File ' + expression_dir + '/' + path + '/README' + ' not found.'

        nex_session.close()
    return dataset_starter

# --------------------- Convert Dataset Column---------------------
def make_datasetcolumn_starter(nex_session_maker, expression_dir):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioitem import Dataset
    def datasetcolumn_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_dataset = dict([(x.unique_key(), x) for x in nex_session.query(Dataset).all()])


        key_to_GSM = dict([((x[0], x[1].strip().decode('ascii','ignore')), x[2]) for x in make_file_starter('src/sgd/convert/data/microarray_05_14/GSM_to_GSE.txt')()])

        for path in os.listdir(expression_dir):
            if os.path.isdir(expression_dir + '/' + path):
                for file in os.listdir(expression_dir + '/' + path):
                    dataset_key = (file[:-4], 'DATASET')
                    if dataset_key in key_to_dataset:
                        f = open(expression_dir + '/' + path + '/' + file, 'r')
                        pieces = f.next().split('\t')
                        f.close()

                        geo_id = key_to_dataset[dataset_key].geo_id



                        i = 0
                        for piece in pieces[3:]:
                            column_name = piece.strip().decode('ascii','ignore')

                            if (geo_id, column_name) not in key_to_GSM and geo_id is not None:
                                print (geo_id, column_name)
                            #print (geo_id, column_name)
                            col_geo_id = None if (geo_id, column_name) not in key_to_GSM else key_to_GSM[(geo_id, column_name)]
                            link = None if col_geo_id is None else 'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + col_geo_id
                            yield {
                                        'description': column_name,
                                        'dataset': key_to_dataset[dataset_key],
                                        'source': key_to_source['SGD'],
                                        'file_order': i,
                                        'geo_id': col_geo_id,
                                        'link': link
                            }
                            i += 1

        nex_session.close()
    return datasetcolumn_starter


# --------------------- Convert Bioitem URL ---------------------
def make_bioitem_url_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioitem import Domain, Chemical, Dataset, Contig

    def bioitem_url_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])



        for dataset in nex_session.query(Dataset).all():
            if dataset.geo_id is not None:
                yield {'display_name': dataset.geo_id,
                       'link': 'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + dataset.geo_id,
                       'source': key_to_source['NCBI'],
                       'category': 'External',
                       'bioitem_id': dataset.id}

        pcl_filename_to_dataset = dict([(x.pcl_filename, x) for x in nex_session.query(Dataset).all()])

        for path in os.listdir('src/sgd/convert/data/microarray_05_14'):
            if os.path.isdir('src/sgd/convert/data/microarray_05_14/' + path):
                for file in os.listdir('src/sgd/convert/data/microarray_05_14/' + path):
                    if file != 'README':
                        if file in pcl_filename_to_dataset:
                            dataset = pcl_filename_to_dataset[file]
                            yield {'display_name': 'Download Data',
                                   'link': 'http://downloads.yeastgenome.org/expression/microarray/' + path + '/',
                                   'source': key_to_source['SGD'],
                                   'category': 'Download',
                                   'bioitem_id': dataset.id}

        nex_session.close()
    return bioitem_url_starter

# --------------------- Convert Bioitem Tag ---------------------
def make_bioitem_tag_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Tag
    from src.sgd.model.nex.bioitem import Dataset
    def bioitem_tag_starter():
        nex_session = nex_session_maker()

        key_to_dataset = dict([(x.unique_key(), x) for x in nex_session.query(Dataset).all()])
        key_to_tag = dict([(x.unique_key(), x) for x in nex_session.query(Tag).all()])

        for row in make_file_starter('src/sgd/convert/data/microarray_05_14/SPELL-tags.txt')():
            dataset_key = (row[1].strip()[:-4], 'DATASET')
            tags = row[2].strip()
            for t in [x.strip() for x in tags.split('|')]:
                if t != '':
                    yield {
                        'bioitem': key_to_dataset[dataset_key],
                        'tag': key_to_tag[create_format_name(t)]
                    }

        nex_session.close()
    return bioitem_tag_starter


