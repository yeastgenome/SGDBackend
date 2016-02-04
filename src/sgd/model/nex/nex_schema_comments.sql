/* Audit */

Comment on table DELETE_LOG is 'Contains a copy of every deleted row, populated by triggers.';
Comment on column DELETE_LOG.DELETE_LOG_ID is 'Unique identifier (Oracle sequence).';
Comment on column DELETE_LOG.BUD_ID is 'PK from BUD.DELETE_LOG.DELETE_LOG_NO.';
Comment on column DELETE_LOG.TAB_NAME is 'Table name.';
Comment on column DELETE_LOG.PRIMARY_KEY is 'Primary key of the row deleted.';
Comment on column DELETE_LOG.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DELETE_LOG.CREATED_BY is 'Username of the person who entered the record into the database.';
Comment on column DELETE_LOG.DELETED_ROW is 'Concatenation of all columns in the row deleted.';

Comment on table UPDATE_LOG is 'Contains a copy of every updated column, populated by triggers.';
Comment on column UPDATE_LOG.UPDATE_LOG_ID is 'Unique identifier (Oracle sequence).';
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
Comment on column DBUSER.DBUSER_ID is 'Unique identifier (Oracle sequence).';
Comment on column DBUSER.USERNAME is 'Database login name.';
Comment on column DBUSER.BUD_ID is 'PK from BUD.DBUSER.DBUSER_NO.';
Comment on column DBUSER.FIRST_NAME is 'First name of the database user.';
Comment on column DBUSER.LAST_NAME is 'Last name of the database user.';
Comment on column DBUSER.STATUS is 'Current state of the database user (Current, Former).';
Comment on column DBUSER.IS_CURATOR is 'Whether the user is a curator.';
Comment on column DBUSER.EMAIL is 'SUNet ID email address of the database user.';
Comment on column DBUSER.DATE_CREATED is 'Date the record was entered into the database.';

Comment on table SOURCE is 'Origin or source of the data.';
Comment on column SOURCE.SOURCE_ID is 'Unique identifier (Oracle sequence).';
Comment on column SOURCE.FORMAT_NAME is 'Unique name to create download files.';
Comment on column SOURCE.DISPLAY_NAME is 'Public display name.';
Comment on column SOURCE.OBJ_URL is 'Relative URL of the object.';
Comment on column SOURCE.BUD_ID is 'PK from BUD.CODE.CODE_NO.';
Comment on column SOURCE.DESCRIPTION is 'Description or comment.';
Comment on column SOURCE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SOURCE.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table SGDID is 'SGD accession identifier for dbentity objects consisting of a letter (S or L) followed by 9 zero-padded numbers (e.g., S000151155).';
Comment on column SGDID.SGDID_ID is 'Unique identifier (Oracle sequence).';
Comment on column SGDID.FORMAT_NAME is 'Unique name to create download files.';
Comment on column SGDID.DISPLAY_NAME is 'Public display name.';
Comment on column SGDID.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column SGDID.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column SGDID.BUD_ID is 'PK from BUD.DBXREF.DBXREF_NO.';
Comment on column SGDID.SUBCLASS is 'Type of dbentity assigned the SGDID (LOCUS, REFERENCE, STRAIN, FILE).';
Comment on column SGDID.SGDID_STATUS is 'State of the SGDID (Primary, Secondary, Deleted, Unassigned).';
Comment on column SGDID.DESCRIPTION is 'Comment about or reason why the SGDID was deleted.';
Comment on column SGDID.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SGDID.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Ontologies and CVs */

