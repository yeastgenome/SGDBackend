from src.sgd.convert import create_format_name
from src.sgd.convert.transformers import TransformerInterface, make_db_starter

__author__ = 'kpaskov'


# --------------------- Convert Interaction Evidence ---------------------
def make_interaction_evidence_starter(bud_session, interaction_type):
    from src.sgd.model.bud.interaction import Interaction as OldInteraction
    return make_db_starter(bud_session.query(OldInteraction).filter_by(interaction_type=interaction_type), 1000)

class BudObj2InteractionEvidenceObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Experiment, Source
        from src.sgd.model.nex.reference import Reference
        from src.sgd.model.nex.bioentity import Locus
        from src.sgd.model.nex.bioconcept import Phenotype

        #Grab cached dictionaries
        self.key_to_experiment = dict([(x.unique_key(), x) for x in self.session.query(Experiment).all()])
        self.key_to_phenotype = dict([(x.unique_key(), x) for x in self.session.query(Phenotype).all()])
        self.id_to_bioents = dict([(x.id, x) for x in self.session.query(Locus).all()])
        self.id_to_reference = dict([(x.id, x) for x in self.session.query(Reference).all()])
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.nex.evidence import Geninteractionevidence, Physinteractionevidence
        from src.sgd.model.nex.bioconcept import create_phenotype_format_name
        reference_ids = bud_obj.reference_ids
        if len(reference_ids) != 1:
            print 'Too many references'
            return None
        reference_id = reference_ids[0]
        reference = None if reference_id not in self.id_to_reference else self.id_to_reference[reference_id]

        note = bud_obj.interaction_references[0].note

        if bud_obj.interaction_features[0].feature_id < bud_obj.interaction_features[1].feature_id:
            bioent1_id = bud_obj.interaction_features[0].feature_id
            bioent2_id = bud_obj.interaction_features[1].feature_id
            bait_hit = bud_obj.interaction_features[0].action + '-' + bud_obj.interaction_features[1].action
        else:
            bioent1_id = bud_obj.interaction_features[1].feature_id
            bioent2_id = bud_obj.interaction_features[0].feature_id
            bait_hit = bud_obj.interaction_features[1].action + '-' + bud_obj.interaction_features[0].action

        bioentity1 = None if bioent1_id not in self.id_to_bioents else self.id_to_bioents[bioent1_id]
        bioentity2 = None if bioent2_id not in self.id_to_bioents else self.id_to_bioents[bioent2_id]

        experiment_key = create_format_name(bud_obj.experiment_type)
        experiment = None if experiment_key not in self.key_to_experiment else self.key_to_experiment[experiment_key]

        source_key = bud_obj.source
        source = None if source_key not in self.key_to_source else self.key_to_source[source_key]

        if bud_obj.interaction_type == 'genetic interactions':
            mutant_type = None
            phenotype = None
            phenotypes = bud_obj.interaction_phenotypes
            if len(phenotypes) == 1:
                phenotype_key = (create_phenotype_format_name(phenotypes[0].observable, phenotypes[0].qualifier), 'PHENOTYPE')
                if phenotype_key in self.key_to_phenotype:
                    phenotype = None if phenotype_key is None else self.key_to_phenotype[phenotype_key]
                    mutant_type = phenotypes[0].mutant_type
                else:
                    print 'Phenotype not found: ' + str(phenotype_key)
            elif len(phenotypes) > 1:
                print 'Too many phenotypes'

            return Geninteractionevidence(source, reference, experiment,
                                                                bioentity1, bioentity2, phenotype, mutant_type,
                                                                bud_obj.annotation_type, bait_hit, note,
                                                                bud_obj.date_created, bud_obj.created_by)
        elif bud_obj.interaction_type == 'physical interactions':
            return Physinteractionevidence(source, reference, experiment,
                                                                bioentity1, bioentity2,
                                                                bud_obj.modification, bud_obj.annotation_type, bait_hit, note,
                                                                bud_obj.date_created, bud_obj.created_by)
        return None

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None
