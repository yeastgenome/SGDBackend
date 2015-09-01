CREATE OR REPLACE TRIGGER PhenotypeCondition_BIUR
--
-- Before insert or update trigger for the phenotype_condition table
--
  BEFORE INSERT OR UPDATE ON phenotype_condition
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.condition_id IS NULL) THEN
        SELECT condition_seq.NEXTVAL INTO :new.condition_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.condition_id != :old.condition_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
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

END PhenotypeCondition_BIUR;
/
SHOW ERROR