Comment on table RO is 'Relation Ontology (RO) used to describe data relationships.';
Comment on column RO.RO_ID is 'Unique identifier (Oracle sequence).';
Comment on column RO.FORMAT_NAME is 'Unique name to create download files.';
Comment on column RO.DISPLAY_NAME is 'Public display name.';
Comment on column RO.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column RO.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column RO.BUD_ID is 'Not in BUD.';
Comment on column RO.ROID is 'Relation identifier  (e.g., RO:0002434) or new term requests (NTR).';
Comment on column RO.DESCRIPTION is 'Description or comment.';
Comment on column RO.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column RO.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table RO_URL is 'URLs associated with the relation ontology.';
Comment on column RO_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column RO_URL.DISPLAY_NAME is 'Public display name.';
Comment on column RO_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column RO_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column RO_URL.BUD_ID is 'Not in BUD';
Comment on column RO_URL.RO_ID is 'FK to RO.RO_ID.';
Comment on column RO_URL.URL_TYPE is 'Type of URL (Ontobee).';
Comment on column RO_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column RO_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table RO_RELATION is 'Relationship between two relations.';
Comment on column RO_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column RO_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column RO_RELATION.BUD_ID is 'Not in BUD.';
Comment on column RO_RELATION.PARENT_ID is 'FK to RO.RO_ID.';
Comment on column RO_RELATION.CHILD_ID is 'FK to RO.RO_ID.';
Comment on column RO_RELATION.RELATION_TYPE is 'Type of relation (is a).';
Comment on column RO_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column RO_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table APO is 'Ascomycete Phenotype Ontology (APO) created and maintained SGD.';
Comment on column APO.APO_ID is 'Unique identifier (Oracle sequence).';
Comment on column APO.FORMAT_NAME is 'Unique name to create download files.';
Comment on column APO.DISPLAY_NAME is 'Public display name.';
Comment on column APO.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column APO.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column APO.BUD_ID is 'Not in BUD';
Comment on column APO.APOID is 'Phenotype identifier (e.g., APO:0000009) or new term requests (NTR).';
Comment	on column APO.APO_NAMESPACE is 'Aspect or vocabulary groupings (observable, qualifier, experiment_type, mutant_type).';
Comment on column APO.DESCRIPTION is 'Description or comment.';
Comment on column APO.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column APO.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table APO_ALIAS is 'Other names or synonyms for the phenotype.';
Comment on column APO_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column APO_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column APO_ALIAS.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column APO_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column APO_ALIAS.BUD_ID is 'Not in BUD.';
Comment on column APO_ALIAS.APO_ID is 'FK to APO.APO_ID.';
Comment on column APO_ALIAS.ALIAS_TYPE is 'Type of alias (EXACT, RELATED).';
Comment on column APO_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column APO_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table APO_URL is 'URLs associated with phenotype.';
Comment on column APO_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column APO_URL.DISPLAY_NAME is 'Public display name (BioPortal, OLS).';
Comment on column APO_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column APO_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column APO_URL.BUD_ID is 'Not in BUD.';
Comment on column APO_URL.APO_ID is 'FK to APO.APO_ID.';
Comment on column APO_URL.URL_TYPE is 'Type of URL (BioPortal, OLS).';
Comment on column APO_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column APO_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table APO_RELATION is 'Relationship between two phenotypes.';
Comment on column APO_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column APO_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column APO_RELATION.BUD_ID is 'Not in BUD.';
Comment on column APO_RELATION.PARENT_ID is 'FK to APO.APO_ID.';
Comment on column APO_RELATION.CHILD_ID is 'FK to APO.APO_ID.';
Comment on column APO_RELATION.RO_ID is 'FK to RO.RO_ID.';
Comment on column APO_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column APO_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table CHEBI is 'Chemical Entities of Biological Interest (ChEBI) from the EBI.';
Comment on column CHEBI.CHEBI_ID is 'Unique identifier (Oracle sequence).';
Comment on column CHEBI.FORMAT_NAME is 'Unique name to create download files.';
Comment on column CHEBI.DISPLAY_NAME is 'Public display name.';
Comment on column CHEBI.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column CHEBI.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CHEBI.BUD_ID is 'PK from BUD.CV_TERM.CV_TERM_NO.';
Comment on column CHEBI.CHEBIID is 'Chemical identifier from the EBI (e.g., CHEBI:58471) or new term requests (NTR).';
Comment on column CHEBI.DESCRIPTION is 'Description or comment.';
Comment on column CHEBI.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CHEBI.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table CHEBI_ALIAS is 'Other names or synonyms for the chemical.';
Comment on column CHEBI_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column CHEBI_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column CHEBI_ALIAS.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column CHEBI_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CHEBI_ALIAS.BUD_ID is 'PK from BUD.CVTERM_SYNONYM.CVTERM_SYNONYM_NO.';
Comment on column CHEBI_ALIAS.CHEBI_ID is 'FK to CHEBI.CHEBI_ID.';
Comment on column CHEBI_ALIAS.ALIAS_TYPE is 'Type of alias (EXACT, RELATED, Secondary ChEBI ID, IUPAC name).';
Comment on column CHEBI_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CHEBI_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table CHEBI_URL is 'URLs associated with chemicals.';
Comment on column CHEBI_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column CHEBI_URL.DISPLAY_NAME is 'Public display name (ChEBI).';
Comment on column CHEBI_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column CHEBI_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CHEBI_URL.BUD_ID is 'PK from BUD.URL.URL_NO';
Comment on column CHEBI_URL.CHEBI_ID is 'FK to CHEBI.CHEBI_ID.';
Comment on column CHEBI_URL.URL_TYPE is 'Type of URL (ChEBI).';
Comment on column CHEBI_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CHEBI_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table CHEBI_RELATION is 'Relationship between two chemicals.';
Comment on column CHEBI_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column CHEBI_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CHEBI_RELATION.BUD_ID is 'PK from BUD.CVTERM_RELATIONSIHP.CVTERM_RELATIONSIHP_NO.';
Comment on column CHEBI_RELATION.PARENT_ID is 'FK to CHEBI_ID.';
Comment on column CHEBI_RELATION.CHILD_ID is 'FK to CHEBI_ID.';
Comment on column CHEBI_RELATION.RO_ID is 'FK to RO.RO_ID.';
Comment on column CHEBI_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CHEBI_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table EC is 'Enzyme Commission (EC) numbers based on chemical reactions catalyzed by enzymes.';
Comment on column EC.EC_ID is 'Unique identifier (Oracle sequence).';
Comment on column EC.FORMAT_NAME is 'Unique name to create download files.';
Comment on column EC.DISPLAY_NAME is 'Public display name (e.g., 3.1.26.5).';
Comment on column EC.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column EC.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EC.BUD_ID is 'PK from BUD.DBXREF.DBXREF_NO.';
Comment on column EC.ECID is 'Enzyme Commission number (e.g., EC:3.1.26.5) or new term requests (NTR).';
Comment on column EC.DESCRIPTION is 'Description or comment.';
Comment on column EC.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EC.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table EC_ALIAS is 'Other names or synonyms for an enzyme.';
Comment on column EC_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column EC_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column EC_ALIAS.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column EC_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EC_ALIAS.BUD_ID is 'Not in BUD.';
Comment on column EC_ALIAS.EC_ID is 'FK to EC.EC_ID.';
Comment on column EC_ALIAS.ALIAS_TYPE is 'Type of alias (Synonym).';
Comment on column EC_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EC_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table EC_URL is 'URLs associated with enzyzmes.';
Comment on column EC_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column EC_URL.DISPLAY_NAME is 'Public display name (ExPASy, BRENDA).';
Comment on column EC_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column EC_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EC_URL.BUD_ID is 'Not from BUD';
Comment on column EC_URL.EC_ID is 'FK to EC.EC_ID.';
Comment on column EC_URL.URL_TYPE is 'Type of URL (ExPASy, BRENDA).';
Comment on column EC_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EC_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table ECO is 'Evidence Ontology (ECO) describes types of scientific evidence.';
Comment on column ECO.ECO_ID is 'Unique identifier (Oracle sequence).';
Comment on column ECO.FORMAT_NAME is 'Unique name to create download files.';
Comment on column ECO.DISPLAY_NAME is 'Public display name.';
Comment on column ECO.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column ECO.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column ECO.BUD_ID is 'Not from BUD.';
Comment on column ECO.ECOID is 'Evidence ontology identifier (e.g. ECO:0000168) or new term requests (NTR).';
Comment on column ECO.DESCRIPTION is 'Description or comment.';
Comment on column ECO.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ECO.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table ECO_ALIAS is 'Other names or synonyms for types of evidence.';
Comment on column ECO_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column ECO_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column ECO_ALIAS.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column ECO_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column ECO_ALIAS.BUD_ID is 'Not from BUD.';
Comment on column ECO_ALIAS.ECO_ID is 'FK to ECO.ECO_ID.';
Comment on column ECO_ALIAS.ALIAS_TYPE is 'Type of alias (BROAD, EXACT, RELATED, NARROW).';
Comment on column ECO_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ECO_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table ECO_URL is 'URLs associated with evidence types.';
Comment on column ECO_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column ECO_URL.DISPLAY_NAME is 'Public display name (BioPortal, OLS).';
Comment on column ECO_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column ECO_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column ECO_URL.BUD_ID is 'Not from BUD.';
Comment on column ECO_URL.ECO_ID is 'FK to ECO.ECO_ID.';
Comment on column ECO_URL.URL_TYPE is 'Type of URL (BioPortal, OLS).';
Comment on column ECO_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ECO_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table ECO_RELATION is 'Relationship between two evidence types.';
Comment on column ECO_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column ECO_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column ECO_RELATION.BUD_ID is 'Not from BUD.';
Comment on column ECO_RELATION.PARENT_ID is 'FK to ECO.ECO_ID.';
Comment on column ECO_RELATION.CHILD_ID is 'FK to ECO.ECO_ID.';
Comment on column ECO_RELATION.RO_ID is 'FK to RO.RO_ID.';
Comment on column ECO_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ECO_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table EDAM is 'EDAM is an ontology of bioinformatics topics, operations, types of data including identifiers, and data formats.';
Comment on column EDAM.EDAM_ID is 'Unique identifier (Oracle sequence).';
Comment on column EDAM.FORMAT_NAME is 'Unique name to create download files.';
Comment on column EDAM.DISPLAY_NAME is 'Public display name.';
Comment on column EDAM.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column EDAM.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EDAM.BUD_ID is 'Not from BUD.';
Comment on column EDAM.EDAMID is 'EDAM identifier (e.g. EDAM:0928).';
Comment on column EDAM.EDAM_NAMESPACE is 'Four separate domains or namespaces (data, format, operation, topic).';
Comment on column EDAM.DESCRIPTION is 'Description or comment.';
Comment on column EDAM.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EDAM.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table EDAM_ALIAS is 'Other names or synonyms for a EDAM term.';
Comment on column EDAM_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column EDAM_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column EDAM_ALIAS.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column EDAM_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EDAM_ALIAS.BUD_ID is 'Not from BUD.';
Comment on column EDAM_ALIAS.EDAM_ID is 'FK to EDAM.EDAM_ID.';
Comment on column EDAM_ALIAS.ALIAS_TYPE is 'Type of alias (BROAD, EXACT, RELATED, NARROW).';
Comment on column EDAM_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EDAM_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table EDAM_URL is 'URLs associated with EDAM terms.';
Comment on column EDAM_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column EDAM_URL.DISPLAY_NAME is 'Public display name.';
Comment on column EDAM_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column EDAM_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EDAM_URL.BUD_ID is 'Not from BUD.';
Comment on column EDAM_URL.EDAM_ID is 'FK to EDAM.EDAM_ID.';
Comment on column EDAM_URL.URL_TYPE is 'Type of URL (BioPortal, Ontobee).';
Comment on column EDAM_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EDAM_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table EDAM_RELATION is 'Relationship between two EDAM terms.';
Comment on column EDAM_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column EDAM_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EDAM_RELATION.BUD_ID is 'Not from BUD.';
Comment on column EDAM_RELATION.PARENT_ID is 'FK to EDAM.EDAM_ID.';
Comment on column EDAM_RELATION.CHILD_ID is 'FK to EDAM.EDAM_ID.';
Comment on column EDAM_RELATION.RO_ID is 'FK to RO.RO_ID.';
Comment on column EDAM_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EDAM_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table GO is 'Gene Ontology (GO) terms used to describe genes and gene products.';
Comment on column GO.GO_ID is 'Unique identifier (Oracle sequence).';
Comment on column GO.FORMAT_NAME is 'Unique name to create download files.';
Comment on column GO.DISPLAY_NAME is 'Public display name.';
Comment on column GO.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column GO.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GO.BUD_ID is 'Not from BUD.';
Comment on column GO.GOID is 'Gene Ontology identifier (e.g. GO:0016233).';
Comment on column GO.GO_NAMESPACE is 'Three separate domains to describe gene products  (cellular component, biological process, molecular function).';
Comment on column GO.DESCRIPTION is 'Description or comment.';
Comment on column GO.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GO.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table GO_ALIAS is 'Other names or synonyms for a GO term.';
Comment on column GO_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column GO_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column GO_ALIAS.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column GO_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GO_ALIAS.BUD_ID is 'Not from BUD.';
Comment on column GO_ALIAS.GO_ID is 'FK to GO.GO_ID.';
Comment on column GO_ALIAS.ALIAS_TYPE is 'Type of alias (BROAD, EXACT, RELATED, NARROW).';
Comment on column GO_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GO_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table GO_URL is 'URLs associated with GO terms.';
Comment on column GO_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column GO_URL.DISPLAY_NAME is 'Public display name (GO, Amigo).';
Comment on column GO_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column GO_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GO_URL.BUD_ID is 'Not from BUD.';
Comment on column GO_URL.GO_ID is 'FK to GO.GO_ID.';
Comment on column GO_URL.URL_TYPE is 'Type of URL (GO, Amigo).';
Comment on column GO_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GO_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table GO_RELATION is 'Relationship between two GO terms.';
Comment on column GO_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column GO_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GO_RELATION.BUD_ID is 'Not from BUD.';
Comment on column GO_RELATION.PARENT_ID is 'FK to GO.GO_ID.';
Comment on column GO_RELATION.CHILD_ID is 'FK to GO.GO_ID.';
Comment on column GO_RELATION.RO_ID is 'FK to RO.RO_ID.';
Comment on column GO_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GO_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table KEYWORD is 'Controlled vocabulary to describe broad categories of biology, used to filter or group data.';
Comment on column KEYWORD.KEYWORD_ID is 'Unique identifier (Oracle sequence).';
Comment on column KEYWORD.FORMAT_NAME is 'Unique name to create download files.';
Comment on column KEYWORD.DISPLAY_NAME is 'Public display name.';
Comment on column KEYWORD.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column KEYWORD.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column KEYWORD.BUD_ID is 'From BUD.KEYWORD.KEYWORD_NO and SPELL tags.';
Comment on column KEYWORD.DESCRIPTION is 'Description or comment.';
Comment on column KEYWORD.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column KEYWORD.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table OBI is 'Ontology for Biomedical Investigations (OBI) describes biomedical studies.';
Comment on column OBI.OBI_ID is 'Unique identifier (Oracle sequence).';
Comment on column OBI.FORMAT_NAME is 'Unique name to create download files.';
Comment on column OBI.DISPLAY_NAME is 'Public display name.';
Comment on column OBI.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column OBI.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column OBI.BUD_ID is 'Not from BUD.';
Comment on column OBI.OBIID is 'Biomedical investigations identifier (e.g. OBI:0000185) or new term requests (NTR).';
Comment on column OBI.DESCRIPTION is 'Description or comment.';
Comment on column OBI.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column OBI.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table OBI_URL is 'URLs associated with biomedical investigations.';
Comment on column OBI_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column OBI_URL.DISPLAY_NAME is 'Public display name (Ontobee).';
Comment on column OBI_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column OBI_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column OBI_URL.BUD_ID is 'Not from BUD.';
Comment on column OBI_URL.OBI_ID is 'FK to OBI.OBI_ID.';
Comment on column OBI_URL.URL_TYPE is 'Type of URL (Ontobee).';
Comment on column OBI_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column OBI_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table OBI_RELATION is 'Relationship between two biomedical investigation ontology terms.';
Comment on column OBI_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column OBI_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column OBI_RELATION.BUD_ID is 'Not from BUD.';
Comment on column OBI_RELATION.PARENT_ID is 'FK to OBI.OBI_ID.';
Comment on column OBI_RELATION.CHILD_ID is 'FK to OBI.OBI_ID.';
Comment on column OBI_RELATION.RO_ID is 'FK to RO.RO_ID.';
Comment on column OBI_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column OBI_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PSIMOD is 'Protein modification ontology (PSI-MOD) developed by the Proteomics Standards Initiative (PSI).';
Comment on column PSIMOD.PSIMOD_ID is 'Unique identifier (Oracle sequence).';
Comment on column PSIMOD.FORMAT_NAME is 'Unique name to create download files.';
Comment on column PSIMOD.DISPLAY_NAME is 'Public display name.';
Comment on column PSIMOD.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column PSIMOD.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PSIMOD.BUD_ID is 'Not from BUD.';
Comment on column PSIMOD.PSIMODID is 'Protein modification ontology identifier (e.g., MOD:01152) or new term requests (NTR).';
Comment on column PSIMOD.DESCRIPTION is 'Description or comment.';
Comment on column PSIMOD.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PSIMOD.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table PSIMOD_URL is 'URLs associated with the protein modification ontology.';
Comment on column PSIMOD_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column PSIMOD_URL.DISPLAY_NAME is 'Public display name (BioPortal, OLS, Ontobee).';
Comment on column PSIMOD_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column PSIMOD_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PSIMOD_URL.BUD_ID is 'Not from BUD.';
Comment on column PSIMOD_URL.PSIMOD_ID is 'FK to PSIMOD.PSIMOD_ID.';
Comment on column PSIMOD_URL.URL_TYPE is 'Type of URL (BioPortal, OLS, Ontobee).';
Comment on column PSIMOD_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PSIMOD_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PSIMOD_RELATION is 'Relationship between two protein modification ontology terms.';
Comment on column PSIMOD_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column PSIMOD_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PSIMOD_RELATION.BUD_ID is 'Not from BUD.';
Comment on column PSIMOD_RELATION.PARENT_ID is 'FK to PSIMOD.PSIMOD_ID.';
Comment on column PSIMOD_RELATION.CHILD_ID is 'FK to PSIMOD.PSIMOD_ID.';
Comment on column PSIMOD_RELATION.RO_ID is 'FK to RO.RO_ID.';
Comment on column PSIMOD_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PSIMOD_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table SO is 'Sequence features as defined by the Sequence Ontology (SO).';
Comment on column SO.SO_ID is 'Unique identifier (Oracle sequence).';
Comment on column SO.FORMAT_NAME is 'Unique name to create download files.';
Comment on column SO.DISPLAY_NAME is 'Public display name.';
Comment on column SO.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column SO.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column SO.BUD_ID is 'Not from BUD.';
Comment on column SO.SOID is 'Sequence Ontology identifier (e.g., SO:0000368) or new term requests (NTR).';
Comment on column SO.DESCRIPTION is 'Description or comment.';
Comment on column SO.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SO.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table SO_ALIAS is 'Other names or synonyms for the sequence feature.';
Comment on column SO_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column SO_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column SO_ALIAS.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column SO_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column SO_ALIAS.BUD_ID is 'Not from BUD.';
Comment on column SO_ALIAS.SO_ID is 'FK to SO.SO_ID.';
Comment on column SO_ALIAS.ALIAS_TYPE is 'Type of alias (BROAD, EXACT, RELATED, NARROW).';
Comment on column SO_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SO_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table SO_URL is 'URLs associated with sequence features.';
Comment on column SO_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column SO_URL.DISPLAY_NAME is 'Public display name (MISO, OLS).';
Comment on column SO_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column SO_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column SO_URL.BUD_ID is 'Not from BUD.';
Comment on column SO_URL.SO_ID is 'FK to SO.SO_ID.';
Comment on column SO_URL.URL_TYPE is 'Type of URL (MISO, OLS).';
Comment on column SO_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SO_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table SO_RELATION is 'Relationship between two sequence features.';
Comment on column SO_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column SO_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column SO_RELATION.BUD_ID is 'Not from BUD.';
Comment on column SO_RELATION.PARENT_ID is 'FK to SO.SO_ID.';
Comment on column SO_RELATION.CHILD_ID is 'FK to SO.SO_ID.';
Comment on column SO_RELATION.RO_ID is 'FK to RO.RO_ID.';
Comment on column SO_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SO_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table TAXONOMY is 'Taxonomy information descended from the family Saccharomycetaceae from NCBI.';
Comment on column TAXONOMY.TAXONOMY_ID is 'Unique identifier (Oracle sequence).';
Comment on column TAXONOMY.FORMAT_NAME is 'Unique name to create download files.';
Comment on column TAXONOMY.DISPLAY_NAME is 'Public display name.';
Comment on column TAXONOMY.OBJ_URL is 'Relative URL of the object.';
Comment on column TAXONOMY.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column TAXONOMY.TAXID is 'Taxonomy identifier assigned by NCBI (e.g., TAX:1290389) or new term requests (NTR).';
Comment on column TAXONOMY.COMMON_NAME is 'First common name from NCBI.';
Comment on column TAXONOMY.RANK is 'Rank of the taxonomy term from NCBI (e.g., Saccharomyces cerevisiae = species).';
Comment on column TAXONOMY.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column TAXONOMY.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table TAXONOMY_ALIAS is 'Synonym or other name of a the taxonomy term from NCBI.';
Comment on column TAXONOMY_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column TAXONOMY_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column TAXONOMY_ALIAS.OBJ_URL is 'Relative URL of the object.';
Comment on column TAXONOMY_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column TAXONOMY_ALIAS.BUD_ID is 'PK from BUD.TAX_SYNONYM.TAX_SYNONYM_NO.';
Comment on column TAXONOMY_ALIAS.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column TAXONOMY_ALIAS.ALIAS_TYPE is 'Type of alias (Synonym, Secondary common name).';
Comment on column TAXONOMY_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column TAXONOMY_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table TAXONOMY_URL is 'URLs associated with taxonomy.';
Comment on column TAXONOMY_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column TAXONOMY_URL.NAME is 'Public display name (NCBI Taxonomy).';
Comment on column TAXONOMY_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column TAXONOMY_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column TAXONOMY_URL.BUD_ID is 'Not from BUD.';
Comment on column TAXONOMY_URL.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column TAXONOMY_URL.URL_TYPE is 'Type of URL (NCBI Taxonomy).';
Comment on column TAXONOMY_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column TAXONOMY_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table TAXONOMY_RELATION is 'Relationship between the taxonomy terms from NCBI.';
Comment on column TAXONOMY_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column TAXONOMY_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column TAXONOMY_RELATION.BUD_ID is 'PK from BUD.TAX_RELATIONSHIP.TAX_RELATIONSHIP_NO .';
Comment on column TAXONOMY_RELATION.PARENT_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column TAXONOMY_RELATION.CHILD_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column TAXONOMY_RELATION.RO_ID is 'FK to RO.RO_ID.';
Comment on column TAXONOMY_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column TAXONOMY_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Dbentity (Locus, Reference, Strain, File) */

Comment on table DBENTITY is 'Primary objects that are the focus of curation. They are strain independent and require an SGDID.';
Comment on column DBENTITY.DBENTITY_ID is 'Unique identifier (Oracle sequence).';
Comment on column DBENTITY.FORMAT_NAME is 'Unique name to create download files.';
Comment on column DBENTITY.DISPLAY_NAME is 'Public display name.';
Comment on column DBENTITY.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column DBENTITY.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column DBENTITY.BUD_ID is 'PK from BUD.FEATURE.FEATURE_NO.';
Comment on column DBENTITY.SGDID is 'SGD accession identifier.';
Comment on column DBENTITY.SUBCLASS is 'What object inherits from DBENTITY (FILE, LOCUS, REFERENCE, STRAIN, PATHWAY).';
Comment on column DBENTITY.DBENTITY_STATUS is 'Current state of the dbentity (Active, Merged, Deleted, Archived).';
Comment on column DBENTITY.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DBENTITY.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Locus */

Comment on table LOCUSDBENTITY is 'Features located on a sequence, that are associate with a locus. Inherits from DBENTITY.';
Comment on column LOCUSDBENTITY.DBENTITY_ID is 'Unique identifier (Oracle sequence).';
Comment on column LOCUSDBENTITY.SYSTEMATIC_NAME is 'Unique name for the dbentity. Subfeatures have a number appended after the systematic name.';
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
Comment on column LOCUS_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column LOCUS_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column LOCUS_ALIAS.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column LOCUS_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column LOCUS_ALIAS.BUD_ID is 'PK from BUD.ALIAS.ALIAS_NO or BUD.DBXREF.DBXREF_NO.';
Comment on column LOCUS_ALIAS.LOCUS_ID is 'FK to LOCUSDBENTITY.DBENTITY_ID.';
Comment on column LOCUS_ALIAS.HAS_EXTERNAL_ID_SECTION is 'Whether the alias is displayed in the Protein tab External Identifier section.';
Comment on column LOCUS_ALIAS.ALIAS_TYPE is 'Type of alias or dbxref.';
Comment on column LOCUS_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column LOCUS_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table LOCUS_URL is 'URLs associated with locus dbentities or features.';
Comment on column LOCUS_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column LOCUS_URL.DISPLAY_NAME is 'Public display name.';
Comment on column LOCUS_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column LOCUS_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column LOCUS_URL.BUD_ID is 'PK from BUD.URL.URL_NO.';
Comment on column LOCUS_URL.LOCUS_ID is 'FK to LOCUSDBENTITY.DBENTITY_ID.';
Comment on column LOCUS_URL.URL_TYPE is 'Type of URL (CGI, External id, Systematic name, SGDID).';
Comment on column LOCUS_URL.PLACEMENT is 'Location of the URL on the web page.';
Comment on column LOCUS_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column LOCUS_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table LOCUS_RELATION is 'Relationship between two locus dbentities or features.';
Comment on column LOCUS_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column LOCUS_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column LOCUS_RELATION.BUD_ID is 'PK from BUD.FEAT_RELATIONSHIP.FEAT_RELATIONSHIP_NO.';
Comment on column LOCUS_RELATION.PARENT_ID is 'FK to LOCUSDBENTITY.DBENTITY_ID.';
Comment on column LOCUS_RELATION.CHILD_ID is 'FK to LOCUSDBENTITY.DBENTITY_ID.';
Comment on column LOCUS_RELATION.RO_ID is 'FK to RO.RO_ID.';
Comment on column LOCUS_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column LOCUS_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Strain */

