from src.sgd.convert.into_curate import basic_convert

__author__ = 'kpaskov'

chemical_phenotypes = {'chemical compound accumulation': 'APO:0000095', 'chemical compound excretion': 'APO:0000222', 'resistance to chemicals': 'APO:0000087'}

def phenotype_starter(bud_session_maker):
    from src.sgd.model.bud.phenotype import Phenotype, PhenotypeFeature

    bud_session = bud_session_maker()

    for bud_obj in bud_session.query(Phenotype).all():
        obj_json = {
            'source': {'display_name': 'SGD'},
            'observable': {'display_name': bud_obj.observable},
            'date_created': str(bud_obj.date_created),
            'created_by': bud_obj.created_by
            }
        if bud_obj.qualifier is not None:
            obj_json['qualifier'] = {'display_name': bud_obj.qualifier}

        yield obj_json

    #Chemical Phenotypes
    for bud_obj in bud_session.query(PhenotypeFeature).join(PhenotypeFeature.phenotype).filter(Phenotype.observable.in_(chemical_phenotypes.keys())).all():
        if bud_obj.experiment is not None:
            chemicals = bud_obj.experiment.chemicals
            if len(chemicals) > 0:
                chemical = ' and '.join([x[0] for x in chemicals])
                old_observable = bud_obj.phenotype.observable
                if old_observable == 'resistance to chemicals':
                    new_observable = bud_obj.phenotype.observable.replace('chemicals', chemical)
                    yield {'source': {'display_name': 'SGD'},
                           'observable': {'display_name': new_observable},
                           'qualifier': {'display_name': bud_obj.phenotype.qualifier}
                    }
                elif old_observable == 'chemical compound accumulation':
                    new_observable = bud_obj.phenotype.observable.replace('chemical compound', chemical)
                    yield {'source': {'display_name': 'SGD'},
                           'observable': {'display_name': new_observable},
                           'qualifier': {'display_name': bud_obj.phenotype.qualifier}
                    }
                elif old_observable == 'chemical compound excretion':
                    new_observable = bud_obj.phenotype.observable.replace('chemical compound', chemical)
                    yield {'source': {'display_name': 'SGD'},
                           'observable': {'display_name': new_observable},
                           'qualifier': {'display_name': bud_obj.phenotype.qualifier}
                    }

    bud_session.close()


def convert(bud_db, nex_db):
    basic_convert(bud_db, nex_db, phenotype_starter, 'phenotype', lambda x: (x['observable']['display_name'], None if 'qualifier' not in x else x['qualifier']['display_name']))


if __name__ == '__main__':
    convert('pastry.stanford.edu:1521', 'curator-dev-db')
