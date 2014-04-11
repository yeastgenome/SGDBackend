from sqlalchemy.orm import joinedload

from src.sgd.convert.transformers import make_db_starter


__author__ = 'kpaskov'

#1.23.14 Maitenance (sgd-dev): 1:04

# --------------------- Convert Observable ---------------------
def make_observable_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.cv import CVTerm, CVTermRel
    from src.sgd.model.bud.phenotype import Phenotype, PhenotypeFeature
    def observable_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        old_cvterms = bud_session.query(CVTerm).filter(CVTerm.cv_no == 6).all()
        observable_to_ancestor = dict()
        child_id_to_parent_id = dict([(x.child_id, x.parent_id) for x in bud_session.query(CVTermRel).all()])
        id_to_observable = dict([(x.id, x.name) for x in old_cvterms])

        for old_obj in old_cvterms:
            observable_id = old_obj.id
            if observable_id in child_id_to_parent_id:
                ancestry = [observable_id, child_id_to_parent_id[observable_id]]
            else:
                ancestry = [observable_id, None]

            while ancestry[len(ancestry)-1] is not None:
                latest_parent_id = ancestry[len(ancestry)-1]
                if latest_parent_id in child_id_to_parent_id:
                    ancestry.append(child_id_to_parent_id[latest_parent_id])
                else:
                    ancestry.append(None)
            if len(ancestry) > 2:
                ancestor_id = ancestry[len(ancestry)-3]
                observable_to_ancestor[old_obj.name] = id_to_observable[ancestor_id]
            else:
                observable_to_ancestor[old_obj.name] = id_to_observable[ancestry[0]]

        for bud_obj in make_db_starter(bud_session.query(CVTerm).filter(CVTerm.cv_no == 6), 1000)():
            observable = bud_obj.name
            source = key_to_source['SGD']
            ancestor_type = None if observable not in observable_to_ancestor else observable_to_ancestor[observable]
            if ancestor_type is None:
                print 'No ancestor type: ' + str(observable)
                yield None
            description = bud_obj.definition
            if observable == 'observable':
                description = 'Features of Saccharomyces cerevisiae cells, cultures, or colonies that can be detected, observed, measured, or monitored.'
            yield {'source': source,
                    'description': description,
                    'display_name': observable,
                    'ancestor_type': ancestor_type,
                    'date_created': bud_obj.date_created,
                    'created_by': bud_obj.created_by}

        for bud_obj in make_db_starter(bud_session.query(PhenotypeFeature).join(PhenotypeFeature.phenotype).filter(Phenotype.observable.in_(chemical_phenotypes)), 1000)():
            if bud_obj.experiment is None:
                yield None

            chemicals = bud_obj.experiment.chemicals
            if len(chemicals) == 0:
                yield None

            chemical = ' and '.join([x[0] for x in chemicals])

            source = key_to_source['SGD']
            old_observable = bud_obj.phenotype.observable
            description = None
            if old_observable == 'resistance to chemicals':
                new_observable = bud_obj.phenotype.observable.replace('chemicals', chemical)
                description = 'The level of resistance to exposure to ' + chemical + '.'
            elif old_observable == 'chemical compound accumulation':
                new_observable = bud_obj.phenotype.observable.replace('chemical compound', chemical)
                description = 'The production and/or storage of ' + chemical + '.'
            elif old_observable == 'chemical compound excretion':
                new_observable = bud_obj.phenotype.observable.replace('chemical compound', chemical)
                description = 'The excretion from the cell of ' + chemical + '.'
            else:
                yield None

            ancestor_type = None if old_observable not in observable_to_ancestor else observable_to_ancestor[old_observable]
            yield {'source': source,
                       'description': description,
                       'display_name': new_observable,
                       'ancestor_type': ancestor_type,
                       'date_created': bud_obj.date_created,
                       'created_by': bud_obj.created_by}
        bud_session.close()
        nex_session.close()
    return observable_starter

