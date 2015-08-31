CREATE OR REPLACE FUNCTION CheckPhenotype (
--
-- Checks to see if a phenotype:namespace exists in the APO table
-- Returns TRUE if the phenotype is found
-- or FALSE if no match was found
--
    p_phenotype IN VARCHAR2,
    p_namespace IN VARCHAR2)
    RETURN NUMBER
IS
    v_PhenotypeId	  apo.apo_id%TYPE;
	v_Namespace       apo.apo_namespace%TYPE;
BEGIN

    SELECT count(apo_id) INTO v_PhenotypeId
    FROM apo
    WHERE apo_id = p_phenotype
    AND apo_namespace = p_namespace;

    v_Namespace := upper(p_namespace);

    IF v_PhenotypeId = 0 
    THEN 
       RAISE_APPLICATION_ERROR
          (-20043, 'APO_ID "' || p_phenotype || '" for ' || v_Namespace || ' namespace does NOT exist in the APO table.');
       RETURN (0);
    END IF;

    RETURN (1);

End CheckPhenotype;
/
GRANT EXECUTE ON CheckPhenotype to PUBLIC
/
SHOW ERROR

