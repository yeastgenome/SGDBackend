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
Comment on column SGDID.DISPLAY_NAME is 'Public display name.';
Comment on column SGDID.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column SGDID.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column SGDID.BUD_ID is 'PK from BUD.DBXREF.DBXREF_NO.';
Comment on column SGDID.SUBCLASS is 'Type of dbentity assigned the SGDID (LOCUS, REFERENCE, STRAIN, FILE).';
Comment on column SGDID.SGDID_STATUS is 'State of the SGDID (Primary, Secondary, Deleted, Unassigned).';
Comment on column SGDID.DESCRIPTION is 'Comment about or reason why the SGDID was deleted.';
Comment on column SGDID.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SGDID.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Ontologies */

Comment on table RO is 'Relation Ontology (RO) used to describe data relationships.';
Comment on column RO.RELATION_ONTOLOGY_ID is 'Unique identifier (Oracle sequence).';
Comment on column RO.FORMAT_NAME is 'Unique name to create download files.';
Comment on column RO.DISPLAY_NAME is 'Public display name.';
Comment on column RO.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column RO.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column RO.BUD_ID is 'Not in BUD.';
Comment on column RO.RO_ID is 'Relation identifier  (e.g., RO:0002434).';
Comment on column RO.DESCRIPTION is 'Description or comment.';
Comment on column RO.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column RO.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table RO_URL is 'URLs associated with the relation ontology.';
Comment on column RO_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column RO_URL.DISPLAY_NAME is 'Public display name.';
Comment on column RO_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column RO_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column RO_URL.BUD_ID is 'Not in BUD';
Comment on column RO_URL.RELATION_ONTOLOGY_ID is 'FK to RO.RELATION_ONTOLOGY_ID.';
Comment on column RO_URL.URL_TYPE is 'Type of URL (Ontobee).';
Comment on column RO_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column RO_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table RO_RELATION is 'Relationship between two relations.';
Comment on column RO_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column RO_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column RO_RELATION.BUD_ID is 'Not in BUD.';
Comment on column RO_RELATION.PARENT_ID is 'FK to RO.RELATION_ONTOLOGY_ID.';
Comment on column RO_RELATION.CHILD_ID is 'FK to RO.RELATION_ONTOLOGY_ID.';
Comment on column RO_RELATION.RELATION_TYPE is 'Type of relation (is a).';
Comment on column RO_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column RO_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table CHEMICAL is 'Chemical Entities of Biological Interest (ChEBI) from the EBI.';
Comment on column CHEMICAL.CHEMICAL_ID is 'Unique identifier (Oracle sequence).';
Comment on column CHEMICAL.FORMAT_NAME is 'Unique name to create download files.';
Comment on column CHEMICAL.DISPLAY_NAME is 'Public display name.';
Comment on column CHEMICAL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column CHEMICAL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CHEMICAL.BUD_ID is 'PK from BUD.CV_TERM.CV_TERM_NO.';
Comment on column CHEMICAL.CHEBI_ID is 'Chemical identifier from the EBI (e.g., CHEBI:58471) or new term requests (NTR).';
Comment on column CHEMICAL.DESCRIPTION is 'Description or comment.';
Comment on column CHEMICAL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CHEMICAL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table CHEMICAL_ALIAS is 'Other names or synonyms for the chemical.';
Comment on column CHEMICAL_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column CHEMICAL_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column CHEMICAL_ALIAS.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column CHEMICAL_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CHEMICAL_ALIAS.BUD_ID is 'PK from BUD.CVTERM_SYNONYM.CVTERM_SYNONYM_NO.';
Comment on column CHEMICAL_ALIAS.CHEMICAL_ID is 'FK to CHEMICAL.CHEMICAL_ID.';
Comment on column CHEMICAL_ALIAS.ALIAS_TYPE is 'Type of alias (EXACT, RELATED, Secondary ChEBI ID, IUPAC name).';
Comment on column CHEMICAL_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CHEMICAL_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table CHEMICAL_URL is 'URLs associated with chemicals.';
Comment on column CHEMICAL_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column CHEMICAL_URL.DISPLAY_NAME is 'Public display name (ChEBI).';
Comment on column CHEMICAL_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column CHEMICAL_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CHEMICAL_URL.BUD_ID is 'PK from BUD.URL.URL_NO';
Comment on column CHEMICAL_URL.CHEMICAL_ID is 'FK to CHEMICAL.CHEMICAL_ID.';
Comment on column CHEMICAL_URL.URL_TYPE is 'Type of URL (ChEBI).';
Comment on column CHEMICAL_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CHEMICAL_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table CHEMICAL_RELATION is 'Relationship between two chemicals.';
Comment on column CHEMICAL_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column CHEMICAL_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column CHEMICAL_RELATION.BUD_ID is 'PK from BUD.CVTERM_RELATIONSIHP.CVTERM_RELATIONSIHP_NO.';
Comment on column CHEMICAL_RELATION.PARENT_ID is 'FK to CHEMICAL_ID.';
Comment on column CHEMICAL_RELATION.CHILD_ID is 'FK to CHEMICAL_ID.';
Comment on column CHEMICAL_RELATION.RELATION_ONTOLOGY_ID is 'FK to RO.RELATION_ONTOLOGY_ID.';
Comment on column CHEMICAL_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column CHEMICAL_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table ENZYME is 'Enzyme Commission (EC) numbers based on chemical reactions catalyzed by enzymes.';
Comment on column ENZYME.ENZYME_ID is 'Unique identifier (Oracle sequence).';
Comment on column ENZYME.FORMAT_NAME is 'Unique name to create download files.';
Comment on column ENZYME.DISPLAY_NAME is 'Public display name (e.g., 3.1.26.5).';
Comment on column ENZYME.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column ENZYME.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column ENZYME.BUD_ID is 'PK from BUD.DBXREF.DBXREF_NO.';
Comment on column ENZYME.DESCRIPTION is 'Description or comment.';
Comment on column ENZYME.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ENZYME.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table ENZYME_ALIAS is 'Other names or synonyms for the enzyme.';
Comment on column ENZYME_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column ENZYME_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column ENZYME_ALIAS.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column ENZYME_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column ENZYME_ALIAS.BUD_ID is 'Not in BUD.';
Comment on column ENZYME_ALIAS.ENZYME_ID is 'FK to ENZYME.ENZYME_ID.';
Comment on column ENZYME_ALIAS.ALIAS_TYPE is 'Type of alias (Synonym).';
Comment on column ENZYME_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ENZYME_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table ENZYME_URL is 'URLs associated with contigs.';
Comment on column ENZYME_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column ENZYME_URL.DISPLAY_NAME is 'Public display name (ExPASy, BRENDA).';
Comment on column ENZYME_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column ENZYME_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column ENZYME_URL.BUD_ID is 'Not from BUD';
Comment on column ENZYME_URL.ENZYME_ID is 'FK to ENZYME.ENZYME_ID.';
Comment on column ENZYME_URL.URL_TYPE is 'Type of URL (ExPASy, BRENDA).';
Comment on column ENZYME_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column ENZYME_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table EVIDENCE is 'Evidence Ontology (ECO) describes types of scientific evidence.';
Comment on column EVIDENCE.EVIDENCE_ID is 'Unique identifier (Oracle sequence).';
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
Comment on column EVIDENCE_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column EVIDENCE_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column EVIDENCE_ALIAS.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column EVIDENCE_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EVIDENCE_ALIAS.BUD_ID is 'Not from BUD.';
Comment on column EVIDENCE_ALIAS.EVIDENCE_ID is 'FK to EVIDENCE.EVIDENCE_ID.';
Comment on column EVIDENCE_ALIAS.ALIAS_TYPE is 'Type of alias (BROAD, EXACT, RELATED, NARROW).';
Comment on column EVIDENCE_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EVIDENCE_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table EVIDENCE_URL is 'URLs associated with evidence types.';
Comment on column EVIDENCE_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column EVIDENCE_URL.DISPLAY_NAME is 'Public display name (BioPortal, OLS).';
Comment on column EVIDENCE_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column EVIDENCE_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EVIDENCE_URL.BUD_ID is 'Not from BUD.';
Comment on column EVIDENCE_URL.EVIDENCE_ID is 'FK to EVIDENCE.EVIDENCE_ID.';
Comment on column EVIDENCE_URL.URL_TYPE is 'Type of URL (BioPortal, OLS).';
Comment on column EVIDENCE_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EVIDENCE_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table EVIDENCE_RELATION is 'Relationship between two evidence types.';
Comment on column EVIDENCE_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column EVIDENCE_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column EVIDENCE_RELATION.BUD_ID is 'Not from BUD.';
Comment on column EVIDENCE_RELATION.PARENT_ID is 'FK to EVIDENCE.EVIDENCE_ID.';
Comment on column EVIDENCE_RELATION.CHILD_ID is 'FK to EVIDENCE.EVIDENCE_ID.';
Comment on column EVIDENCE_RELATION.RELATION_ONTOLOGY_ID is 'FK to RO.RELATION_ONTOLOGY_ID.';
Comment on column EVIDENCE_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column EVIDENCE_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table KEYWORD is 'Controlled vocabulary to describe broad categories of biology, used to filter or group data.';
Comment on column KEYWORD.KEYWORD_ID is 'Unique identifier (Oracle sequence).';
Comment on column KEYWORD.FORMAT_NAME is 'Unique name to create download files.';
Comment on column KEYWORD.DISPLAY_NAME is 'Public display name.';
Comment on column KEYWORD.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column KEYWORD.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column KEYWORD.BUD_ID is 'From BUD.KEYWORD.KEYWORD_NO and SPELL tags.';
Comment on column KEYWORD.DESCRIPTION is 'Description or comment.';
Comment on column KEYWORD.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column KEYWORD.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table OBINVESTIGATION is 'Ontology for Biomedical Investigations (OBI) describes biomedical studies.';
Comment on column OBINVESTIGATION.OBINVESTIGATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column OBINVESTIGATION.FORMAT_NAME is 'Unique name to create download files.';
Comment on column OBINVESTIGATION.DISPLAY_NAME is 'Public display name.';
Comment on column OBINVESTIGATION.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column OBINVESTIGATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column OBINVESTIGATION.BUD_ID is 'Not from BUD.';
Comment on column OBINVESTIGATION.OBI_ID is 'Biomedical investigations identifier (e.g. OBI:0000185).';
Comment on column OBINVESTIGATION.DESCRIPTION is 'Description or comment.';
Comment on column OBINVESTIGATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column OBINVESTIGATION.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table OBINVESTIGATION_URL is 'URLs associated with biomedical investigations.';
Comment on column OBINVESTIGATION_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column OBINVESTIGATION_URL.DISPLAY_NAME is 'Public display name (Ontobee).';
Comment on column OBINVESTIGATION_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column OBINVESTIGATION_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column OBINVESTIGATION_URL.BUD_ID is 'Not from BUD.';
Comment on column OBINVESTIGATION_URL.OBINVESTIGATION_ID is 'FK to OBINVESTIGATION.OBINVESTIGATION_ID.';
Comment on column OBINVESTIGATION_URL.URL_TYPE is 'Type of URL (Ontobee).';
Comment on column OBINVESTIGATION_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column OBINVESTIGATION_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table OBINVESTIGATION_RELATION is 'Relationship between two biomedical investigation ontology terms.';
Comment on column OBINVESTIGATION_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column OBINVESTIGATION_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column OBINVESTIGATION_RELATION.BUD_ID is 'Not from BUD.';
Comment on column OBINVESTIGATION_RELATION.PARENT_ID is 'FK to OBINVESTIGATION.OBINVESTIGATION_ID.';
Comment on column OBINVESTIGATION_RELATION.CHILD_ID is 'FK to OBINVESTIGATION.OBINVESTIGATION_ID.';
Comment on column OBINVESTIGATION_RELATION.RELATION_ONTOLOGY_ID is 'FK to RO.RELATION_ONTOLOGY_ID.';
Comment on column OBINVESTIGATION_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column OBINVESTIGATION_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table SEQUENCEFEATURE is 'Sequence features as defined by the Sequence Ontology (SO).';
Comment on column SEQUENCEFEATURE.SEQUENCEFEATURE_ID is 'Unique identifier (Oracle sequence).';
Comment on column SEQUENCEFEATURE.FORMAT_NAME is 'Unique name to create download files.';
Comment on column SEQUENCEFEATURE.DISPLAY_NAME is 'Public display name.';
Comment on column SEQUENCEFEATURE.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column SEQUENCEFEATURE.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column SEQUENCEFEATURE.BUD_ID is 'Not from BUD.';
Comment on column SEQUENCEFEATURE.SO_ID is 'Sequence Ontology identifier (e.g., SO:0000368).';
Comment on column SEQUENCEFEATURE.DESCRIPTION is 'Description or comment.';
Comment on column SEQUENCEFEATURE.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SEQUENCEFEATURE.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table SEQUENCEFEATURE_ALIAS is 'Other names or synonyms for the sequence feature.';
Comment on column SEQUENCEFEATURE_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column SEQUENCEFEATURE_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column SEQUENCEFEATURE_ALIAS.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column SEQUENCEFEATURE_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column SEQUENCEFEATURE_ALIAS.BUD_ID is 'Not from BUD.';
Comment on column SEQUENCEFEATURE_ALIAS.SEQUENCEFEATURE_ID is 'FK to SEQUENCEFEATURE.SEQUENCEFEATURE_ID.';
Comment on column SEQUENCEFEATURE_ALIAS.ALIAS_TYPE is 'Type of alias (BROAD, EXACT, RELATED, NARROW).';
Comment on column SEQUENCEFEATURE_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SEQUENCEFEATURE_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table SEQUENCEFEATURE_URL is 'URLs associated with sequence features.';
Comment on column SEQUENCEFEATURE_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column SEQUENCEFEATURE_URL.DISPLAY_NAME is 'Public display name (MISO, OLS).';
Comment on column SEQUENCEFEATURE_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column SEQUENCEFEATURE_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column SEQUENCEFEATURE_URL.BUD_ID is 'Not from BUD.';
Comment on column SEQUENCEFEATURE_URL.SEQUENCEFEATURE_ID is 'FK to SEQUENCEFEATURE.SEQUENCEFEATURE_ID.';
Comment on column SEQUENCEFEATURE_URL.URL_TYPE is 'Type of URL (MISO, OLS).';
Comment on column SEQUENCEFEATURE_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SEQUENCEFEATURE_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table SEQUENCEFEATURE_RELATION is 'Relationship between two sequence features.';
Comment on column SEQUENCEFEATURE_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column SEQUENCEFEATURE_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column SEQUENCEFEATURE_RELATION.BUD_ID is 'Not from BUD.';
Comment on column SEQUENCEFEATURE_RELATION.PARENT_ID is 'FK to SEQUENCEFEATURE.SEQUENCEFEATURE_ID.';
Comment on column SEQUENCEFEATURE_RELATION.CHILD_ID is 'FK to SEQUENCEFEATURE.SEQUENCEFEATURE_ID.';
Comment on column SEQUENCEFEATURE_RELATION.RELATION_ONTOLOGY_ID is 'FK to RO.RELATION_ONTOLOGY_ID.';
Comment on column SEQUENCEFEATURE_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column SEQUENCEFEATURE_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

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
Comment on column TAXONOMY_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
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
Comment on column TAXONOMY_RELATION.RELATION_ONTOLOGY_ID is 'FK to RO.RELATION_ONTOLOGY_ID.';
Comment on column TAXONOMY_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column TAXONOMY_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Dbentity (Locus, Reference, Strain, File) */