Comment on table STRAINDBENTITY is 'A yeast strain which has sequence data. Inherits from DBENTITY';
Comment on column STRAINDBENTITY.DBENTITY_ID is 'Unique identifier (Oracle sequence).';
Comment on column STRAINDBENTITY.TAXONOMY_ID is  'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column STRAINDBENTITY.STRAIN_TYPE is 'Strain designation assigned by SGD (Reference, Alternative Reference, Other).';
Comment on column STRAINDBENTITY.GENOTYPE is 'Genotype of the strain.';
Comment on column STRAINDBENTITY.GENBANK_ID is 'GenBank accession ID of the strain (e.g., JRII00000000).';
Comment on column STRAINDBENTITY.ASSEMBLY_SIZE is 'Total number of nucleotides in the assembly.';
Comment on column STRAINDBENTITY.FOLD_COVERAGE is 'Average number of reads per nucleotide in the assembly.';
Comment on column STRAINDBENTITY.SCAFFOLD_NUMBER is 'Number of scaffolds in the assembly.';
Comment on column STRAINDBENTITY.LONGEST_SCAFFOLD is 'Length of the longest scaffold.';
Comment on column STRAINDBENTITY.SCAFFOLD_NFIFTY is 'Weighted median statistic such that 50% of the entire assembly is contained in scaffolds equal to or larger than this value';
Comment on column STRAINDBENTITY.FEATURE_COUNT is 'Number of features identified in this strain.';

Comment on table STRAIN_URL is 'URLs associated with a strain.';
Comment on column STRAIN_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column STRAIN_URL.DISPLAY_NAME is 'Public display name.';
Comment on column STRAIN_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column STRAIN_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column STRAIN_URL.BUD_ID is 'Not from BUD';
Comment on column STRAIN_URL.STRAIN_ID is 'FK to STRAINDBENTITY.DBENTITY_ID.';
Comment on column STRAIN_URL.URL_TYPE is 'Type of URL (External id, Wiki, PubMed, GenBank, Download).';
Comment on column STRAIN_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column STRAIN_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Pathway */

Comment on table PATHWAYDBENTITY is 'A biochemical pathway. Inherits from DBENTITY';
Comment on column PATHWAYDBENTITY.DBENTITY_ID is 'Unique identifier (Oracle sequence).';
Comment on column PATHWAYDBENTITY.BIOCYC_ID is  'Unique identifier for the pathway from BioCyc.';

Comment on table PATHWAY_ALIAS is 'Other names, synonyms, or dbxrefs for a pathway.';
Comment on column PATHWAY_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column PATHWAY_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column PATHWAY_ALIAS.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column PATHWAY_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PATHWAY_ALIAS.BUD_ID is 'From yeastbase.ocelot file';
Comment on column PATHWAY_ALIAS.LOCUS_ID is 'FK to PATHWAYDBENTITY.DBENTITY_ID.';
Comment on column PATHWAY_ALIAS.ALIAS_TYPE is 'Type of alias or dbxref (Synonym).';
Comment on column PATHWAY_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PATHWAY_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PATHWAY_URL is 'URLs associated with a pathway.';
Comment on column PATHWAY_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column PATHWAY_URL.DISPLAY_NAME is 'Public display name.';
Comment on column PATHWAY_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column PATHWAY_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PATHWAY_URL.BUD_ID is 'Not from BUD';
Comment on column PATHWAY_URL.PATHWAY_ID is 'FK to PATHWAYDBENTITY.DBENTITY_ID.';
Comment on column PATHWAY_URL.URL_TYPE is 'Type of URL (BioCyc, YeastPathways).';
Comment on column PATHWAY_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PATHWAY_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

/* File */

Comment on table FILEPATH is 'Virtual path to a file for browsing purposes.';
Comment on column FILEPATH.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column FILEPATH.FILEPATH is 'Virtual path to a file for browsing purposes.';
Comment on column FILEPATH.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column FILEPATH.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table FILEDBENTITY is 'Details about files loaded into or dumped from the database or associated with the Download Server.';
Comment on column FILEDBENTITY.DBENTITY_ID is 'Unique identifier (Oracle sequence).';
Comment on column FILEDBENTITY.TOPIC_ID is 'A broad domain or category of the file, FK to EDAM topic namespace.';
Comment on column FILEDBENTITY.FORMAT_ID is 'Standard file format, FK to EDAM format namespace.';
Comment on column FILEDBENTITY.EXTENSION_ID is 'File name extension, FK to EDAM format namespace.';
Comment on column FILEDBENTITY.FILE_DATE is 'Release date or date the file was created.';
Comment on column FILEDBENTITY.IS_PUBLIC is 'Whether the file is viewable to the public.';
Comment on column FILEDBENTITY.IS_IN_SPELL is 'Whether the file was loaded into SPELL.';
Comment on column FILEDBENTITY.IS_IN_BROWSER is 'Whether the file was loaded into a genome browser, such as JBrowse.';
Comment on column FILEDBENTITY.MD5SUM is 'The 128-bit MD5 hash or checksum of the file.';
Comment on column FILEDBENTITY.FILEPATH_ID is 'FK to FILEPATH.FILEPATH_ID.';
Comment on column FILEDBENTITY.PREVIOUS_FILE_NAME is 'File name on the Download Server.';
Comment on column FILEDBENTITY.README_URL is 'URL of the README associated with this file, if exists.';

Comment on table FILE_KEYWORD is 'Keywords associated with a file.';
Comment on column FILE_KEYWORD.FILE_KEYWORD_ID is 'Unique identifier (Oracle sequence).';
Comment on column FILE_KEYWORD.FILE_ID is 'FK to FILEDBENTITY.DBENTITY_ID.';
Comment on column FILE_KEYWORD.KEYWORD_ID is 'FK to KEYWORD.KEYWORD_ID.';
Comment on column FILE_KEYWORD.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column FILE_KEYWORD.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column FILE_KEYWORD.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Reference */

Comment on table BOOK is 'Details about book references.';
Comment on column BOOK.BOOK_ID is 'Unique identifier (Oracle sequence).';
Comment on column BOOK.FORMAT_NAME is 'Unique name to create download files.';
Comment on column BOOK.DISPLAY_NAME is 'Public display name.';
Comment on column BOOK.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column BOOK.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column BOOK.BUD_ID is 'PK from BUD.BOOK.BOOK_NO.';
Comment on column BOOK.TITLE is 'Title of the book.';
Comment on column BOOK.VOLUME_TITLE is 'Title if the book is part of a volume.';
Comment on column BOOK.ISBN is 'International Standard Book Number.';
Comment on column BOOK.TOTAL_PAGES is 'Total number of pages in the book.';
Comment on column BOOK.PUBLISHER is 'Publisher of the book.';
Comment on column BOOK.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column BOOK.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table JOURNAL is 'Details about journal references.';
Comment on column JOURNAL.JOURNAL_ID is 'Unique identifier (Oracle sequence).';
Comment on column JOURNAL.FORMAT_NAME is 'Unique name to create download files.';
Comment on column JOURNAL.DISPLAY_NAME is 'Public display name.';
Comment on column JOURNAL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column JOURNAL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column JOURNAL.BUD_ID is 'PK from BUD.JOURNAL.JOURNAL_NO.';
Comment on column JOURNAL.MED_ABBR is 'NLM abbreviation of the journal name.';
Comment on column JOURNAL.TITLE is 'Full name of the journal.';
Comment on column JOURNAL.ISSN_PRINT is 'International Standard Serial Number.';
Comment on column JOURNAL.ISSN_ELECTRONIC is 'Electronic International Standard Serial Number.';
Comment on column JOURNAL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column JOURNAL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REFERENCEDBENTITY is 'Details about references associated with annotations. Inherits from DBENTITY';
Comment on column REFERENCEDBENTITY.DBENTITY_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCEDBENTITY.METHOD_OBTAINED is 'How the reference was obtained (Curator PubMed reference, Curator triage, Curator non-PubMed reference, Gene registry, PDB script, PubMed script, SacchDB, YPD)';
Comment on column REFERENCEDBENTITY.PUBLICATION_STATUS is 'Publication state of the reference (Epub ahead of print, In preparation, In press, Published, Submitted, Unpublished).';
Comment on column REFERENCEDBENTITY.FULLTEXT_STATUS is 'State of the full text for the reference (N, NAA, NAM, NAP, Y, YF, YT).';
Comment on column REFERENCEDBENTITY.CITATION is 'Full citation of the reference.';
Comment on column REFERENCEDBENTITY.YEAR is 'Year the reference was published.';
Comment on column REFERENCEDBENTITY.PMID is 'PMID of the reference from NCBI.';
Comment on column REFERENCEDBENTITY.PMCID is 'PMCID of the reference from NCBI.';
Comment on column REFERENCEDBENTITY.DATE_PUBLISHED is 'Full date the reference was published.';
Comment on column REFERENCEDBENTITY.DATE_REVISED is 'Date if the reference was updated by NCBI.';
Comment on column REFERENCEDBENTITY.ISSUE is 'Issue of the reference.';
Comment on column REFERENCEDBENTITY.PAGE is 'Page numbers of the reference.';
Comment on column REFERENCEDBENTITY.VOLUME is 'Volume of the reference.';
Comment on column REFERENCEDBENTITY.TITLE is 'Title of the reference.';
Comment on column REFERENCEDBENTITY.DOI is 'Digital Object Identifier from the International DOI Foundation.';
Comment on column REFERENCEDBENTITY.JOURNAL_ID is 'FK to JOURNAL.JOURNAL_ID.';
Comment on column REFERENCEDBENTITY.BOOK_ID is 'FK to BOOK.BOOK_ID.';

Comment on table REFERENCE_ALIAS is 'Other names or synonyms for the reference.';
Comment on column REFERENCE_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCE_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column REFERENCE_ALIAS.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column REFERENCE_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column REFERENCE_ALIAS.BUD_ID is 'PK from BUD.DBXREF.DBXREF_NO.';
Comment on column REFERENCE_ALIAS.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_ALIAS.ALIAS_TYPE is 'Type of alias (Secondary SGDID).';
Comment on column REFERENCE_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REFERENCE_URL is 'URLs associated with references.';
Comment on column REFERENCE_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCE_URL.DISPLAY_NAME is 'Public display name.';
Comment on column REFERENCE_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column REFERENCE_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column REFERENCE_URL.BUD_ID is 'PK from BUD.URL.URL_NO.';
Comment on column REFERENCE_URL.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_URL.URL_TYPE is 'Type of URL (DOI full text, PMC full text, PubMed, PubMedCentral, Reference supplement).';
Comment on column REFERENCE_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REFERENCE_REFTYPE is 'Links a reference with a reftype.';
Comment on column REFERENCE_REFTYPE.REFERENCE_REFTYPE_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCE_REFTYPE.DISPLAY_NAME is 'Public display name.';
Comment on column REFERENCE_REFTYPE.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column REFERENCE_REFTYPE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column REFERENCE_REFTYPE.BUD_ID is 'PK from BUD.REF_REFTYPE.REF_REFTYPE_NO.';
Comment on column REFERENCE_REFTYPE.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_REFTYPE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_REFTYPE.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REFERENCE_CORRECTION is 'Relationship between two references, used for published errata, comments, retractions, etc.';
Comment on column REFERENCE_CORRECTION.REFERENCE_CORRECTION_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCE_CORRECTION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column REFERENCE_CORRECTION.PARENT_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_CORRECTION.CHILD_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_CORRECTION.CORRECTION_TYPE is 'Type of correction or comment (Erratum in, Comment on, etc.).';
Comment on column REFERENCE_CORRECTION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_CORRECTION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REFERENCE_DOCUMENT is 'Abstract or Medline entry associated with references.';
Comment on column REFERENCE_DOCUMENT.REFERENCE_DOCUMENT_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCE_DOCUMENT.DOCUMENT_TYPE is 'Type of document (Abstract, Medline).';
Comment on column REFERENCE_DOCUMENT.TEXT is 'Plain text of the document.';
Comment on column REFERENCE_DOCUMENT.HTML is 'HTML mark-up of the document.';
Comment on column REFERENCE_DOCUMENT.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column REFERENCE_DOCUMENT.BUD_ID is 'PK from BUD.ABSTRACT.REFERENCE_NO.';
Comment on column REFERENCE_DOCUMENT.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_DOCUMENT.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_DOCUMENT.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REFERENCE_AUTHOR is 'Links authors with references.';
Comment on column REFERENCE_AUTHOR.REFERENCE_AUTHOR_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCE_AUTHOR.DISPLAY_NAME is 'Public display name.';
Comment on column REFERENCE_AUTHOR.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column REFERENCE_AUTHOR.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column REFERENCE_AUTHOR.BUD_ID is 'PK from BUD.AUTHOR_EDITOR.AUTHOR_EDITOR_NO.';
Comment on column REFERENCE_AUTHOR.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_AUTHOR.ORCID is 'Author Open Researcher and Contributor ID.';
Comment on column REFERENCE_AUTHOR.AUTHOR_ORDER is 'Order of the authors.';
Comment on column REFERENCE_AUTHOR.AUTHOR_TYPE is 'Type of author (Author, Editor).';
Comment on column REFERENCE_AUTHOR.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_AUTHOR.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REFERENCE_FILE is 'Files associated with a reference.';
Comment on column REFERENCE_FILE.REFERENCE_FILE_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCE_FILE.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_FILE.FILE_ID is 'FK to FILEDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_FILE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column REFERENCE_FILE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_FILE.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REFERENCE_UNLINK is 'References that should not be associated with a specific locus, but should remain in the database.';
Comment on column REFERENCE_UNLINK.REFERENCE_UNLINK_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCE_UNLINK.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_UNLINK.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_UNLINK.BUD_ID is 'PK from BUD.REF_UNLINK.REF_UNLINK_NO.';
Comment on column REFERENCE_UNLINK.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_UNLINK.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REFERENCE_DELETED is 'References permanently removed from the database via curator triage.';
Comment on column REFERENCE_DELETED.REFERENCE_DELETED_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCE_DELETED.PMID is 'PubMed ID of the reference from NCBI.';
Comment on column REFERENCE_DELETED.SGDID is 'SGDID of the reference assigned before removal from the database.';
Comment on column REFERENCE_DELETED.BUD_ID is 'PK in BUD is PubMed ID.';
Comment on column REFERENCE_DELETED.REASON_DELETED is 'Why the reference was deleted from the database.';
Comment on column REFERENCE_DELETED.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_DELETED.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Colleague */

