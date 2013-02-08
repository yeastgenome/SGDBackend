'''
Created on Jan 16, 2013

@author: kpaskov
'''
from model_new_schema.config import DBTYPE as NEW_DBTYPE, DBHOST as NEW_DBHOST, \
    DBNAME as NEW_DBNAME, SCHEMA as NEW_SCHEMA, DBUSER as NEW_DBUSER, \
    DBPASS as NEW_DBPASS
from model_new_schema.model import Model as NewModel
from model_old_schema.config import DBTYPE as OLD_DBTYPE, DBHOST as OLD_DBHOST, \
    DBNAME as OLD_DBNAME, SCHEMA as OLD_SCHEMA, DBUSER as OLD_DBUSER, \
    DBPASS as OLD_DBPASS
from model_old_schema.model import Model as OldModel
from schema_conversion.old_to_new import feature_to_bioent, \
    reference_to_reference, journal_to_journal, book_to_book, abstract_to_abstract, \
    reftype_to_reftype, author_to_author, interaction_to_biorel, \
    experiment_property_to_phenoevidence_property
import datetime
import model_new_schema
import model_old_schema

def convert():
    old_model = OldModel(OLD_DBTYPE, OLD_DBHOST, OLD_DBNAME, OLD_SCHEMA)
    old_model.connect(OLD_DBUSER, OLD_DBPASS)
    
    new_model = NewModel(NEW_DBTYPE, NEW_DBHOST, NEW_DBNAME, NEW_SCHEMA)
    new_model.connect(NEW_DBUSER, NEW_DBPASS)
    
    #convert_features_to_bioents(old_model, new_model)
    #convert_references_to_references(old_model, new_model)
    
    #convert_interactions_to_biorels(old_model, new_model, 0, 400000)
    #convert_interactions_to_biorels(old_model, new_model, 400000, 450000)
    #convert_interactions_to_biorels(old_model, new_model, 450000, 500000)
    #convert_interactions_to_biorels(old_model, new_model, 500000, 600000)
    #convert_interactions_to_biorels(old_model, new_model, 600000, 900000)
    #convert_interactions_to_biorels(old_model, new_model, 900000, 1000000)
    #convert_interactions_to_biorels(old_model, new_model, 1000000, 1100000)
    #convert_interactions_to_biorels(old_model, new_model, 1100000, 1120000)
    #convert_interactions_to_biorels(old_model, new_model, 1120000, 1140000)
    #convert_interactions_to_biorels(old_model, new_model, 1140000, 1141000)
    #convert_interactions_to_biorels(old_model, new_model, 1141000, 1145000)
    #convert_interactions_to_biorels(old_model, new_model, 1145000, 1150000)
    #convert_interactions_to_biorels(old_model, new_model, 1150000, 1155000)
    #convert_interactions_to_biorels(old_model, new_model, 1155000, 1160000)
    #convert_interactions_to_biorels(old_model, new_model, 1160000, 1165000)
    #convert_interactions_to_biorels(old_model, new_model, 1165000, 1170000)
    #convert_interactions_to_biorels(old_model, new_model, 1170000, 1175000)
    #convert_interactions_to_biorels(old_model, new_model, 1175000, 1180000)
    
    #convert_interactions_to_biorels(old_model, new_model, 1180000, 1190000)
    #convert_interactions_to_biorels(old_model, new_model, 1190000, 1200000)
    #convert_interactions_to_biorels(old_model, new_model, 1200000, 1210000)
    #convert_interactions_to_biorels(old_model, new_model, 1210000, 1220000)
    
    #continue from here
    convert_interactions_to_biorels(old_model, new_model, 1220000, 1230000)
#    convert_interactions_to_biorels(old_model, new_model, 1230000, 1240000)

#    convert_interactions_to_biorels(old_model, new_model, 1240000, 1260000)
#    convert_interactions_to_biorels(old_model, new_model, 1260000, 1280000)
#    convert_interactions_to_biorels(old_model, new_model, 1280000, 1300000)
#    convert_interactions_to_biorels(old_model, new_model, 1300000, 1500000)
    
    #convert_phenotypes_to_bioconcepts(old_model, new_model, 0, 1000)
    #convert_phenotypes_to_bioconcepts(old_model, new_model, 1000, 5000)
    #convert_phenotypes_to_bioconcepts(old_model, new_model, 5000, 20000)
    #convert_phenotypes_to_bioconcepts(old_model, new_model, 20000, 40000)
    
    #continue from here
    #convert_phenotypes_to_bioconcepts(old_model, new_model, 40000, 60000)
    #convert_phenotypes_to_bioconcepts(old_model, new_model, 60000, 92000)

    #convert_sequences_to_sequences(old_model, new_model)

