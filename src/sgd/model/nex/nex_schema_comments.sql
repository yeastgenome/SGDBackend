/* Audit */

Comment on table DELETE_LOG is 'Contains a copy of every deleted row, populated by triggers.';
Comment on column DELETE_LOG.DELETE_LOG_ID is 'Unique random identifier (Oracle sequence).';
Comment on column DELETE_LOG.BUD_ID is 'PK from BUD.DELETE_LOG.DELETE_LOG_NO.';
Comment on column DELETE_LOG.TAB_NAME is 'Table name.';
Comment on column DELETE_LOG.PRIMARY_KEY is 'Primary key of the row deleted.';
Comment on column DELETE_LOG.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DELETE_LOG.CREATED_BY is 'Username of the person who entered the record into the database.';
Comment on column DELETE_LOG.DELETED_ROW is 'Concatenation of all columns in the row deleted.';

Comment on table UPDATE_LOG is 'Contains a copy of every updated column, populated by triggers.';
Comment on column UPDATE_LOG.UPDATE_LOG_ID is 'Unique random identifier (Oracle sequence).';
Comment on column UPDATE_LOG.BUD_ID is 'PK from BUD.DELETE_LOG.UPDATE_LOG_NO.';
Comment on column UPDATE_LOG.TAB_NAME is 'Name of the table updated.';
Comment on column UPDATE_LOG.COL_NAME is 'Name of the column updated.';
Comment on column UPDATE_LOG.PRIMARY_KEY is 'Primary key of the row that was updated.';
Comment on column UPDATE_LOG.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column UPDATE_LOG.CREATED_BY is 'Username of the person who entered the record into the database.';
Comment on column UPDATE_LOG.OLD_VALUE is 'Column old value.';
Comment on column UPDATE_LOG.NEW_VALUE is 'Column new value.';

/* Basic */

Comment on table DBUSER is 'Current or former users with logins to the SGD database.';
Comment on column DBUSER.DBUSER_ID is 'Unique random identifier (Oracle sequence).';
Comment on column DBUSER.USERNAME is 'Database login name.';
Comment on column DBUSER.BUD_ID is 'PK from BUD.DBUSER.DBUSER_NO.';
Comment on column DBUSER.FIRST_NAME is 'First name of the database user.';
Comment on column DBUSER.LAST_NAME is 'Last name of the database user.';
Comment on column DBUSER.STATUS is 'Current state of the database user (Current, Former).';
Comment on column DBUSER.EMAIL is 'Email address of the database user.';
Comment on column DBUSER.DATE_CREATED is 'Date the record was entered into the database.';

Comment on table SOURCE is 'Origin or source of the data.';
Comment on column SOURCE.SOURCE_ID is 'Unique random identifier (Oracle sequence).';
Comment on column SOURCE.FORMAT_NAME is 'Unique name to create download files.';
Comment on column SOURCE.DISPLAY_NAME is 'Public display name.';
Comment on column SOURCE.OBJ_URL is 'Relative URL of the object.';
Comment on column SOURCE.BUD_ID is 'PK from BUD.CODE.CODE_NO.';
Comment on column SOURCE.DESCRIPTION is 'Description or comment.';
Comment on column SOURCE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SOURCE.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Ontologies */

