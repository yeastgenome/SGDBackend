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
from schema_conversion.old_to_new_bioconcept import convert_go
from schema_conversion.old_to_new_bioentity import feature_to_bioent
from schema_conversion.old_to_new_biorelation import interaction_to_biorel
from schema_conversion.old_to_new_reference import convert_reference
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
    #convert_interactions_to_biorels(old_model, new_model, 1220000, 1230000)
    #convert_interactions_to_biorels(old_model, new_model, 1230000, 1240000)
    #convert_interactions_to_biorels(old_model, new_model, 1240000, 1250000)
    #convert_interactions_to_biorels(old_model, new_model, 1250000, 1260000)
    #convert_interactions_to_biorels(old_model, new_model, 1260000, 1270000)
    #convert_interactions_to_biorels(old_model, new_model, 1270000, 1280000)
    #convert_interactions_to_biorels(old_model, new_model, 1280000, 1290000)
    #convert_interactions_to_biorels(old_model, new_model, 1290000, 1300000)
    #convert_interactions_to_biorels(old_model, new_model, 1300000, 1500000)
    
    #convert_phenotypes_to_bioconcepts(old_model, new_model, 0, 1000)
    #convert_phenotypes_to_bioconcepts(old_model, new_model, 1000, 5000)
    #convert_phenotypes_to_bioconcepts(old_model, new_model, 5000, 20000)
    #convert_phenotypes_to_bioconcepts(old_model, new_model, 20000, 40000)
    #convert_phenotypes_to_bioconcepts(old_model, new_model, 40000, 60000)
    #convert_phenotypes_to_bioconcepts(old_model, new_model, 60000, 92000)
    #convert_phenotypes_to_observable(old_model, new_model)
    
    

    #fill_typeahead_table(old_model, new_model, 'ORF')
    #fill_typeahead_table(old_model, new_model, 'ARS')
    #fill_typeahead_table(old_model, new_model, 'CENTROMERE')
    #fill_typeahead_table(old_model, new_model, 'GENE_CASSETTE')
    #fill_typeahead_table(old_model, new_model, 'LONG_TERMINAL_REPEAT')
    #fill_typeahead_table(old_model, new_model, 'MATING_LOCUS')
    #fill_typeahead_table(old_model, new_model, 'MULTIGENE LOCUS')
    #fill_typeahead_table(old_model, new_model, 'NCRNA')
    #fill_typeahead_table(old_model, new_model, 'NOT IN SYSTEMATIC SEQUENCE OF S288C')
    #fill_typeahead_table(old_model, new_model, 'NOT PHYSICALLY MAPPED')
    #fill_typeahead_table(old_model, new_model, 'PSEUDOGENE')
    #fill_typeahead_table(old_model, new_model, 'RETROTRANSPOSON')
    #fill_typeahead_table(old_model, new_model, 'RRNA')
    #fill_typeahead_table(old_model, new_model, 'SNORNA')
    #fill_typeahead_table(old_model, new_model, 'SNRNA')
    #fill_typeahead_table(old_model, new_model, 'TELOMERE')
    #fill_typeahead_table(old_model, new_model, 'TELOMERIC_REPEAT')
    #fill_typeahead_table(old_model, new_model, 'TRANSPOSABLE_ELEMENT_GENE')
    #fill_typeahead_table(old_model, new_model, 'TRNA')
    #fill_typeahead_table(old_model, new_model, 'X_ELEMENT_COMBINATORIAL_REPEATS')
    #fill_typeahead_table(old_model, new_model, 'X_ELEMENT_CORE_SEQUENCE')
    #fill_typeahead_table(old_model, new_model, "Y'_ELEMENT")
    
    #fill_typeahead_table_aliases(old_model, new_model)
    #convert_alias_to_alias(old_model, new_model)

    #convert_sequences_to_sequences(old_model, new_model)
    
    def f(session):
        #fill_cache(session)
        #update_phenotypes(old_model, 80000, 100000, session)
        #go_to_bioconcept(old_model, session)
        convert_go(old_model, session)
        #convert_reference(old_model, session)
    
    new_model.execute(f, NEW_DBUSER, commit=True)


    

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
            
def convert_references_to_references(session, old_model):
    print "Convert References to References"
    from model_old_schema.reference import Reference as OldReference

    rs = old_model.execute(model_old_schema.model.get(OldReference), OLD_DBUSER)
    
    count = 0;
    time = datetime.datetime.now()
    for r in rs:
        new_r = reference_to_reference(r)
        model_new_schema.model.add(new_r, session)       
            
        count = count+1
        if count%1000 == 0:
            session.commit()
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
        
def update_phenotypes(old_model, min_id, max_id, session):
    print "Convert Phenotypes to Bioconcepts"

    from model_old_schema.phenotype import Phenotype_Feature as OldPhenotype_Feature

    time = datetime.datetime.now()
    ps = old_model.execute(model_old_schema.model.get_filter(OldPhenotype_Feature, OldPhenotype_Feature.id>=min_id, OldPhenotype_Feature.id < max_id), OLD_DBUSER)

    count = 0
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for p in ps:
        new_p = update_phenoevidence(p)
        if new_p is not None:
            model_new_schema.model.add(new_p, session=session)
            
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(ps)) +  " " + str(new_time - time)
            time = new_time
   