Comment on table COLLEAGUE is 'A researcher or associate who registered with the database.';
Comment on column COLLEAGUE.COLLEAGUE_ID is 'Unique identifier (Oracle sequence).';
Comment on column COLLEAGUE.FORMAT_NAME is 'Unique name to create download files ([first_name]_[last_name]_[sequentialnumber].';
Comment on column COLLEAGUE.DISPLAY_NAME is 'Public display name.';
Comment on column COLLEAGUE.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column COLLEAGUE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column COLLEAGUE.BUD_ID is 'PK from BUD.COLLEAGUE.COLLEAGUE_NO.';
Comment on column COLLEAGUE.ORCID is 'Unique Author Open Researcher and Contributor ID.';
Comment on column COLLEAGUE.LAST_NAME is 'Last name of the colleague.';
Comment on column COLLEAGUE.FIRST_NAME is 'First name of the colleague, including middle name if any.';
Comment on column COLLEAGUE.SUFFIX is 'Name suffix (II, III, IV, Jr., Sr.).';
Comment on column COLLEAGUE.OTHER_LAST_NAME is 'Maiden or other last name used.';
Comment on column COLLEAGUE.PROFESSION is 'Profession (e.g., yeast molecular biologist, bioinformaticist).';
Comment on column COLLEAGUE.JOB_TITLE is 'Position (e.g., Professor, Post-doc, Staff scientist),';
Comment on column COLLEAGUE.INSTITUTION is 'University, company, or organization of the colleague.';
Comment on column COLLEAGUE.ADDRESS1 is 'First line of street address.';
Comment on column COLLEAGUE.ADDRESS2 is 'Second line of street address.';
Comment on column COLLEAGUE.ADDRESS3 is 'Third line of street address.';
Comment on column COLLEAGUE.CITY is 'City.';
Comment on column COLLEAGUE.STATE is 'State or region (US and Canada coded).';
Comment on column COLLEAGUE.COUNTRY is 'Country (Coded).';
Comment on column COLLEAGUE.POSTAL_CODE is 'Postal or zip code.';
Comment on column COLLEAGUE.WORK_PHONE is 'Colleague work phone number.';
Comment on column COLLEAGUE.OTHER_PHONE is 'Another phone number for the colleague.';
Comment on column COLLEAGUE.FAX is 'Fax number.';
Comment on column COLLEAGUE.EMAIL is 'Email address.';
Comment	on column COLLEAGUE.COLLEAGUE_NOTE is 'Note or comment about the colleague entered by a curator.';
Comment on column COLLEAGUE.RESEARCH_INTEREST is 'Research interests of the colleague.';
Comment on column COLLEAGUE.IS_PI is 'Whether the colleague is a PI.';
Comment on column COLLEAGUE.IS_CONTACT is 'Whether the colleague is a contact for SGD.';
Comment on column COLLEAGUE.DISPLAY_EMAIL is 'Whether to display the colleague email address.';
Comment on column COLLEAGUE.DATE_LAST_MODIFIED is 'Date the record was last updated.';
Comment on column COLLEAGUE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column COLLEAGUE.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table COLLEAGUE_URL is 'URLs associated with colleagues.';
Comment on column COLLEAGUE_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column COLLEAGUE_URL.DISPLAY_NAME is 'Public display name.';
Comment on column COLLEAGUE_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column COLLEAGUE_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column COLLEAGUE_URL.BUD_ID is 'PK from BUD.URL.URL_NO.';
Comment on column COLLEAGUE_URL.COLLEAGUE_ID is 'FK to COLLEAGUE.COLLEAGUE_ID.';
Comment on column COLLEAGUE_URL.URL_TYPE is 'Type of URL (Lab, Research summary).';
Comment on column COLLEAGUE_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column COLLEAGUE_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table COLLEAGUE_ASSOCIATION is 'Association between two colleagues.';
Comment on column COLLEAGUE_ASSOCIATION.COLLEAGUE_ASSOCIATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column COLLEAGUE_ASSOCIATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column COLLEAGUE_ASSOCIATION.BUD_ID is 'PK from BUD.COLL_RELATIONSHIP.COLL_RELATIONSHIP_NO.';
Comment on column COLLEAGUE_ASSOCIATION.COLLEAGUE_ID is 'FK to COLLEAGUE.COLLEAGUE_ID.';
Comment on column COLLEAGUE_ASSOCIATION.ASSOCIATE_ID is 'FK to COLLEAGUE.COLLEAGUE_ID.';
Comment on column COLLEAGUE_ASSOCIATION.ASSOCIATION_TYPE is 'Type of association or relationship (Associate, Lab member, Head of Lab).';
Comment on column COLLEAGUE_ASSOCIATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column COLLEAGUE_ASSOCIATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table COLLEAGUE_KEYWORD is 'Keywords associated with a colleague.';
Comment on column COLLEAGUE_KEYWORD.COLLEAGUE_KEYWORD_ID is 'Unique identifier (Oracle sequence).';
Comment on column COLLEAGUE_KEYWORD.COLLEAGUE_ID is 'FK to COLLEAGUE.COLLEAGUE_ID.';
Comment on column COLLEAGUE_KEYWORD.KEYWORD_ID is 'FK to KEYWORD.KEYWORD_ID.';
Comment on column COLLEAGUE_KEYWORD.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column COLLEAGUE_KEYWORD.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column COLLEAGUE_KEYWORD.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table COLLEAGUE_LOCUS is 'Links a colleague with a locus of research interest.';
Comment on column COLLEAGUE_LOCUS.COLLEAGUE_LOCUS_ID is 'Unique identifier (Oracle sequence).';
Comment on column COLLEAGUE_LOCUS.COLLEAGUE_ID is 'FK to COLLEAGUE.COLLEAGUE_ID.';
Comment on column COLLEAGUE_LOCUS.LOCUS_ID is 'FK to LOCUSDBENTITY.DBENTITY_ID.';
Comment on column COLLEAGUE_LOCUS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column COLLEAGUE_LOCUS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column COLLEAGUE_LOCUS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table COLLEAGUE_REFERENCE is 'Links a colleague with a reference, primarily through ORCIDs.';
Comment on column COLLEAGUE_REFERENCE.COLLEAGUE_REFERENCE_ID is 'Unique identifier (Oracle sequence).';
Comment on column COLLEAGUE_REFERENCE.COLLEAGUE_ID is 'FK to COLLEAGUE.COLLEAGUE_ID.';
Comment on column COLLEAGUE_REFERENCE.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column COLLEAGUE_REFERENCE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column COLLEAGUE_REFERENCE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column COLLEAGUE_REFERENCE.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Data objects */
/* Summaries */

Comment on table LOCUS_SUMMARY is 'Summaries or paragraphs associated with locus features.';
Comment on column LOCUS_SUMMARY.SUMMARY_ID is 'Unique identifier (Oracle sequence).';
Comment on column LOCUS_SUMMARY.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column LOCUS_SUMMARY.BUD_ID is 'PK from BUD.PARAGRAPH.PARAGRAPH_NO.';
Comment on column LOCUS_SUMMARY.LOCUS_ID is 'FK to LOCUSDBENTITY.DBENTITY_ID.';
Comment on column LOCUS_SUMMARY.SUMMARY_TYPE is 'Type of summary (Gene, Function, Phenotype, Regulation).';
Comment on column LOCUS_SUMMARY.SUMMARY_ORDER is 'Order of summaries when composed of multiple paragraphs (default = 1).';
Comment on column LOCUS_SUMMARY.TEXT is 'Summary plain text.';
Comment on column LOCUS_SUMMARY.HTML is 'Summary HTML mark-up.';
Comment on column LOCUS_SUMMARY.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column LOCUS_SUMMARY.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table LOCUS_SUMMARY_REFERENCE is 'References associated with a locus summary.';
Comment on column LOCUS_SUMMARY_REFERENCE.SUMMARY_REFERENCE_ID is 'Unique identifier (Oracle sequence).';
Comment on column LOCUS_SUMMARY_REFERENCE.SUMMARY_ID is 'FK to LOCUS_SUMMARY.SUMMARY_ID.';
Comment on column LOCUS_SUMMARY_REFERENCE.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column LOCUS_SUMMARY_REFERENCE.REFERENCE_ORDER is 'Order of the references in the summary.';
Comment on column LOCUS_SUMMARY_REFERENCE.SOURCE_ID is  'FK to SOURCE.SOURCE_ID.';
Comment on column LOCUS_SUMMARY_REFERENCE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column LOCUS_SUMMARY_REFERENCE.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table STRAIN_SUMMARY is 'Summaries or paragraphs associated with strains.';
Comment on column STRAIN_SUMMARY.SUMMARY_ID is 'Unique identifier (Oracle sequence).';
Comment on column STRAIN_SUMMARY.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column STRAIN_SUMMARY.BUD_ID is 'Not from BUD.';
Comment on column STRAIN_SUMMARY.STRAIN_ID is 'FK to STRAINDBENTITY.DBENTITY_ID.';
Comment on column STRAIN_SUMMARY.SUMMARY_TYPE is 'Type of summary (Strain).';
Comment on column STRAIN_SUMMARY.TEXT is 'Summary plain text.';
Comment on column STRAIN_SUMMARY.HTML is 'Summary HTML mark-up.';
Comment on column STRAIN_SUMMARY.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column STRAIN_SUMMARY.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table STRAIN_SUMMARY_REFERENCE is 'References associatd with a strain summary.';
Comment on column STRAIN_SUMMARY_REFERENCE.SUMMARY_REFERENCE_ID is 'Unique identifier (Oracle sequence).';
Comment on column STRAIN_SUMMARY_REFERENCE.SUMMARY_ID is 'FK to STRAIN_SUMMARY.SUMMARY_ID.';
Comment on column STRAIN_SUMMARY_REFERENCE.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column STRAIN_SUMMARY_REFERENCE.REFERENCE_ORDER is 'Order of the references in the summary.';
Comment on column STRAIN_SUMMARY_REFERENCE.SOURCE_ID is  'FK to SOURCE.SOURCE_ID.';
Comment on column STRAIN_SUMMARY_REFERENCE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column STRAIN_SUMMARY_REFERENCE.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PATHWAY_SUMMARY is 'Summaries or paragraphs associated with pathways.';
Comment on column PATHWAY_SUMMARY.SUMMARY_ID is 'Unique identifier (Oracle sequence).';
Comment on column PATHWAY_SUMMARY.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PATHWAY_SUMMARY.BUD_ID is 'Not from BUD.';
Comment on column PATHWAY_SUMMARY.PATHWAY_ID is 'FK to PATHWAYDBENTITY.DBENTITY_ID.';
Comment on column PATHWAY_SUMMARY.SUMMARY_TYPE is 'Type of summary (Metabolic).';
Comment on column PATHWAY_SUMMARY.TEXT is 'Summary plain text.';
Comment on column PATHWAY_SUMMARY.HTML is 'Summary HTML mark-up.';
Comment on column PATHWAY_SUMMARY.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PATHWAY_SUMMARY.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PATHWAY_SUMMARY_REFERENCE is 'References associatd with a paragraph summary.';
Comment on column PATHWAY_SUMMARY_REFERENCE.SUMMARY_REFERENCE_ID is 'Unique identifier (Oracle sequence).';
Comment on column PATHWAY_SUMMARY_REFERENCE.SUMMARY_ID is 'FK to PATHWAY_SUMMARY.SUMMARY_ID.';
Comment on column PATHWAY_SUMMARY_REFERENCE.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column PATHWAY_SUMMARY_REFERENCE.REFERENCE_ORDER is 'Order of the references in the summary.';
Comment on column PATHWAY_SUMMARY_REFERENCE.SOURCE_ID is  'FK to SOURCE.SOURCE_ID.';
Comment on column PATHWAY_SUMMARY_REFERENCE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PATHWAY_SUMMARY_REFERENCE.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Gene reservations */

Comment on table RESERVEDNAME is 'Reserved gene names according to the Gene Registration Guidelines.';
Comment on column RESERVEDNAME.RESERVEDNAME_ID is 'Unique identifier (Oracle sequence).';
Comment on column RESERVEDNAME.FORMAT_NAME is 'Unique name to create download files.';
Comment on column RESERVEDNAME.DISPLAY_NAME is 'Public display name.';
Comment on column RESERVEDNAME.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column RESERVEDNAME.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column RESERVEDNAME.BUD_ID is 'From BUD.GENE_RESERVATION.FEATURE_NO.';
Comment on column RESERVEDNAME.LOCUS_ID is 'FK to LOCUSDBENTITY.DBENTITY_ID.';
Comment on column RESERVEDNAME.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column RESERVEDNAME.COLLEAGUE_ID is 'FK to COLLEAGUE.COLLEAGUE_ID.';
Comment on column RESERVEDNAME.RESERVATION_DATE is 'Date the gene reservation was made.';
Comment on column RESERVEDNAME.EXPIRATION_DATE is 'Date the gene reservation expires (default = RESERVATION_DATE + 365 days).';
Comment on column RESERVEDNAME.DESCRIPTION is 'Description or comment.';
Comment on column RESERVEDNAME.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column RESERVEDNAME.CREATED_BY  is 'Username of the person who entered the record into the database.';

/* GO Slim */
Comment on table GOSLIM is 'Broader upper level GO terms grouped into useful sub-sets.';
Comment on column GOSLIM.GOSLIM_ID is 'Unique identifier (Oracle sequence).';
Comment on column GOSLIM.FORMAT_NAME is 'Unique name to create download files.';
Comment on column GOSLIM.DISPLAY_NAME is 'Public display name.';
Comment on column GOSLIM.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column GOSLIM.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GOSLIM.BUD_ID is 'PK from BUD.GO_SET.GO_SET_NO.';
Comment on column GOSLIM.GO_ID is 'FK to GO.GO_ID.';
Comment on column GOSLIM.SLIM_NAME is 'Name of the grouping of GO terms (Yeast GO-Slim, Macromolecular complex terms, Generic GO-Slim).';
Comment on column GOSLIM.GENOME_COUNT is 'Number of dbentities assigned to this GO slim term, used by the GO Tools.';
Comment on column GOSLIM.DESCRIPTION is 'Description or comment.';
Comment on column GOSLIM.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GOSLIM.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Phenotype */