Comment on table CHEMICAL is 'Chemical Entities of Biological Interest (ChEBI) from the EBI.';
Comment on column CHEMICAL.CHEMICAL_ID is 'Unique random identifier (Oracle sequence).';
Comment on column CHEMICAL.FORMAT_NAME is 'Unique name to create download files.';
Comment on column CHEMICAL.DISPLAY_NAME is 'Public display name.';
Comment on column CHEMICAL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column CHEMICAL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CHEMICAL.BUD_ID is 'PK from BUD.CV_TERM.CV_TERM_NO.';
Comment on column CHEMICAL.CHEBI_ID is 'Chemical identifier from the EBI (e.g., CHEBI:58471).';
Comment on column CHEMICAL.DESCRIPTION is 'Description or comment.';
Comment on column CHEMICAL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CHEMICAL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table CHEMICAL_ALIAS is 'Other names or synonyms for the chemical.';
Comment on column CHEMICAL_ALIAS.ALIAS_ID is 'Unique random identifier (Oracle sequence).';
Comment on column CHEMICAL_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column CHEMICAL_ALIAS.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column CHEMICAL_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CHEMICAL_ALIAS.BUD_ID is 'PK from BUD.CVTERM_SYNONYM.CVTERM_SYNONYM_NO.';
Comment on column CHEMICAL_ALIAS.CHEMICAL_ID is 'FK to CHEMICAL.CHEMICAL_ID.';
Comment on column CHEMICAL_ALIAS.ALIAS_TYPE is 'Type of alias (EXACT, RELATED, Secondary ChEBI ID).';
Comment on column CHEMICAL_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CHEMICAL_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table CHEMICAL_URL is 'URLs associated with chemicals.';
Comment on column CHEMICAL_URL.URL_ID is 'Unique random identifier (Oracle sequence).';
Comment on column CHEMICAL_URL.DISPLAY_NAME is 'Public display name (ChEBI).';
Comment on column CHEMICAL_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column CHEMICAL_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CHEMICAL_URL.BUD_ID is 'PK from BUD.URL.URL_NO';
Comment on column CHEMICAL_URL.CHEMICAL_ID is 'FK to CHEMICAL.CHEMICAL_ID.';
Comment on column CHEMICAL_URL.URL_TYPE is 'Type of URL (ChEBI).';
Comment on column CHEMICAL_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CHEMICAL_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table CHEMICAL_RELATION is 'Relationship between two chemicals.';
Comment on column CHEMICAL_RELATION.RELATION_ID is 'Unique random identifier (Oracle sequence).';
Comment on column CHEMICAL_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CHEMICAL_RELATION.BUD_ID is 'PK from BUD.CVTERM_RELATIONSIHP.CVTERM_RELATIONSIHP_NO.';
Comment on column CHEMICAL_RELATION.PARENT_ID is 'FK to CHEMICAL_ID.';
Comment on column CHEMICAL_RELATION.CHILD_ID is 'FK to CHEMICAL_ID.';
Comment on column CHEMICAL_RELATION.RELATION_TYPE is 'Type of relation (is a).';
Comment on column CHEMICAL_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CHEMICAL_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table ENZYME is 'Enzyme Commission (EC) numbers based on chemical reactions catalyzed by enzymes.';
Comment on column ENZYME.ENZYME_ID is 'Unique random identifier (Oracle sequence).';
Comment on column ENZYME.FORMAT_NAME is 'Unique name to create download files.';
Comment on column ENZYME.DISPLAY_NAME is 'Public display name (e.g., 3.1.26.5).';
Comment on column ENZYME.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column ENZYME.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column ENZYME.BUD_ID is 'PK from BUD.DBXREF.DBXREF_NO.';
Comment on column ENZYME.DESCRIPTION is 'Description or comment.';
Comment on column ENZYME.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ENZYME.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table ENZYME_ALIAS is 'Other names or synonyms for the enzyme.';
Comment on column ENZYME_ALIAS.ALIAS_ID is 'Unique random identifier (Oracle sequence).';
Comment on column ENZYME_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column ENZYME_ALIAS.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column ENZYME_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column ENZYME_ALIAS.BUD_ID is 'Not in BUD.';
Comment on column ENZYME_ALIAS.ENZYME_ID is 'FK to ENZYME.ENZYME_ID.';
Comment on column ENZYME_ALIAS.ALIAS_TYPE is 'Type of alias (Synonym).';
Comment on column ENZYME_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ENZYME_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table ENZYME_URL is 'URLs associated with contigs.';
Comment on column ENZYME_URL.URL_ID is 'Unique random identifier (Oracle sequence).';
Comment on column ENZYME_URL.DISPLAY_NAME is 'Public display name (ExPASy, BRENDA).';
Comment on column ENZYME_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column ENZYME_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column ENZYME_URL.BUD_ID is 'Not from BUD';
Comment on column ENZYME_URL.ENZYME_ID is 'FK to ENZYME.ENZYME_ID.';
Comment on column ENZYME_URL.URL_TYPE is 'Type of URL (ExPASy, BRENDA).';
Comment on column ENZYME_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ENZYME_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table EVIDENCE is 'Evidence Ontology (ECO) describes types of scientific evidence.';
Comment on column EVIDENCE.EVIDENCE_ID is 'Unique random identifier (Oracle sequence).';
Comment on column EVIDENCE.FORMAT_NAME is 'Unique name to create download files.';
Comment on column EVIDENCE.DISPLAY_NAME is 'Public display name.';
Comment on column EVIDENCE.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column EVIDENCE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EVIDENCE.BUD_ID is 'Not from BUD.';
Comment on column EVIDENCE.ECO_ID is 'Evidence ontology identifier (e.g. ECO:0000168).';
Comment on column EVIDENCE.DESCRIPTION is 'Description or comment.';
Comment on column EVIDENCE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EVIDENCE.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table EVIDENCE_ALIAS is 'Other names or synonyms for types of evidence.';
Comment on column EVIDENCE_ALIAS.ALIAS_ID is 'Unique random identifier (Oracle sequence).';
Comment on column EVIDENCE_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column EVIDENCE_ALIAS.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column EVIDENCE_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EVIDENCE_ALIAS.BUD_ID is 'Not from BUD.';
Comment on column EVIDENCE_ALIAS.EVIDENCE_ID is 'FK to EVIDENCE.EVIDENCE_ID.';
Comment on column EVIDENCE_ALIAS.ALIAS_TYPE is 'Type of alias (BROAD, EXACT, RELATED, NARROW).';
Comment on column EVIDENCE_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EVIDENCE_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table EVIDENCE_URL is 'URLs associated with evidence types.';
Comment on column EVIDENCE_URL.URL_ID is 'Unique random identifier (Oracle sequence).';
Comment on column EVIDENCE_URL.DISPLAY_NAME is 'Public display name (BioPortal, OLS).';
Comment on column EVIDENCE_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column EVIDENCE_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EVIDENCE_URL.BUD_ID is 'Not from BUD.';
Comment on column EVIDENCE_URL.EVIDENCE_ID is 'FK to EVIDENCE.EVIDENCE_ID.';
Comment on column EVIDENCE_URL.URL_TYPE is 'Type of URL (BioPortal, OLS).';
Comment on column EVIDENCE_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EVIDENCE_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table EVIDENCE_RELATION is 'Relationship between two evidence types.';
Comment on column EVIDENCE_RELATION.RELATION_ID is 'Unique random identifier (Oracle sequence).';
Comment on column EVIDENCE_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EVIDENCE_RELATION.BUD_ID is 'Not from BUD.';
Comment on column EVIDENCE_RELATION.PARENT_ID is 'FK to EVIDENCE.EVIDENCE_ID.';
Comment on column EVIDENCE_RELATION.CHILD_ID is 'FK to EVIDENCE.EVIDENCE_ID.';
Comment on column EVIDENCE_RELATION.RELATION_TYPE is 'Type of relation (is a).';
Comment on column EVIDENCE_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EVIDENCE_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table TAXONOMY is 'Taxonomy information descended from the family Saccharomycetaceae from NCBI.';
Comment on column TAXONOMY.TAXONOMY_ID is 'Unique random identifier (Oracle sequence).';
Comment on column TAXONOMY.FORMAT_NAME is 'Unique name to create download files.';
Comment on column TAXONOMY.DISPLAY_NAME is 'Public display name.';
Comment on column TAXONOMY.OBJ_URL is 'Relative URL of the object.';
Comment on column TAXONOMY.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column TAXONOMY.TAXID is 'Taxonomy identifier assigned by NCBI (from BUD.TAXONOMY.TAXON_ID).';
Comment on column TAXONOMY.COMMON_NAME is 'First common name from NCBI.';
Comment on column TAXONOMY.RANK is 'Rank of the taxonomy term from NCBI (e.g., Saccharomyces cerevisiae = species).';
Comment on column TAXONOMY.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column TAXONOMY.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table TAXONOMY_ALIAS is 'Synonym or other name of a the taxonomy term from NCBI.';
Comment on column TAXONOMY_ALIAS.ALIAS_ID is 'Unique random identifier (Oracle sequence).';
Comment on column TAXONOMY_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column TAXONOMY_ALIAS.OBJ_URL is 'Relative URL of the object.';
Comment on column TAXONOMY_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column TAXONOMY_ALIAS.BUD_ID is 'PK from BUD.TAX_SYNONYM.TAX_SYNONYM_NO.';
Comment on column TAXONOMY_ALIAS.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column TAXONOMY_ALIAS.ALIAS_TYPE is 'Type of alias (Synonym, Secondary common name).';
Comment on column TAXONOMY_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column TAXONOMY_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table TAXONOMY_URL is 'URLs associated with taxonomy.';
Comment on column TAXONOMY_URL.URL_ID is 'Unique random identifier (Oracle sequence).';
Comment on column TAXONOMY_URL.NAME is 'Public display name (NCBI Taxonomy).';
Comment on column TAXONOMY_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column TAXONOMY_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column TAXONOMY_URL.BUD_ID is 'Not from BUD.';
Comment on column TAXONOMY_URL.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column TAXONOMY_URL.URL_TYPE is 'Type of URL (NCBI Taxonomy).';
Comment on column TAXONOMY_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column TAXONOMY_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table TAXONOMY_RELATION is 'Relationship between the taxonomy terms from NCBI.';
Comment on column TAXONOMY_RELATION.RELATION_ID is 'Unique random identifier (Oracle sequence).';
Comment on column TAXONOMY_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column TAXONOMY_RELATION.BUD_ID is 'PK from BUD.TAX_RELATIONSHIP.TAX_RELATIONSHIP_NO .';
Comment on column TAXONOMY_RELATION.PARENT_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column TAXONOMY_RELATION.CHILD_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column TAXONOMY_RELATION.RELATION_TYPE is 'Type of relation (is a).';
Comment on column TAXONOMY_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column TAXONOMY_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Dbentity (Locus, Reference, Strain, File) */

