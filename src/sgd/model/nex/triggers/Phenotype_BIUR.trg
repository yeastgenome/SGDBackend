Create OR REPLACE TRIGGER Phenotype_BIUR
--
-- Before insert or update trigger for phenotype table
--
  BEFORE INSERT OR UPDATE ON phenotype
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
  v_DoesPhenotypeExist	apo.apo_id%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.phenotype_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.phenotype_id FROM DUAL;
    END IF;

	v_DoesPhenotypeExist := CheckPhenotype(:new.observable_id, 'observable');

	IF (:new.qualifier_id is NOT NULL) THEN
	    v_DoesPhenotypeExist := CheckPhenotype(:new.qualifier_id, 'qualifier');
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.phenotype_id != :old.phenotype_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    v_DoesPhenotypeExist := CheckPhenotype(:new.observable_id, 'observable');
    
    IF (:new.qualifier_id is NOT NULL) THEN
        v_DoesPhenotypeExist := CheckPhenotype(:new.qualifier_id, 'qualifier');
    END IF;

    IF (:new.date_created != :old.date_created) THEN    
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

    IF (:new.created_by != :old.created_by) THEN    
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

  END IF;

END Phenotype_BIUR;
/
SHOW ERROR
