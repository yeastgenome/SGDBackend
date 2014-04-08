from src.sgd.convert.transformers import TransformerInterface, make_db_starter, make_multi_starter, make_mode_db_starter


__author__ = 'kpaskov'

#1.23.14 Maitenance (sgd-dev): 1:04

# --------------------- Convert Phenotype ---------------------
def make_phenotype_starter(bud_session):
    from src.sgd.model.bud.cv import CVTerm
    from src.sgd.model.bud.phenotype import Phenotype, PhenotypeFeature

    chemical_phenotypes = {'chemical compound accumulation', 'chemical compound excretion', 'resistance to chemicals'}
    return make_multi_starter([make_db_starter(bud_session.query(CVTerm).filter(CVTerm.cv_no == 6), 1000),
                               make_db_starter(bud_session.query(Phenotype), 1000),
                               make_mode_db_starter(bud_session.query(PhenotypeFeature).join(PhenotypeFeature.phenotype).filter(Phenotype.observable.in_(chemical_phenotypes)),
                                                    1000, ['Observable', 'Phenotype'])])

class BudObj2PhenotypeObj(TransformerInterface):

    def __init__(self, old_session_maker, new_session_maker):
        self.old_session = old_session_maker()
        self.new_session = new_session_maker()

        from src.sgd.model.nex.misc import Source
        from src.sgd.model.bud.cv import CVTerm, CVTermRel
        self.key_to_source = dict([(x.unique_key(), x) for x in self.new_session.query(Source).all()])

        #Grab old objects
        old_cvterms = self.old_session.query(CVTerm).filter(CVTerm.cv_no == 6).all()

        #Get ancestory_types
        self.observable_to_ancestor = dict()
        child_id_to_parent_id = dict([(x.child_id, x.parent_id) for x in self.old_session.query(CVTermRel).all()])
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
                self.observable_to_ancestor[old_obj.name] = id_to_observable[ancestor_id]
            else:
                self.observable_to_ancestor[old_obj.name] = id_to_observable[ancestry[0]]

    def convert(self, bud_obj):
        from src.sgd.model.nex.bioconcept import Phenotype
        from src.sgd.model.bud.phenotype import Phenotype as OldPhenotype, PhenotypeFeature as OldPhenotypeFeature
        from src.sgd.model.bud.cv import CVTerm as OldCVTerm

        if isinstance(bud_obj, OldPhenotype):
            observable = bud_obj.observable
            if observable == 'dessication resistance':
                observable = 'desiccation resistance'
            qualifier = bud_obj.qualifier

            source = self.key_to_source['SGD']
            phenotype_type = create_phenotype_type(bud_obj.observable)
            ancestor_type = None if observable not in self.observable_to_ancestor else self.observable_to_ancestor[observable]
            if ancestor_type is None:
                print 'No ancestor type: ' + str(observable)
                return None
            return Phenotype(source, None, None, observable, qualifier, phenotype_type, ancestor_type,
                                         bud_obj.date_created, bud_obj.created_by)
        elif isinstance(bud_obj, OldCVTerm):
            observable = bud_obj.name
            source = self.key_to_source['SGD']
            phenotype_type = create_phenotype_type(observable)
            ancestor_type = None if observable not in self.observable_to_ancestor else self.observable_to_ancestor[observable]
            if ancestor_type is None:
                print 'No ancestor type: ' + str(observable)
                return None
            description = bud_obj.definition
            if observable == 'observable':
                description = 'Features of Saccharomyces cerevisiae cells, cultures, or colonies that can be detected, observed, measured, or monitored.'
            return Phenotype(source, None, description,  observable, None, phenotype_type, ancestor_type,
                                         bud_obj.date_created, bud_obj.created_by)
        elif isinstance(bud_obj, tuple) and isinstance(bud_obj[1], OldPhenotypeFeature):
            mode, phenofeat = bud_obj

            if phenofeat.experiment is None:
                return None

            chemicals = phenofeat.experiment.chemicals
            if len(chemicals) == 0:
                return None

            chemical = ' and '.join([x[0] for x in chemicals])

            source = self.key_to_source['SGD']
            old_observable = phenofeat.phenotype.observable
            if old_observable == 'resistance to chemicals':
                new_observable = phenofeat.phenotype.observable.replace('chemicals', chemical)
                description = 'The level of resistance to exposure to ' + chemical + '.'
            elif old_observable == 'chemical compound accumulation':
                new_observable = phenofeat.phenotype.observable.replace('chemical compound', chemical)
                description = 'The production and/or storage of ' + chemical + '.'
            elif old_observable == 'chemical compound excretion':
                new_observable = phenofeat.phenotype.observable.replace('chemical compound', chemical)
                description = 'The excretion from the cell of ' + chemical + '.'
            else:
                return None

            qualifier = phenofeat.phenotype.qualifier
            phenotype_type = create_phenotype_type(old_observable)
            ancestor_type = None if old_observable not in self.observable_to_ancestor else self.observable_to_ancestor[old_observable]
            if mode == 'Observable':
                return Phenotype(source, None, description,
                                         new_observable, None, phenotype_type, ancestor_type,
                                         phenofeat.date_created, phenofeat.created_by)
            elif mode == 'Phenotype':
                return Phenotype(source, None, None,
                                         new_observable, qualifier, phenotype_type, ancestor_type,
                                         phenofeat.date_created, phenofeat.created_by)
        return None

    def finished(self, delete_untouched=False, commit=False):
        self.old_session.close()
        self.new_session.close()
        return None

