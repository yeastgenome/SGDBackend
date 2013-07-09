from model_new_schema import config as new_config
from model_new_schema.bioconcept import Bioconcept, BioconAncestor, \
    BioconRelation
from model_new_schema.bioentity import Bioentity, Locus, BioentUrl
from model_new_schema.biofact import Biofact
from model_new_schema.chemical import Chemical
from model_new_schema.evelement import Experiment, Strain
from model_new_schema.evidence import EvidenceChemical
from model_new_schema.go import Goevidence, Go
from model_new_schema.interaction import GeneticInterevidence, \
    GeneticInteraction, PhysicalInterevidence, PhysicalInteraction, BioentRelation
from model_new_schema.litguide import Bioentevidence
from model_new_schema.misc import Url
from model_new_schema.phenotype import Phenoevidence, Phenotype
from model_new_schema.reference import Reference, Author, AuthorReference
from model_new_schema.search import Typeahead
from model_new_schema.sequence import Sequence
from schema_conversion import prepare_schema_connection
from sgdbackend.models import DBSession
from sqlalchemy.orm import joinedload, subqueryload_all, subqueryload
from sqlalchemy.orm.util import with_polymorphic
from sqlalchemy.sql.expression import func, or_
import datetime
import math
import model_new_schema
import string

session = DBSession
#session = prepare_schema_connection(model_new_schema, new_config)()


biocon_type_to_class = {'PHENOTYPE':Phenotype, 'GO':Go}
bioent_type_to_class = {'LOCUS':Locus}
biorel_type_to_class = {'GENETIC_INTERACTION':GeneticInteraction, 'PHYSICAL_INTERACTION':PhysicalInteraction}

#Used for go and phenotype pages and go_evidence, phenotype_evidence pages
#Also used for go_graph, go_ontology_graph, and phenotype_ontology_graph.
def get_biocon(biocon_name, biocon_type, print_query=False):
    '''
    get_biocon('DNA_repair', 'GO', print_query=True)
    
    SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.description AS sprout_biocon_description, sprout.goterm.biocon_id AS sprout_goterm_biocon_id, sprout.goterm.go_go_id AS sprout_goterm_go_go_id, sprout.goterm.go_term AS sprout_goterm_go_term, sprout.goterm.go_aspect AS sprout_goterm_go_aspect, sprout.goterm.go_definition AS sprout_goterm_go_definition, sprout.goterm.direct_gene_count AS sprout_goterm_direct_gen_1 
    FROM sprout.biocon LEFT OUTER JOIN sprout.goterm ON sprout.goterm.biocon_id = sprout.biocon.biocon_id 
    WHERE sprout.biocon.biocon_type = :biocon_type_1 AND sprout.biocon.name = :name_1
    '''
    query = session.query(with_polymorphic(Bioconcept, [biocon_type_to_class[biocon_type]])).filter(Bioconcept.biocon_type==biocon_type).filter(Bioconcept.format_name==biocon_name)
    biocon = query.first()
    if print_query:
        print query
    return biocon

#Used for go_overview, phenotype_overview, go_evidence, and phenotype_evidence tables
def get_biocon_id(biocon_name, biocon_type, print_query=False):
    '''
    get_biocon_id('DNA_repair', 'GO', print_query=True)
    
    SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.description AS sprout_biocon_description 
    FROM sprout.biocon 
    WHERE sprout.biocon.biocon_type = :biocon_type_1 AND sprout.biocon.name = :name_1
    '''
    query = session.query(Bioconcept).filter(Bioconcept.biocon_type==biocon_type).filter(Bioconcept.format_name==biocon_name)
    biocon = query.first()
    biocon_id = None
    if biocon is not None:
        biocon_id = biocon.id
    if print_query:
        print query
    return biocon_id

#Used for LSP (Locus summary page) and go_evidence, phenotype_evidence, interaction_evidence pages. 
#Also used for interaction_overview, interaction_evidence table
#Also used for go_graph, interaction_graph.
def get_bioent(bioent_name, bioent_type, print_query=False):
    '''
    get_bioent('YFL039C', print_query=True)

    SELECT sprout.bioent.bioent_id AS sprout_bioent_bioent_id, sprout.bioent.name AS sprout_bioent_name, sprout.bioent.dbxref AS sprout_bioent_dbxref, sprout.bioent.bioent_type AS sprout_bioent_bioent_type, sprout.bioent.source AS sprout_bioent_source, sprout.bioent.secondary_name AS sprout_bioent_secondary_name, sprout.bioent.date_created AS sprout_bioent_date_created, sprout.bioent.created_by AS sprout_bioent_created_by, sprout.gene.bioent_id AS sprout_gene_bioent_id, sprout.gene.short_description AS sprout_gene_short_description, sprout.gene.qualifier AS sprout_gene_qualifier, sprout.gene.attribute AS sprout_gene_attribute, sprout.gene.headline AS sprout_gene_headline, sprout.gene.description AS sprout_gene_description, sprout.gene.genetic_position AS sprout_gene_genetic_position, sprout.gene.gene_type AS sprout_gene_gene_type 
    FROM sprout.bioent LEFT OUTER JOIN sprout.gene ON sprout.gene.bioent_id = sprout.bioent.bioent_id 
    WHERE sprout.bioent.name = :name_1
    '''
    query = session.query(with_polymorphic(Bioentity, [bioent_type_to_class[bioent_type]])).filter(Bioentity.format_name==bioent_name)
    bioent = query.first()
    if print_query:
        print query
    return bioent

#Used to create go_overview, phenotype_overview, go_evidence, and phenotype_evidence tables
def get_bioent_id(bioent_name, bioent_type, print_query=False):
    '''
    get_bioent_id('YFL039C', print_query=True)

    SELECT sprout.bioent.bioent_id AS sprout_bioent_bioent_id, sprout.bioent.name AS sprout_bioent_name, sprout.bioent.dbxref AS sprout_bioent_dbxref, sprout.bioent.bioent_type AS sprout_bioent_bioent_type, sprout.bioent.source AS sprout_bioent_source, sprout.bioent.secondary_name AS sprout_bioent_secondary_name, sprout.bioent.date_created AS sprout_bioent_date_created, sprout.bioent.created_by AS sprout_bioent_created_by 
    FROM sprout.bioent 
    WHERE sprout.bioent.name = :name_1
    '''
    query = session.query(Bioentity).filter(Bioentity.bioent_type==bioent_type).filter(Bioentity.format_name==bioent_name)
    bioent = query.first()
    bioent_id = None
    if bioent is not None:
        bioent_id = bioent.id
    if print_query:
        print query
    return bioent_id

#Used for Interaction Evidence page.
def get_biorel(biorel_name, biorel_type, print_query=False):
    '''
    get_biorel('YFL039C---YDR129C', 'INTERACTION', print_query=True)
    
    SELECT sprout.bioentrel.biorel_id AS sprout_bioentrel_biorel_id, sprout.bioentrel.name AS sprout_bioentrel_name, sprout.bioentrel.bioent_id1 AS sprout_bioentrel_bioent_id1, sprout.bioentrel.bioent_id2 AS sprout_bioentrel_bioent_id2, sprout.bioentrel.biorel_type AS sprout_bioentrel_biorel_type, sprout.bioentrel.date_created AS sprout_bioentrel_date_created, sprout.bioentrel.created_by AS sprout_bioentrel_created_by 
    FROM sprout.bioentrel 
    WHERE sprout.bioentrel.biorel_type = :biorel_type_1 AND sprout.bioentrel.name = :name_1
    '''
    query = session.query(BioentRelation).filter(BioentRelation.biorel_type==biorel_type).filter(BioentRelation.format_name==biorel_name)
    biorel = query.first()
    if print_query:
        print query
    return biorel

#Used to create interaction_evidence table.
def get_biorel_id(biorel_name, biorel_type, print_query=False):
    '''
    get_biorel_id('YFL039C---YDR129C', 'INTERACTION', print_query=True)

    SELECT sprout.bioentrel.biorel_id AS sprout_bioentrel_biorel_id, sprout.bioentrel.name AS sprout_bioentrel_name, sprout.bioentrel.bioent_id1 AS sprout_bioentrel_bioent_id1, sprout.bioentrel.bioent_id2 AS sprout_bioentrel_bioent_id2, sprout.bioentrel.biorel_type AS sprout_bioentrel_biorel_type, sprout.bioentrel.date_created AS sprout_bioentrel_date_created, sprout.bioentrel.created_by AS sprout_bioentrel_created_by 
    FROM sprout.bioentrel 
    WHERE sprout.bioentrel.biorel_type = :biorel_type_1 AND sprout.bioentrel.name = :name_1
    '''
    query = session.query(BioentRelation).filter(BioentRelation.biorel_type==biorel_type).filter(BioentRelation.format_name==biorel_name)
    biorel = query.first()
    biorel_id = None
    if biorel is not None:
        biorel_id = biorel.id
    if print_query:
        print query
    return biorel_id

#Used to create phenotype_overview table.
def get_chemical_id(chemical_name, print_query=False):
    query = session.query(Chemical).filter(Chemical.format_name==chemical_name)
    chemical = query.first()
    chemical_id = None
    if chemical is not None:
        chemical_id = chemical.id
    if print_query:
        print query
    return chemical_id

#Used to create chemical page.
def get_chemical(chemical_name, print_query=False):
    query = session.query(Chemical).filter(Chemical.format_name==chemical_name)
    chemical = query.first()
    return chemical

#Used for Reference page.
def get_reference(reference_name, print_query=False):
    '''
    get_reference('7635312', print_query=True)
    
    SELECT sprout.reference.reference_id AS sprout_reference_reference_id, sprout.reference.citation AS sprout_reference_citation, sprout.reference.fulltext_url AS sprout_reference_fulltext_url, sprout.reference.source AS sprout_reference_source, sprout.reference.status AS sprout_reference_status, sprout.reference.pdf_status AS sprout_reference_pdf_status, sprout.reference.dbxref_id AS sprout_reference_dbxref_id, sprout.reference.year AS sprout_reference_year, sprout.reference.pubmed_id AS sprout_reference_pubmed_id, sprout.reference.date_published AS sprout_reference_date_pu_1, sprout.reference.date_revised AS sprout_reference_date_revised, sprout.reference.issue AS sprout_reference_issue, sprout.reference.page AS sprout_reference_page, sprout.reference.volume AS sprout_reference_volume, sprout.reference.title AS sprout_reference_title, sprout.reference.journal_id AS sprout_reference_journal_id, sprout.reference.book_id AS sprout_reference_book_id, sprout.reference.doi AS sprout_reference_doi, sprout.reference.created_by AS sprout_reference_created_by, sprout.reference.date_created AS sprout_reference_date_created, abstract_1.abstract AS abstract_1_abstract, abstract_1.reference_id AS abstract_1_reference_id, author_reference_1.author_reference_id AS author_reference_1_autho_2, author_reference_1.author_order AS author_reference_1_autho_3, author_reference_1.author_type AS author_reference_1_author_type, author_1.author_id AS author_1_author_id, author_1.author_name AS author_1_author_name, author_1.created_by AS author_1_created_by, author_1.date_created AS author_1_date_created, author_reference_1.author_id AS author_reference_1_author_id, author_reference_1.reference_id AS author_reference_1_refer_4 
    FROM sprout.reference LEFT OUTER JOIN sprout.abstract abstract_1 ON sprout.reference.reference_id = abstract_1.reference_id LEFT OUTER JOIN sprout.author_reference author_reference_1 ON sprout.reference.reference_id = author_reference_1.reference_id LEFT OUTER JOIN sprout.author author_1 ON author_1.author_id = author_reference_1.author_id 
    WHERE sprout.reference.pubmed_id = :pubmed_id_1
    '''
    query = session.query(Reference).filter(Reference.format_name==reference_name)
    
    reference = query.first() 
    
    if print_query:
        print query
    return reference

