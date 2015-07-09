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

Comment on table SOURCE is 'Origin or source of the data'.;
Comment on column SOURCE.SOURCE_ID is 'Unique random identifier (Oracle sequence).';
Comment on column SOURCE.FORMAT_NAME is 'Unique name to create download files.';
Comment on column SOURCE.DISPLAY_NAME is 'Public display name.';
Comment on column SOURCE.OBJ_URL is 'Relative URL of the object.';
Comment on column SOURCE.BUD_ID is 'PK from BUD.CODE.CODE_NO.';
Comment on column SOURCE.DESCRIPTION is 'Description or comment.';
Comment on column SOURCE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SOURCE.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Taxonomy */

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