Comment on table PHENOTYPE is 'Phenotypes defined by the Ascomycete Phenotype Ontology (APO) as an observable:qualifier combination.';
Comment on column PHENOTYPE.PHENOTYPE_ID is 'Unique identifier (Oracle sequence).';
Comment on column PHENOTYPE.FORMAT_NAME is 'Unique name to create download files.';
Comment on column PHENOTYPE.DISPLAY_NAME is 'Public display name.';
Comment on column PHENOTYPE.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column PHENOTYPE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PHENOTYPE.BUD_ID is 'Not from BUD.';
Comment on column PHENOTYPE.OBSERVABLE_ID is 'FK to APO.APO_ID.';
Comment on column PHENOTYPE.QUALIFIER_ID is 'FK to APO.APO_ID.';
Comment on column PHENOTYPE.DESCRIPTION is 'Description or comment.';
Comment on column PHENOTYPE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PHENOTYPE.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table ALLELE is 'Gene variants or alleles that show observable phenotypic traits.';
Comment on column ALLELE.ALLELE_ID is 'Unique identifier (Oracle sequence).';
Comment on column ALLELE.FORMAT_NAME is 'Unique name to create download files.';
Comment on column ALLELE.DISPLAY_NAME is 'Public display name.';
Comment on column ALLELE.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column ALLELE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column ALLELE.BUD_ID is 'PK from BUD.EXPT_PROPERTY.EXPT_PROPERTY_NO.';
Comment on column ALLELE.DESCRIPTION is 'Description or comment.';
Comment on column ALLELE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ALLELE.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REPORTER is 'Gene variants or alleles that show observable phenotypic traits.';
Comment on column REPORTER.REPORTER_ID is 'Unique identifier (Oracle sequence).';
Comment on column REPORTER.FORMAT_NAME is 'Unique name to create download files.';
Comment on column REPORTER.DISPLAY_NAME is 'Public display name.';
Comment on column REPORTER.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column REPORTER.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column REPORTER.BUD_ID is 'PK from BUD.EXPT_PROPERTY.EXPT_PROPERTY_NO.';
Comment on column REPORTER.DESCRIPTION is 'Description or comment.';
Comment on column REPORTER.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REPORTER.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Dataset */


Comment on table DATASETLAB is 'Laboratory which conducted the dataset experiment.';
Comment on column DATASETLAB.DATASETLAB_ID is 'Unique identifier (Oracle sequence).';
Comment on column DATASETLAB.DATASET_ID is 'FK to DATASET.DATASET_ID.';
Comment on column DATASETLAB.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column DATASETLAB.LAB_NAME is 'PI last name.';
Comment on column DATASETLAB.LAB_LOCATION is 'Institution or location of the PI.';
Comment on column DATASETLAB.COLLEAGUE_ID is 'FK to COLLEAGUE.COLLEAGUE_ID.';
Comment on column DATASETLAB.DATE_CREATED is 'Date the record Comment on table DATASET is 'High throughput gene expression data from NCBI’s GEO database and displayed using SPELL.';
Comment on column DATASET.DATASET_ID is 'Unique identifier (Oracle sequence).';
Comment on column DATASET.FORMAT_NAME is 'Unique name to create download files.';
Comment on column DATASET.DISPLAY_NAME is 'Public display name.';
Comment on column DATASET.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column DATASET.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column DATASET.BUD_ID is 'Not in BUD.';
Comment on column DATASET.DBXREF_ID is 'GEO Series ID (GSE), ArrayExpress ID, or Sequence Read Archive ID.';
Comment on column DATASET.DBXREF_TYPE is 'Type of database cross reference (GEO,ArrayExpress,SRA).';
Comment on column DATASET.ASSAY_ID is 'FK to OBI.OBI_ID.';
Comment on column DATASET.CHANNEL_COUNT is 'Number of channels (1 or 2) in the experiment.';
Comment on column DATASET.SAMPLE_COUNT is 'Number of samples in the experiment.';
Comment on column DATASET.TAXONOMY_ID is 'Strain background. FK to TAXONOMY.TAXONOMY_ID.';
Comment on column DATASET.IS_IN_SPELL is 'Whether this dataset has been loaded into SPELL.';
Comment on column DATASET.IS_IN_BROWSER is 'Whether this dataset has been loaded into a genome browser, such as JBrowse.';
Comment on column DATASET.DESCRIPTION is 'Description or summary.';
Comment on column DATASET.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DATASET.CREATED_BY  is 'Username of the person who entered the record into the database.';
was entered into the database.';
Comment on column DATASETLAB.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table DATASET_URL is 'URLs associated with a dataset.';
Comment on column DATASET_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column DATASET_URL.DISPLAY_NAME is 'Public display name.';
Comment on column DATASET_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column DATASET_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column DATASET_URL.BUD_ID is 'Not from BUD.';
Comment on column DATASET_URL.DATASET_ID is 'FK to DATASET.DATASET_ID.';
Comment on column DATASET_URL.URL_TYPE is 'Type of URL (GSE, ArrayExpress, SRA).';
Comment on column DATASET_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DATASET_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table DATASET_KEYWORD is 'A category or keyword that describes the whole dataset.';
Comment on column DATASET_KEYWORD.DATASET_KEYWORD_ID is 'Unique identifier (Oracle sequence).';
Comment on column DATASET_KEYWORD.KEYWORD_ID is 'FK to KEYWORD.KEYWORD_ID.';
Comment on column DATASET_KEYWORD.DATASET_ID is 'FK to DATASET.DATASET_ID.';
Comment on column DATASET_KEYWORD.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column DATASET_KEYWORD.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DATASET_KEYWORD.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table DATASET_REFERENCE is 'References associated with a dataset.';
Comment on column DATASET_REFERENCE.DATASET_REFERENCE_ID is 'Unique identifier (Oracle sequence).';
Comment on column DATASET_REFERENCE.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column DATASET_REFERENCE.DATASET_ID is 'FK to DATASET.DATASET_ID.';
Comment on column DATASET_REFERENCE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column DATASET_REFERENCE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DATASET_REFERENCE.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table DATASET_FILE is 'Files associated with a dataset.';
Comment on column DATASET_FILE.DATASET_FILE_ID is 'Unique identifier (Oracle sequence).';
Comment on column DATASET_FILE.FILE_ID is 'FK to FILEDBENTITY.DBENTITY_ID.';
Comment on column DATASET_FILE.DATASET_ID is 'FK to DATASET.DATASET_ID.';
Comment on column DATASET_FILE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column DATASET_FILE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DATASET_FILE.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table DATASETSAMPLE is 'Samples or experiments in a dataset.';
Comment on column DATASETSAMPLE.DATASETSAMPLE_ID is 'Unique identifier (Oracle sequence).';
Comment on column DATASETSAMPLE.FORMAT_NAME is 'Unique name to create download files.';
Comment on column DATASETSAMPLE.DISPLAY_NAME is 'Public display name.';
Comment on column DATASETSAMPLE.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column DATASETSAMPLE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column DATASETSAMPLE.BUD_ID is 'Not in BUD.';
Comment on column DATASETSAMPLE.DATASET_ID is 'FK to DATASET.DATASET_ID.';
Comment on column DATASETSAMPLE.SAMPLE_ORDER is 'Order to display the samples.';
Comment on column DATASETSAMPLE.DBXREF_ID is 'GEO Sample identifier (GSM) or other external database identifier.';
Comment on column DATASETSAMPLE.DBXREF_TYPE is 'Type of database cross reference (GEO,ArrayExpress,SRA).';
Comment on column DATASETSAMPLE.BIOSAMPLE is 'List of OBI term names for one or more biosamples used in the experiment, separated by '|'.';
Comment on column DATASETSAMPLE.STRAIN_NAME is 'List of strain names for one or more strains used in the experiment, separated by '|'.';
Comment on column DATASETSAMPLE.DESCRIPTION is 'Description or summary of the sample.';
Comment on column DATASETSAMPLE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DATASETSAMPLE.CREATED_BY  is 'Username of the person who entered the record into the database.';

/* Sequence objects - Genome Release, Contig, Protein Domain */

Comment on table GENOMERELEASE is 'S288C reference genome release numbers, in the format R[sequence release]-[annotation release]-[curation release] (e.g., R64-1-1).';
Comment on column GENOMERELEASE.GENOMERELEASE_ID is 'Unique identifier (Oracle sequence).';
Comment on column GENOMERELEASE.FORMAT_NAME is 'Unique name to create download files.';
Comment on column GENOMERELEASE.DISPLAY_NAME is 'Public display name.';
Comment on column GENOMERELEASE.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column GENOMERELEASE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GENOMERELEASE.BUD_ID is 'From BUD.RELEASE.RELEASE_NO.';
Comment on column GENOMERELEASE.FILE_ID is 'FK to FILEDBENTITY.DBENTITY_ID.';
Comment on column GENOMERELEASE.SEQUENCE_RELEASE is 'Release or version number of the sequence.';
Comment on column GENOMERELEASE.ANNOTATION_RELEASE is 'Annotation release associated with a particular sequence release, incremented when feature coordinates change or features are added, merged or deleted.';
Comment on column GENOMERELEASE.CURATION_RELEASE is 'Incremented when new annotation files added to the Download Server.';
Comment on column GENOMERELEASE.RELEASE_DATE is 'Date the genome release was made.';
Comment on column GENOMERELEASE.DESCRIPTION is 'Description or comment.';
Comment on column GENOMERELEASE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GENOMERELEASE.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table CONTIG is 'Current whole chromosome or contig sequences.';
Comment on column CONTIG.CONTIG_ID is 'Unique identifier (Oracle sequence).';
Comment on column CONTIG.FORMAT_NAME is 'Unique name to create download files.';
Comment on column CONTIG.DISPLAY_NAME is 'Public display name.';
Comment on column CONTIG.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column CONTIG.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CONTIG.BUD_ID is 'PK from BUD.SEQ.SEQ_NO.';
Comment on column CONTIG.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column CONTIG.SO_ID is 'FK to SO.SO_ID (contig, chromosome, plasmid).';
Comment on column CONTIG.CENTROMERE_START is 'Start coordinate of the centromere.';
Comment on column CONTIG.CENTROMERE_END is 'End coordinate of the centromere.';
Comment on column CONTIG.GENBANK_ACCESSION is 'GenBank Accession id including version number (e.g., BK006939.2).';
Comment on column CONTIG.GI_NUMBER is 'GenInfo identifier assigned by NCBI.';
Comment on column CONTIG.REFSEQ_ID is 'REFerence SEQuence identifier assigned by NCBI.';
Comment on column CONTIG.REFERENCE_CHROMOSOME_ID is 'FK to CONTIG.CONTIG_ID.';
Comment on column CONTIG.REFERENCE_START is 'Start coordinate relative to the reference sequence S288C.';
Comment on column CONTIG.REFERENCE_END is 'End coordinate relative to the reference sequence S288C.';
Comment on column CONTIG.REFERENCE_PERCENT_IDENTITY is 'Percent identify to the reference sequence S288C.';
Comment on column CONTIG.REFERENCE_ALIGNMENT_LENGTH is 'Length of the sequence alignment to the reference sequence S288C.';
Comment on column CONTIG.SEQ_VERSION is 'From BUD.SEQ.SEQ_VERSION.';
Comment on column CONTIG.COORD_VERSION is 'From BUD.FEAT_LOCATION.COORD_VERSION.';
Comment on column CONTIG.GENOMERELEASE_ID is 'FK to GENOMERELEASE.GENOMERELEASE_ID.';
Comment on column CONTIG.FILE_HEADER is 'Header line of the download file.';
Comment on column CONTIG.DOWNLOAD_FILENAME is 'User interface download filename.';
Comment on column CONTIG.FILE_ID is 'FK to FILEDBENTITY.DBENTITY_ID.';
Comment on column CONTIG.RESIDUES is 'DNA sequence of the contig, chromosome or plasmid.';
Comment on column CONTIG.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CONTIG.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table CONTIG_URL is 'URLs associated with chromosomes or contigs.';
Comment on column CONTIG_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column CONTIG_URL.DISPLAY_NAME is 'Public display name.';
Comment on column CONTIG_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column CONTIG_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CONTIG_URL.BUD_ID is 'Not from BUD.';
Comment on column CONTIG_URL.CONTIG_ID is 'FK to CONTIG.CONTIG_ID.';
Comment on column CONTIG_URL.URL_TYPE is 'Type of URL (GenBank).';
Comment on column CONTIG_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CONTIG_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PROTEINDOMAIN is 'Collection of computationally identified domains and motifs, determined by InterProScan analysis.';
Comment on column PROTEINDOMAIN.PROTEINDOMAIN_ID is 'Unique identifier (Oracle sequence).';
Comment on column PROTEINDOMAIN.FORMAT_NAME is 'Unique name to create download files.';
Comment on column PROTEINDOMAIN.DISPLAY_NAME is 'Public display name.';
Comment on column PROTEINDOMAIN.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column PROTEINDOMAIN.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PROTEINDOMAIN.BUD_ID is 'Not from BUD.';
Comment on column PROTEINDOMAIN.INTERPRO_ID is 'InterPro Identifier from EBI.';
Comment on column PROTEINDOMAIN.DESCRIPTION is 'Description or comment.';
Comment on column PROTEINDOMAIN.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PROTEINDOMAIN.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table PROTEINDOMAIN_URL is 'URLs associated with protein domains.';
Comment on column PROTEINDOMAIN_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column PROTEINDOMAIN_URL.DISPLAY_NAME is 'Public display name.';
Comment on column PROTEINDOMAIN_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column PROTEINDOMAIN_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PROTEINDOMAIN_URL.BUD_ID is 'Not from BUD.';
Comment on column PROTEINDOMAIN_URL.PROTEINDOMAIN_ID is 'FK to PROTEINDOMAIN.PROTEINDOMAIN_ID.';
Comment on column PROTEINDOMAIN_URL.URL_TYPE is 'Type of URL (InterPro,PROSITE,HAMAP,Pfam,PRINTS,ProDom,SMART,TIGRFAM,PIRSF,SUPERFAMILY,GENE3D,PANTHER).';
Comment on column PROTEINDOMAIN_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PROTEINDOMAIN_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Annotations */