#Used to create go_overview and phenotype_overview tables
def get_reference_id(reference_name, print_query=False):
    '''
    get_reference_id('7635312', print_query=True)
    
    SELECT sprout.reference.reference_id AS sprout_reference_reference_id, sprout.reference.citation AS sprout_reference_citation, sprout.reference.fulltext_url AS sprout_reference_fulltext_url, sprout.reference.source AS sprout_reference_source, sprout.reference.status AS sprout_reference_status, sprout.reference.pdf_status AS sprout_reference_pdf_status, sprout.reference.dbxref_id AS sprout_reference_dbxref_id, sprout.reference.year AS sprout_reference_year, sprout.reference.pubmed_id AS sprout_reference_pubmed_id, sprout.reference.date_published AS sprout_reference_date_pu_1, sprout.reference.date_revised AS sprout_reference_date_revised, sprout.reference.issue AS sprout_reference_issue, sprout.reference.page AS sprout_reference_page, sprout.reference.volume AS sprout_reference_volume, sprout.reference.title AS sprout_reference_title, sprout.reference.journal_id AS sprout_reference_journal_id, sprout.reference.book_id AS sprout_reference_book_id, sprout.reference.doi AS sprout_reference_doi, sprout.reference.created_by AS sprout_reference_created_by, sprout.reference.date_created AS sprout_reference_date_created 
    FROM sprout.reference 
    WHERE sprout.reference.pubmed_id = :pubmed_id_1
    '''
    query = session.query(Reference).filter(Reference.format_name==reference_name)
        
    reference = query.first() 
    ref_id = None
    if reference is not None:
        ref_id = reference.id
    if print_query:
        print query
    return ref_id

#Used for Author page.
def get_author(author_name, print_query=False):
    '''
    get_author('Brower_SM', print_query=True)

    SELECT sprout.author.author_id AS sprout_author_author_id, sprout.author.author_name AS sprout_author_author_name, sprout.author.created_by AS sprout_author_created_by, sprout.author.date_created AS sprout_author_date_created, author_reference_1.author_reference_id AS author_reference_1_autho_1, author_reference_1.author_order AS author_reference_1_autho_2, author_reference_1.author_type AS author_reference_1_author_type, author_reference_1.author_id AS author_reference_1_author_id, author_reference_1.reference_id AS author_reference_1_refer_3 
    FROM sprout.author LEFT OUTER JOIN sprout.author_reference author_reference_1 ON sprout.author.author_id = author_reference_1.author_id 
    WHERE sprout.author.author_name = :author_name_1
    '''
    query = session.query(Author).options(joinedload('author_references')).filter(Author.format_name==author_name)
    author = query.first()
    if print_query:
        print query
    return author

#Used for Author page.
def get_author_id(author_name, print_query=False):
    query = session.query(Author).filter(Author.format_name==author_name)
    author = query.first()
    author_id = None
    if author is not None:
        author_id = author.id
    if print_query:
        print query
    return author_id

#Used for Graph Views.
def get_experiment(experiment_name, print_query=False):
    query = session.query(Experiment).filter(Experiment.format_name==experiment_name)
    experiment = query.first()
    if print_query:
        print query
    return experiment

#Used for Graph Views.
def get_strain(strain_name, print_query=False):
    query = session.query(Strain).filter(Strain.format_name==strain_name)
    strain = query.first()
    if print_query:
        print query
    return strain

#Used for Author page.
def get_assoc_reference(author_id=None, print_query=False):
    query = session.query(AuthorReference).options(joinedload('reference')).filter(AuthorReference.author_id==author_id)
    auth_refs = query.all()
    references = [auth_ref.reference for auth_ref in auth_refs]
    if print_query:
        print query
    return references

#Used for Interaction resources
def get_resources(category, bioent_id=None, print_query=False):
    if bioent_id is not None:
        query = session.query(BioentUrl).filter(BioentUrl.bioent_id==bioent_id).filter(BioentUrl.category==category)
    urls = query.all()
    if print_query:
        print query
    return urls
 
#Used for interaction_overview_table.
def get_biorels(biorel_type, bioent_id, print_query=False):
    '''
    get_biorels('INTERACTION', get_bioent_id('YFL039C'), print_query=True)
    
    SELECT sprout.bioentrel.biorel_id AS sprout_bioentrel_biorel_id, sprout.bioentrel.name AS sprout_bioentrel_name, sprout.bioentrel.bioent_id1 AS sprout_bioentrel_bioent_id1, sprout.bioentrel.bioent_id2 AS sprout_bioentrel_bioent_id2, sprout.bioentrel.biorel_type AS sprout_bioentrel_biorel_type, sprout.bioentrel.date_created AS sprout_bioentrel_date_created, sprout.bioentrel.created_by AS sprout_bioentrel_created_by, sprout.interaction.biorel_id AS sprout_interaction_biorel_id, sprout.interaction.physical_evidence_count AS sprout_interaction_physi_1, sprout.interaction.genetic_evidence_count AS sprout_interaction_genet_2, sprout.interaction.evidence_count AS sprout_interaction_evide_3, bioent_1.bioent_id AS bioent_1_bioent_id, bioent_1.name AS bioent_1_name, bioent_1.dbxref AS bioent_1_dbxref, bioent_1.bioent_type AS bioent_1_bioent_type, bioent_1.source AS bioent_1_source, bioent_1.secondary_name AS bioent_1_secondary_name, bioent_1.date_created AS bioent_1_date_created, bioent_1.created_by AS bioent_1_created_by, bioent_2.bioent_id AS bioent_2_bioent_id, bioent_2.name AS bioent_2_name, bioent_2.dbxref AS bioent_2_dbxref, bioent_2.bioent_type AS bioent_2_bioent_type, bioent_2.source AS bioent_2_source, bioent_2.secondary_name AS bioent_2_secondary_name, bioent_2.date_created AS bioent_2_date_created, bioent_2.created_by AS bioent_2_created_by 
    FROM sprout.bioentrel LEFT OUTER JOIN sprout.interaction ON sprout.interaction.biorel_id = sprout.bioentrel.biorel_id LEFT OUTER JOIN sprout.bioent bioent_1 ON sprout.bioentrel.bioent_id1 = bioent_1.bioent_id LEFT OUTER JOIN sprout.bioent bioent_2 ON sprout.bioentrel.bioent_id2 = bioent_2.bioent_id 
    WHERE sprout.bioentrel.biorel_type = :biorel_type_1 AND sprout.bioentrel.bioent_id1 = :bioent_id1_1
    
    SELECT sprout.bioentrel.biorel_id AS sprout_bioentrel_biorel_id, sprout.bioentrel.name AS sprout_bioentrel_name, sprout.bioentrel.bioent_id1 AS sprout_bioentrel_bioent_id1, sprout.bioentrel.bioent_id2 AS sprout_bioentrel_bioent_id2, sprout.bioentrel.biorel_type AS sprout_bioentrel_biorel_type, sprout.bioentrel.date_created AS sprout_bioentrel_date_created, sprout.bioentrel.created_by AS sprout_bioentrel_created_by, sprout.interaction.biorel_id AS sprout_interaction_biorel_id, sprout.interaction.physical_evidence_count AS sprout_interaction_physi_1, sprout.interaction.genetic_evidence_count AS sprout_interaction_genet_2, sprout.interaction.evidence_count AS sprout_interaction_evide_3, bioent_1.bioent_id AS bioent_1_bioent_id, bioent_1.name AS bioent_1_name, bioent_1.dbxref AS bioent_1_dbxref, bioent_1.bioent_type AS bioent_1_bioent_type, bioent_1.source AS bioent_1_source, bioent_1.secondary_name AS bioent_1_secondary_name, bioent_1.date_created AS bioent_1_date_created, bioent_1.created_by AS bioent_1_created_by, bioent_2.bioent_id AS bioent_2_bioent_id, bioent_2.name AS bioent_2_name, bioent_2.dbxref AS bioent_2_dbxref, bioent_2.bioent_type AS bioent_2_bioent_type, bioent_2.source AS bioent_2_source, bioent_2.secondary_name AS bioent_2_secondary_name, bioent_2.date_created AS bioent_2_date_created, bioent_2.created_by AS bioent_2_created_by 
    FROM sprout.bioentrel LEFT OUTER JOIN sprout.interaction ON sprout.interaction.biorel_id = sprout.bioentrel.biorel_id LEFT OUTER JOIN sprout.bioent bioent_1 ON sprout.bioentrel.bioent_id1 = bioent_1.bioent_id LEFT OUTER JOIN sprout.bioent bioent_2 ON sprout.bioentrel.bioent_id2 = bioent_2.bioent_id 
    WHERE sprout.bioentrel.biorel_type = :biorel_type_1 AND sprout.bioentrel.bioent_id2 = :bioent_id2_1
    '''
    
    query = session.query(with_polymorphic(BioentRelation, [biorel_type_to_class[biorel_type]])).filter(
                                or_(BioentRelation.source_bioent_id == bioent_id, 
                                    BioentRelation.sink_bioent_id == bioent_id)).filter(
                                BioentRelation.biorel_type==biorel_type)                                                                                    
    interactions = query.all()
    if print_query:
        print query
    return interactions

#Used for interaction graph
def get_interactions(bioent_ids, print_query=False):
    '''
    get_interactions([get_bioent_id('YFL039C')], print_query=True)
    
    SELECT sprout.bioentrel.biorel_id AS sprout_bioentrel_biorel_id, sprout.bioentrel.name AS sprout_bioentrel_name, sprout.bioentrel.bioent_id1 AS sprout_bioentrel_bioent_id1, sprout.bioentrel.bioent_id2 AS sprout_bioentrel_bioent_id2, sprout.bioentrel.biorel_type AS sprout_bioentrel_biorel_type, sprout.bioentrel.date_created AS sprout_bioentrel_date_created, sprout.bioentrel.created_by AS sprout_bioentrel_created_by, sprout.interaction.biorel_id AS sprout_interaction_biorel_id, sprout.interaction.physical_evidence_count AS sprout_interaction_physi_1, sprout.interaction.genetic_evidence_count AS sprout_interaction_genet_2, sprout.interaction.evidence_count AS sprout_interaction_evide_3 
    FROM sprout.bioentrel LEFT OUTER JOIN sprout.interaction ON sprout.interaction.biorel_id = sprout.bioentrel.biorel_id 
    WHERE sprout.bioentrel.biorel_type = :biorel_type_1 AND sprout.bioentrel.bioent_id1 IN (:bioent_id1_1)
    SELECT sprout.bioentrel.biorel_id AS sprout_bioentrel_biorel_id, sprout.bioentrel.name AS sprout_bioentrel_name, sprout.bioentrel.bioent_id1 AS sprout_bioentrel_bioent_id1, sprout.bioentrel.bioent_id2 AS sprout_bioentrel_bioent_id2, sprout.bioentrel.biorel_type AS sprout_bioentrel_biorel_type, sprout.bioentrel.date_created AS sprout_bioentrel_date_created, sprout.bioentrel.created_by AS sprout_bioentrel_created_by, sprout.interaction.biorel_id AS sprout_interaction_biorel_id, sprout.interaction.physical_evidence_count AS sprout_interaction_physi_1, sprout.interaction.genetic_evidence_count AS sprout_interaction_genet_2, sprout.interaction.evidence_count AS sprout_interaction_evide_3 
    FROM sprout.bioentrel LEFT OUTER JOIN sprout.interaction ON sprout.interaction.biorel_id = sprout.bioentrel.biorel_id 
    WHERE sprout.bioentrel.biorel_type = :biorel_type_1 AND sprout.bioentrel.bioent_id2 IN (:bioent_id2_1)
    '''
    query1 = session.query(BioentRelation).filter(BioentRelation.bioent_id.in_(bioent_ids)).filter(
                            or_(BioentMultiRelationBioent.biorel_type=='GENETIC_INTERACTION', 
                                BioentMultiRelationBioent.biorel_type=='PHYSICAL_INTERACTION'))
    biorel_ids = [x.biorel_id for x in query1.all()]
    
    def f(chunk_biorel_ids):
        new_query = session.query(BioentMultiRelation).filter(BioentMultiRelation.id.in_(chunk_biorel_ids))
        biorels = set(new_query.all())
        if print_query:
            print new_query
        return biorels
    interactions = set(retrieve_in_chunks(biorel_ids, f))
        
    if print_query:
        print query1
    return interactions

