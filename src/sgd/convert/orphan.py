from src.sgd.convert.into_curate import basic_convert, remove_nones

__author__ = 'kpaskov'


def orphan_starter(bud_session_maker):
    from src.sgd.model.bud.phenotype import ExperimentProperty
    from src.sgd.model.bud.go import GorefDbxref

    bud_session = bud_session_maker()

    for bud_obj in bud_session.query(ExperimentProperty).filter(ExperimentProperty.type == 'Reporter').all():
        if bud_obj.type == 'Reporter':
            yield {'display_name': bud_obj.value,
                   'source': {'display_name': 'SGD'},
                   'bud_id': bud_obj.id,
                   'orphan_type': 'experiment_property',
                   'date_created': str(bud_obj.date_created),
                   'created_by': bud_obj.created_by}

    for bud_obj in bud_session.query(GorefDbxref).all():
        dbxref = bud_obj.dbxref
        dbxref_type = dbxref.dbxref_type
        if dbxref_type != 'GOID' and dbxref_type != 'EC number' and dbxref_type != 'DBID Primary' and dbxref_type != 'PANTHER' and dbxref_type != 'Prosite':
            link = None
            bioitem_type = None
            if dbxref_type == 'UniProt/Swiss-Prot ID':
                urls = dbxref.urls
                if len(urls) == 1:
                    link = urls[0].url.replace('_SUBSTITUTE_THIS_', dbxref.dbxref_id)
                bioitem_type = 'UniProtKB'
            elif dbxref_type == 'UniProtKB Subcellular Location':
                link = "http://www.uniprot.org/locations/" + dbxref.dbxref_id
                bioitem_type = 'UniProtKB-SubCell'
            elif dbxref_type == 'InterPro':
                link = "http://www.ebi.ac.uk/interpro/entry/" + dbxref.dbxref_id
                bioitem_type = 'InterPro'
            elif dbxref_type == 'DNA accession ID':
                link = None
                bioitem_type = 'EMBL'
            elif dbxref_type == 'Gene ID':
                link = None
                bioitem_type = dbxref.source
            elif dbxref_type == 'HAMAP ID' or dbxref_type == 'HAMAP':
                link = None
                bioitem_type = 'HAMAP'
            elif dbxref_type == 'PDB identifier':
                link = None
                bioitem_type = 'PDB'
            elif dbxref_type == 'Protein version ID':
                link = None
                bioitem_type = 'protein_id'
            elif dbxref_type == 'UniPathway ID':
                link = 'http://www.grenoble.prabi.fr/obiwarehouse/unipathway/upa?upid=' + dbxref.dbxref_id
                bioitem_type = 'UniPathway'
            elif dbxref_type == 'UniProtKB Keyword':
                link = 'http://www.uniprot.org/keywords/' + dbxref.dbxref_id
                bioitem_type = 'UniProtKB-KW'

            obj_json = remove_nones({'display_name': dbxref.dbxref_id,
                        'source': {'display_name': dbxref.source},
                        'description': dbxref.dbxref_name,
                        'orphan_type': bioitem_type,
                        'date_created': str(dbxref.date_created),
                        'created_by': dbxref.created_by,
                        'bud_id': dbxref.id,
                        })
            if link is not None:
                obj_json['urls'] = [{'display_name': bioitem_type, 'link': link, 'source': {'display_name': dbxref.source}, 'url_type': 'External'}]
            yield obj_json

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, orphan_starter, 'orphan', lambda x: x['display_name'])


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')