chemical_phenotypes = {'chemical compound accumulation', 'chemical compound excretion', 'resistance to chemicals'}

# --------------------- Convert Phenotype ---------------------
def make_phenotype_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex import create_format_name
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioconcept import Observable
    from src.sgd.model.bud.phenotype import Phenotype, PhenotypeFeature
    def phenotype_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_observable = dict([(x.unique_key(), x) for x in nex_session.query(Observable).all()])

        for bud_obj in make_db_starter(bud_session.query(Phenotype), 1000)():
            observable_key = (create_format_name(bud_obj.observable), 'OBSERVABLE')
            if observable_key in key_to_observable:
                yield {'source': key_to_source['SGD'],
                       'observable': key_to_observable[observable_key],
                       'qualifier': bud_obj.qualifier,
                       'date_created': bud_obj.date_created,
                       'created_by': bud_obj.created_by}

        for bud_obj in make_db_starter(bud_session.query(PhenotypeFeature).join(PhenotypeFeature.phenotype).filter(Phenotype.observable.in_(chemical_phenotypes)), 1000)():
            if bud_obj.experiment is None:
                yield None

            chemicals = bud_obj.experiment.chemicals
            if len(chemicals) == 0:
                yield None

            chemical = ' and '.join([x[0] for x in chemicals])

            old_observable = bud_obj.phenotype.observable
            description = None
            if old_observable == 'resistance to chemicals':
                new_observable = bud_obj.phenotype.observable.replace('chemicals', chemical)
                description = 'The level of resistance to exposure to ' + chemical + '.'
            elif old_observable == 'chemical compound accumulation':
                new_observable = bud_obj.phenotype.observable.replace('chemical compound', chemical)
                description = 'The production and/or storage of ' + chemical + '.'
            elif old_observable == 'chemical compound excretion':
                new_observable = bud_obj.phenotype.observable.replace('chemical compound', chemical)
                description = 'The excretion from the cell of ' + chemical + '.'
            else:
                yield None

            observable_key = (new_observable, 'OBSERVABLE')
            if observable_key in key_to_observable:
                yield {'source': key_to_source['SGD'],
                       'observable': observable_key[key_to_observable],
                       'qualifier': bud_obj.phenotype.qualifier,
                       'description': description,
                       'date_created': bud_obj.date_created,
                       'created_by': bud_obj.created_by}
        bud_session.close()
        nex_session.close()
    return phenotype_starter

# --------------------- Convert GO ---------------------
def make_go_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.go import Go
    def go_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for bud_obj in make_db_starter(bud_session.query(Go), 1000)():
            yield {'display_name': bud_obj.go_term,
                   'source': key_to_source['GO'],
                   'description': bud_obj.go_definition,
                   'go_id': 'GO:' + str(bud_obj.go_go_id).zfill(7),
                   'go_aspect': abbrev_to_go_aspect[bud_obj.go_aspect],
                   'date_created': bud_obj.date_created,
                   'created_by': bud_obj.created_by}

        bud_session.close()
        nex_session.close()
    return go_starter

abbrev_to_go_aspect = {'C':'cellular component', 'F':'molecular function', 'P':'biological process'}

# --------------------- Convert EC ---------------------
def make_ecnumber_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.general import Dbxref
    def ecnumber_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for bud_obj in make_db_starter(bud_session.query(Dbxref).filter(Dbxref.dbxref_type == 'EC number'), 1000)():
            yield {'display_name': bud_obj.dbxref_id,
                   'source': key_to_source[bud_obj.source],
                   'description': bud_obj.dbxref_name,
                   'date_created': bud_obj.date_created,
                   'created_by': bud_obj.created_by}

        bud_session.close()
        nex_session.close()
    return ecnumber_starter