def get_biofacts(biocon_type, biocon=None, bioent=None, print_query=False):
    '''
    get_biofacts('GO', biocon=get_biocon('DNA_repair', 'GO'), print_query=True)
    
    SELECT sprout.biofact.biofact_id AS sprout_biofact_biofact_id, sprout.biofact.use_for_graph AS sprout_biofact_use_for_graph, sprout.biofact.bioent_id AS sprout_biofact_bioent_id, sprout.biofact.biocon_id AS sprout_biofact_biocon_id, sprout.biofact.biocon_type AS sprout_biofact_biocon_type, bioent_1.bioent_id AS bioent_1_bioent_id, bioent_1.name AS bioent_1_name, bioent_1.dbxref AS bioent_1_dbxref, bioent_1.bioent_type AS bioent_1_bioent_type, bioent_1.source AS bioent_1_source, bioent_1.secondary_name AS bioent_1_secondary_name, bioent_1.date_created AS bioent_1_date_created, bioent_1.created_by AS bioent_1_created_by, biocon_1.biocon_id AS biocon_1_biocon_id, biocon_1.name AS biocon_1_name, biocon_1.biocon_type AS biocon_1_biocon_type, biocon_1.description AS biocon_1_description 
    FROM sprout.biofact LEFT OUTER JOIN sprout.bioent bioent_1 ON bioent_1.bioent_id = sprout.biofact.bioent_id LEFT OUTER JOIN sprout.biocon biocon_1 ON biocon_1.biocon_id = sprout.biofact.biocon_id 
    WHERE sprout.biofact.biocon_type = :biocon_type_1 AND sprout.biofact.biocon_id = :biocon_id_1
    '''
    if biocon is None and bioent is None:
        raise Exception()
    
    query = session.query(Biofact).options(joinedload('bioentity'), joinedload('bioconcept')).filter(Biofact.biocon_type==biocon_type)
    if bioent is not None:
        query = query.filter(Biofact.bioent_id==bioent.id)
    if biocon is not None:
        query = query.filter(Biofact.biocon_id==biocon.id)
    if print_query:
        print query
    return query.all()

#Used for go_ontology and phenotype_ontology graphs.
def get_biocon_family(biocon, print_query=False):
    '''
    get_biocon_family(get_biocon('DNA_repair', 'GO'), print_query=True)
   
    SELECT sprout.biocon_ancestor.biocon_ancestor_id AS sprout_biocon_ancestor_b_1, sprout.biocon_ancestor.ancestor_biocon_id AS sprout_biocon_ancestor_a_2, sprout.biocon_ancestor.child_biocon_id AS sprout_biocon_ancestor_c_3, sprout.biocon_ancestor.generation AS sprout_biocon_ancestor_g_4, sprout.biocon_ancestor.bioconanc_type AS sprout_biocon_ancestor_b_5, anon_1.sprout_biocon_biocon_id AS anon_1_sprout_biocon_biocon_id, anon_1.sprout_biocon_name AS anon_1_sprout_biocon_name, anon_1.sprout_biocon_biocon_type AS anon_1_sprout_biocon_bio_6, anon_1.sprout_biocon_description AS anon_1_sprout_biocon_des_7, anon_1.sprout_goterm_biocon_id AS anon_1_sprout_goterm_biocon_id, anon_1.sprout_goterm_go_go_id AS anon_1_sprout_goterm_go_go_id, anon_1.sprout_goterm_go_term AS anon_1_sprout_goterm_go_term, anon_1.sprout_goterm_go_aspect AS anon_1_sprout_goterm_go_aspect, anon_1.sprout_goterm_go_definition AS anon_1_sprout_goterm_go__8, anon_1.sprout_goterm_direct_gen_a AS anon_1_sprout_goterm_dir_9 
    FROM sprout.biocon_ancestor LEFT OUTER JOIN (SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.description AS sprout_biocon_description, sprout.goterm.biocon_id AS sprout_goterm_biocon_id, sprout.goterm.go_go_id AS sprout_goterm_go_go_id, sprout.goterm.go_term AS sprout_goterm_go_term, sprout.goterm.go_aspect AS sprout_goterm_go_aspect, sprout.goterm.go_definition AS sprout_goterm_go_definition, sprout.goterm.direct_gene_count AS sprout_goterm_direct_gen_a 
    FROM sprout.biocon LEFT OUTER JOIN sprout.goterm ON sprout.goterm.biocon_id = sprout.biocon.biocon_id) anon_1 ON sprout.biocon_ancestor.ancestor_biocon_id = anon_1.sprout_biocon_biocon_id 
    WHERE sprout.biocon_ancestor.child_biocon_id = :child_biocon_id_1

    SELECT sprout.bioconrel.biocon_biocon_id AS sprout_bioconrel_biocon__1, sprout.bioconrel.parent_biocon_id AS sprout_bioconrel_parent__2, sprout.bioconrel.child_biocon_id AS sprout_bioconrel_child_b_3, sprout.bioconrel.relationship_type AS sprout_bioconrel_relatio_4, sprout.bioconrel.bioconrel_type AS sprout_bioconrel_bioconr_5, anon_1.sprout_biocon_biocon_id AS anon_1_sprout_biocon_biocon_id, anon_1.sprout_biocon_name AS anon_1_sprout_biocon_name, anon_1.sprout_biocon_biocon_type AS anon_1_sprout_biocon_bio_6, anon_1.sprout_biocon_description AS anon_1_sprout_biocon_des_7, anon_1.sprout_goterm_biocon_id AS anon_1_sprout_goterm_biocon_id, anon_1.sprout_goterm_go_go_id AS anon_1_sprout_goterm_go_go_id, anon_1.sprout_goterm_go_term AS anon_1_sprout_goterm_go_term, anon_1.sprout_goterm_go_aspect AS anon_1_sprout_goterm_go_aspect, anon_1.sprout_goterm_go_definition AS anon_1_sprout_goterm_go__8, anon_1.sprout_goterm_direct_gen_a AS anon_1_sprout_goterm_dir_9 
    FROM sprout.bioconrel LEFT OUTER JOIN (SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.description AS sprout_biocon_description, sprout.goterm.biocon_id AS sprout_goterm_biocon_id, sprout.goterm.go_go_id AS sprout_goterm_go_go_id, sprout.goterm.go_term AS sprout_goterm_go_term, sprout.goterm.go_aspect AS sprout_goterm_go_aspect, sprout.goterm.go_definition AS sprout_goterm_go_definition, sprout.goterm.direct_gene_count AS sprout_goterm_direct_gen_a 
    FROM sprout.biocon LEFT OUTER JOIN sprout.goterm ON sprout.goterm.biocon_id = sprout.biocon.biocon_id) anon_1 ON sprout.bioconrel.child_biocon_id = anon_1.sprout_biocon_biocon_id 
    WHERE sprout.bioconrel.parent_biocon_id = :parent_biocon_id_1
    '''
    biocon_class = biocon_type_to_class[biocon.biocon_type]
    family = set([biocon])
    query1 = session.query(BioconAncestor).options(joinedload(BioconAncestor.ancestor_biocon.of_type(biocon_class))).filter(BioconAncestor.child_id==biocon.id)
    biocon_ancs = query1.all()
    family.update([biocon_anc.ancestor_biocon for biocon_anc in biocon_ancs])
    
    query2 = session.query(BioconRelation).options(joinedload(BioconRelation.child_biocon.of_type(biocon_class))).filter(BioconRelation.parent_id==biocon.id)
    biocon_children = query2.all()
    family.update([biocon_child.child_biocon for biocon_child in biocon_children])
    
    child_ids = set([biocon_child.child_biocon.id for biocon_child in biocon_children])
    all_ids = set([b.id for b in family])
    
    if print_query:
        print query1
        print query2
    return {'family':family, 'child_ids':child_ids, 'all_ids':all_ids}

#Used for go_ontology and phenotype_ontology graphs.
def get_biocon_biocons(biocon_ids, print_query=False):
    '''
    get_biocon_biocons([get_biocon_id('DNA_repair', 'GO')], print_query=True)

    SELECT sprout.bioconrel.biocon_biocon_id AS sprout_bioconrel_biocon__1, sprout.bioconrel.parent_biocon_id AS sprout_bioconrel_parent__2, sprout.bioconrel.child_biocon_id AS sprout_bioconrel_child_b_3, sprout.bioconrel.relationship_type AS sprout_bioconrel_relatio_4, sprout.bioconrel.bioconrel_type AS sprout_bioconrel_bioconr_5 
    FROM sprout.bioconrel 
    WHERE sprout.bioconrel.parent_biocon_id IN (:parent_biocon_id_1)

    SELECT sprout.bioconrel.biocon_biocon_id AS sprout_bioconrel_biocon__1, sprout.bioconrel.parent_biocon_id AS sprout_bioconrel_parent__2, sprout.bioconrel.child_biocon_id AS sprout_bioconrel_child_b_3, sprout.bioconrel.relationship_type AS sprout_bioconrel_relatio_4, sprout.bioconrel.bioconrel_type AS sprout_bioconrel_bioconr_5 
    FROM sprout.bioconrel 
    WHERE sprout.bioconrel.child_biocon_id IN (:child_biocon_id_1)
    '''
    biocon_ids = set(biocon_ids)
    related_biocon_biocons = set()
    
    query1 = session.query(BioconRelation).filter(BioconRelation.parent_id.in_(biocon_ids))
    ancestor_in_list = query1.all()
    related_biocon_biocons.update([biocon_biocon for biocon_biocon in ancestor_in_list if biocon_biocon.child_id in biocon_ids])
    
    query2 = session.query(BioconRelation).filter(BioconRelation.child_id.in_(biocon_ids))
    child_in_list = query2.all()
    related_biocon_biocons.update([biocon_biocon for biocon_biocon in child_in_list if biocon_biocon.parent_id in biocon_ids])
    
    if print_query:
        print query1
        print query2
    return related_biocon_biocons

