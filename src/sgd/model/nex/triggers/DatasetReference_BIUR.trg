CREATE OR REPLACE TRIGGER DatasetReference_BIUR
--
-- Before insert or update trigger for dataset_reference table
--
  BEFORE INSERT OR UPDATE ON dataset_reference
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.dataset_reference_id IS NULL) THEN
        SELECT dataset_reference_seq.NEXTVAL INTO :new.dataset_reference_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);
 
  ELSE

    IF (:new.dataset_reference_id != :old.dataset_reference_id) THEN    
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

END DatasetReference_BIUR;
/
SHOW ERROR