def create_phenotype_type(observable):
    if observable in {'chemical compound accumulation', 'resistance to chemicals', 'osmotic stress resistance', 'alkaline pH resistance',
                      'ionic stress resistance', 'oxidative stress resistance', 'small molecule transport', 'metal resistance',
                      'acid pH resistance', 'hyperosmotic stress resistance', 'hypoosmotic stress resistance', 'chemical compound excretion'}:
        return 'chemical'
    elif observable in {'protein/peptide accumulation', 'protein/peptide modification', 'protein/peptide distribution',
                        'RNA accumulation', 'RNA localization', 'RNA modification'}:
        return 'pp_rna'
    else:
        return 'cellular'

# --------------------- Convert GO ---------------------
def make_go_starter(bud_session):
    from src.sgd.model.bud.go import Go
    return make_db_starter(bud_session.query(Go), 1000)

class BudObj2GoObj(TransformerInterface):

    def __init__(self, new_session_maker):
        self.new_session = new_session_maker()

        from src.sgd.model.nex.misc import Source
        self.key_to_source = dict([(x.unique_key(), x) for x in self.new_session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.nex.bioconcept import Go as NewGo

        display_name = bud_obj.go_term
        source = self.key_to_source['GO']
        return NewGo(display_name, source, None, bud_obj.go_definition,
                       'GO:' + str(bud_obj.go_go_id).zfill(7), abbrev_to_go_aspect[bud_obj.go_aspect],
                       bud_obj.date_created, bud_obj.created_by)

    def finished(self, delete_untouched=False, commit=False):
        self.new_session.close()
        return None

abbrev_to_go_aspect = {'C':'cellular component', 'F':'molecular function', 'P':'biological process'}

# --------------------- Convert EC ---------------------
def make_ecnumber_starter(bud_session):
    from src.sgd.model.bud.general import Dbxref
    return make_db_starter(bud_session.query(Dbxref).filter(Dbxref.dbxref_type == 'EC number'), 1000)

class BudObj2ECNumberObj(TransformerInterface):

    def __init__(self, new_session_maker):
        self.new_session = new_session_maker()

        from src.sgd.model.nex.misc import Source
        self.key_to_source = dict([(x.unique_key(), x) for x in self.new_session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.nex.bioconcept import ECNumber

        display_name = bud_obj.dbxref_id
        source = self.key_to_source[bud_obj.source]

        return ECNumber(display_name, source, bud_obj.dbxref_name, bud_obj.date_created, bud_obj.created_by)

    def finished(self, delete_untouched=False, commit=False):
        self.new_session.close()
        return None