#Used for go_graph.
def get_related_biofacts(biocon_type, biocon_ids=None, bioent_ids=None, print_query=False):
    '''
    get_related_biofacts([get_biocon_id('DNA_repair', 'GO')], 'GO', print_query=True)
    
    SELECT sprout.biofact.biofact_id AS sprout_biofact_biofact_id, sprout.biofact.use_for_graph AS sprout_biofact_use_for_graph, sprout.biofact.bioent_id AS sprout_biofact_bioent_id, sprout.biofact.biocon_id AS sprout_biofact_biocon_id, sprout.biofact.biocon_type AS sprout_biofact_biocon_type, bioent_1.bioent_id AS bioent_1_bioent_id, bioent_1.name AS bioent_1_name, bioent_1.dbxref AS bioent_1_dbxref, bioent_1.bioent_type AS bioent_1_bioent_type, bioent_1.source AS bioent_1_source, bioent_1.secondary_name AS bioent_1_secondary_name, bioent_1.date_created AS bioent_1_date_created, bioent_1.created_by AS bioent_1_created_by, anon_1.sprout_biocon_biocon_id AS anon_1_sprout_biocon_biocon_id, anon_1.sprout_biocon_name AS anon_1_sprout_biocon_name, anon_1.sprout_biocon_biocon_type AS anon_1_sprout_biocon_bio_1, anon_1.sprout_biocon_description AS anon_1_sprout_biocon_des_2, anon_1.sprout_goterm_biocon_id AS anon_1_sprout_goterm_biocon_id, anon_1.sprout_goterm_go_go_id AS anon_1_sprout_goterm_go_go_id, anon_1.sprout_goterm_go_term AS anon_1_sprout_goterm_go_term, anon_1.sprout_goterm_go_aspect AS anon_1_sprout_goterm_go_aspect, anon_1.sprout_goterm_go_definition AS anon_1_sprout_goterm_go__3, anon_1.sprout_goterm_direct_gen_5 AS anon_1_sprout_goterm_dir_4 
    FROM sprout.biofact LEFT OUTER JOIN sprout.bioent bioent_1 ON bioent_1.bioent_id = sprout.biofact.bioent_id LEFT OUTER JOIN (SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.description AS sprout_biocon_description, sprout.goterm.biocon_id AS sprout_goterm_biocon_id, sprout.goterm.go_go_id AS sprout_goterm_go_go_id, sprout.goterm.go_term AS sprout_goterm_go_term, sprout.goterm.go_aspect AS sprout_goterm_go_aspect, sprout.goterm.go_definition AS sprout_goterm_go_definition, sprout.goterm.direct_gene_count AS sprout_goterm_direct_gen_5 
    FROM sprout.biocon LEFT OUTER JOIN sprout.goterm ON sprout.goterm.biocon_id = sprout.biocon.biocon_id) anon_1 ON anon_1.sprout_biocon_biocon_id = sprout.biofact.biocon_id 
    WHERE sprout.biofact.biocon_id IN (:biocon_id_1)
    '''
    biocon_class = biocon_type_to_class[biocon_type]
    query = session.query(Biofact).filter(Biofact.biocon_type==biocon_type).options(joinedload('bioentity'), joinedload(Biofact.bioconcept.of_type(biocon_class)))
    
    if biocon_ids is not None:
        query = query.filter(Biofact.biocon_id.in_(biocon_ids))
    if bioent_ids is not None:
        query = query.filter(Biofact.bioent_id.in_(bioent_ids))
    biofacts = query.all()
    if print_query:
        print query
    return biofacts

#Used for go_evidence table.
def get_go_evidence(bioent_id=None, biocon_id=None, reference_id=None, print_query=False):
    '''
    get_go_evidence(bioent_id=get_bioent_id('YFL039C'), print_query=True)

    SELECT sprout.goevidence.evidence_id AS sprout_goevidence_evidence_id, sprout.evidence.evidence_id AS sprout_evidence_evidence_id, sprout.evidence.experiment_type AS sprout_evidence_experime_1, sprout.evidence.reference_id AS sprout_evidence_reference_id, sprout.evidence.evidence_type AS sprout_evidence_evidence_type, sprout.evidence.strain_id AS sprout_evidence_strain_id, sprout.evidence.source AS sprout_evidence_source, sprout.evidence.date_created AS sprout_evidence_date_created, sprout.evidence.created_by AS sprout_evidence_created_by, sprout.goevidence.go_evidence AS sprout_goevidence_go_evidence, sprout.goevidence.annotation_type AS sprout_goevidence_annota_2, sprout.goevidence.date_last_reviewed AS sprout_goevidence_date_l_3, sprout.goevidence.qualifier AS sprout_goevidence_qualifier, sprout.goevidence.bioent_id AS sprout_goevidence_bioent_id, sprout.goevidence.biocon_id AS sprout_goevidence_biocon_id, anon_1.sprout_gene_bioent_id AS anon_1_sprout_gene_bioent_id, anon_1.sprout_bioent_bioent_id AS anon_1_sprout_bioent_bioent_id, anon_1.sprout_gene_short_description AS anon_1_sprout_gene_short_4, anon_1.sprout_bioent_name AS anon_1_sprout_bioent_name, anon_1.sprout_bioent_dbxref AS anon_1_sprout_bioent_dbxref, anon_1.sprout_bioent_bioent_type AS anon_1_sprout_bioent_bio_5, anon_1.sprout_bioent_source AS anon_1_sprout_bioent_source, anon_1.sprout_bioent_secondary_name AS anon_1_sprout_bioent_sec_6, anon_1.sprout_bioent_date_created AS anon_1_sprout_bioent_dat_7, anon_1.sprout_bioent_created_by AS anon_1_sprout_bioent_cre_8, anon_1.sprout_gene_qualifier AS anon_1_sprout_gene_qualifier, anon_1.sprout_gene_attribute AS anon_1_sprout_gene_attribute, anon_1.sprout_gene_headline AS anon_1_sprout_gene_headline, anon_1.sprout_gene_description AS anon_1_sprout_gene_description, anon_1.sprout_gene_genetic_position AS anon_1_sprout_gene_genet_9, anon_1.sprout_gene_gene_type AS anon_1_sprout_gene_gene_type, anon_2.sprout_goterm_biocon_id AS anon_2_sprout_goterm_biocon_id, anon_2.sprout_biocon_biocon_id AS anon_2_sprout_biocon_biocon_id, anon_2.sprout_biocon_name AS anon_2_sprout_biocon_name, anon_2.sprout_biocon_biocon_type AS anon_2_sprout_biocon_bio_a, anon_2.sprout_biocon_description AS anon_2_sprout_biocon_des_b, anon_2.sprout_goterm_go_go_id AS anon_2_sprout_goterm_go_go_id, anon_2.sprout_goterm_go_term AS anon_2_sprout_goterm_go_term, anon_2.sprout_goterm_go_aspect AS anon_2_sprout_goterm_go_aspect, anon_2.sprout_goterm_go_definition AS anon_2_sprout_goterm_go__c, anon_2.sprout_goterm_direct_gen_e AS anon_2_sprout_goterm_dir_d, reference_1.reference_id AS reference_1_reference_id, reference_1.citation AS reference_1_citation, reference_1.fulltext_url AS reference_1_fulltext_url, reference_1.source AS reference_1_source, reference_1.status AS reference_1_status, reference_1.pdf_status AS reference_1_pdf_status, reference_1.dbxref_id AS reference_1_dbxref_id, reference_1.year AS reference_1_year, reference_1.pubmed_id AS reference_1_pubmed_id, reference_1.date_published AS reference_1_date_published, reference_1.date_revised AS reference_1_date_revised, reference_1.issue AS reference_1_issue, reference_1.page AS reference_1_page, reference_1.volume AS reference_1_volume, reference_1.title AS reference_1_title, reference_1.journal_id AS reference_1_journal_id, reference_1.book_id AS reference_1_book_id, reference_1.doi AS reference_1_doi, reference_1.created_by AS reference_1_created_by, reference_1.date_created AS reference_1_date_created 
    FROM sprout.evidence JOIN sprout.goevidence ON sprout.goevidence.evidence_id = sprout.evidence.evidence_id LEFT OUTER JOIN (SELECT sprout.bioent.bioent_id AS sprout_bioent_bioent_id, sprout.bioent.name AS sprout_bioent_name, sprout.bioent.bioent_type AS sprout_bioent_bioent_type, sprout.bioent.dbxref AS sprout_bioent_dbxref, sprout.bioent.source AS sprout_bioent_source, sprout.bioent.secondary_name AS sprout_bioent_secondary_name, sprout.bioent.date_created AS sprout_bioent_date_created, sprout.bioent.created_by AS sprout_bioent_created_by, sprout.gene.bioent_id AS sprout_gene_bioent_id, sprout.gene.qualifier AS sprout_gene_qualifier, sprout.gene.attribute AS sprout_gene_attribute, sprout.gene.short_description AS sprout_gene_short_description, sprout.gene.headline AS sprout_gene_headline, sprout.gene.description AS sprout_gene_description, sprout.gene.genetic_position AS sprout_gene_genetic_position, sprout.gene.gene_type AS sprout_gene_gene_type 
    FROM sprout.bioent JOIN sprout.gene ON sprout.gene.bioent_id = sprout.bioent.bioent_id) anon_1 ON anon_1.sprout_gene_bioent_id = sprout.goevidence.bioent_id LEFT OUTER JOIN (SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.description AS sprout_biocon_description, sprout.goterm.biocon_id AS sprout_goterm_biocon_id, sprout.goterm.go_go_id AS sprout_goterm_go_go_id, sprout.goterm.go_term AS sprout_goterm_go_term, sprout.goterm.go_aspect AS sprout_goterm_go_aspect, sprout.goterm.go_definition AS sprout_goterm_go_definition, sprout.goterm.direct_gene_count AS sprout_goterm_direct_gen_e 
    FROM sprout.biocon JOIN sprout.goterm ON sprout.goterm.biocon_id = sprout.biocon.biocon_id) anon_2 ON anon_2.sprout_goterm_biocon_id = sprout.goevidence.biocon_id LEFT OUTER JOIN sprout.reference reference_1 ON reference_1.reference_id = sprout.evidence.reference_id 
    WHERE sprout.goevidence.bioent_id = :bioent_id_1
    '''
    query = session.query(Goevidence).options(joinedload('reference'), joinedload('bioentity'), joinedload('bioconcept'))
    if bioent_id is not None:
        query = query.filter(Goevidence.bioent_id==bioent_id)
    if biocon_id is not None:
        query = query.filter(Goevidence.biocon_id==biocon_id)
    if reference_id is not None:
        query = query.filter(Goevidence.reference_id==reference_id)
    
    evidences = query.all()
    
    if print_query:
        print query
    return evidences

