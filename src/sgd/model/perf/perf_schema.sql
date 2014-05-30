/* Perf_Core */

DROP TABLE BIOENTITY CASCADE CONSTRAINTS;
CREATE TABLE BIOENTITY (
BIOENTITY_ID INTEGER NOT NULL, 
JSON VARCHAR2(4000) NOT NULL, 
CONSTRAINT BIOENTITY_PK PRIMARY KEY (BIOENTITY_ID) ) TABLESPACE PDATA1;
GRANT SELECT ON BIOENTITY TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON BIOENTITY TO AUXILIARY;

DROP TABLE LOCUSTAB CASCADE CONSTRAINTS;
CREATE TABLE LOCUSTAB (
BIOENTITY_ID INTEGER NOT NULL,
JSON VARCHAR2(4000) NOT NULL,
CONSTRAINT LOCUSTAB_PK PRIMARY KEY (BIOENTITY_ID) ) TABLESPACE PDATA1;
GRANT SELECT ON LOCUSTAB TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON LOCUSTAB TO AUXILIARY;

DROP TABLE LOCUSENTRY CASCADE CONSTRAINTS;
CREATE TABLE LOCUSENTRY (
BIOENTITY_ID INTEGER NOT NULL,
JSON VARCHAR2(4000) NOT NULL,
CONSTRAINT LOCUSENTRY_PK PRIMARY KEY (BIOENTITY_ID) ) TABLESPACE PDATA1;
GRANT SELECT ON LOCUSENTRY TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON LOCUSENTRY TO AUXILIARY;

DROP TABLE BIOCONCEPT CASCADE CONSTRAINTS;
CREATE TABLE BIOCONCEPT ( 
BIOCONCEPT_ID INTEGER NOT NULL, 
JSON CLOB NOT NULL,
CONSTRAINT BIOCONCEPT_PK PRIMARY KEY (BIOCONCEPT_ID) ) TABLESPACE PDATA1;
GRANT SELECT ON BIOCONCEPT TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON BIOCONCEPT TO AUXILIARY;

DROP TABLE REFERENCE CASCADE CONSTRAINTS;
CREATE TABLE REFERENCE ( 
REFERENCE_ID INTEGER NOT NULL, 
JSON CLOB NOT NULL,
CONSTRAINT REFERENCE_PK PRIMARY KEY (REFERENCE_ID) ) TABLESPACE PDATA2;
GRANT SELECT ON REFERENCE TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON REFERENCE TO AUXILIARY;

DROP TABLE BIBENTRY CASCADE CONSTRAINTS;
CREATE TABLE BIBENTRY (
REFERENCE_ID INTEGER NOT NULL,
JSON CLOB NOT NULL,
CONSTRAINT BIBENTRY_PK PRIMARY KEY (REFERENCE_ID) ) TABLESPACE PDATA2;
GRANT SELECT ON BIBENTRY TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON BIBENTRY TO AUXILIARY;

DROP TABLE BIOITEM CASCADE CONSTRAINTS;
CREATE TABLE BIOITEM (
BIOITEM_ID INTEGER NOT NULL,
JSON VARCHAR2(4000) NOT NULL,
CONSTRAINT BIOITEM_PK PRIMARY KEY (BIOITEM_ID) ) TABLESPACE PDATA1;
GRANT SELECT ON BIOITEM TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON BIOITEM TO AUXILIARY;

DROP TABLE AUTHOR CASCADE CONSTRAINTS;
CREATE TABLE AUTHOR (
AUTHOR_ID INTEGER NOT NULL,
JSON CLOB NOT NULL,
CONSTRAINT AUTHOR_PK PRIMARY KEY (AUTHOR_ID) ) TABLESPACE PDATA1;
GRANT SELECT ON AUTHOR TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON AUTHOR TO AUXILIARY;

DROP TABLE STRAIN CASCADE CONSTRAINTS;
CREATE TABLE STRAIN (
STRAIN_ID INTEGER NOT NULL,
JSON CLOB NOT NULL,
CONSTRAINT STRAIN_PK PRIMARY KEY (STRAIN_ID) ) TABLESPACE PDATA1;
GRANT SELECT ON STRAIN TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON STRAIN TO AUXILIARY;