Comment on table DBENTITY is 'Primary objects that are the focus of curation. They are strain independent and require an SGDID.';
Comment on column DBENTITY.DBENTITY_ID is 'Unique identifier (Oracle sequence).';
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
Comment on column LOCUSDBENTITY.DBENTITY_ID is 'Unique identifier (Oracle sequence).';
Comment on column LOCUSDBENTITY.SYSTEMATIC_NAME is 'Unique name for the dbentity. Subfeatures have a number appended after the systematic name.';
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
Comment on column LOCUS_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
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
Comment on column LOCUS_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column LOCUS_URL.DISPLAY_NAME is 'Public display name.';
Comment on column LOCUS_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
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
Comment on column LOCUS_RELATION.RELATION_ONTOLOGY_ID is 'FK to RO.RELATION_ONTOLOGY_ID.';
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
Comment on column STRAIN_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
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
Comment on column BOOK.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
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
Comment on column JOURNAL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
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
Comment on column REFERENCEDBENTITY.PUBMED_ID is 'PMID of the reference from NCBI.';
Comment on column REFERENCEDBENTITY.PUBMED_CENTRAL_ID is 'PMCID of the reference from NCBI.';
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
Comment on column REFERENCE_ALIAS.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column REFERENCE_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column REFERENCE_ALIAS.BUD_ID is 'PK from BUD.DBXREF.DBXREF_NO.';
Comment on column REFERENCE_ALIAS.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_ALIAS.ALIAS_TYPE is 'Type of alias (Secondary SGDID).';
Comment on column REFERENCE_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REFERENCE_URL is 'URLs associated with references.';
Comment on column REFERENCE_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCE_URL.DISPLAY_NAME is 'Public display name.';
Comment on column REFERENCE_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column REFERENCE_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column REFERENCE_URL.BUD_ID is 'PK from BUD.URL.URL_NO.';
Comment on column REFERENCE_URL.REFERENCE_ID is 'FK to REFERENCEDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_URL.URL_TYPE is 'Type of URL (DOI full text, PMC full text, PubMed, PubMedCentral, Reference supplement).';
Comment on column REFERENCE_URL.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REFERENCE_REFTYPE is 'Links a reference with a reftype.';
Comment on column REFERENCE_REFTYPE.REFERENCE_REFTYPE_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCE_REFTYPE.DISPLAY_NAME is 'Public display name.';
Comment on column REFERENCE_REFTYPE.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
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
Comment on column REFERENCE_AUTHOR.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
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
Comment on column REFERENCE_UNLINK.LOCUS_ID is 'FK to LOCUSDBENTITY.DBENTITY_ID.';
Comment on column REFERENCE_UNLINK.BUD_ID is 'PK from BUD.REF_UNLINK.REF_UNLINK_NO.';
Comment on column REFERENCE_UNLINK.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_UNLINK.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table REFERENCE_DELETED is 'References permanently removed from the database via curator triage.';
Comment on column REFERENCE_DELETED.REFERENCE_DELETED_ID is 'Unique identifier (Oracle sequence).';
Comment on column REFERENCE_DELETED.PUBMED_ID is 'PubMed ID of the reference from NCBI.';
Comment on column REFERENCE_DELETED.SGDID is 'SGDID of the reference assigned before removal from the database.';
Comment on column REFERENCE_DELETED.BUD_ID is 'PK in BUD is PubMed ID.';
Comment on column REFERENCE_DELETED.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column REFERENCE_DELETED.CREATED_BY is 'Username of the person who entered the record into the database.';

