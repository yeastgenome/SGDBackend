CREATE OR REPLACE PACKAGE AuditLog AS
--
-- Write to update_log and delete_log tables
--
PROCEDURE InsertDeleteLog(p_table IN VARCHAR2,
                          p_key IN VARCHAR2,
                          p_row IN CLOB,
                          p_user IN VARCHAR2);

PROCEDURE InsertUpdateLog(p_table IN VARCHAR2,
                          p_column VARCHAR2,
                          p_key IN VARCHAR2,
                          p_old IN VARCHAR2,
                          p_new IN VARCHAR2,
                          p_user IN VARCHAR2);

END AuditLog;
/
GRANT EXECUTE ON AuditLog to PUBLIC
/
SHOW ERROR