DROP TABLE DISAMBIG CASCADE CONSTRAINTS;
CREATE TABLE DISAMBIG ( 
DISAMBIG_ID INTEGER NOT NULL, 
DISAMBIG_KEY VARCHAR2(200) NOT NULL, 
CLASS VARCHAR(40) NOT NULL, 
SUBCLASS VARCHAR(40), 
OBJ_ID INTEGER NOT NULL, 
CONSTRAINT DISAMBIG_PK PRIMARY KEY (DISAMBIG_ID), 
CONSTRAINT DISAMBIG_UK UNIQUE (DISAMBIG_KEY, CLASS, SUBCLASS) ) TABLESPACE PDATA2;
GRANT SELECT ON DISAMBIG TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON DISAMBIG TO AUXILIARY;
DROP SEQUENCE DISAMBIG_SEQ;
CREATE SEQUENCE DISAMBIG_SEQ NOCACHE;

/* Bioentity */
DROP TABLE BIOENTITY_GRAPH CASCADE CONSTRAINTS;
CREATE TABLE BIOENTITY_GRAPH (
BIOENTITY_GRAPH_ID INTEGER NOT NULL,
BIOENTITY_ID INTEGER NOT NULL,
CLASS VARCHAR2(40) NOT NULL CHECK (CLASS IN ('INTERACTION', 'REGULATION', 'LITERATURE', 'GO', 'PHENOTYPE')),
JSON CLOB,
CONSTRAINT BIOENTITY_GRAPH_PK PRIMARY KEY (BIOENTITY_GRAPH_ID),
CONSTRAINT BIOENTITY_GRAPH_UK UNIQUE (BIOENTITY_ID, CLASS)) TABLESPACE PDATA1;
CREATE INDEX BIOENTITY_GRAPH_FK_INDX ON BIOENTITY_GRAPH (BIOENTITY_ID) TABLESPACE PDATA1;
CREATE INDEX BIOENTITY_GRAPH_CLS_INDX ON BIOENTITY_GRAPH (CLASS) TABLESPACE PDATA1;
GRANT SELECT ON BIOENTITY_GRAPH TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON BIOENTITY_GRAPH TO AUXILIARY;
DROP SEQUENCE BIOENTITY_GRAPH_SEQ;
CREATE SEQUENCE BIOENTITY_GRAPH_SEQ NOCACHE;

DROP TABLE BIOENTITY_ENRICHMENT CASCADE CONSTRAINTS;
CREATE TABLE BIOENTITY_ENRICHMENT (
BIOENTITY_ENRICHMENT_ID INTEGER NOT NULL,
BIOENTITY_ID INTEGER NOT NULL,
CLASS VARCHAR2(40) NOT NULL CHECK (CLASS IN ('REGULATION_TARGET')),
JSON CLOB,
CONSTRAINT BIOENTITY_ENRICHMENT_PK PRIMARY KEY (BIOENTITY_ENRICHMENT_ID),
CONSTRAINT BIOENTITY_ENRICHMENT_UK UNIQUE (BIOENTITY_ID, CLASS)) TABLESPACE PDATA1;
CREATE INDEX BIOENTITY_ENRICHMENT_FK_INDX ON BIOENTITY_ENRICHMENT (BIOENTITY_ID) TABLESPACE PDATA1;
CREATE INDEX BIOENTITY_ENRICHMENT_CLS_INDX ON BIOENTITY_ENRICHMENT (CLASS) TABLESPACE PDATA1;
GRANT SELECT ON BIOENTITY_ENRICHMENT TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON BIOENTITY_ENRICHMENT TO AUXILIARY;
DROP SEQUENCE BIOENTITY_ENRICHMENT_SEQ;
CREATE SEQUENCE BIOENTITY_ENRICHMENT_SEQ NOCACHE;

DROP TABLE BIOENTITY_DETAILS CASCADE CONSTRAINTS;
CREATE TABLE BIOENTITY_DETAILS (
BIOENTITY_DETAILS_ID INTEGER NOT NULL,
BIOENTITY_ID INTEGER NOT NULL,
CLASS VARCHAR2(40) NOT NULL CHECK (CLASS IN ('REGULATION', 'INTERACTION', 'GO', 'PHENOTYPE', 'LITERATURE', 'BINDING', 'DOMAIN')),
JSON CLOB,
CONSTRAINT BIOENTITY_DETAILS_PK PRIMARY KEY (BIOENTITY_DETAILS_ID),
CONSTRAINT BIOENTITY_DETAILS_UK UNIQUE (BIOENTITY_ID, CLASS)) TABLESPACE PDATA2;
CREATE INDEX BIOENTITY_DETAILS_CLS_INDX ON BIOENTITY_DETAILS (CLASS) TABLESPACE PDATA2;
CREATE INDEX BIOENTITY_DETAILS_BIOENT_INDX ON BIOENTITY_DETAILS (BIOENTITY_ID, CLASS) TABLESPACE PDATA2;
GRANT SELECT ON BIOENTITY_DETAILS TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON BIOENTITY_DETAILS TO AUXILIARY;
DROP SEQUENCE BIOENTITY_DETAILS_SEQ;
CREATE SEQUENCE BIOENTITY_DETAILS_SEQ NOCACHE;

