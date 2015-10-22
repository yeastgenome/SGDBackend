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
Comment on column DBUSER.EMAIL is 'Email address of the database user.';
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
Comment on column RO.ROID is 'Relation identifier  (e.g., RO:0002434).';
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
Comment on column EC.EC_NUMBER is 'Enzyme Commission number (e.g., EC 3.1.26.5).';
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
Comment on column ECO.ECOID is 'Evidence ontology identifier (e.g. ECO:0000168).';
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
Comment on column OBI.OBIID is 'Biomedical investigations identifier (e.g. OBI:0000185).';
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
Comment on column PSIMOD.PSIMODID is 'Protein modification ontology identifier (e.g., MOD:01152).';
Comment on column PSIMOD.DESCRIPTION is 'Description or comment.';
Comment on column PSIMOD.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PSIMOD.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table PSIMOD_URL is 'URLs associated with the protein modification ontology.';
Comment on column PSIMOD_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column PSIMOD_URL.DISPLAY_NAME is 'Public display name (BioPortal, OLS).';
Comment on column PSIMOD_URL.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column PSIMOD_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column PSIMOD_URL.BUD_ID is 'Not from BUD.';
Comment on column PSIMOD_URL.PSIMOD_ID is 'FK to PSIMOD.PSIMOD_ID.';
Comment on column PSIMOD_URL.URL_TYPE is 'Type of URL (BioPortal, OLS).';
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
Comment on column SO.SOID is 'Sequence Ontology identifier (e.g., SO:0000368).';
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
Comment on column TAXONOMY.TAXID is 'Taxonomy identifier assigned by NCBI (from BUD.TAXONOMY.TAXON_ID).';
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
Comment on column DBENTITY.SUBCLASS is 'What object inherits from DBENTITY (FILE, LOCUS, REFERENCE, STRAIN).';
Comment on column DBENTITY.DBENTITY_STATUS is 'Current state of the dbentity (Active, Merged, Deleted, Archived).';
Comment on column DBENTITY.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column DBENTITY.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Locus */

Comment on table LOCUSDBENTITY is 'Features located on a sequence, that are associate with a locus. Inherits from DBENTITY.';
Comment on column LOCUSDBENTITY.DBENTITY_ID is 'Unique identifier (Oracle sequence).';
Comment on column LOCUSDBENTITY.SYSTEMATIC_NAME is 'Unique name for the dbentity. Subfeatures have a number appended after the systematic name.';
Comment on column LOCUSDBENTITY.SO_ID is 'FK to SO.SO_ID.';
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
Comment on column REFERENCE_DELETED.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_DELETED.CREATED_BY is 'Username of the person who entered the record into the database.';

/* File */

Comment on table FILEDBENTITY is 'Details about files loaded into or dumped from the database or associated with the Download Server.';
Comment on column FILEDBENTITY.DBENTITY_ID is 'Unique identifier (Oracle sequence).';
Comment on column FILEDBENTITY.MD5SUM is 'The 128-bit MD5 hash or checksum of the file.';
Comment on column FILEDBENTITY.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column FILEDBENTITY.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column FILEDBENTITY.PREVIOUS_FILE_NAME is 'File name on the Download Server.';
Comment on column FILEDBENTITY.FILE_STATUS is 'Status of the file (current, archived, removed)';
Comment on column FILEDBENTITY.FILE_DATA_TYPE is 'File type, FK to EDAM data.';
Comment on column FILEDBENTITY.FILE_OPERATION is 'A function or process performed generating the file output, FK to EDAM operation.';
Comment on column FILEDBENTITY.FILE_VERSION is 'File version or release date.';
Comment on column FILEDBENTITY.FILE_FORMAT is 'Standard file format, FK to EDAM format.';
Comment on column FILEDBENTITY.FILE_EXTENSION is 'File name extension (.gff, .tsv, .fsa.gz, .jpg, etc.).';

Comment on table FILE_RELATION is 'Relationship between two files.';
Comment on column FILE_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column FILE_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column FILE_RELATION.BUD_ID is 'Not in BUD.';
Comment on column FILE_RELATION.PARENT_ID is 'FK to FILE_ID.';
Comment on column FILE_RELATION.CHILD_ID is 'FK to FILE_ID.';
Comment on column FILE_RELATION.RO_ID is 'FK TO RO.RO_ID.';
Comment on column FILE_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column FILE_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

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
Comment on column COLLEAGUE_ASSOCIATION.ASSOCIATION_TYPE is 'Type of association or relationship (Associate, Lab member).';
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