Comment on table DBENTITY is 'Primary objects that are the focus of curation. They are strain independent and require an SGDID.';
Comment on column DBENTITY.DBENTITY_ID is 'Unique random identifier (Oracle sequence).';
Comment on column DBENTITY.FORMAT_NAME is 'Unique name to create download files.';
Comment on column DBENTITY.DISPLAY_NAME is 'Public display name.';
Comment on column DBENTITY.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column DBENTITY.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column DBENTITY.BUD_ID is 'PK from BUD.FEATURE.FEATURE_NO.';
Comment on column DBENTITY.SGDID is 'SGD accession identifier.';
Comment on column DBENTITY.SUBCLASS is 'What object inherits from DBENTITY (DBENTITY, FILE, LOCUS, REFERENCE, STRAIN).';
Comment on column DBENTITY.DBENTITY_STATUS is 'Current state of the dbentity (Active, Merged, Deleted, Archived).';
Comment on column DBENTITY.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DBENTITY.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Locus */

Comment on table LOCUSDBENTITY is 'Features located on a sequence, that are associate with a locus. Inherits from DBENTITY.';
Comment on column LOCUSDBENTITY.DBENTITY_ID is 'Unique random identifier (Oracle sequence).';
Comment on column LOCUSDBENTITY.SYSTEMATIC_NAME is 'Unique name for the dbentity. Subfeature names have a number appended after the systematic name.';
Comment on column LOCUSDBENTITY.SEQUENCEFEATURE_ID is 'FK to SEQUENCEFEATURE.SEQUENCEFEATURE_ID.';
Comment on column LOCUSDBENTITY.GENE_NAME is 'Registered gene name consisting of 3 letters followed by an integer (e.g., ADE12).';
Comment on column LOCUSDBENTITY.QUALIFIER is 'Categorization of the gene (Verified, Uncharacterized, Dubious).';
Comment on column LOCUSDBENTITY.GENETIC_POSITION is 'Genetic position of the locus.';
Comment on column LOCUSDBENTITY.NAME_DESCRIPTION is 'Description of the gene name acronym.';
Comment on column LOCUSDBENTITY.HEADLINE is 'An abbreviated version of the LOCUSDBENTITY.DESCRIPTION.';
Comment on column LOCUSDBENTITY.DESCRIPTION is 'Brief description of the gene product or role the feature plays in the cell.';
Comment on column LOCUSDBENTITY.HAS_SUMMARY is 'Has a Locus web page.';
Comment on column LOCUSDBENTITY.HAS_SEQUENCE is 'Has a Sequence tab page.';
Comment on column LOCUSDBENTITY.HAS_HISTORY is 'Has a History section on the Locus page.';
Comment on column LOCUSDBENTITY.HAS_LITERATURE is 'Has a Literature tab page.';
Comment on column LOCUSDBENTITY.HAS_GO is 'Has a Gene Ontology tab page.';
Comment on column LOCUSDBENTITY.HAS_PHENOTYPE is 'Has a Phenotype tab page.';
Comment on column LOCUSDBENTITY.HAS_INTERACTION is 'Has an Interaction tab page.';
Comment on column LOCUSDBENTITY.HAS_EXPRESSION is 'Has an Expression tab page.';
Comment on column LOCUSDBENTITY.HAS_REGULATION is 'Has a Regulation tab page.';
Comment on column LOCUSDBENTITY.HAS_PROTEIN is 'Has a Protein tab page.';
Comment on column LOCUSDBENTITY.HAS_SEQUENCE_SECTION is 'Has a Sequence section on the Locus page.';

