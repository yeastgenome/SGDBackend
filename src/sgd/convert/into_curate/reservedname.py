from src.sgd.convert.into_curate import basic_convert

__author__ = 'kkarra'

# --------------------- Convert Reservedname ---------------------
def reservedname_starter(nex_session_maker, bud_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.feature import GeneReservation
    from src.sgd.model.bud.reference import Reflink

    nex_session = nex_session_maker()
    bud_session = bud_session_maker()
    key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
    id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
    id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
    locus_id_to_reference = dict([(x.primary_key, x.reference_id) for x in bud_session.query(Reflink).filter_by(tab_name='GENE_RESERVATION')])

    for gene_reservation in bud_session.query(GeneReservation).filter_by(date_standardized=None).all():
            yield dict(display_name=gene_reservation.reserved_gene_name,
                       locus=None if gene_reservation.id not in id_to_bioentity else id_to_bioentity[gene_reservation.id],
                       reference=None if gene_reservation.id not in locus_id_to_reference else id_to_reference[locus_id_to_reference[gene_reservation.id]],
                       reservation_date=gene_reservation.reservation_date,
                       expiration_date=gene_reservation.expiration_date, source=key_to_source['SGD'],
                       date_created=gene_reservation.date_created, created_by=gene_reservation.created_by)
    nex_session.close()
    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, reservedname_starter, 'reservedname', lambda x: x ['display_name'])

if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')








