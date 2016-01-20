CREATE OR REPLACE PACKAGE InsertArchive AS
--
-- Routines to insert data into the arch_locuschange table
--
PROCEDURE InsertLocusChange(p_dbentityId IN VARCHAR2,
                        p_sourceName IN VARCHAR2,
                        p_changeType IN VARCHAR2,
                        p_oldValue IN VARCHAR2,
                        p_newValue IN VARCHAR2,
                        p_changeDate IN DATE,
                        p_user IN VARCHAR2);

END InsertLocusChange;

END InsertArchive;
/
GRANT EXECUTE ON InsertArchive to PUBLIC
/
SHOW ERROR
