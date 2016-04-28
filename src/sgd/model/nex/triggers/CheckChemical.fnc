CREATE OR REPLACE FUNCTION CheckChemical (
--
-- Checks to see if a chemical name exists in the CHEBI table
-- Returns TRUE if the display_name is found
-- or FALSE if no match was found
--
    p_chemical IN VARCHAR2)
    RETURN NUMBER
IS
    v_ChemicalName	  chebi.display_name%TYPE;
BEGIN

    SELECT count(display_name) INTO v_ChemicalName
    FROM chebi
    WHERE display_name = p_chemical;

    IF v_ChemicalName = 0 
    THEN 
       RAISE_APPLICATION_ERROR
          (-20044, 'CHEBI name "' || p_chemical || '" does NOT exist in the CHEBI table.');
       RETURN (0);
    END IF;

    RETURN (1);

End CheckChemical;
/
GRANT EXECUTE ON CheckChemical to PUBLIC
/
SHOW ERROR