#Used for phenotype_evidence table.
def get_phenotype_evidence(bioent_id=None, biocon_id=None, reference_id=None, chemical_id=None, print_query=False):
    '''
    get_phenotype_evidence(bioent_id=get_bioent_id('YFL039C'), print_query=True)

    SELECT sprout.phenoevidence.evidence_id AS sprout_phenoevidence_evi_1, sprout.evidence.evidence_id AS sprout_evidence_evidence_id, sprout.phenoevidence.mutant_allele AS sprout_phenoevidence_mut_2, sprout.evidence.experiment_type AS sprout_evidence_experime_3, sprout.evidence.reference_id AS sprout_evidence_reference_id, sprout.evidence.evidence_type AS sprout_evidence_evidence_type, sprout.evidence.strain_id AS sprout_evidence_strain_id, sprout.evidence.source AS sprout_evidence_source, sprout.evidence.date_created AS sprout_evidence_date_created, sprout.evidence.created_by AS sprout_evidence_created_by, sprout.phenoevidence.mutant_type AS sprout_phenoevidence_mut_4, sprout.phenoevidence.qualifier AS sprout_phenoevidence_qualifier, sprout.phenoevidence.reporter AS sprout_phenoevidence_reporter, sprout.phenoevidence.reporter_desc AS sprout_phenoevidence_rep_5, sprout.phenoevidence.allele_info AS sprout_phenoevidence_all_6, sprout.phenoevidence.strain_details AS sprout_phenoevidence_str_7, sprout.phenoevidence.details AS sprout_phenoevidence_details, sprout.phenoevidence.experiment_details AS sprout_phenoevidence_exp_8, sprout.phenoevidence.conditions AS sprout_phenoevidence_con_9, sprout.phenoevidence.budding_index AS sprout_phenoevidence_bud_a, sprout.phenoevidence.glutathione_excretion AS sprout_phenoevidence_glu_b, sprout.phenoevidence.z_score AS sprout_phenoevidence_z_score, sprout.phenoevidence.relative_fitness_score AS sprout_phenoevidence_rel_c, sprout.phenoevidence.chitin_level AS sprout_phenoevidence_chi_d, sprout.phenoevidence.bioent_id AS sprout_phenoevidence_bioent_id, sprout.phenoevidence.biocon_id AS sprout_phenoevidence_biocon_id, anon_1.sprout_gene_bioent_id AS anon_1_sprout_gene_bioent_id, anon_1.sprout_bioent_bioent_id AS anon_1_sprout_bioent_bioent_id, anon_1.sprout_gene_short_description AS anon_1_sprout_gene_short_e, anon_1.sprout_bioent_name AS anon_1_sprout_bioent_name, anon_1.sprout_bioent_dbxref AS anon_1_sprout_bioent_dbxref, anon_1.sprout_bioent_bioent_type AS anon_1_sprout_bioent_bio_f, anon_1.sprout_bioent_source AS anon_1_sprout_bioent_source, anon_1.sprout_bioent_secondary_name AS anon_1_sprout_bioent_sec_10, anon_1.sprout_bioent_date_created AS anon_1_sprout_bioent_dat_11, anon_1.sprout_bioent_created_by AS anon_1_sprout_bioent_cre_12, anon_1.sprout_gene_qualifier AS anon_1_sprout_gene_qualifier, anon_1.sprout_gene_attribute AS anon_1_sprout_gene_attribute, anon_1.sprout_gene_headline AS anon_1_sprout_gene_headline, anon_1.sprout_gene_description AS anon_1_sprout_gene_description, anon_1.sprout_gene_genetic_position AS anon_1_sprout_gene_genet_13, anon_1.sprout_gene_gene_type AS anon_1_sprout_gene_gene_type, anon_2.sprout_phenotype_biocon_id AS anon_2_sprout_phenotype__14, anon_2.sprout_biocon_biocon_id AS anon_2_sprout_biocon_biocon_id, anon_2.sprout_biocon_name AS anon_2_sprout_biocon_name, anon_2.sprout_biocon_biocon_type AS anon_2_sprout_biocon_bio_15, anon_2.sprout_biocon_description AS anon_2_sprout_biocon_des_16, anon_2.sprout_phenotype_observable AS anon_2_sprout_phenotype__17, anon_2.sprout_phenotype_phenoty_19 AS anon_2_sprout_phenotype__18, anon_2.sprout_phenotype_direct__1b AS anon_2_sprout_phenotype__1a, reference_1.reference_id AS reference_1_reference_id, reference_1.citation AS reference_1_citation, reference_1.fulltext_url AS reference_1_fulltext_url, reference_1.source AS reference_1_source, reference_1.status AS reference_1_status, reference_1.pdf_status AS reference_1_pdf_status, reference_1.dbxref_id AS reference_1_dbxref_id, reference_1.year AS reference_1_year, reference_1.pubmed_id AS reference_1_pubmed_id, reference_1.date_published AS reference_1_date_published, reference_1.date_revised AS reference_1_date_revised, reference_1.issue AS reference_1_issue, reference_1.page AS reference_1_page, reference_1.volume AS reference_1_volume, reference_1.title AS reference_1_title, reference_1.journal_id AS reference_1_journal_id, reference_1.book_id AS reference_1_book_id, reference_1.doi AS reference_1_doi, reference_1.created_by AS reference_1_created_by, reference_1.date_created AS reference_1_date_created 
    FROM sprout.evidence JOIN sprout.phenoevidence ON sprout.phenoevidence.evidence_id = sprout.evidence.evidence_id LEFT OUTER JOIN (SELECT sprout.bioent.bioent_id AS sprout_bioent_bioent_id, sprout.bioent.name AS sprout_bioent_name, sprout.bioent.bioent_type AS sprout_bioent_bioent_type, sprout.bioent.dbxref AS sprout_bioent_dbxref, sprout.bioent.source AS sprout_bioent_source, sprout.bioent.secondary_name AS sprout_bioent_secondary_name, sprout.bioent.date_created AS sprout_bioent_date_created, sprout.bioent.created_by AS sprout_bioent_created_by, sprout.gene.bioent_id AS sprout_gene_bioent_id, sprout.gene.qualifier AS sprout_gene_qualifier, sprout.gene.attribute AS sprout_gene_attribute, sprout.gene.short_description AS sprout_gene_short_description, sprout.gene.headline AS sprout_gene_headline, sprout.gene.description AS sprout_gene_description, sprout.gene.genetic_position AS sprout_gene_genetic_position, sprout.gene.gene_type AS sprout_gene_gene_type 
    FROM sprout.bioent JOIN sprout.gene ON sprout.gene.bioent_id = sprout.bioent.bioent_id) anon_1 ON anon_1.sprout_gene_bioent_id = sprout.phenoevidence.bioent_id LEFT OUTER JOIN (SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.description AS sprout_biocon_description, sprout.phenotype.biocon_id AS sprout_phenotype_biocon_id, sprout.phenotype.observable AS sprout_phenotype_observable, sprout.phenotype.phenotype_type AS sprout_phenotype_phenoty_19, sprout.phenotype.direct_gene_count AS sprout_phenotype_direct__1b 
    FROM sprout.biocon JOIN sprout.phenotype ON sprout.phenotype.biocon_id = sprout.biocon.biocon_id) anon_2 ON anon_2.sprout_phenotype_biocon_id = sprout.phenoevidence.biocon_id LEFT OUTER JOIN sprout.reference reference_1 ON reference_1.reference_id = sprout.evidence.reference_id 
    WHERE sprout.phenoevidence.bioent_id = :bioent_id_1
    '''
    query = session.query(Phenoevidence).options(joinedload('reference'), joinedload('bioentity'), joinedload('bioconcept'))
    phenoevidences = None
    if chemical_id is not None:
        phenoevidence_ids = [x.evidence_id for x in session.query(EvidenceChemical).filter(EvidenceChemical.chemical_id==chemical_id).all()]
        phenoevidences = set()
        def f(chunk_phenoevidence_ids):
            new_query = query.filter(Phenoevidence.id.in_(chunk_phenoevidence_ids))
            phenoevidences.update(new_query.all())
            if print_query:
                print new_query
            return phenoevidences
        phenoevidences = set(retrieve_in_chunks(phenoevidence_ids, f))
    if bioent_id is not None:
        query = query.filter(Phenoevidence.bioent_id==bioent_id)
        new_phenoevidences = set(query.all())
        if phenoevidences is None:
            phenoevidences = new_phenoevidences
        else:
            phenoevidences = phenoevidences.intersection(new_phenoevidences)
    if biocon_id is not None:
        query = query.filter(Phenoevidence.biocon_id==biocon_id)
        new_phenoevidences = set(query.all())
        if phenoevidences is None:
            phenoevidences = new_phenoevidences
        else:
            phenoevidences = phenoevidences.intersection(new_phenoevidences)
    if reference_id is not None:
        query = query.filter(Phenoevidence.reference_id==reference_id)
        new_phenoevidences = set(query.all())
        if phenoevidences is None:
            phenoevidences = new_phenoevidences
        else:
            phenoevidences = phenoevidences.intersection(new_phenoevidences)
        
    if print_query:
        print query
    return phenoevidences