/* File */

Comment on table FILEDBENTITY is 'Details about files loaded into or dumped from the database.';
Comment on column FILEDBENTITY.DBENTITY_ID is 'Unique identifier (Oracle sequence).';
Comment on column FILEDBENTITY.MD5SUM is 'The 128-bit MD5 hash or checksum of the file.';
Comment on column FILEDBENTITY.FILE_VERSION is 'Version or release of the file.';
Comment on column FILEDBENTITY.FILE_FORMAT is 'Standard file format.';
Comment on column FILEDBENTITY.FILE_EXTENSION is 'Extension of the file name.';
Comment on column FILEDBENTITY.FILE_CATEGORY is 'Type or category of file.';
Comment on column FILEDBENTITY.FILE_OUTPUT_TYPE is 'Description of the purpose or contents of the file.';
Comment on column FILEDBENTITY.REFERENCE_ID is 'FK to REFERENCEBENTITY.DBENTITY_ID.';
Comment on column FILEDBENTITY.TAXONOMY_ID is 'FK to TAXONOMY.TAXONOMY_ID, need species as well as strains.';

Comment on table FILE_RELATION is 'Relationship between two files.';
Comment on column FILE_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column FILE_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column FILE_RELATON.BUD_ID is 'Not in BUD.';
Comment on column FILE_RELATION.PARENT_ID is 'FK to FILE_ID.';
Comment on column FILE_RELATION.CHILD_ID is 'FK to FILE_ID.';
Comment on column FILE_RELATION.RELATION_ONTOLOGY_ID is 'FK TO RO.RELATION_ONTOLOGY_ID.';
Comment on column FILE_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column FILE_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Colleague */