Comment on table BINDINGMOTIFANNOTATION is 'Transcription factor motif logos from the YeTFaSCo database.';
Comment on column BINDINGMOTIFANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column BINDINGMOTIFANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column BINDINGMOTIFANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column BINDINGMOTIFANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column BINDINGMOTIFANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column BINDINGMOTIFANNOTATION.BUD_ID is 'From BUD.SEQ.SEQ_NO.';
Comment on column BINDINGMOTIFANNOTATION.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column BINDINGMOTIFANNOTATION.MOTIF_ID is 'Motif ID from the YeTFaSCo database.';
Comment on column BINDINGMOTIFANNOTATION.LOGO_URL is 'URL to the motif logo.';
Comment on column BINDINGMOTIFANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column BINDINGMOTIFANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table CONTIGNOTEANNOTATION is 'Notes about chromosomes or contigs.';
Comment on column CONTIGNOTEANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column CONTIGNOTEANNOTATION.CONTIG_ID is 'FK to CONTIG.CONTIG_ID.';
Comment on column CONTIGNOTEANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CONTIGNOTEANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column CONTIGNOTEANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column CONTIGNOTEANNOTATION.BUD_ID is 'From BUD.NOTE.NOTE_NO for SEQ_CHANGE_ARCHIVE.';
Comment on column CONTIGNOTEANNOTATION.NOTE_TYPE is 'What type of data the note is about (Chromosome).';
Comment on column CONTIGNOTEANNOTATION.DISPLAY_NAME is 'Public display name.';
Comment on column CONTIGNOTEANNOTATION.NOTE is 'Note or comment.';
Comment on column CONTIGNOTEANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CONTIGNOTEANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table DNASEQUENCEANNOTATION is 'Current DNA sequence details for contig, chromosomal, or plasmid features.';
Comment on column DNASEQUENCEANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column DNASEQUENCEANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column DNASEQUENCEANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column DNASEQUENCEANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column DNASEQUENCEANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column DNASEQUENCEANNOTATION.BUD_ID is 'From BUD.SEQ.SEQ_NO.';
Comment on column DNASEQUENCEANNOTATION.SO_ID is 'FK to SO.SO_ID.';
Comment on column DNASEQUENCEANNOTATION.DNA_TYPE is 'Type of DNA sequence (CODING, 1KB, GENOMIC).';
Comment on column DNASEQUENCEANNOTATION.CONTIG_ID is 'FK to CONTIG.CONTIG_ID.';
Comment on column DNASEQUENCEANNOTATION.SEQ_VERSION is 'Date of the sequence version.';
Comment on column DNASEQUENCEANNOTATION.COORD_VERSION is 'Date of the coordinate version.';
Comment on column DNASEQUENCEANNOTATION.GENOMERELEASE_ID is 'FK to GENOMERELEASE.GENOMERELEASE_ID.';
Comment on column DNASEQUENCEANNOTATION.START_INDEX is 'Start coordinate.';
Comment on column DNASEQUENCEANNOTATION.END_INDEX is 'End coordinate.';
Comment on column DNASEQUENCEANNOTATION.STRAND is 'Which strand the sequence is on (Watson = +, Crick = -, None = 0).';
Comment on column DNASEQUENCEANNOTATION.FILE_HEADER is 'Fasta header line of the download file.';
Comment on column DNASEQUENCEANNOTATION.DOWNLOAD_FILENAME is 'User interface download filename.';
Comment on column DNASEQUENCEANNOTATION.FILE_ID is 'FK to FILE.FILE_ID.';
Comment on column DNASEQUENCEANNOTATION.RESIDUES is 'DNA sequence of the feature.';
Comment on column DNASEQUENCEANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DNASEQUENCEANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table DNASUBSEQUENCE is 'Current DNA sequence details for subfeatures.';
Comment on column DNASUBSEQUENCE.DNASUBSEQUENCE_ID is  'Unique identifier (Oracle sequence).';
Comment on column DNASUBSEQUENCE.ANNOTATION_ID is 'FK to DNASEQUENCEANNOTATION.ANNOTATION_ID.';
Comment on column DNASUBSEQUENCE.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column DNASUBSEQUENCE.DISPLAY_NAME is 'Public display name.';
Comment on column DNASUBSEQUENCE.BUD_ID is 'From BUD.SEQ.SEQ_NO.';
Comment on column DNASUBSEQUENCE.SO_ID is 'FK to the SO.SO_ID.';
Comment on column DNASUBSEQUENCE.RELATIVE_START_INDEX is 'Relative start coordinate based on the dbentity (feature).';
Comment on column DNASUBSEQUENCE.RELATIVE_END_INDEX is 'Relative stop coordinate based on the dbentity (feature).';
Comment on column DNASUBSEQUENCE.CONTIG_START_INDEX is 'Start coordinate based on the contig.';
Comment on column DNASUBSEQUENCE.CONTIG_END_INDEX is 'Stop coordinate based on the contig.';
Comment on column DNASUBSEQUENCE.SEQ_VERSION is 'Date of the sequence version.';
Comment on column DNASUBSEQUENCE.COORD_VERSION is 'Date of the coordinate version.';
Comment on column DNASUBSEQUENCE.GENOMERELEASE_ID is 'FK to GENOMERELEASE.GENOMERELEASE_ID.';
Comment on column DNASUBSEQUENCE.FILE_HEADER is 'Fasta header line of the download file.';
Comment on column DNASUBSEQUENCE.DOWNLOAD_FILENAME is 'User interface download filename.';
Comment on column DNASUBSEQUENCE.FILE_ID is 'FK to FILE.FILE_ID.';
Comment on column DNASUBSEQUENCE.RESIDUES is 'DNA subfeature sequence.';
Comment on column DNASUBSEQUENCE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DNASUBSEQUENCE.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table ENZYMEANNOTATION is 'EC number annotations.';
Comment on column ENZYMEANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column ENZYMEANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column ENZYMEANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column ENZYMEANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column ENZYMEANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column ENZYMEANNOTATION.BUD_ID is 'Not from BUD.';
Comment on column ENZYMEANNOTATION.EC_ID is 'FK to EC.EC_ID.';
Comment on column ENZYMEANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ENZYMEANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table EXPRESSIONANNOTATION is 'High throughput gene expression annotations from GEO.';
Comment on column EXPRESSIONANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column EXPRESSIONANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column EXPRESSIONANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EXPRESSIONANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column EXPRESSIONANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column EXPRESSIONANNOTATION.BUD_ID is 'Not from BUD.';
Comment on column EXPRESSIONANNOTATION.DATASETSAMPLE_ID is 'FK to DATASAMPLE.DATASAMPLE_ID.';
Comment on column EXPRESSIONANNOTATION.EXPRESSION_VALUE is 'Numerical value of the expression annotation.';
Comment on column EXPRESSIONANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EXPRESSIONANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table GENINTERACTIONANNOTATION is 'Genetic interaction annotations from BioGRID.';
Comment on column GENINTERACTIONANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column GENINTERACTIONANNOTATION.DBENTITY1_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column GENINTERACTIONANNOTATION.DBENTITY2_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column GENINTERACTIONANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GENINTERACTIONANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column GENINTERACTIONANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column GENINTERACTIONANNOTATION.BUD_ID is 'From BUD.INTERACTION.INTERACTION_NO.';
Comment on column GENINTERACTIONANNOTATION.PHENOTYPE_ID is 'FK to PHENOTYPE.PHENOTYPE_ID.';
Comment on column GENINTERACTIONANNOTATION.BIOGRID_EXPERIMENTAL_SYSTEM is 'Experimental system as defined by BIOGRID.';
Comment on column GENINTERACTIONANNOTATION.ANNOTATION_TYPE is 'Type of annotation (high-throughput, manually curated).';
Comment on column GENINTERACTIONANNOTATION.BAIT_HIT is 'Direction of the genetic interaction (Bait-Hit, Hit-Bait).';
Comment on column GENINTERACTIONANNOTATION.DESCRIPTION is 'Extended description or note.';
Comment on column GENINTERACTIONANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GENINTERACTIONANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table GOANNOTATION is 'Gene Ontology annotations.';
Comment on column GOANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column GOANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column GOANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GOANNOTATION.BUD_ID is 'From BUD.GO_ANNOTATION.GO_ANNOTATION_NO.';
Comment on column GOANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column GOANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column GOANNOTATION.GO_ID is 'FK to GO.GO_ID.';
Comment on column GOANNOTATION.ECO_ID is 'FK to ECO.ECO_ID.';
Comment on column GOANNOTATION.ANNOTATION_TYPE is 'Type of GO annotation (high-throughput, manually curated, computational).';
Comment on column GOANNOTATION.GO_QUALIFIER is 'Qualifier of the GO annotation (enables, involved in, part of, NOT, colocalizes_with, contributed_to).';
Comment on column GOANNOTATION.DATE_ASSIGNED is 'Date the GO annotation was assigned or last reviewed.';
Comment on column GOANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GOANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table GOSUPPORTINGEVIDENCE is 'Evidence to support the GO annotation (column 8 of the GAF file).';
Comment on column GOSUPPORTINGEVIDENCE.GOSUPPORTINGEVIDENCE_ID is 'Unique identifier (Oracle sequence).';
Comment on column GOSUPPORTINGEVIDENCE.ANNOTATION_ID is 'FK to GOANNOTATION.ANNOTATION_ID.';
Comment on column GOSUPPORTINGEVIDENCE.GROUP_ID is 'A grouping number.';
Comment on column GOSUPPORTINGEVIDENCE.DBXREF_ID is 'External cross reference identifier.';
Comment on column GOSUPPORTINGEVIDENCE.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column GOSUPPORTINGEVIDENCE.EVIDENCE_TYPE is 'How the supporting evidence is associated with the GO annotation (with, from).';
Comment on column GOSUPPORTINGEVIDENCE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GOSUPPORTINGEVIDENCE.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table GOEXTENSION is 'Cross references used to qualify or enhance the GO annotation (column 16 of the GAF file).';
Comment on column GOEXTENSION.GOEXTENSION_ID is 'Unique identifier (Oracle sequence).';
Comment on column GOEXTENSION.ANNOTATION_ID is 'FK to GOANNOTATION.ANNOTATION_ID.';
Comment on column GOEXTENSION.GROUP_ID is 'A grouping number.';
Comment on column GOEXTENSION.DBXREF_ID is 'External cross reference identifier.';
Comment on column GOEXTENSION.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column GOEXTENSION.RO_ID is 'FK to RO.RO_ID.';
Comment on column GOEXTENSION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GOEXTENSION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table GOSLIMANNOTATION is 'A subset of GO annotations that provide a broad overview, often used to summarize results.';
Comment on column GOSLIMANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column GOSLIMANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column GOSLIMANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GOSLIMANNOTATION.BUD_ID is 'From BUD.GO_SET.GO_SET_NO.';
Comment on column GOSLIMANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column GOSLIMANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column GOSLIMANNOTATION.GOSLIM_ID is 'FK to GOSLIM.GOSLIM_ID.';
Comment on column GOSLIMANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GOSLIMANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table LITERATUREANNOTATION is 'Literature topics or categories assigned to references.';
Comment on column LITERATUREANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column LITERATUREANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column LITERATUREANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column LITERATUREANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column LITERATUREANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column LITERATUREANNOTATION.BUD_ID is 'From BUD.LIT_GUIDE.LIT_GUIDE_NO.';
Comment on column LITERATUREANNOTATION.TOPIC is 'Topic or category assigned to a reference (Additional Literature, Omics, Primary Literature, Reviews).';
Comment on column LITERATUREANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column LITERATUREANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table LOCUSNOTEANNOTATION is 'Historical and informative notes about loci and their sequences.';
Comment on column LOCUSNOTEANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column LOCUSNOTEANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column LOCUSNOTEANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column LOCUSNOTEANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column LOCUSNOTEANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column LOCUSNOTEANNOTATION.BUD_ID is 'From BUD.NOTE.NOTE_NO.';
Comment on column LOCUSNOTEANNOTATION.NOTE_TYPE is 'What type of data the note is about (Locus, Sequence).';
Comment on column LOCUSNOTEANNOTATION.DISPLAY_NAME is 'Public display name.';
Comment on column LOCUSNOTEANNOTATION.NOTE is 'Note or comment.';
Comment on column LOCUSNOTEANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column LOCUSNOTEANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PATHWAYANNOTATION is 'Annotations associated with a pathway.';
Comment on column PATHWAYANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column PATHWAYANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column PATHWAYANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PATHWAYANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column PATHWAYANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column PATHWAYANNOTATION.BUD_ID is 'Not from BUD.';
Comment on column PATHWAYANNOTATION.PATHWAY_ID is 'FK to PATHWAYDBENTITY.DBENTITY_ID.';
Comment on column PATHWAYANNOTATION.EC_ID is 'FK to EC.EC_ID.';
Comment on column PATHWAYANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PATHWAYANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PHENOTYPEANNOTATION is 'Annotations associated with a phenotype.';
Comment on column PHENOTYPEANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column PHENOTYPEANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column PHENOTYPEANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PHENOTYPEANNOTATION.BUD_ID is 'From BUD.PHENO_ANNOTATION.PHENO_ANNOTATION_NO.';
Comment on column PHENOTYPEANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column PHENOTYPEANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column PHENOTYPEANNOTATION.PHENOTYPE_ID is 'FK to PHENOTYPE.PHENOTYPE_ID.';
Comment on column PHENOTYPEANNOTATION.EXPERIMENT_ID is 'FK to APO.APO_ID.';
Comment on column PHENOTYPEANNOTATION.MUTANT_ID is 'FK to APO.APO_ID.';
Comment on column PHENOTYPEANNOTATION.ALLELE_ID is 'FK to ALLELE.ALLELE_ID.';
Comment on column PHENOTYPEANNOTATION.REPORTER_ID is 'FK to REPORTER.REPORTER_ID.';
Comment on column PHENOTYPEANNOTATION.ASSAY_ID is 'FK to OBI.OBI_ID.';
Comment on column PHENOTYPEANNOTATION.STRAIN_NAME is 'Additional information about the strain background.';
Comment on column PHENOTYPEANNOTATION.DETAILS is 'Details about the phenotype that are not related to the experimental conditions.';
Comment on column PHENOTYPEANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PHENOTYPEANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PHENOTYPEANNOTATION_COND is 'Conditions associated with a phenotype annotation.';
Comment on column PHENOTYPEANNOTATION_COND.CONDITION_ID is 'Unique identifier (Oracle sequence).';
Comment on column PHENOTYPEANNOTATION_COND.ANNOTATION_ID is 'FK to PHENOTYPEANNOTATION.ANNOTATION_ID.';
Comment on column PHENOTYPEANNOTATION_COND.CONDITION_TYPE is 'Type of the condition (Temperature, Chemical, Media, Phase, etc.).';
Comment on column PHENOTYPEANNOTATION_COND.CONDITION_NAME is 'Specific name of the condition.';
Comment on column PHENOTYPEANNOTATION_COND.CONDITION_VALUE is 'Value of the condition, often numeric.';
Comment on column PHENOTYPEANNOTATION_COND.CONDITION_UNIT is 'Unit associated with a numerical condition value (C, hr, %, mM, etc.).';
Comment on column PHENOTYPEANNOTATION_COND.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PHENOTYPEANNOTATION_COND.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PHYSINTERACTIONANNOTATION is 'Physical interaction annotations from BioGRID.';
Comment on column PHYSINTERACTIONANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column PHYSINTERACTIONANNOTATION.DBENTITY1_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column PHYSINTERACTIONANNOTATION.DBENTITY2_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column PHYSINTERACTIONANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PHYSINTERACTIONANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column PHYSINTERACTIONANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column PHYSINTERACTIONANNOTATION.BUD_ID is 'From BUD.INTERACTION.INTERACTION_NO.';
Comment on column PHYSINTERACTIONANNOTATION.PSIMOD_ID is 'FK to PSIMOD.PSIMOD_ID.';
Comment on column PHYSINTERACTIONANNOTATION.BIOGRID_EXPERIMENTAL_SYSTEM is 'Experimental system as defined by BIOGRID.';
Comment on column PHYSINTERACTIONANNOTATION.ANNOTATION_TYPE is 'Type of annotation (high-throughput, manually curated).';
Comment on column PHYSINTERACTIONANNOTATION.BAIT_HIT is 'Direction of the genetic interaction (Bait-Hit, Hit-Bait).';
Comment on column PHYSINTERACTIONANNOTATION.DESCRIPTION is 'Extended description or note.';
Comment on column PHYSINTERACTIONANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PHYSINTERACTIONANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table POSTTRANSLATIONANNOTATION is 'Post-translational protein modification annotations.';
Comment on column POSTTRANSLATIONANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column POSTTRANSLATIONANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column POSTTRANSLATIONANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column POSTTRANSLATIONANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column POSTTRANSLATIONANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column POSTTRANSLATIONANNOTATION.SITE_INDEX is 'Start coordinate of the PTM.';
Comment on column POSTTRANSLATIONANNOTATION.SITE_RESIDUE is 'Residue of the PTM.';
Comment on column POSTTRANSLATIONANNOTATION.PSIMOD_ID is	'FK to PSIMOD.PSIMOD_ID.';
Comment on column POSTTRANSLATIONANNOTATION.MODIFIER_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column POSTTRANSLATIONANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column POSTTRANSLATIONANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PROTEINDOMAINANNOTATION is 'Protein domains as predicted by InterProScan.';
Comment on column PROTEINDOMAINANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column PROTEINDOMAINANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column PROTEINDOMAINANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PROTEINDOMAINANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column PROTEINDOMAINANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column PROTEINDOMAINANNOTATION.BUD_ID is 'Not from BUD.';
Comment on column PROTEINDOMAINANNOTATION.PROTEINDOMAIN_ID is 'FK to PROTEINDOMAIN.PROTEINDOMAIN_ID.';
Comment on column PROTEINDOMAINANNOTATION.START_INDEX is 'Start coordinate of the protein domain relative to the locus.';
Comment on column PROTEINDOMAINANNOTATION.END_INDEX is 'End coordinate of the protein domain relative to the locus.';
Comment on column PROTEINDOMAINANNOTATION.DATE_OF_RUN is 'When the InterProScan analysis was run.';
Comment on column PROTEINDOMAINANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PROTEINDOMAINANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PROTEINEXPTANNOTATION is 'Protein experiment data gathered from literature.';
Comment on column PROTEINEXPTANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column PROTEINEXPTANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column PROTEINEXPTANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PROTEINEXPTANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column PROTEINEXPTANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column PROTEINEXPTANNOTATION.BUD_ID is 'Not from BUD.';
Comment on column PROTEINEXPTANNOTATION.EXPERIMENT_TYPE is 'Type of protein experiment (abundance, localization).';
Comment on column PROTEINEXPTANNOTATION.DATA_VALUE is 'Protein experimental value.';
Comment on column PROTEINEXPTANNOTATION.DATA_UNIT is 'Units for the protein experimental value.';
Comment on column PROTEINEXPTANNOTATION.ASSAY_ID is 'FK to OBI.OBI_ID.';
Comment on column PROTEINEXPTANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PROTEINEXPTANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PROTEINEXPTANNOTATION_COND is 'Conditions associated with a protein experiment annotation.';
Comment on column PROTEINEXPTANNOTATION_COND.CONDITION_ID is 'Unique identifier (Oracle sequence).';
Comment on column PROTEINEXPTANNOTATION_COND.ANNOTATION_ID is 'FK to PROTEINEXPTANNOTATION.ANNOTATION_ID.';
Comment on column PROTEINEXPTANNOTATION_COND.CONDITION_TYPE is 'Type of the condition (Temperature, Chemical, Media, Phase, etc.).';
Comment on column PROTEINEXPTANNOTATION_COND.CONDITION_NAME is 'Specific name of the condition.';
Comment on column PROTEINEXPTANNOTATION_COND.CONDITION_VALUE is 'Value of the condition, often numeric.';
Comment on column PROTEINEXPTANNOTATION_COND.CONDITION_UNIT is 'Unit associated with a numerical condition value (C, hr, %, mM, etc.).';
Comment on column PROTEINEXPTANNOTATION_COND.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PROTEINEXPTANNOTATION_COND.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PROTEINSEQUENCEANNOTATION is 'Current protein sequence information.';
Comment on column PROTEINSEQUENCEANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column PROTEINSEQUENCEANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column PROTEINSEQUENCEANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PROTEINSEQUENCEANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column PROTEINSEQUENCEANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column PROTEINSEQUENCEANNOTATION.BUD_ID is 'From BUD.PROTEIN.INFO.';
Comment on column PROTEINSEQUENCEANNOTATION.CONTIG_ID is 'FK to CONTIG.CONTIG_ID.';
Comment on column PROTEINSEQUENCEANNOTATION.SEQ_VERSION is 'Date of the protein sequence release.';
Comment on column PROTEINSEQUENCEANNOTATION.COORD_VERSION is 'Date of the protein coordinate release.';
Comment on column PROTEINSEQUENCEANNOTATION.GENOMERELEASE_ID is 'FK to GENOMERELEASE.GENOMERELEASE_ID.';
Comment on column PROTEINSEQUENCEANNOTATION.FILE_ID is 'FK to FILE.FILE_ID.';
Comment on column PROTEINSEQUENCEANNOTATION.FILE_HEADER is 'Fasta header line of the download file.';
Comment on column PROTEINSEQUENCEANNOTATION.DOWNLOAD_FILENAME is 'User interface download filename.';
Comment on column PROTEINSEQUENCEANNOTATION.RESIDUES is 'Current sequence of the protein.';
Comment on column PROTEINSEQUENCEANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PROTEINSEQUENCEANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PROTEINSEQUENCE_DETAIL is 'Properties of the current protein sequence.';
Comment on column PROTEINSEQUENCE_DETAIL.DETAIL_ID is 'Unique identifier (Oracle sequence).';
Comment on column PROTEINSEQUENCE_DETAIL.ANNOTATION_ID is 'FK to PROTEINSEQUENCEANNOTATION.ANNOTATION_ID.';
Comment on column PROTEINSEQUENCE_DETAIL.BUD_ID is 'From BUD.PROTEIN.INFO and BUD.PROTEIN_DETAIL.';
Comment on column PROTEINSEQUENCE_DETAIL.MOLECULAR_WEIGHT is 'Molecular weight of the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.PROTEIN_LENGTH is 'Length of the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.N_TERM_SEQ is 'N terminal sequence of the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.C_TERM_SEQ is 'C terminal sequence of the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.PI is 'Isoelectric point of the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.CAI is 'Codon adaptation index.';
Comment on column PROTEINSEQUENCE_DETAIL.CODON_BIAS is 'Codon bias of the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.FOP_SCORE is 'Frequency of optimal condons (ratio of optimal codons to synonymous codons).';
Comment on column PROTEINSEQUENCE_DETAIL.GRAVY_SCORE is 'General average hydropathicity score for the hypothetical translated gene product.';
Comment on column PROTEINSEQUENCE_DETAIL.AROMATICITY_SCORE is 'Frequency of aromatic amino acids (Phe, Tyr, Trp) in the hypothetical translated gene product.';
Comment on column PROTEINSEQUENCE_DETAIL.ALIPHATIC_INDEX is 'Relative volume occupied by aliphatic side chains (alanine, valine, isoleucine, and leucine).';
Comment on column PROTEINSEQUENCE_DETAIL.INSTABILITY_INDEX is 'Correlation between stability of a protein and its dipeptide composition.';
Comment on column PROTEINSEQUENCE_DETAIL.ALA is 'Number of alanines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.ARG is 'Number of arginines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.ASN is 'Number of asparagines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.ASP is 'Number of aspartic acids in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.CYS is 'Number of cysteines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.GLN is 'Number of glutamines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.GLU is 'Number of glutamic acids in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.GLY is 'Number of glycines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.HIS is 'Number of histidines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.ILE is 'Number of isoleucines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.LEU is 'Number of leucines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.LYS is 'Number of lysines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.MET is 'Number of methionines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.PHE is 'Number of phenylalanines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.PRO is 'Number of prolines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.SER is 'Number of serines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.THR is 'Number of thereonines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.TRP is 'Number of tryptophans in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.TYR is 'Number of tyrosines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.VAL is 'Number of valines in the protein.';
Comment on column PROTEINSEQUENCE_DETAIL.HYDROGEN is 'Number of hydrogen atoms in the protein atomic composition.';
Comment on column PROTEINSEQUENCE_DETAIL.SULFUR is 'Number of sulfur atoms in the protein atomic composition.';
Comment on column PROTEINSEQUENCE_DETAIL.NITROGEN is 'Number of nitrogen atoms in the protein atomic composition.';
Comment on column PROTEINSEQUENCE_DETAIL.OXYGEN is 'Number of oxygen atoms in the protein atomic composition.';
Comment on column PROTEINSEQUENCE_DETAIL.CARBON is 'Number of carbon atoms in the protein atomic composition.';
Comment on column PROTEINSEQUENCE_DETAIL.NO_CYS_EXT_COEFF is 'No Cys residues appear as half cystines.';
Comment on column PROTEINSEQUENCE_DETAIL.ALL_CYS_EXT_COEFF is 'All Cys residues appear as half cystines.';
Comment on column PROTEINSEQUENCE_DETAIL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PROTEINSEQUENCE_DETAIL.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Curation tables */

