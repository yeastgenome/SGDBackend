CREATE OR REPLACE TRIGGER Curation_BIUR
--
-- Before insert or update trigger for the curation table
--
  BEFORE INSERT OR UPDATE ON curation
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.curation_id IS NULL) THEN
        SELECT curation_seq.NEXTVAL INTO :new.curation_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.curation_id != :old.curation_id) THEN    
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

END Curation_BIUR;
/
SHOW ERROR