Comment on table COLLEAGUE is 'A researcher or associate who registered with the database.';
Comment on column COLLEAGUE.COLLEAGUE_ID is 'Unique identifier (Oracle sequence).';
Comment on column COLLEAGUE.FORMAT_NAME is 'Unique name to create download files.';
Comment on column COLLEAGUE.DISPLAY_NAME is 'Public display name.';
Comment on column COLLEAGUE.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
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
Comment on column COLLEAGUE_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
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
Comment on column RESERVEDNAME.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
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

/* GO */

Comment on table GOTERM is 'Gene Ontology (GO) terms used to describe genes and gene products.';
Comment on column GOTERM.GOTERM_ID is 'Unique identifier (Oracle sequence).';
Comment on column GOTERM.FORMAT_NAME is 'Unique name to create download files.';
Comment on column GOTERM.DISPLAY_NAME is 'Public display name.';
Comment on column GOTERM.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column GOTERM.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GOTERM.BUD_ID is 'Not from BUD.';
Comment on column GOTERM.GO_ID is 'Gene Ontology identifier (e.g. GO:0016233).';
Comment on column GOTERM.GO_ASPECT is 'Three separate domains to describe gene products  (cellular component, biological process, molecular function).';
Comment on column GOTERM.DESCRIPTION is 'Description or comment.';
Comment on column GOTERM.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GOTERM.CREATED_BY  is 'Username of the person who entered the record into the database.';

