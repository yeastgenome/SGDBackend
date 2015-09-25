CREATE OR REPLACE FUNCTION CheckChebi (
--
-- Checks to see if a chebi_id exists in the CHIBI table
-- Returns TRUE if the chebi_id is found
-- or FALSE if no match was found
--
    p_chebi IN VARCHAR2,
    p_chebi_type IN VARCHAR2)
    RETURN NUMBER
IS
    v_ChebiId	  chebi.chebi_id%TYPE;
BEGIN

	IF (p_chebi_type = 'CHEBI') THEN

	    SELECT count(chebi_id) INTO v_ChebiId
    	FROM chebi
    	WHERE chebi_id = p_chebi
    	AND REGEXP_LIKE (format_name, '^CHEBI:\d+$');

	ELSE
		IF (p_chebi_type = 'NTR') THEN

		    SELECT count(chebi_id) INTO v_ChebiId
        	FROM chebi
        	WHERE chebi_id = p_chebi
        	AND REGEXP_LIKE (format_name, '^NTR:\d+$');

		END IF;
	END IF;

    IF v_ChebiId = 0 
    THEN 
       RAISE_APPLICATION_ERROR
          (-20044, 'CHEBI_ID "' || p_chebi || '" does NOT exist in the CHEBI table.');
       RETURN (0);
    END IF;

    RETURN (1);

End CheckChebi;
/
GRANT EXECUTE ON CheckChebi to PUBLIC
/
SHOW ERROR

