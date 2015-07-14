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
Comment on column CHEMICAL_URL.URL_TYPE is 'Type of URL (External).';
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
Comment on column TAXONOMY_URL.NAME is 'Public display name (Taxonomy Browser).';
Comment on column TAXONOMY_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column TAXONOMY_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column TAXONOMY_URL.BUD_ID is 'Not from BUD.';
Comment on column TAXONOMY_URL.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID.';
Comment on column TAXONOMY_URL.URL_TYPE is 'Type of URL (External).';
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