/* Bioconcept */

DROP TABLE BIOCONCEPT_GRAPH CASCADE CONSTRAINTS;
CREATE TABLE BIOCONCEPT_GRAPH (
BIOCONCEPT_GRAPH_ID INTEGER NOT NULL,
BIOCONCEPT_ID INTEGER NOT NULL,
CLASS VARCHAR2(40) NOT NULL CHECK (CLASS IN ('ONTOLOGY')),
JSON CLOB,
CONSTRAINT BIOCONCEPT_GRAPH_PK PRIMARY KEY (BIOCONCEPT_GRAPH_ID),
CONSTRAINT BIOCONCEPT_GRAPH_UK UNIQUE (BIOCONCEPT_ID, CLASS)) TABLESPACE PDATA1;
CREATE INDEX BIOCONCEPT_GRAPH_FK_INDX ON BIOCONCEPT_GRAPH (BIOCONCEPT_ID) TABLESPACE PDATA1;
GRANT SELECT ON BIOCONCEPT_GRAPH TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON BIOCONCEPT_GRAPH TO AUXILIARY;
DROP SEQUENCE BIOCONCEPT_GRAPH_SEQ;
CREATE SEQUENCE BIOCONCEPT_GRAPH_SEQ NOCACHE;

DROP TABLE BIOCONCEPT_DETAILS CASCADE CONSTRAINTS;
CREATE TABLE BIOCONCEPT_DETAILS (
BIOCONCEPT_DETAILS_ID INTEGER NOT NULL,
BIOCONCEPT_ID INTEGER NOT NULL,
CLASS VARCHAR2(40) NOT NULL CHECK (CLASS IN ('LOCUS', 'LOCUS_ALL_CHILDREN')),
JSON CLOB,
CONSTRAINT BIOCONCEPT_DETAILS_PK PRIMARY KEY (BIOCONCEPT_DETAILS_ID),
CONSTRAINT BIOCONCEPT_DETAILS_UK UNIQUE (BIOCONCEPT_ID, CLASS)) TABLESPACE PDATA2;
GRANT SELECT ON BIOCONCEPT_DETAILS TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON BIOCONCEPT_DETAILS TO AUXILIARY;
DROP SEQUENCE BIOCONCEPT_DETAILS_SEQ;
CREATE SEQUENCE BIOCONCEPT_DETAILS_SEQ NOCACHE;

/* Bioitem */
DROP TABLE BIOITEM_DETAILS CASCADE CONSTRAINTS;
CREATE TABLE BIOITEM_DETAILS (
BIOITEM_DETAILS_ID INTEGER NOT NULL,
BIOITEM_ID INTEGER NOT NULL,
CLASS VARCHAR2(40) NOT NULL CHECK (CLASS IN ('LOCUS')),
JSON CLOB,
CONSTRAINT BIOITEM_DETAILS_PK PRIMARY KEY (BIOITEM_DETAILS_ID),
CONSTRAINT BIOITEM_DETAILS_UK UNIQUE (BIOITEM_ID, CLASS)) TABLESPACE PDATA2;
GRANT SELECT ON BIOITEM_DETAILS TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON BIOITEM_DETAILS TO AUXILIARY;
DROP SEQUENCE BIOITEM_DETAILS_SEQ;
CREATE SEQUENCE BIOITEM_DETAILS_SEQ NOCACHE;

/* Reference */
DROP TABLE REFERENCE_DETAILS CASCADE CONSTRAINTS;
CREATE TABLE REFERENCE_DETAILS (
REFERENCE_DETAILS_ID INTEGER NOT NULL,
REFERENCE_ID INTEGER NOT NULL,
CLASS VARCHAR2(40) NOT NULL CHECK (CLASS IN ('REGULATION', 'INTERACTION', 'GO', 'PHENOTYPE', 'LITERATURE')),
JSON CLOB,
CONSTRAINT REFERENCE_DETAILS_PK PRIMARY KEY (REFERENCE_DETAILS_ID),
CONSTRAINT REFERENCE_DETAILS_UK UNIQUE (REFERENCE_ID, CLASS)) TABLESPACE PDATA2;
GRANT SELECT ON REFERENCE_DETAILS TO DBSELECT;
GRANT DELETE, INSERT, SELECT, UPDATE ON REFERENCE_DETAILS TO AUXILIARY;
DROP SEQUENCE REFERENCE_DETAILS_SEQ;
CREATE SEQUENCE REFERENCE_DETAILS_SEQ NOCACHE;




