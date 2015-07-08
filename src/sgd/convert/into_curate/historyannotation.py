from src.sgd.convert.into_curate import basic_convert, remove_nones

__author__ = 'kkarra'

# --------------------- Convert Reservedname ---------------------
def historyannotation_starter(bud_session_maker):
    from src.sgd.model.bud.feature import GeneReservation
    from src.sgd.model.bud.reference import Reflink

    bud_session = bud_session_maker()

    for gene_reservation in bud_session.query(GeneReservation).filter_by(date_standardized=None).all():
        reflink = bud_session.query(Reflink).filter_by(tab_name='GENE_RESERVATION').filter_by(primary_key=gene_reservation.id).first()
        print gene_reservation.created_by
        print gene_reservation.feature.created_by
        yield dict(name=gene_reservation.reserved_gene_name,
                   locus={'gene_name': gene_reservation.feature.gene_name,
                            'systematic_name': gene_reservation.feature.name,
                            'source': {
                                'name': gene_reservation.feature.source
                            },
                            'bud_id': gene_reservation.feature.id,
                            'sgdid': gene_reservation.feature.dbxref_id,
                            'dbentity_status': gene_reservation.feature.status,
                            'locus_type': gene_reservation.feature.type,
                            'date_created': str(gene_reservation.feature.date_created),
                            'created_by': gene_reservation.feature.created_by},
                   reference={'sgdid': reflink.reference.dbxref_id},
                   date_annotation_made=str(gene_reservation.reservation_date),
                   source={'name': 'SGD'},
                   date_created=str(gene_reservation.date_created),
                   created_by=gene_reservation.created_by)
    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, historyannotation_starter, 'historyannotation', lambda x: x['name'])

if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')
