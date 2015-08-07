CREATE OR REPLACE FUNCTION CheckPubmed (
--
-- Checks to see if a particular PubMed value exists in the referencedbentity table
-- Returns TRUE if the PubMed is found
-- or FALSE if no match was found
--
    p_pubmed IN VARCHAR2)
    RETURN NUMBER
IS
    v_PubmedId	  referencedbentity.pmid%TYPE;
BEGIN

    SELECT count(pmid) INTO v_PubmedId
    FROM referencedbentity
    WHERE pmid = p_pubmed;

    IF v_PubMedId > 0 
    THEN 
       RAISE_APPLICATION_ERROR
          (-20025, 'PMID "' || p_pubmed || '" exists in the REFERENCEDBENTITY table.');
       RETURN (0);
    END IF;

    RETURN (1);

End CheckPubmed;
/
GRANT EXECUTE ON CheckPubmed to PUBLIC
/
SHOW ERROR