Comment on table GOTERM_ALIAS is 'Other names or synonyms for a GO term.';
Comment on column GOTERM_ALIAS.ALIAS_ID is 'Unique identifier (Oracle sequence).';
Comment on column GOTERM_ALIAS.DISPLAY_NAME is 'Public display name.';
Comment on column GOTERM_ALIAS.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column GOTERM_ALIAS.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GOTERM_ALIAS.BUD_ID is 'Not from BUD.';
Comment on column GOTERM_ALIAS.GOTERM_ID is 'FK to GOTERM.GOTERM_ID.';
Comment on column GOTERM_ALIAS.ALIAS_TYPE is 'Type of alias (BROAD, EXACT, RELATED, NARROW).';
Comment on column GOTERM_ALIAS.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GOTERM_ALIAS.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table GOTERM_URL is 'URLs associated with GO terms.';
Comment on column GOTERM_URL.URL_ID is 'Unique identifier (Oracle sequence).';
Comment on column GOTERM_URL.DISPLAY_NAME is 'Public display name.';
Comment on column GOTERM_URL.OBJ_URL is 'URL of the object (relative for local links and complete for external links).';
Comment on column GOTERM_URL.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GOTERM_URL.BUD_ID is 'Not from BUD.';
Comment on column GOTERM_URL.GOTERM_ID is 'FK to GOTERM.GOTERM_ID.';
Comment on column GOTERM_URL.URL_TYPE is 'Type of URL (GO, Amigo).';
Comment on column GOTERM_URL.DATE_CREATED is 'Date the record was entered into the database.';                                                     \
Comment on column GOTERM_URL.CREATED_BY is 'Username of the person who entered the record into the database.';

Comment on table GOTERM_RELATION is 'Relationship between two GO terms.';
Comment on column GOTERM_RELATION.RELATION_ID is 'Unique identifier (Oracle sequence).';
Comment on column GOTERM_RELATION.SOURCE_ID is 'FK to SOURCE.SOURCE_ID.';
Comment on column GOTERM_RELATION.BUD_ID is 'Not from BUD.';
Comment on column GOTERM_RELATION.PARENT_ID is 'FK to GOTERM.GOTERM_ID.';
Comment on column GOTERM_RELATION.CHILD_ID is 'FK to GOTERM.GOTERM_ID.';
Comment on column GOTERM_RELATION.RELATION_TYPE is 'Type of relation (is a).';
Comment on column GOTERM_RELATION.DATE_CREATED is 'Date the record was entered into the database.';
Comment on column GOTERM_RELATION.CREATED_BY is 'Username of the person who entered the record into the database.';

/* Phenotype */

