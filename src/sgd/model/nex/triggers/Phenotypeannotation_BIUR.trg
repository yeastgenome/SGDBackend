CREATE OR REPLACE TRIGGER Phenotypeannotation_BIUR
--
-- Before insert or update trigger for the phenotypeannotation table
--
  BEFORE INSERT OR UPDATE ON phenotypeannotation
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.phenotypeannotation_id IS NULL) THEN
        SELECT annotation_seq.NEXTVAL INTO :new.phenotypeannotation_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.phenotypeannotation_id != :old.phenotypeannotation_id) THEN    
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

END Phenotypeannotation_BIUR;
/
SHOW ERROR