#Used for interaction_overview and interaction_evidence tables.
def get_genetic_interaction_evidence(bioent_id=None, reference_id=None, print_query=False):
    '''
    get_interaction_evidence(bioent_id=get_bioent_id('YFL039C'), print_query=True)
    
    SELECT sprout.interevidence.evidence_id AS sprout_interevidence_evi_1, sprout.evidence.evidence_id AS sprout_evidence_evidence_id, sprout.evidence.experiment_type AS sprout_evidence_experime_2, sprout.evidence.reference_id AS sprout_evidence_reference_id, sprout.evidence.evidence_type AS sprout_evidence_evidence_type, sprout.evidence.strain_id AS sprout_evidence_strain_id, sprout.evidence.source AS sprout_evidence_source, sprout.evidence.date_created AS sprout_evidence_date_created, sprout.evidence.created_by AS sprout_evidence_created_by, sprout.interevidence.observable AS sprout_interevidence_obs_3, sprout.interevidence.qualifier AS sprout_interevidence_qualifier, sprout.interevidence.note AS sprout_interevidence_note, sprout.interevidence.annotation_type AS sprout_interevidence_ann_4, sprout.interevidence.modification AS sprout_interevidence_mod_5, sprout.interevidence.direction AS sprout_interevidence_direction, sprout.interevidence.interaction_type AS sprout_interevidence_int_6, sprout.interevidence.biorel_id AS sprout_interevidence_biorel_id, reference_1.reference_id AS reference_1_reference_id, reference_1.citation AS reference_1_citation, reference_1.fulltext_url AS reference_1_fulltext_url, reference_1.source AS reference_1_source, reference_1.status AS reference_1_status, reference_1.pdf_status AS reference_1_pdf_status, reference_1.dbxref_id AS reference_1_dbxref_id, reference_1.year AS reference_1_year, reference_1.pubmed_id AS reference_1_pubmed_id, reference_1.date_published AS reference_1_date_published, reference_1.date_revised AS reference_1_date_revised, reference_1.issue AS reference_1_issue, reference_1.page AS reference_1_page, reference_1.volume AS reference_1_volume, reference_1.title AS reference_1_title, reference_1.journal_id AS reference_1_journal_id, reference_1.book_id AS reference_1_book_id, reference_1.doi AS reference_1_doi, reference_1.created_by AS reference_1_created_by, reference_1.date_created AS reference_1_date_created 
    FROM sprout.evidence JOIN sprout.interevidence ON sprout.interevidence.evidence_id = sprout.evidence.evidence_id LEFT OUTER JOIN sprout.reference reference_1 ON reference_1.reference_id = sprout.evidence.reference_id 
    WHERE sprout.interevidence.biorel_id IN (:biorel_id_1, :biorel_id_2, :biorel_id_3, :biorel_id_4, :biorel_id_5, :biorel_id_6, :biorel_id_7, :biorel_id_8, :biorel_id_9, :biorel_id_10, :biorel_id_11, :biorel_id_12, :biorel_id_13, :biorel_id_14, :biorel_id_15, :biorel_id_16, :biorel_id_17, :biorel_id_18, :biorel_id_19, :biorel_id_20, :biorel_id_21, :biorel_id_22, :biorel_id_23, :biorel_id_24, :biorel_id_25, :biorel_id_26, :biorel_id_27, :biorel_id_28, :biorel_id_29, :biorel_id_30, :biorel_id_31, :biorel_id_32, :biorel_id_33, :biorel_id_34, :biorel_id_35, :biorel_id_36, :biorel_id_37, :biorel_id_38, :biorel_id_39, :biorel_id_40, :biorel_id_41, :biorel_id_42, :biorel_id_43, :biorel_id_44, :biorel_id_45, :biorel_id_46, :biorel_id_47, :biorel_id_48, :biorel_id_49, :biorel_id_50, :biorel_id_51, :biorel_id_52, :biorel_id_53, :biorel_id_54, :biorel_id_55, :biorel_id_56, :biorel_id_57, :biorel_id_58, :biorel_id_59, :biorel_id_60, :biorel_id_61, :biorel_id_62, :biorel_id_63, :biorel_id_64, :biorel_id_65, :biorel_id_66, :biorel_id_67, :biorel_id_68, :biorel_id_69, :biorel_id_70, :biorel_id_71, :biorel_id_72, :biorel_id_73, :biorel_id_74, :biorel_id_75, :biorel_id_76, :biorel_id_77, :biorel_id_78, :biorel_id_79, :biorel_id_80, :biorel_id_81, :biorel_id_82, :biorel_id_83, :biorel_id_84, :biorel_id_85, :biorel_id_86, :biorel_id_87, :biorel_id_88, :biorel_id_89, :biorel_id_90, :biorel_id_91, :biorel_id_92, :biorel_id_93, :biorel_id_94, :biorel_id_95, :biorel_id_96, :biorel_id_97, :biorel_id_98, :biorel_id_99, :biorel_id_100, :biorel_id_101, :biorel_id_102, :biorel_id_103, :biorel_id_104, :biorel_id_105, :biorel_id_106, :biorel_id_107, :biorel_id_108, :biorel_id_109, :biorel_id_110, :biorel_id_111, :biorel_id_112, :biorel_id_113, :biorel_id_114, :biorel_id_115, :biorel_id_116, :biorel_id_117, :biorel_id_118, :biorel_id_119, :biorel_id_120, :biorel_id_121, :biorel_id_122, :biorel_id_123, :biorel_id_124, :biorel_id_125, :biorel_id_126, :biorel_id_127, :biorel_id_128, :biorel_id_129, :biorel_id_130, :biorel_id_131, :biorel_id_132, :biorel_id_133, :biorel_id_134, :biorel_id_135, :biorel_id_136, :biorel_id_137, :biorel_id_138, :biorel_id_139, :biorel_id_140, :biorel_id_141, :biorel_id_142, :biorel_id_143, :biorel_id_144, :biorel_id_145, :biorel_id_146, :biorel_id_147, :biorel_id_148, :biorel_id_149, :biorel_id_150, :biorel_id_151, :biorel_id_152, :biorel_id_153, :biorel_id_154, :biorel_id_155, :biorel_id_156, :biorel_id_157, :biorel_id_158, :biorel_id_159, :biorel_id_160, :biorel_id_161, :biorel_id_162, :biorel_id_163, :biorel_id_164, :biorel_id_165, :biorel_id_166, :biorel_id_167, :biorel_id_168, :biorel_id_169, :biorel_id_170, :biorel_id_171, :biorel_id_172, :biorel_id_173, :biorel_id_174, :biorel_id_175, :biorel_id_176, :biorel_id_177, :biorel_id_178, :biorel_id_179, :biorel_id_180, :biorel_id_181, :biorel_id_182, :biorel_id_183, :biorel_id_184, :biorel_id_185, :biorel_id_186, :biorel_id_187, :biorel_id_188, :biorel_id_189, :biorel_id_190, :biorel_id_191, :biorel_id_192, :biorel_id_193, :biorel_id_194, :biorel_id_195, :biorel_id_196, :biorel_id_197, :biorel_id_198, :biorel_id_199, :biorel_id_200, :biorel_id_201, :biorel_id_202, :biorel_id_203, :biorel_id_204, :biorel_id_205, :biorel_id_206, :biorel_id_207, :biorel_id_208, :biorel_id_209, :biorel_id_210, :biorel_id_211, :biorel_id_212, :biorel_id_213, :biorel_id_214, :biorel_id_215, :biorel_id_216, :biorel_id_217, :biorel_id_218, :biorel_id_219, :biorel_id_220, :biorel_id_221, :biorel_id_222, :biorel_id_223, :biorel_id_224, :biorel_id_225, :biorel_id_226, :biorel_id_227, :biorel_id_228, :biorel_id_229, :biorel_id_230, :biorel_id_231, :biorel_id_232, :biorel_id_233, :biorel_id_234, :biorel_id_235, :biorel_id_236, :biorel_id_237, :biorel_id_238, :biorel_id_239, :biorel_id_240, :biorel_id_241, :biorel_id_242, :biorel_id_243, :biorel_id_244, :biorel_id_245, :biorel_id_246, :biorel_id_247, :biorel_id_248, :biorel_id_249, :biorel_id_250, :biorel_id_251, :biorel_id_252, :biorel_id_253, :biorel_id_254, :biorel_id_255, :biorel_id_256, :biorel_id_257, :biorel_id_258, :biorel_id_259, :biorel_id_260, :biorel_id_261, :biorel_id_262, :biorel_id_263, :biorel_id_264, :biorel_id_265, :biorel_id_266, :biorel_id_267, :biorel_id_268, :biorel_id_269, :biorel_id_270, :biorel_id_271, :biorel_id_272, :biorel_id_273, :biorel_id_274, :biorel_id_275, :biorel_id_276, :biorel_id_277, :biorel_id_278, :biorel_id_279, :biorel_id_280, :biorel_id_281, :biorel_id_282, :biorel_id_283, :biorel_id_284, :biorel_id_285, :biorel_id_286, :biorel_id_287, :biorel_id_288, :biorel_id_289, :biorel_id_290, :biorel_id_291, :biorel_id_292, :biorel_id_293, :biorel_id_294, :biorel_id_295, :biorel_id_296, :biorel_id_297, :biorel_id_298, :biorel_id_299, :biorel_id_300, :biorel_id_301, :biorel_id_302, :biorel_id_303, :biorel_id_304, :biorel_id_305, :biorel_id_306, :biorel_id_307, :biorel_id_308, :biorel_id_309, :biorel_id_310, :biorel_id_311, :biorel_id_312, :biorel_id_313, :biorel_id_314, :biorel_id_315, :biorel_id_316, :biorel_id_317, :biorel_id_318, :biorel_id_319, :biorel_id_320, :biorel_id_321, :biorel_id_322, :biorel_id_323, :biorel_id_324, :biorel_id_325, :biorel_id_326, :biorel_id_327, :biorel_id_328, :biorel_id_329, :biorel_id_330, :biorel_id_331, :biorel_id_332, :biorel_id_333, :biorel_id_334, :biorel_id_335, :biorel_id_336, :biorel_id_337, :biorel_id_338, :biorel_id_339, :biorel_id_340, :biorel_id_341, :biorel_id_342, :biorel_id_343, :biorel_id_344, :biorel_id_345, :biorel_id_346, :biorel_id_347, :biorel_id_348, :biorel_id_349, :biorel_id_350, :biorel_id_351, :biorel_id_352, :biorel_id_353, :biorel_id_354, :biorel_id_355, :biorel_id_356, :biorel_id_357, :biorel_id_358, :biorel_id_359, :biorel_id_360, :biorel_id_361, :biorel_id_362, :biorel_id_363, :biorel_id_364, :biorel_id_365, :biorel_id_366, :biorel_id_367, :biorel_id_368, :biorel_id_369, :biorel_id_370, :biorel_id_371, :biorel_id_372, :biorel_id_373, :biorel_id_374, :biorel_id_375, :biorel_id_376, :biorel_id_377, :biorel_id_378, :biorel_id_379, :biorel_id_380, :biorel_id_381, :biorel_id_382, :biorel_id_383, :biorel_id_384, :biorel_id_385, :biorel_id_386, :biorel_id_387, :biorel_id_388, :biorel_id_389, :biorel_id_390, :biorel_id_391, :biorel_id_392, :biorel_id_393, :biorel_id_394, :biorel_id_395, :biorel_id_396, :biorel_id_397, :biorel_id_398, :biorel_id_399, :biorel_id_400, :biorel_id_401, :biorel_id_402, :biorel_id_403, :biorel_id_404, :biorel_id_405, :biorel_id_406, :biorel_id_407, :biorel_id_408, :biorel_id_409, :biorel_id_410, :biorel_id_411, :biorel_id_412, :biorel_id_413, :biorel_id_414, :biorel_id_415, :biorel_id_416, :biorel_id_417, :biorel_id_418, :biorel_id_419, :biorel_id_420, :biorel_id_421, :biorel_id_422, :biorel_id_423, :biorel_id_424, :biorel_id_425, :biorel_id_426, :biorel_id_427, :biorel_id_428, :biorel_id_429, :biorel_id_430, :biorel_id_431, :biorel_id_432, :biorel_id_433, :biorel_id_434, :biorel_id_435, :biorel_id_436, :biorel_id_437, :biorel_id_438, :biorel_id_439, :biorel_id_440, :biorel_id_441, :biorel_id_442, :biorel_id_443, :biorel_id_444, :biorel_id_445, :biorel_id_446, :biorel_id_447, :biorel_id_448, :biorel_id_449, :biorel_id_450, :biorel_id_451, :biorel_id_452, :biorel_id_453, :biorel_id_454, :biorel_id_455, :biorel_id_456, :biorel_id_457, :biorel_id_458, :biorel_id_459, :biorel_id_460, :biorel_id_461, :biorel_id_462, :biorel_id_463, :biorel_id_464, :biorel_id_465, :biorel_id_466, :biorel_id_467, :biorel_id_468, :biorel_id_469, :biorel_id_470, :biorel_id_471, :biorel_id_472, :biorel_id_473, :biorel_id_474, :biorel_id_475, :biorel_id_476, :biorel_id_477, :biorel_id_478, :biorel_id_479, :biorel_id_480, :biorel_id_481, :biorel_id_482, :biorel_id_483, :biorel_id_484, :biorel_id_485, :biorel_id_486, :biorel_id_487, :biorel_id_488, :biorel_id_489, :biorel_id_490, :biorel_id_491, :biorel_id_492, :biorel_id_493, :biorel_id_494, :biorel_id_495, :biorel_id_496, :biorel_id_497, :biorel_id_498, :biorel_id_499, :biorel_id_500)
    '''
    start_time = datetime.datetime.now()
    print start_time
    query = session.query(GeneticInterevidence)
    if bioent_id is not None:
        query = query.filter(or_(GeneticInterevidence.bioent1_id == bioent_id, GeneticInterevidence.bioent2_id == bioent_id))
    if reference_id is not None:
        query = query.filter(GeneticInterevidence.reference_id==reference_id)
    
    interevidences = query.all()
    if print_query:
        print query
    print datetime.datetime.now() - start_time
    return interevidences