def convert_features_to_bioents(old_model, new_model):
    print "Convert Features to Bioentities"
    from model_old_schema.feature import Feature as OldFeature
    from model_new_schema.bioentity import Bioentity as NewBioentity

    fs = old_model.execute(model_old_schema.model.get(OldFeature), OLD_DBUSER)
    
    count = 0;
    time = datetime.datetime.now()
    for f in fs:
        if not new_model.execute(model_new_schema.model.exists(NewBioentity, id=f.id), NEW_DBUSER):
            b = feature_to_bioent(f)
            new_model.execute(model_new_schema.model.add(b), NEW_DBUSER, commit=True)
              
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(fs)) +  " " + str(new_time - time)
            time = new_time
            
def convert_references_to_references(old_model, new_model):
    print "Convert References to References"
    from model_old_schema.reference import Reference as OldReference
    from model_new_schema.reference import Reference as NewReference, Journal as NewJournal, Book as NewBook, Abstract as NewAbstract, \
        Author as NewAuthor, Reftype as NewReftype, AuthorReference as NewAuthorReference

    rs = old_model.execute(model_old_schema.model.get(OldReference), OLD_DBUSER)
    
    count = 0;
    time = datetime.datetime.now()
    for r in rs:
        if not new_model.execute(model_new_schema.model.exists(NewReference, id=r.id), NEW_DBUSER):
            new_r = reference_to_reference(r)
            if r.journal is not None:
                new_j = new_model.execute(model_new_schema.model.get_first(NewJournal, id=r.journal.id), NEW_DBUSER)
                if new_j is None:
                    new_j = journal_to_journal(r.journal)
                new_r.journal = new_j
                    
            if r.book is not None:
                new_b = new_model.execute(model_new_schema.model.get_first(NewBook, id=r.book.id), NEW_DBUSER)
                if new_b is None:
                    new_b = book_to_book(r.book)
                new_r.book = new_b
                    
            if r.abst is not None:
                new_a = new_model.execute(model_new_schema.model.get_first(NewAbstract, reference_id=r.id), NEW_DBUSER)
                if new_a is None:
                    new_a = abstract_to_abstract(r.abst)
                new_r.abst = new_a
                    
            author_ids = set()
            for index, author_reference in r.author_references.items():
                new_ar = new_model.execute(model_new_schema.model.get_first(NewAuthorReference, id=author_reference.id), NEW_DBUSER)
                author = author_reference.author
                if not author.id in author_ids:
                    if new_ar is None:
                        new_au = new_model.execute(model_new_schema.model.get_first(NewAuthor, id=author.id), NEW_DBUSER)
                        if new_au is None:
                            new_au = author_to_author(author)
                        new_ar = NewAuthorReference(new_au, author_reference.order, author_reference.type, author_reference_id=author_reference.id)
                    new_r.author_references[index] = new_ar
                    author_ids.add(author.id)
                else:
                    print "Double author in " + str(r.id) + " author_id =" + str(author.id)
                
            for mapping_id, reftype in r.reftypes.items():
                new_rt = new_model.execute(model_new_schema.model.get_first(NewReftype, id=reftype.id), NEW_DBUSER)
                if new_rt is None:
                    new_r.reftypes[mapping_id] = reftype_to_reftype(reftype)
                else:
                    new_r.reftypes[mapping_id] = new_rt
            new_model.execute(model_new_schema.model.add(new_r), NEW_DBUSER, commit=True)
            
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(rs)) +  " " + str(new_time - time)
            time = new_time
            