# --------------------- Convert Bioconcept Relation ---------------------
def make_bioconcept_relation_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioconcept import Bioconcept, Bioconceptrelation
    from src.sgd.model.nex import create_format_name
    from src.sgd.model.bud.go import GoPath, GoSet
    from src.sgd.model.bud.cv import CVTermRel
    from src.sgd.model.bud.phenotype import Phenotype as OldPhenotype

    def bioconcept_relation_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_bioconcept = dict([(x.unique_key(), x) for x in nex_session.query(Bioconcept).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        # GO relations
        for gopath in make_db_starter(bud_session.query(GoPath).filter(GoPath.generation == 1).options(joinedload('child'), joinedload('ancestor')), 1000)():
            parent_key = (get_go_format_name(gopath.ancestor.go_go_id), 'GO')
            child_key = (get_go_format_name(gopath.child.go_go_id), 'GO')

            if parent_key in key_to_bioconcept and child_key in key_to_bioconcept:
                yield {'source': key_to_source['SGD'],
                        'relation_type': gopath.relationship_type,
                        'parent_id': key_to_bioconcept[parent_key].id,
                        'child_id': key_to_bioconcept[child_key].id}
            else:
                print 'Could not find go. Parent: ' + str(parent_key) + ' Child: ' + str(child_key)
                yield None

        old_gosets = bud_session.query(GoSet).filter(GoSet.name == 'Yeast GO-Slim').options(joinedload('go')).all()
        slim_ids = set()
        for old_goset in old_gosets:
            go_key = (get_go_format_name(old_goset.go.go_go_id), 'GO')
            if go_key[0] != 'GO:0008150' and go_key[0] != 'GO:0003674' and go_key[0] != 'GO:0005575' and go_key in key_to_bioconcept:
                slim_ids.add(key_to_bioconcept[go_key].id)
            else:
                print 'GO term not found: ' + str(go_key)

        go_child_id_to_parent_ids = {}
        for go_relation in nex_session.query(Bioconceptrelation).filter(Bioconceptrelation.relation_type == 'is a'):
            if go_relation.child_id in go_child_id_to_parent_ids:
                go_child_id_to_parent_ids[go_relation.child_id].append(go_relation.parent_id)
            else:
                go_child_id_to_parent_ids[go_relation.child_id] = [go_relation.parent_id]

        for child_id in go_child_id_to_parent_ids:
            parent_ids = go_child_id_to_parent_ids[child_id]
            while len(parent_ids) > 0:
                new_parent_ids = set()
                for parent_id in parent_ids:
                    if parent_id in slim_ids:
                        yield {'source': key_to_source['SGD'],
                               'parent_id': parent_id,
                               'child_id': child_id,
                               'relation_type': 'GO_SLIM'}
                        if parent_id in go_child_id_to_parent_ids:
                            new_parent_ids.update(go_child_id_to_parent_ids[parent_id])
                parent_ids = new_parent_ids

        #Phenotype relations
        for cvtermrel in make_db_starter(bud_session.query(CVTermRel).options(joinedload('child'), joinedload('parent')), 1000)():
            parent_key = (create_format_name(cvtermrel.parent.name.lower()), 'OBSERVABLE')
            child_key = (create_format_name(cvtermrel.child.name.lower()), 'OBSERVABLE')

            if parent_key == ('observable', 'OBSERVABLE'):
                parent_key = ('ypo', 'OBSERVABLE')

            if parent_key in key_to_bioconcept and child_key in key_to_bioconcept:
                yield {'source': key_to_source['SGD'],
                       'relation_type': cvtermrel.relationship_type,
                       'parent_id': key_to_bioconcept[parent_key].id,
                       'child_id': key_to_bioconcept[child_key].id,
                       'date_created': cvtermrel.date_created,
                       'created_by': cvtermrel.created_by}

        for old_phenotype in make_db_starter(bud_session.query(OldPhenotype).filter(OldPhenotype.observable.in_(chemical_phenotypes)).options(
                                        joinedload('phenotype_features'), joinedload('phenotype_features.experiment')), 1000)():
            for phenotype_feature in old_phenotype.phenotype_features:
                chemical = ' and '.join([x[0] for x in phenotype_feature.experiment.chemicals])
                old_observable = old_phenotype.observable
                if old_observable == 'resistance to chemicals':
                    new_observable = old_phenotype.observable.replace('chemicals', chemical)
                else:
                    new_observable = old_phenotype.observable.replace('chemical compound', chemical)

                parent_key = (create_format_name(old_observable.lower()), 'OBSERVABLE')
                child_key = (create_format_name(new_observable.lower()), 'OBSERVABLE')

                if parent_key in key_to_bioconcept and child_key in key_to_bioconcept:
                    yield {'source': key_to_source['SGD'],
                           'relation_type': 'is a',
                           'parent_id': key_to_bioconcept[parent_key].id,
                           'child_id': key_to_bioconcept[child_key].id}
                else:
                    print 'Could not find phenotype. Parent: ' + str(parent_key) + ' Child: ' + str(child_key)
                    yield None

        bud_session.close()
        nex_session.close()
    return bioconcept_relation_starter

def get_go_format_name(go_id):
    if int(go_id) == 8150:
        return 'biological_process'
    elif int(go_id) == 3674:
        return 'molecular_function'
    elif int(go_id) == 5575:
        return 'cellular_component'
    else:
        return 'GO:' + str(int(go_id)).zfill(7)

# --------------------- Convert Bioconcept Alias ---------------------
def make_bioconcept_alias_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex import create_format_name
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioconcept import Bioconcept
    from src.sgd.model.bud.go import Go
    from src.sgd.model.bud.cv import CVTermSynonym, CVTermDbxref, CVTerm
    def bioconcept_alias_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_bioconcept = dict([(x.unique_key(), x) for x in nex_session.query(Bioconcept).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        #Go aliases
        for old_goterm in make_db_starter(bud_session.query(Go).options(joinedload('go_gosynonyms')), 1000)():
            go_key = (get_go_format_name(old_goterm.go_go_id), 'GO')

            if go_key in key_to_bioconcept:
                for go_gosynonym in old_goterm.go_gosynonyms:
                    synonym = go_gosynonym.gosynonym
                    yield {'display_name': synonym.name,
                           'source': key_to_source['SGD'],
                           'bioconcept_id': key_to_bioconcept[go_key].id,
                           'date_created': synonym.date_created,
                           'created_by': synonym.created_by}
            else:
                print 'Go term not found: ' + str(go_key)
                yield None

        #Phenotype aliases
        for cvtermsynonym in make_db_starter(bud_session.query(CVTermSynonym).join(CVTerm).filter(CVTerm.cv_no == 6), 1000)():
            phenotype_key = (create_format_name(cvtermsynonym.cvterm.name.lower()), 'OBSERVABLE')

            if phenotype_key in key_to_bioconcept:
                yield {'display_name': cvtermsynonym.synonym,
                       'source': key_to_source['SGD'],
                       'bioconcept_id': key_to_bioconcept[phenotype_key].id,
                       'date_created': cvtermsynonym.date_created,
                       'created_by': cvtermsynonym.created_by}
            else:
                print 'Phenotype not found: ' + str(phenotype_key)
                yield None

        for cvterm_dbxref in make_db_starter(bud_session.query(CVTermDbxref).join(CVTerm).filter(CVTerm.cv_no == 6).options(joinedload('dbxref')), 1000)():
            phenotype_key = (create_format_name(cvterm_dbxref.cvterm.name.lower()), 'OBSERVABLE')

            if phenotype_key in key_to_bioconcept:
                yield {'display_name': cvterm_dbxref.dbxref.dbxref_id,
                       'source': key_to_source['SGD'],
                       'category': cvterm_dbxref.dbxref.dbxref_type,
                       'bioconcept_id': key_to_bioconcept[phenotype_key].id,
                       'date_created': cvterm_dbxref.dbxref.date_created,
                       'created_by': cvterm_dbxref.dbxref.created_by}
            else:
                print 'Phenotype not found: ' + str(phenotype_key)
                yield None

        bud_session.close()
        nex_session.close()
    return bioconcept_alias_starter