#Used for interaction_overview and interaction_evidence tables.
def get_physical_interaction_evidence(bioent_id=None, biorel_id=None, reference_id=None, print_query=False):
    '''
    get_interaction_evidence(bioent_id=get_bioent_id('YFL039C'), print_query=True)
    
    SELECT sprout.interevidence.evidence_id AS sprout_interevidence_evi_1, sprout.evidence.evidence_id AS sprout_evidence_evidence_id, sprout.evidence.experiment_type AS sprout_evidence_experime_2, sprout.evidence.reference_id AS sprout_evidence_reference_id, sprout.evidence.evidence_type AS sprout_evidence_evidence_type, sprout.evidence.strain_id AS sprout_evidence_strain_id, sprout.evidence.source AS sprout_evidence_source, sprout.evidence.date_created AS sprout_evidence_date_created, sprout.evidence.created_by AS sprout_evidence_created_by, sprout.interevidence.observable AS sprout_interevidence_obs_3, sprout.interevidence.qualifier AS sprout_interevidence_qualifier, sprout.interevidence.note AS sprout_interevidence_note, sprout.interevidence.annotation_type AS sprout_interevidence_ann_4, sprout.interevidence.modification AS sprout_interevidence_mod_5, sprout.interevidence.direction AS sprout_interevidence_direction, sprout.interevidence.interaction_type AS sprout_interevidence_int_6, sprout.interevidence.biorel_id AS sprout_interevidence_biorel_id, reference_1.reference_id AS reference_1_reference_id, reference_1.citation AS reference_1_citation, reference_1.fulltext_url AS reference_1_fulltext_url, reference_1.source AS reference_1_source, reference_1.status AS reference_1_status, reference_1.pdf_status AS reference_1_pdf_status, reference_1.dbxref_id AS reference_1_dbxref_id, reference_1.year AS reference_1_year, reference_1.pubmed_id AS reference_1_pubmed_id, reference_1.date_published AS reference_1_date_published, reference_1.date_revised AS reference_1_date_revised, reference_1.issue AS reference_1_issue, reference_1.page AS reference_1_page, reference_1.volume AS reference_1_volume, reference_1.title AS reference_1_title, reference_1.journal_id AS reference_1_journal_id, reference_1.book_id AS reference_1_book_id, reference_1.doi AS reference_1_doi, reference_1.created_by AS reference_1_created_by, reference_1.date_created AS reference_1_date_created 
    FROM sprout.evidence JOIN sprout.interevidence ON sprout.interevidence.evidence_id = sprout.evidence.evidence_id LEFT OUTER JOIN sprout.reference reference_1 ON reference_1.reference_id = sprout.evidence.reference_id 
    WHERE sprout.interevidence.biorel_id IN (:biorel_id_1, :biorel_id_2, :biorel_id_3, :biorel_id_4, :biorel_id_5, :biorel_id_6, :biorel_id_7, :biorel_id_8, :biorel_id_9, :biorel_id_10, :biorel_id_11, :biorel_id_12, :biorel_id_13, :biorel_id_14, :biorel_id_15, :biorel_id_16, :biorel_id_17, :biorel_id_18, :biorel_id_19, :biorel_id_20, :biorel_id_21, :biorel_id_22, :biorel_id_23, :biorel_id_24, :biorel_id_25, :biorel_id_26, :biorel_id_27, :biorel_id_28, :biorel_id_29, :biorel_id_30, :biorel_id_31, :biorel_id_32, :biorel_id_33, :biorel_id_34, :biorel_id_35, :biorel_id_36, :biorel_id_37, :biorel_id_38, :biorel_id_39, :biorel_id_40, :biorel_id_41, :biorel_id_42, :biorel_id_43, :biorel_id_44, :biorel_id_45, :biorel_id_46, :biorel_id_47, :biorel_id_48, :biorel_id_49, :biorel_id_50, :biorel_id_51, :biorel_id_52, :biorel_id_53, :biorel_id_54, :biorel_id_55, :biorel_id_56, :biorel_id_57, :biorel_id_58, :biorel_id_59, :biorel_id_60, :biorel_id_61, :biorel_id_62, :biorel_id_63, :biorel_id_64, :biorel_id_65, :biorel_id_66, :biorel_id_67, :biorel_id_68, :biorel_id_69, :biorel_id_70, :biorel_id_71, :biorel_id_72, :biorel_id_73, :biorel_id_74, :biorel_id_75, :biorel_id_76, :biorel_id_77, :biorel_id_78, :biorel_id_79, :biorel_id_80, :biorel_id_81, :biorel_id_82, :biorel_id_83, :biorel_id_84, :biorel_id_85, :biorel_id_86, :biorel_id_87, :biorel_id_88, :biorel_id_89, :biorel_id_90, :biorel_id_91, :biorel_id_92, :biorel_id_93, :biorel_id_94, :biorel_id_95, :biorel_id_96, :biorel_id_97, :biorel_id_98, :biorel_id_99, :biorel_id_100, :biorel_id_101, :biorel_id_102, :biorel_id_103, :biorel_id_104, :biorel_id_105, :biorel_id_106, :biorel_id_107, :biorel_id_108, :biorel_id_109, :biorel_id_110, :biorel_id_111, :biorel_id_112, :biorel_id_113, :biorel_id_114, :biorel_id_115, :biorel_id_116, :biorel_id_117, :biorel_id_118, :biorel_id_119, :biorel_id_120, :biorel_id_121, :biorel_id_122, :biorel_id_123, :biorel_id_124, :biorel_id_125, :biorel_id_126, :biorel_id_127, :biorel_id_128, :biorel_id_129, :biorel_id_130, :biorel_id_131, :biorel_id_132, :biorel_id_133, :biorel_id_134, :biorel_id_135, :biorel_id_136, :biorel_id_137, :biorel_id_138, :biorel_id_139, :biorel_id_140, :biorel_id_141, :biorel_id_142, :biorel_id_143, :biorel_id_144, :biorel_id_145, :biorel_id_146, :biorel_id_147, :biorel_id_148, :biorel_id_149, :biorel_id_150, :biorel_id_151, :biorel_id_152, :biorel_id_153, :biorel_id_154, :biorel_id_155, :biorel_id_156, :biorel_id_157, :biorel_id_158, :biorel_id_159, :biorel_id_160, :biorel_id_161, :biorel_id_162, :biorel_id_163, :biorel_id_164, :biorel_id_165, :biorel_id_166, :biorel_id_167, :biorel_id_168, :biorel_id_169, :biorel_id_170, :biorel_id_171, :biorel_id_172, :biorel_id_173, :biorel_id_174, :biorel_id_175, :biorel_id_176, :biorel_id_177, :biorel_id_178, :biorel_id_179, :biorel_id_180, :biorel_id_181, :biorel_id_182, :biorel_id_183, :biorel_id_184, :biorel_id_185, :biorel_id_186, :biorel_id_187, :biorel_id_188, :biorel_id_189, :biorel_id_190, :biorel_id_191, :biorel_id_192, :biorel_id_193, :biorel_id_194, :biorel_id_195, :biorel_id_196, :biorel_id_197, :biorel_id_198, :biorel_id_199, :biorel_id_200, :biorel_id_201, :biorel_id_202, :biorel_id_203, :biorel_id_204, :biorel_id_205, :biorel_id_206, :biorel_id_207, :biorel_id_208, :biorel_id_209, :biorel_id_210, :biorel_id_211, :biorel_id_212, :biorel_id_213, :biorel_id_214, :biorel_id_215, :biorel_id_216, :biorel_id_217, :biorel_id_218, :biorel_id_219, :biorel_id_220, :biorel_id_221, :biorel_id_222, :biorel_id_223, :biorel_id_224, :biorel_id_225, :biorel_id_226, :biorel_id_227, :biorel_id_228, :biorel_id_229, :biorel_id_230, :biorel_id_231, :biorel_id_232, :biorel_id_233, :biorel_id_234, :biorel_id_235, :biorel_id_236, :biorel_id_237, :biorel_id_238, :biorel_id_239, :biorel_id_240, :biorel_id_241, :biorel_id_242, :biorel_id_243, :biorel_id_244, :biorel_id_245, :biorel_id_246, :biorel_id_247, :biorel_id_248, :biorel_id_249, :biorel_id_250, :biorel_id_251, :biorel_id_252, :biorel_id_253, :biorel_id_254, :biorel_id_255, :biorel_id_256, :biorel_id_257, :biorel_id_258, :biorel_id_259, :biorel_id_260, :biorel_id_261, :biorel_id_262, :biorel_id_263, :biorel_id_264, :biorel_id_265, :biorel_id_266, :biorel_id_267, :biorel_id_268, :biorel_id_269, :biorel_id_270, :biorel_id_271, :biorel_id_272, :biorel_id_273, :biorel_id_274, :biorel_id_275, :biorel_id_276, :biorel_id_277, :biorel_id_278, :biorel_id_279, :biorel_id_280, :biorel_id_281, :biorel_id_282, :biorel_id_283, :biorel_id_284, :biorel_id_285, :biorel_id_286, :biorel_id_287, :biorel_id_288, :biorel_id_289, :biorel_id_290, :biorel_id_291, :biorel_id_292, :biorel_id_293, :biorel_id_294, :biorel_id_295, :biorel_id_296, :biorel_id_297, :biorel_id_298, :biorel_id_299, :biorel_id_300, :biorel_id_301, :biorel_id_302, :biorel_id_303, :biorel_id_304, :biorel_id_305, :biorel_id_306, :biorel_id_307, :biorel_id_308, :biorel_id_309, :biorel_id_310, :biorel_id_311, :biorel_id_312, :biorel_id_313, :biorel_id_314, :biorel_id_315, :biorel_id_316, :biorel_id_317, :biorel_id_318, :biorel_id_319, :biorel_id_320, :biorel_id_321, :biorel_id_322, :biorel_id_323, :biorel_id_324, :biorel_id_325, :biorel_id_326, :biorel_id_327, :biorel_id_328, :biorel_id_329, :biorel_id_330, :biorel_id_331, :biorel_id_332, :biorel_id_333, :biorel_id_334, :biorel_id_335, :biorel_id_336, :biorel_id_337, :biorel_id_338, :biorel_id_339, :biorel_id_340, :biorel_id_341, :biorel_id_342, :biorel_id_343, :biorel_id_344, :biorel_id_345, :biorel_id_346, :biorel_id_347, :biorel_id_348, :biorel_id_349, :biorel_id_350, :biorel_id_351, :biorel_id_352, :biorel_id_353, :biorel_id_354, :biorel_id_355, :biorel_id_356, :biorel_id_357, :biorel_id_358, :biorel_id_359, :biorel_id_360, :biorel_id_361, :biorel_id_362, :biorel_id_363, :biorel_id_364, :biorel_id_365, :biorel_id_366, :biorel_id_367, :biorel_id_368, :biorel_id_369, :biorel_id_370, :biorel_id_371, :biorel_id_372, :biorel_id_373, :biorel_id_374, :biorel_id_375, :biorel_id_376, :biorel_id_377, :biorel_id_378, :biorel_id_379, :biorel_id_380, :biorel_id_381, :biorel_id_382, :biorel_id_383, :biorel_id_384, :biorel_id_385, :biorel_id_386, :biorel_id_387, :biorel_id_388, :biorel_id_389, :biorel_id_390, :biorel_id_391, :biorel_id_392, :biorel_id_393, :biorel_id_394, :biorel_id_395, :biorel_id_396, :biorel_id_397, :biorel_id_398, :biorel_id_399, :biorel_id_400, :biorel_id_401, :biorel_id_402, :biorel_id_403, :biorel_id_404, :biorel_id_405, :biorel_id_406, :biorel_id_407, :biorel_id_408, :biorel_id_409, :biorel_id_410, :biorel_id_411, :biorel_id_412, :biorel_id_413, :biorel_id_414, :biorel_id_415, :biorel_id_416, :biorel_id_417, :biorel_id_418, :biorel_id_419, :biorel_id_420, :biorel_id_421, :biorel_id_422, :biorel_id_423, :biorel_id_424, :biorel_id_425, :biorel_id_426, :biorel_id_427, :biorel_id_428, :biorel_id_429, :biorel_id_430, :biorel_id_431, :biorel_id_432, :biorel_id_433, :biorel_id_434, :biorel_id_435, :biorel_id_436, :biorel_id_437, :biorel_id_438, :biorel_id_439, :biorel_id_440, :biorel_id_441, :biorel_id_442, :biorel_id_443, :biorel_id_444, :biorel_id_445, :biorel_id_446, :biorel_id_447, :biorel_id_448, :biorel_id_449, :biorel_id_450, :biorel_id_451, :biorel_id_452, :biorel_id_453, :biorel_id_454, :biorel_id_455, :biorel_id_456, :biorel_id_457, :biorel_id_458, :biorel_id_459, :biorel_id_460, :biorel_id_461, :biorel_id_462, :biorel_id_463, :biorel_id_464, :biorel_id_465, :biorel_id_466, :biorel_id_467, :biorel_id_468, :biorel_id_469, :biorel_id_470, :biorel_id_471, :biorel_id_472, :biorel_id_473, :biorel_id_474, :biorel_id_475, :biorel_id_476, :biorel_id_477, :biorel_id_478, :biorel_id_479, :biorel_id_480, :biorel_id_481, :biorel_id_482, :biorel_id_483, :biorel_id_484, :biorel_id_485, :biorel_id_486, :biorel_id_487, :biorel_id_488, :biorel_id_489, :biorel_id_490, :biorel_id_491, :biorel_id_492, :biorel_id_493, :biorel_id_494, :biorel_id_495, :biorel_id_496, :biorel_id_497, :biorel_id_498, :biorel_id_499, :biorel_id_500)
    '''
    query = session.query(PhysicalInterevidence)
    if bioent_id is not None:
        query = query.filter(or_(PhysicalInterevidence.bioent1_id == bioent_id, PhysicalInterevidence.bioent2_id == bioent_id))
    if reference_id is not None:
        query = query.filter(PhysicalInterevidence.reference_id==reference_id)
    
    interevidences = query.all()
    if print_query:
        print_query
    return interevidences