Comment on table CURATION is 'Tasks and notes associated with locus and reference curation.';
Comment on column CURATION.CURATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column CURATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column CURATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CURATION.BUD_ID is 'Not from BUD.';
Comment on column CURATION.SUBCLASS is 'Type of curation (Locus, Reference).';
Comment on column CURATION.CURATION_TASK is 'Type of curation task (Classical phenotype information,Delay,Fast Track,
GO information,GO needs review,Gene model,Headline needs review,Headline reviewed,Headline information,High Priority,Homology/Disease,
HTP phenotype,Non-phenotype HTP,Not yet curated,Paragraph needs review,Paragraph not needed,Pathways,Phenotype needs review,
Phenotype uncuratable,Post-translational modifications,Regulation information).';
Comment on column CURATION.CURATOR_COMMENT is 'Comment or note.';
Comment on column CURATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CURATION.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table AUTHORRESPONSE is 'Replies from the Author Reponse System.';
Comment on column AUTHORRESPONSE.CURATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column AUTHORRESPONSE.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column AUTHORRESPONSE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column AUTHORRESPONSE.BUD_ID is 'Not from BUD.';
Comment on column AUTHORRESPONSE.COLLEAGUE_ID is 'FK to COLLEAGUE.COLLEAGUE_ID.';
Comment on column AUTHORRESPONSE.AUTHOR_EMAIL is 'Email address of the author.';
Comment on column AUTHORRESPONSE.HAS_NOVEL_RESEARCH is 'Whether there is novel research in the paper.';
Comment on column AUTHORRESPONSE.HAS_LARGE_SCALE_DATA is 'Whether there is large scale data in the paper.';
Comment on column AUTHORRESPONSE.HAS_FAST_TRACK_TAG is 'Whether a fast track tag has been attached to this paper.';
Comment on column AUTHORRESPONSE.CURATOR_CHECKED_DATASETS is 'Whether a curator has checked the datasets in the paper.';
Comment on column AUTHORRESPONSE.CURATOR_CHECKED_GENELIST is 'Whether a curator has checked the submitted gene list.';
Comment on column AUTHORRESPONSE.NO_ACTION_REQUIRED is 'Whether any further action is needed.';
Comment on column AUTHORRESPONSE.RESEARCH_RESULTS is 'Research results submitted by the author.';
Comment on column AUTHORRESPONSE.GENE_LIST is 'List of gene names contained in the paper submitted by the author.';
Comment on column AUTHORRESPONSE.DATASET_DESCRIPTION is 'Description of the dataset submitted by the author.';
Comment on column AUTHORRESPONSE.OTHER_DESCRIPTION is 'Any other description submitted by the author.';
Comment on column AUTHORRESPONSE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column AUTHORRESPONSE.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table REFERENCETRIAGE is 'Papers obtained via the reference triage system.';
Comment on column REFERENCETRIAGE.CURATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCETRIAGE.PMID is 'Pubmed identifier for the paper.';
Comment on column REFERENCETRIAGE.CITATION is 'Full citation of the paper.';
Comment on column REFERENCETRIAGE.FULLTEXT_URL is 'URL to the fulltext of the paper.';
Comment on column REFERENCETRIAGE.ABSTRACT is 'Paper abstract.';
Comment on column REFERENCETRIAGE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCETRIAGE.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table COLLEAGUETRIAGE is 'New and update colleague submissions.';
Comment on column COLLEAGUETRIAGE.CURATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column COLLEAGUETRIAGE.TRIAGE_TYPE is 'Type of colleague submission (New, Update).';
Comment on column COLLEAGUETRIAGE.COLLEAGUE_ID is 'FK to COLLEAGUE.COLLEAGUE_ID.';
Comment on column COLLEAGUETRIAGE.COLLEAGUE_DATA is 'JSON object of the submitted colleague information.';
Comment on column COLLEAGUETRIAGE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column COLLEAGUETRIAGE.CREATED_BY  is 'Username of the person who entered the record into the database.';

/* Archive tables */

