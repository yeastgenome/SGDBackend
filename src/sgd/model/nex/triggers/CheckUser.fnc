CREATE OR REPLACE FUNCTION CheckUser (
--
-- Checks if the username is valid
-- Returns TRUE if the username is found in the dbuser table
-- or FALSE if no match was found
--
    p_username IN VARCHAR2)
    RETURN VARCHAR2
IS
    v_UserID	dbuser.username%TYPE;
    v_User 		dbuser.username%TYPE;
BEGIN

    v_User := upper(p_username);

    SELECT username INTO v_UserID
    FROM dbuser
    WHERE username = v_User;

    RETURN (v_UserID);

    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RAISE_APPLICATION_ERROR
                (-20024, 'Username "' || p_username || '" not found in dbuser table.');

END CheckUser;
/
GRANT EXECUTE ON CheckUser to PUBLIC
/
SHOW ERROR