Comment on table LOCUS_ALIAS is 'Other names, synonyms, or dbxrefs for a feature or gene.';
Comment on column LOCUS_ALIAS.ALIAS_ID is 'Unique random identifier (Oracle sequence).';
Comment on column LOCUS_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column LOCUS_ALIAS.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column LOCUS_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column LOCUS_ALIAS.BUD_ID is 'PK from BUD.ALIAS.ALIAS_NO or BUD.DBXREF.DBXREF_NO.';
Comment on column LOCUS_ALIAS.LOCUS_ID is 'FK to LOCUSDBENTITY.DBENTITY_ID.';
Comment on column LOCUS_ALIAS.HAS_EXTERNAL_ID_SECTION is 'Whether the alias is displayed in the Protein tab External Identifier section.';
Comment on column LOCUS_ALIAS.ALIAS_TYPE is 'Type of alias or dbxref.';
Comment on column LOCUS_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column LOCUS_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table LOCUS_URL is 'URLs associated with locus dbentities or features.';
Comment on column LOCUS_URL.URL_ID is 'Unique random identifier (Oracle sequence).';
Comment on column LOCUS_URL.DISPLAY_NAME is 'Public display name.';
Comment on column LOCUS_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column LOCUS_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column LOCUS_URL.BUD_ID is 'PK from BUD.URL.URL_NO.';
Comment on column LOCUS_URL.LOCUS_ID is 'FK to LOCUSDBENTITY.DBENTITY_ID.';
Comment on column LOCUS_URL.URL_TYPE is 'Type of URL (CGI, External identifier, Systematic name, SGDID).';
Comment on column LOCUS_URL.PLACEMENT is 'Location of the URL on the web page.';
Comment on column LOCUS_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column LOCUS_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table LOCUS_RELATION is 'Relationship between two locus dbentities or features.';
Comment on column LOCUS_RELATION.RELATION_ID is 'Unique random identifier (Oracle sequence).';
Comment on column LOCUS_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column LOCUS_RELATION.BUD_ID is 'PK from BUD.FEAT_RELATIONSHIP.FEAT_RELATIONSHIP_NO.';
Comment on column LOCUS_RELATION.PARENT_ID is 'FK to LOCUSDBENTITY.DBENTITY_ID.';
Comment on column LOCUS_RELATION.CHILD_ID is 'FK to LOCUSDBENTITY.DBENTITY_ID.';
Comment on column LOCUS_RELATION.RELATION_TYPE is 'Type of relation (pair, part of, adjacent to).';
Comment on column LOCUS_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column LOCUS_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Strain */