#Used for bioent_evidence table.
def get_bioent_evidence(bioent_id=None, reference_id=None, print_query=False):
    query = session.query(Bioentevidence).options(joinedload('reference'), joinedload('bioentity'))
    if bioent_id is not None:
        query = query.filter(Bioentevidence.bioent_id==bioent_id)
    if reference_id is not None:
        query = query.filter(Phenoevidence.reference_id==reference_id)
    
    evidences = query.all()
    
    if print_query:
        print query
    return evidences

def get_sequences(bioent, print_query=False):
    '''
    get_sequences(get_bioent('YFL039C'), print_query=True)

    SELECT sprout.seq.seq_id AS sprout_seq_seq_id, sprout.seq.bioent_id AS sprout_seq_bioent_id, sprout.seq.seq_version AS sprout_seq_seq_version, sprout.seq.coord_version AS sprout_seq_coord_version, sprout.seq.min_coord AS sprout_seq_min_coord, sprout.seq.max_coord AS sprout_seq_max_coord, sprout.seq.strand AS sprout_seq_strand, sprout.seq.is_current AS sprout_seq_is_current, sprout.seq.length AS sprout_seq_length, sprout.seq.ftp_file AS sprout_seq_ftp_file, sprout.seq.residues AS sprout_seq_residues, sprout.seq.seq_type AS sprout_seq_seq_type, sprout.seq.source AS sprout_seq_source, sprout.seq.rootseq_id AS sprout_seq_rootseq_id, sprout.seq.strain_id AS sprout_seq_strain_id, sprout.seq.date_created AS sprout_seq_date_created, sprout.seq.created_by AS sprout_seq_created_by, seqtag_1.seqtag_id AS seqtag_1_seqtag_id, seqtag_1.dbxref AS seqtag_1_dbxref, seqtag_1.seq_id AS seqtag_1_seq_id, seqtag_1.name AS seqtag_1_name, seqtag_1.seqtag_type AS seqtag_1_seqtag_type, seqtag_1.source AS seqtag_1_source, seqtag_1.secondary_name AS seqtag_1_secondary_name, seqtag_1.relative_coord AS seqtag_1_relative_coord, seqtag_1.chrom_coord AS seqtag_1_chrom_coord, seqtag_1.length AS seqtag_1_length, seqtag_1.orf_classification AS seqtag_1_orf_classification, seqtag_1.score AS seqtag_1_score, seqtag_1.strand AS seqtag_1_strand, seqtag_1.frame AS seqtag_1_frame, seqtag_1.date_created AS seqtag_1_date_created, seqtag_1.created_by AS seqtag_1_created_by 
    FROM sprout.seq LEFT OUTER JOIN sprout.seqtag seqtag_1 ON sprout.seq.seq_id = seqtag_1.seq_id 
    WHERE sprout.seq.bioent_id IN (:bioent_id_1, :bioent_id_2, :bioent_id_3)
    '''
    id_to_type = {}
    if bioent.bioent_type == 'GENE':
        id_to_type[bioent.id] = 'GENE'
        for transcript in bioent.transcripts:
            id_to_type[transcript.id] = 'TRANSCRIPT'
            id_to_type.update([(protein_id, 'PROTEIN') for protein_id in transcript.protein_ids])
    elif bioent.bioent_type == 'TRANSCRIPT':
        id_to_type[bioent.id] = 'TRANSCRIPT'
        id_to_type[bioent.gene_id] = 'GENE'
        id_to_type.update([(protein_id, 'PROTEIN') for protein_id in bioent.protein_ids])
    elif bioent.bioent_type == 'PROTEIN':
        id_to_type[bioent.id] = 'PROTEIN'
        id_to_type[bioent.transcript_id] = 'TRANSCRIPT'
        id_to_type[bioent.transcript.gene_id] = 'GENE'
         
    query = session.query(Sequence).options(joinedload('seq_tags')).filter(Sequence.bioent_id.in_(id_to_type.keys()))
    seqs = query.all()
    
    if print_query:
        print query
    return seqs, id_to_type;
  
#Used for search autocomplete.      
def typeahead(search_str, print_query=False):
    '''
    typeahead('ACT', print_query=True)
    
    SELECT sprout.typeahead3.typeahead_id AS sprout_typeahead3_typeahead_id, sprout.typeahead3.name AS sprout_typeahead3_name, sprout.typeahead3.full_name AS sprout_typeahead3_full_name, sprout.typeahead3.bio_type AS sprout_typeahead3_bio_type, sprout.typeahead3.bio_id AS sprout_typeahead3_bio_id, sprout.typeahead3.source AS sprout_typeahead3_source, sprout.typeahead3.use_for_typeahead AS sprout_typeahead3_use_fo_1, sprout.typeahead3.use_for_search AS sprout_typeahead3_use_fo_2 
    FROM sprout.typeahead3 
    WHERE upper(sprout.typeahead3.name) = :upper_1 AND sprout.typeahead3.use_for_typeahead = :use_for_typeahead_1
    '''
    query = session.query(Typeahead).filter(func.upper(Typeahead.name) == search_str).filter(Typeahead.use_for_typeahead == 'Y')
    possible = query.all()
    
    if print_query:
        print query
    return possible

#Used for search_results_table.
def search(search_strs, bio_type, print_query=False): 
    '''
    search(['ACT'], None, print_query=True)

    SELECT sprout.typeahead3.typeahead_id AS sprout_typeahead3_typeahead_id, sprout.typeahead3.name AS sprout_typeahead3_name, sprout.typeahead3.full_name AS sprout_typeahead3_full_name, sprout.typeahead3.bio_type AS sprout_typeahead3_bio_type, sprout.typeahead3.bio_id AS sprout_typeahead3_bio_id, sprout.typeahead3.source AS sprout_typeahead3_source, sprout.typeahead3.use_for_typeahead AS sprout_typeahead3_use_fo_1, sprout.typeahead3.use_for_search AS sprout_typeahead3_use_fo_2 
    FROM sprout.typeahead3 
    WHERE sprout.typeahead3.name = :name_1
    '''  
    for search_str in search_strs: 
        query = session.query(Typeahead).filter(Typeahead.name == search_str.lower()) 
        if bio_type != None:
            query = query.filter(Typeahead.bio_type == bio_type)          
        search_results = query.all() 
        
        if print_query:
            print query  
        return search_results

#Used for search_results_table.
def get_objects(search_results, print_query=False):
    '''
    get_objects(search(['ACT'], None), print_query=True)
    
    None
    
    SELECT sprout.biocon.biocon_id AS sprout_biocon_biocon_id, sprout.biocon.name AS sprout_biocon_name, sprout.biocon.biocon_type AS sprout_biocon_biocon_type, sprout.biocon.description AS sprout_biocon_description 
    FROM sprout.biocon 
    WHERE sprout.biocon.biocon_id IN (:biocon_id_1, :biocon_id_2, :biocon_id_3, :biocon_id_4, :biocon_id_5, :biocon_id_6, :biocon_id_7, :biocon_id_8, :biocon_id_9, :biocon_id_10)
    
    None
    '''
    tuple_to_obj = dict()
    bioent_ids = [search_result.bio_id for search_result in search_results if search_result.bio_type == 'LOCUS']
    biocon_ids = [search_result.bio_id for search_result in search_results if search_result.bio_type in {'PHENOTYPE', 'GO'}]
    reference_ids = [search_result.bio_id for search_result in search_results if search_result.bio_type == 'REFERENCE']    
    
    query1 = None
    query2 = None
    query3 = None
    if len(bioent_ids) > 0:
        query1 = session.query(Bioentity).options(joinedload('bioentaliases')).filter(Bioentity.id.in_(bioent_ids))
        bioents = query1.all()
        tuple_to_obj.update([((obj.type, obj.id), obj) for obj in bioents])
    
    if len(biocon_ids) > 0:
        query2 = session.query(Bioconcept).filter(Bioconcept.id.in_(biocon_ids))
        biocons = query2.all()
        tuple_to_obj.update([((obj.type, obj.id), obj) for obj in biocons])
     
    if len(reference_ids) > 0:   
        query3 = session.query(Reference).options(joinedload('abst')).filter(Reference.id.in_(reference_ids))
        refs = query3.all()
        tuple_to_obj.update([((obj.type, obj.id), obj) for obj in refs])
        
    ordered_objects = []    
    for result in search_results:
        ordered_objects.append(tuple_to_obj[(result.bio_type, result.bio_id)])
        
    if print_query:
        print query1
        print query2
        print query3
    return ordered_objects

#Used to make bioent_names into links for reference abstracts.
def find_bioentities(text, print_query=False):
    """
    Find all bioentities (format_name/display_name) within a piece of text.
    """            
    
    name_to_feature = {}

    if text is not None and text != '':
        words = text.upper().translate(string.maketrans("",""), string.punctuation).split()
    
        upper_words = [x.upper() for x in words]
        bioents_by_format_name = set(session.query(Bioentity).filter(func.upper(Bioentity.format_name).in_(upper_words)).all())
        bioents_by_display_name = set(session.query(Bioentity).filter(func.upper(Bioentity.display_name).in_(upper_words)).all())
                  
        #Create table mapping name -> Feature        
        name_to_feature.update([(bioent.format_name, bioent) for bioent in bioents_by_format_name])
        name_to_feature.update([(bioent.display_name, bioent) for bioent in bioents_by_display_name])
              
    return name_to_feature
        
#Used to break very large queries into a manageable size.
chunk_size = 500
def retrieve_in_chunks(ids, f):
    num_chunks = int(math.ceil(float(len(ids))/chunk_size))
    result = set()
    for i in range(0, num_chunks):
        min_index = i*chunk_size
        max_index = (i+1)*chunk_size
        if max_index > len(ids):
            chunk_ids = ids[min_index:]
        else:
            chunk_ids = ids[min_index:max_index]
        result.update(f(chunk_ids))
    return result
        
if __name__ == "__main__":
    #bioent_id = get_bioent_id('YFL039C', print_query=True)
    #bioent = get_bioent('YFL039C', print_query=True)
    #biocon_id = get_biocon_id('DNA_repair', 'GO', print_query=True)
    #biocon = get_biocon('DNA_repair', 'GO', print_query=True)
    #get_biorel('YFL039C---YDR129C', 'INTERACTION', print_query=True)
    #get_reference_id('7635312', print_query=True)
    #get_reference('7635312', print_query=True)
    #get_author('Brower_SM', print_query=True)
    #get_biorels('INTERACTION', bioent_id, print_query=True)
    #get_interactions([get_bioent_id('YFL039C')], print_query=True)
    #get_biofacts('GO', biocon=get_biocon('DNA_repair', 'GO'), print_query=True)
    #get_biocon_family(get_biocon('DNA_repair', 'GO'), print_query=True)
    #get_biocon_biocons([get_biocon_id('DNA_repair', 'GO')], print_query=True)
    #get_related_biofacts([get_biocon_id('DNA_repair', 'GO')], 'GO', print_query=True)
    #get_go_evidence(bioent_id=get_bioent_id('YFL039C'), print_query=True)
    #get_phenotype_evidence(bioent_id=get_bioent_id('YFL039C'), print_query=True)
    #get_interaction_evidence(bioent_id=get_bioent_id('YFL039C'), print_query=True)
    #get_sequences(get_bioent('YFL039C'), print_query=True)
    #typeahead('ACT', print_query=True)
    #search(['ACT'], None, print_query=True)
    get_objects(search(['ACT'], None)[:10], print_query=True)
    
    
