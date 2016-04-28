CREATE OR REPLACE TRIGGER PhenotypeannotationCond_BIUR
--
-- Before insert or update trigger for the phenotypeannotation_cond table
--
  BEFORE INSERT OR UPDATE ON phenotypeannotation_cond
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
  v_DoesChebiExist      chebi.chebi_id%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.condition_id IS NULL) THEN
        SELECT condition_seq.NEXTVAL INTO :new.condition_id FROM DUAL;
    END IF; 

    IF (:new.condition_class = 'chemical') THEN
        v_DoesChebiExist := CheckChemical(:new.condition_name);
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.condition_id != :old.condition_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF (:new.condition_class = 'chemical') THEN
        v_DoesChebiExist := CheckChemical(:new.condition_name);
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

END PhenotypeannotationCond_BIUR;
/
SHOW ERROR