Comment on table STRAINDBENTITY is 'A yeast strain which has sequence data. Inherits from DBENTITY';
Comment on column STRAINDBENTITY.DBENTITY_ID is 'Unique random identifier (Oracle sequence).';
Comment on column STRAINDBENTITY.TAXONOMY_ID is  'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column STRAINDBENTITY.STRAIN_TYPE is 'Strain designation assigned by SGD (Reference, Alternative Reference, Other).';
Comment on column STRAINDBENTITY.GENOTYPE is 'Genotype of the strain.';
Comment on column STRAINDBENTITY.GENBANK_ID is 'GenBank accession ID of the strain (e.g., JRII00000000).';
Comment on column STRAINDBENTITY.ASSEMBLY_SIZE is 'Total number of nucleotides in the assembly.';
Comment on column STRAINDBENTITY.FOLD_COVERAGE is 'Average number of reads per nucleotide in the assembly.';
Comment on column STRAINDBENTITY.SCAFFOLD_NUMBER is 'Number of scaffolds in the assembly.';
Comment on column STRAINDBENTITY.LONGEST_SCAFFOLD is 'Length of the longest scaffold.';
Comment on column STRAINDBENTITY.SCAFFOLD_NFIFTY is 'Weighted median statistic such that 50% of the entire assembly is contained i\
n scaffolds equal to or larger than this value';
Comment on column STRAINDBENTITY.FEATURE_COUNT is 'Number of features identified in this strain.';

Comment on table STRAIN_URL is 'URLs associated with a strain.';
Comment on column STRAIN_URL.URL_ID is 'Unique random identifier (Oracle sequence).';
Comment on column STRAIN_URL.DISPLAY_NAME is 'Public display name.';
Comment on column STRAIN_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column STRAIN_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column STRAIN_URL.BUD_ID is 'Not from BUD';
Comment on column STRAIN_URL.STRAIN_ID is 'FK to STRAINDBENTITY.DBENTITY_ID.';
Comment on column STRAIN_URL.URL_TYPE is 'Type of URL (Source, Wiki, PubMed, GenBank, Download).';
Comment on column STRAIN_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column STRAIN_URL.CREATED_BY is 'Username of the person who entered the record into the database.';