Comment on table CONTIG is 'Whole chromosome or contig sequences.';
Comment on column CONTIG.CONTIG_ID is 'Unique identifier (Oracle sequence).';
Comment on column CONTIG.FORMAT_NAME is 'Unique name to create download files.';
Comment on column CONTIG.DISPLAY_NAME is 'Public display name.';
Comment on column CONTIG.OBJ_URL is 'URL of the object (relative for local links or complete for external links).';
Comment on column CONTIG.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CONTIG.BUD_ID is 'PK from BUD.SEQ.SEQ_NO.';
Comment on column CONTIG.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column CONTIG.IS_CHROMOSOME is 'Whether the contig is a fully assembled chromosome.';
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
Comment on column CONTIG.HEADER is 'Header line of the download file.';
Comment on column CONTIG.FILE_ID is 'FK to FILEDBENTITY.DBENTITY_ID.';
Comment on column CONTIG.RESIDUES is 'Full DNA sequence of the chromosome or contig.';
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
Comment on column LITERATUREANNOTATION.BUD_ID is 'From BUD.LIT_GUIDE.LIT_GUIDE_NO.';
Comment on column LITERATUREANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column LITERATUREANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column LITERATUREANNOTATION.TOPIC is 'Topic or category assigned to a reference (Additional Literature, Omics, Primary Literature, Reviews).';
Comment on column LITERATUREANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column LITERATUREANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

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
Comment on column PHENOTYPEANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PHENOTYPEANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table PHENOTYPEANNOTATION_DETAIL is 'Treatments, conditions and other details associated with a phenotype annotation.';
Comment on column PHENOTYPEANNOTATION_DETAIL.DETAIL_ID is 'Unique identifier (Oracle sequence).';
Comment on column PHENOTYPEANNOTATION_DETAIL.ANNOTATION_ID is 'FK to PHENOTYPEANNOTATION.ANNOTATION_ID.';
Comment on column PHENOTYPEANNOTATION_DETAIL.CATEGORY is 'Broad category for grouping types of phenotype details.';
Comment on column PHENOTYPEANNOTATION_DETAIL.DETAIL_TYPE is 'Type of phenotype detail (Chemical pending, Temperature, Media, etc.).';
Comment on column PHENOTYPEANNOTATION_DETAIL.DETAIL_VALUE is 'Actual phenotype detail value (nystatin, elevated temperature, YPD, etc.).';
Comment on column PHENOTYPEANNOTATION_DETAIL.DETAIL_NUMBER is 'Numerical value associated with the phenotype detail value (12, 0.6, 37, etc.).';
Comment on column PHENOTYPEANNOTATION_DETAIL.DETAIL_UNIT is 'Unit associated with the phenotype detail number (C, hr, %, mM, etc.).';
Comment on column PHENOTYPEANNOTATION_DETAIL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column PHENOTYPEANNOTATION_DETAIL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table POSTTRANSLATIONALANNOTATION is 'Post-translational protein modification annotations.';
Comment on column POSTTRANSLATIONALANNOTATION.ANNOTATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column POSTTRANSLATIONALANNOTATION.DBENTITY_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column POSTTRANSLATIONALANNOTATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column POSTTRANSLATIONALANNOTATION.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column POSTTRANSLATIONALANNOTATION.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column POSTTRANSLATIONALANNOTATION.SITE_INDEX is 'Start coordinate of the PTM.';
Comment on column POSTTRANSLATIONALANNOTATION.SITE_RESIDUE is 'Residue of the PTM.';
Comment on column POSTTRANSLATIONALANNOTATION.PSIMOD_ID is	'FK to PSIMOD.PSIMOD_ID.';
Comment on column POSTTRANSLATIONALANNOTATION.MODIFIER_ID is 'FK to DBENTITY.DBENTITY_ID.';
Comment on column POSTTRANSLATIONALANNOTATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column POSTTRANSLATIONALANNOTATION.CREATED_BY is 'Username of the person who entered the record into the database.';

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
