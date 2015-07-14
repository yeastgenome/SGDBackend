Create OR REPLACE TRIGGER Enzyme_BIUR
--
-- Before insert or update trigger for enzyme table
--
  BEFORE INSERT OR UPDATE ON enzyme
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.enzyme_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.enzyme_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.enzyme_id != :old.enzyme_id) THEN    
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

END Enzyme_BIUR;
/
SHOW ERROR