def fill_typeahead_table(old_model, new_model, bioent_type):
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.search import Typeahead

    time = datetime.datetime.now()
    fs = new_model.execute(model_new_schema.model.get(NewBioentity, bioent_type=bioent_type), NEW_DBUSER)
    print len(fs)
    count = 0
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for f in fs:
        name = f.name
        if name is not None:
            for i in range (0, len(name)):
                if not new_model.execute(model_new_schema.model.exists(Typeahead, name=name[:i], full_name=name), NEW_DBUSER):
                    typeahead = Typeahead(name[:i], name, 'BIOENT', f.id)
                    new_model.execute(model_new_schema.model.add(typeahead), NEW_DBUSER, commit=True)

        secondary_name = f.secondary_name
        if secondary_name is not None and secondary_name != name:
            for i in range (0, len(secondary_name)):
                if not new_model.execute(model_new_schema.model.exists(Typeahead, name=secondary_name[:i], full_name=secondary_name), NEW_DBUSER):
                    typeahead = Typeahead(secondary_name[:i], secondary_name, 'BIOENT', f.id)
                    new_model.execute(model_new_schema.model.add(typeahead), NEW_DBUSER, commit=True)
        
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(fs)) +  " " + str(new_time - time)
            time = new_time
            
def fill_typeahead_table_aliases(old_model, new_model):
    from model_new_schema.bioentity import Alias as NewAlias
    from model_new_schema.search import Typeahead

    time = datetime.datetime.now()
    aliases = new_model.execute(model_new_schema.model.get(NewAlias, used_for_search='Y'), NEW_DBUSER)

    count = 0
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for alias in aliases:
        name = alias.name
        if name is not None:
            #for i in range (0, len(name)):
            if not new_model.execute(model_new_schema.model.exists(Typeahead, name=name, full_name=name), NEW_DBUSER):
                typeahead = Typeahead(name, name, 'BIOENT', alias.bioent_id)
                new_model.execute(model_new_schema.model.add(typeahead), NEW_DBUSER, commit=True)
        
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(aliases)) +  " " + str(new_time - time)
            time = new_time
 
def convert_alias_to_alias(old_model, new_model):
    from model_old_schema.feature import AliasFeature as OldAliasFeature
    from model_new_schema.bioentity import Alias as NewAlias

    time = datetime.datetime.now()
    aliases = old_model.execute(model_old_schema.model.get(OldAliasFeature),OLD_DBUSER)
   
    count = 0
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for alias in aliases:
        new_a = NewAlias(alias.alias_name, alias.alias_type, alias.used_for_search, 
                         alias_id=alias.id, bioent_id=alias.feature_id, date_created = alias.date_created, created_by = alias.created_by)
        new_model.execute(model_new_schema.model.add(new_a), NEW_DBUSER, commit=True)

        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(aliases)) +  " " + str(new_time - time)
            time = new_time 
            
def convert_phenotypes_to_observable(old_model, new_model):
    print "Convert Phenotypes to Bioconcepts"

    from model_old_schema.phenotype import Phenotype_Feature as OldPhenotype_Feature
    from model_new_schema.evidence import Phenoevidence as NewPhenoevidence
    from model_new_schema.bioconcept import Phenotype as NewPhenotype
    from model_new_schema.bioentity import Bioentity as NewBioentity
    from model_new_schema.bioconcept import BioentBiocon as NewBioentBiocon

    time = datetime.datetime.now()
    ps = old_model.execute(model_old_schema.model.get(OldPhenotype_Feature), OLD_DBUSER)
    
    id_new_ps = {}
    new_ps = new_model.execute(model_new_schema.model.get(NewPhenoevidence), NEW_DBUSER)
    for new_p in new_ps:
        id_new_ps[new_p.id] = new_p
        
    count = 0
    new_time = datetime.datetime.now()
    print 'Loaded in ' + str(new_time-time)
    time = new_time
    for p in ps:
        phenoevidence = id_new_ps[p.id]
        if phenoevidence.qualifier is None:
            qualifier = 'None';
            observable = 'None';
            if p.qualifier is not None:
                qualifier = p.qualifier
            if p.observable is not None:
                observable = p.observable
                
            #Set qualifier for phenoevidence.
            phenoevidence.qualifier = qualifier
                        
            bioent = new_model.execute(model_new_schema.model.get_first(NewBioentity, id=p.feature_id), NEW_DBUSER)

            #Find or create bioconcept
            new_biocon = new_model.execute(model_new_schema.model.get_first(NewPhenotype, observable=observable), NEW_DBUSER)
            if new_biocon is None:
                new_biocon = NewPhenotype(observable, biocon_id=p.id, date_created=p.date_created, created_by=p.created_by)
                new_model.execute(model_new_schema.model.add(new_biocon), NEW_DBUSER, commit=True)
                biocon_id = p.id
            else:
                biocon_id = new_biocon.id
                
            #Find or create BioentBiocon
            bioent_biocon = new_model.execute(model_new_schema.model.get_first(NewBioentBiocon, bioent_id=bioent.id, biocon_id=biocon_id), NEW_DBUSER)
            if bioent_biocon is None:
                bioent_biocon = NewBioentBiocon(bioent, biocon_id)
            bioent_biocon.evidences.append(phenoevidence)
         
            new_model.execute(model_new_schema.model.add(bioent_biocon), NEW_DBUSER, commit=True)
            
        count = count+1
        if count%1000 == 0:
            new_time = datetime.datetime.now()
            print str(count) + '/' + str(len(ps)) +  " " + str(new_time - time)
            time = new_time

          

    
if __name__ == "__main__":
    convert()