def convert_interactions_to_biorels(old_model, new_model, min_id, max_id):
    print "Convert Interaction to Biorelations"
    from model_old_schema.interaction import Interaction as OldInteraction
    from model_new_schema.biorelation import Interaction as NewInteraction
    from model_new_schema.evidence import Interevidence
    
    time = datetime.datetime.now()
    inters = old_model.execute(model_old_schema.model.get_filter(OldInteraction, OldInteraction.id>=min_id, OldInteraction.id < max_id), OLD_DBUSER)
    
    count = 0;
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for old_interaction in inters:
        if not new_model.execute(model_new_schema.model.exists(Interevidence, id=old_interaction.id), NEW_DBUSER):
            bait_id = old_interaction.features['Bait'].id
            hit_id = old_interaction.features['Hit'].id
    
            if bait_id < hit_id:
                new_biorel = new_model.execute(model_new_schema.model.get_first(NewInteraction, source_bioent_id=bait_id, sink_bioent_id=hit_id), NEW_DBUSER)
                direction = 'bait-hit'
            else:
                new_biorel = new_model.execute(model_new_schema.model.get_first(NewInteraction, source_bioent_id=hit_id, sink_bioent_id=bait_id), NEW_DBUSER)
                direction = 'hit-bait'
    
            if new_biorel is None:
                new_biorel = interaction_to_biorel(old_interaction)
    
            reference_id = None
            if len(old_interaction.references) > 0:
                reference_id = old_interaction.references[0].id
            observable = None
            if len(old_interaction.observables) > 0:
                observable = old_interaction.observables[0]
            qualifier = None
            if len(old_interaction.qualifiers) > 0:
                qualifier = old_interaction.qualifiers[0]
            note = None
            if len(old_interaction.notes) > 0:
                note = old_interaction.notes[0]
    
            new_biorel.evidences.append(Interevidence(old_interaction.experiment_type, reference_id, 4932, direction, old_interaction.annotation_type,
                                           old_interaction.modification, old_interaction.source, observable, qualifier, note,
                                           old_interaction.interaction_type,
                                           evidence_id=old_interaction.id, date_created=old_interaction.date_created,
                                           created_by=old_interaction.created_by))
    
            new_model.execute(model_new_schema.model.add(new_biorel), NEW_DBUSER, commit=True)
            
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(inters)) +  " " + str(new_time - time)
            time = new_time
            
def get_strain(properties):
    strain_name = None
    strain_background = None
    for prop in properties:
        if prop.type == 'strain_name':
            strain_name = prop.value
        elif prop.type == 'strain_background':
            strain_background = prop.value
    
    if strain_name is None:
        return strain_background
    else:
        return strain_name
        
def convert_phenotypes_to_bioconcepts(old_model, new_model, min_id, max_id):
    print "Convert Phenotypes to Bioconcepts"

    from model_old_schema.phenotype import Phenotype_Feature as OldPhenotype_Feature
    from model_new_schema.evidence import Phenoevidence as NewPhenoevidence
    from model_new_schema.bioconcept import Phenotype as NewPhenotype
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon

    time = datetime.datetime.now()
    ps = old_model.execute(model_old_schema.model.get_filter(OldPhenotype_Feature, OldPhenotype_Feature.id>=min_id, OldPhenotype_Feature.id < max_id), OLD_DBUSER)

    count = 0
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for p in ps:
        if not new_model.execute(model_new_schema.model.exists(NewPhenoevidence, id=p.id), NEW_DBUSER):
            #Find strain name from expt_properties
            if p.experiment is not None:
                strain = get_strain(p.experiment_properties)
                comment = p.experiment_comment
            else:
                strain = None
                comment = None
            
            new_p = NewPhenoevidence(p.experiment_type, None, strain, p.mutant_type, p.source, comment,
                                  evidence_id=p.id, date_created=p.date_created, created_by=p.created_by)
            
            if p.experiment is not None:
                for prop in p.experiment_properties:
                    new_property = experiment_property_to_phenoevidence_property(prop)
                    new_p.properties.append(new_property)
             
            qualifier = 'None';
            observable = 'None';
            if p.qualifier is not None:
                qualifier = p.qualifier
            if p.observable is not None:
                observable = p.observable
                        
            bioent = new_model.execute(model_new_schema.model.get_first(NewBioentity, id=p.feature_id), NEW_DBUSER)

            #Find or create bioconcept
            new_biocon = new_model.execute(model_new_schema.model.get_first(NewPhenotype, qualifier=qualifier, observable=observable), NEW_DBUSER)
            if new_biocon is None:
                new_biocon = NewPhenotype(qualifier, observable, biocon_id=p.id, date_created=p.date_created, created_by=p.created_by)
                new_model.execute(model_new_schema.model.add(new_biocon), NEW_DBUSER, commit=True)
                biocon_id = p.id
            else:
                biocon_id = new_biocon.id
                
            #Find or create BioentBiocon
            bioent_biocon = new_model.execute(model_new_schema.model.get_first(NewBioentBiocon, bioent_id=bioent.id, biocon_id=biocon_id), NEW_DBUSER)
            if bioent_biocon is None:
                bioent_biocon = NewBioentBiocon(bioent, biocon_id)
            bioent_biocon.evidences.append(new_p)
                        
            new_model.execute(model_new_schema.model.add(bioent_biocon), NEW_DBUSER, commit=True)
            
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(ps)) +  " " + str(new_time - time)
            time = new_time
   
def convert_sequences_to_sequences(old_model, new_model):
    pass
    
if __name__ == "__main__":
    convert()