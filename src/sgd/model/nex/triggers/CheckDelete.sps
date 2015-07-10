CREATE OR REPLACE PACKAGE CheckDelete AS
--
-- Routines to verify whether certain data in certain tables can be deleted
--
FUNCTION CheckTableDelete(p_table IN VARCHAR2) RETURN NUMBER;

END CheckDelete;
/
GRANT EXECUTE ON CheckDelete to PUBLIC
/
SHOW ERROR
