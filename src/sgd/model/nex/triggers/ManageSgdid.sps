CREATE OR REPLACE PACKAGE ManageSgdid AS
--
-- Routines to do manage sgdids
-- not possible directly in triggers
--
PROCEDURE InsertSgdid (p_sgdid IN VARCHAR2,
                       p_source IN VARCHAR2,
                       p_sgdidClass IN VARCHAR2,
                       p_sgdidStatus IN VARCHAR2,
                       p_user IN VARCHAR2);

FUNCTION CheckSgdid (p_sgdid IN VARCHAR2)  RETURN NUMBER;

END ManageSgdid;
/
GRANT EXECUTE ON ManageSgdid to PUBLIC
/
SHOW ERROR