Comment on table ARCH_LOCUSCHANGE is 'Archived changes to a locus that have historical significance.';
Comment on column ARCH_LOCUSCHANGE.ARCHIVE_ID is 'Unique identifier (Oracle sequence).';
Comment on column ARCH_LOCUSCHANGE.DBENTITY_ID is 'From DBENTITY.DBENTITY_ID.';
Comment on column ARCH_LOCUSCHANGE.SOURCE_ID is 'From SOURCE.SOURCE_ID.';
Comment on column ARCH_LOCUSCHANGE.BUD_ID is 'From BUD.ARCHIVE.ARCHIVE_NO.';
Comment on column ARCH_LOCUSCHANGE.CHANGE_TYPE is 'Type of locus change (Status, Qualifier, Gene name).';
Comment	on column ARCH_LOCUSCHANGE.OLD_VALUE is 'Previous value before change.';
Comment on column ARCH_LOCUSCHANGE.NEW_VALUE is 'New value after change.';
Comment on column ARCH_LOCUSCHANGE.DATE_CHANGED is 'Date the change was made.';
Comment on column ARCH_LOCUSCHANGE.CHANGED_BY is 'Username of the person who made the change.';
Comment on column ARCH_LOCUSCHANGE.DATE_ARCHIVED is 'Date the record was archived.';

Comment on table ARCH_LITERATUREANNOTATION is 'Archived literature topics or categories assigned to references.';
Comment on column ARCH_LITERATUREANNOTATION.ARCHIVE_ID is 'Unique identifier (Oracle sequence).';
Comment on column ARCH_LITERATUREANNOTATION.ANNOTATION_ID is 'From LITERATUREANNOTATION.ANNOTATION_ID.';
Comment on column ARCH_LITERATUREANNOTATION.DBENTITY_ID is 'From DBENTITY.DBENTITY_ID.';
Comment on column ARCH_LITERATUREANNOTATION.SOURCE_ID is 'From SOURCE.SOURCE_ID.';
Comment on column ARCH_LITERATUREANNOTATION.REFERENCE_ID is 'From REFERENCEBENTITY.DBENTITY_ID.';
Comment on column ARCH_LITERATUREANNOTATION.TAXONOMY_ID is 'From TAXONOMY.TAXONOMY_ID.';
Comment on column ARCH_LITERATUREANNOTATION.BUD_ID is 'From BUD.LIT_GUIDE.LIT_GUIDE_NO.';
Comment on column ARCH_LITERATUREANNOTATION.TOPIC is 'Topic or category assigned to a reference.';
Comment on column ARCH_LITERATUREANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ARCH_LITERATUREANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';
Comment on column ARCH_LITERATUREANNOTATION.DATE_ARCHIVED is 'Date the record was archived.';

Comment on table ARCH_CONTIG is 'Archived whole chromosome or contig sequences.';
Comment on column ARCH_CONTIG.ARCHIVE_ID is 'Unique identifier (Oracle sequence).';
Comment on column ARCH_CONTIG.CONTIG_ID is 'From CONTIG.CONTIG_ID.';
Comment on column ARCH_CONTIG.FORMAT_NAME is 'Unique name to create download files.';
Comment on column ARCH_CONTIG.DISPLAY_NAME is 'Public display name.';
Comment on column ARCH_CONTIG.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column ARCH_CONTIG.SOURCE_ID is 'From SOURCE.SOURCE_ID.';
Comment on column ARCH_CONTIG.BUD_ID is 'From BUD.SEQ.SEQ_NO.';
Comment on column ARCH_CONTIG.TAXONOMY_ID is 'From TAXONOMY.TAXONOMY_ID.';
Comment on column ARCH_CONTIG.SO_ID is 'From SO.SO_ID (contig, chromosome, plasmid).';
Comment on column ARCH_CONTIG.CENTROMERE_START is 'Start coordinate of the centromere.';
Comment on column ARCH_CONTIG.CENTROMERE_END is 'End coordinate of the centromere.';
Comment on column ARCH_CONTIG.GENBANK_ACCESSION is 'GenBank Accession id including version number (e.g., BK006939.2).';
Comment on column ARCH_CONTIG.GI_NUMBER is 'GenInfo identifier assigned by NCBI.';
Comment on column ARCH_CONTIG.REFSEQ_ID is 'REFerence SEQuence identifier assigned by NCBI.';
Comment on column ARCH_CONTIG.REFERENCE_CHROMOSOME_ID is 'From CONTIG.CONTIG_ID.';
Comment on column ARCH_CONTIG.REFERENCE_START is 'Start coordinate relative to the reference sequence S288C.';
Comment on column ARCH_CONTIG.REFERENCE_END is 'End coordinate relative to the reference sequence S288C.';
Comment on column ARCH_CONTIG.REFERENCE_PERCENT_IDENTITY is 'Percent identify to the reference sequence S288C.';
Comment on column ARCH_CONTIG.REFERENCE_ALIGNMENT_LENGTH is 'Length of the sequence alignment to the reference sequence S288C.';
Comment on column ARCH_CONTIG.SEQ_VERSION is 'From BUD.SEQ.SEQ_VERSION.';
Comment on column ARCH_CONTIG.COORD_VERSION is 'From BUD.FEAT_LOCATION.COORD_VERSION.';
Comment on column ARCH_CONTIG.GENOMERELEASE_ID is 'From GENOMERELEASE.GENOMERELEASE_ID.';
Comment on column ARCH_CONTIG.FILE_HEADER is 'Header line of the download file.';
Comment on column ARCH_CONTIG.DOWNLOAD_FILENAME is 'User interface download filename.';
Comment on column ARCH_CONTIG.FILE_ID is 'From FILEDBENTITY.DBENTITY_ID.';
Comment on column ARCH_CONTIG.RESIDUES is 'DNA sequence of the contig, chromosome or plasmid.';
Comment on column ARCH_CONTIG.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ARCH_CONTIG.CREATED_BY  is 'Username of the person who entered the record into the database.';
Comment on column ARCH_CONTIG.DATE_ARCHIVED is 'Date the record was archived.';

Comment	on table ARCH_CONTIGCHANGE is 'Archived individual changes to the S288C reference chromosome sequence.';
Comment on column ARCH_CONTIGCHANGE.ARCHIVE_ID is 'Unique identifier (Oracle sequence).';
Comment on column ARCH_CONTIGCHANGE.CONTIG_ID is 'From CONTIG.CONTIG_ID.';
Comment on column ARCH_CONTIGCHANGE.BUD_ID is 'From BUD.SEQ_CHANGE_ARCHIVE.SEQ_CHANGE_ARCHIVE_NO.';
Comment on column ARCH_CONTIGCHANGE.GENOMERELEASE_ID is 'From GENOMERELEASE.GENOMERELEASE_ID.';
Comment on column ARCH_CONTIGCHANGE.CHANGE_TYPE is 'Type of sequence change (Deletion, Insertion, Substitution).';
Comment on column ARCH_CONTIGCHANGE.CHANGE_MIN_COORD is 'Minimum coordinate of the change relative to the whole chromosome.';
Comment on column ARCH_CONTIGCHANGE.CHANGE_MAX_COORD is 'Maximum coordinate of the change relative to the whole chromosome.';
Comment on column ARCH_CONTIGCHANGE.OLD_VALUE is 'Sequence prior to the change.';
Comment on column ARCH_CONTIGCHANGE.NEW_VALUE is 'Sequence after the change.';
Comment on column ARCH_CONTIGCHANGE.DATE_CHANGED is 'Date the change was made.';
Comment on column ARCH_CONTIGCHANGE.CHANGED_BY is 'Username of the person who made the change.';
Comment on column ARCH_CONTIGCHANGE.DATE_ARCHIVED is 'Date the record was archived.';

Comment on table ARCH_DNASEQANNOTATION is 'Archived DNA sequence details for contig, chromosomal, or plasmid features.';
Comment on column ARCH_DNASEQANNOTATION.ARCHIVE_ID is 'Unique identifier (Oracle sequence).';
Comment on column ARCH_DNASEQANNOTATION.ANNOTATION_ID is 'From DNASEQUENCEANNOTATION.ANNOTATION_ID.';
Comment on column ARCH_DNASEQANNOTATION.DBENTITY_ID is 'From DBENTITY.DBENTITY_ID.';
Comment on column ARCH_DNASEQANNOTATION.SOURCE_ID is 'From SOURCE.SOURCE_ID.';
Comment on column ARCH_DNASEQANNOTATION.TAXONOMY_ID is 'From TAXONOMY.TAXONOMY_ID.';
Comment on column ARCH_DNASEQANNOTATION.REFERENCE_ID is 'From REFERENCEBENTITY.DBENTITY_ID.';
Comment on column ARCH_DNASEQANNOTATION.BUD_ID is 'From BUD.SEQ.SEQ_NO.';
Comment on column ARCH_DNASEQANNOTATION.SO_ID is 'From SO.SO_ID.';
Comment on column ARCH_DNASEQANNOTATION.DNA_TYPE is 'Type of DNA sequence (CODING, 1KB, GENOMIC).';
Comment on column ARCH_DNASEQANNOTATION.CONTIG_ID is 'From CONTIG.CONTIG_ID.';
Comment on column ARCH_DNASEQANNOTATION.SEQ_VERSION is 'Date of the sequence version.';
Comment on column ARCH_DNASEQANNOTATION.COORD_VERSION is 'Date of the coordinate version.';
Comment on column ARCH_DNASEQANNOTATION.GENOMERELEASE_ID is 'From GENOMERELEASE.GENOMERELEASE_ID.';
Comment on column ARCH_DNASEQANNOTATION.START_INDEX is 'Start coordinate.';
Comment on column ARCH_DNASEQANNOTATION.END_INDEX is 'End coordinate.';
Comment on column ARCH_DNASEQANNOTATION.STRAND is 'Which strand the sequence is on (Watson = +, Crick = -, None = 0).';
Comment on column ARCH_DNASEQANNOTATION.FILE_HEADER is 'Fasta header line of the download file.';
Comment on column ARCH_DNASEQANNOTATION.DOWNLOAD_FILENAME is 'User interface download filename.';
Comment on column ARCH_DNASEQANNOTATION.FILE_ID is 'From FILE.FILE_ID.';
Comment on column ARCH_DNASEQANNOTATION.RESIDUES is 'DNA sequence of the feature.';
Comment on column ARCH_DNASEQANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ARCH_DNASEQANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';
Comment on column ARCH_DNASEQANNOTATION.DATE_ARCHIVED is 'Date the record was archived.';

Comment on table ARCH_DNASUBSEQUENCE is 'Archived DNA sequence details for subfeatures.';
Comment on column ARCH_DNASUBSEQUENCE.ARCHIVE_ID is 'Unique identifier (Oracle sequence).';
Comment on column ARCH_DNASUBSEQUENCE.DNASUBSEQUENCE_ID is 'From DNASUBSEQUENCE.DNASUBSEQUENCE_ID.';
Comment on column ARCH_DNASUBSEQUENCE.ANNOTATION_ID is 'From DNASEQUENCEANNOTATION.ANNOTATION_ID.';
Comment on column ARCH_DNASUBSEQUENCE.DBENTITY_ID is 'From DBENTITY.DBENTITY_ID.';
Comment on column ARCH_DNASUBSEQUENCE.DISPLAY_NAME is 'Public display name.';
Comment on column ARCH_DNASUBSEQUENCE.BUD_ID is 'From BUD.SEQ.SEQ_NO.';
Comment on column ARCH_DNASUBSEQUENCE.SO_ID is 'From SO.SO_ID.';
Comment on column ARCH_DNASUBSEQUENCE.RELATIVE_START_INDEX is 'Relative start coordinate based on the dbentity (feature).';
Comment on column ARCH_DNASUBSEQUENCE.RELATIVE_END_INDEX is 'Relative stop coordinate based on the dbentity (feature).';
Comment on column ARCH_DNASUBSEQUENCE.CONTIG_START_INDEX is 'Start coordinate based on the contig.';
Comment on column ARCH_DNASUBSEQUENCE.CONTIG_END_INDEX is 'Stop coordinate based on the contig.';
Comment on column ARCH_DNASUBSEQUENCE.SEQ_VERSION is 'Date of the sequence version.';
Comment on column ARCH_DNASUBSEQUENCE.COORD_VERSION is 'Date of the coordinate version.';
Comment on column ARCH_DNASUBSEQUENCE.GENOMERELEASE_ID is 'From GENOMERELEASE.GENOMERELEASE_ID.';
Comment on column ARCH_DNASUBSEQUENCE.FILE_HEADER is 'Fasta header line of the download file.';
Comment on column ARCH_DNASUBSEQUENCE.DOWNLOAD_FILENAME is 'User interface download filename.';
Comment on column ARCH_DNASUBSEQUENCE.FILE_ID is 'From FILE.FILE_ID.';
Comment on column ARCH_DNASUBSEQUENCE.RESIDUES is 'DNA subfeature sequence.';
Comment on column ARCH_DNASUBSEQUENCE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ARCH_DNASUBSEQUENCE.CREATED_BY is 'Username of the person who entered the record into the database.';
Comment on column ARCH_DNASUBSEQUENCE.DATE_ARCHIVED is 'Date the record was archived.';

Comment on table ARCH_PROTEINSEQANNOTATION is 'Archived protein sequence information.';
Comment on column ARCH_PROTEINSEQANNOTATION.ARCHIVE_ID is 'Unique identifier (Oracle sequence).';
Comment on column ARCH_PROTEINSEQANNOTATION.ANNOTATION_ID is 'FROM PROTEINSEQUENCEANNOTATION.ANNOTATION_ID.';
Comment on column ARCH_PROTEINSEQANNOTATION.DBENTITY_ID is 'From DBENTITY.DBENTITY_ID.';
Comment on column ARCH_PROTEINSEQANNOTATION.SOURCE_ID is 'From SOURCE.SOURCE_ID.';
Comment on column ARCH_PROTEINSEQANNOTATION.REFERENCE_ID is 'From REFERENCEBENTITY.DBENTITY_ID.';
Comment on column ARCH_PROTEINSEQANNOTATION.TAXONOMY_ID is 'From TAXONOMY.TAXONOMY_ID.';
Comment on column ARCH_PROTEINSEQANNOTATION.BUD_ID is 'From BUD.PROTEIN.INFO.';
Comment on column ARCH_PROTEINSEQANNOTATION.CONTIG_ID is 'From CONTIG.CONTIG_ID.';
Comment on column ARCH_PROTEINSEQANNOTATION.SEQ_VERSION is 'Date of the protein sequence release.';
Comment on column ARCH_PROTEINSEQANNOTATION.GENOMERELEASE_ID is 'From GENOMERELEASE.GENOMERELEASE_ID.';
Comment on column ARCH_PROTEINSEQANNOTATION.FILE_HEADER is 'Fasta header line of the download file.';
Comment on column ARCH_PROTEINSEQANNOTATION.DOWNLOAD_FILENAME is 'User interface download filename.';
Comment on column ARCH_PROTEINSEQANNOTATION.FILE_ID is 'From FILE.FILE_ID.';
Comment on column ARCH_PROTEINSEQANNOTATION.RESIDUES is 'Sequence of the protein.';
Comment on column ARCH_PROTEINSEQANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ARCH_PROTEINSEQANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';
Comment on column ARCH_PROTEINSEQANNOTATION.DATE_ARCHIVED is 'Date the record was archived.';
