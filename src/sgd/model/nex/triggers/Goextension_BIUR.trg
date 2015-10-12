Create OR REPLACE TRIGGER Goextension_BIUR
--
-- Before insert or update trigger for goextension table
--
  BEFORE INSERT OR UPDATE ON goextension
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.goextension_id IS NULL) THEN
        SELECT goextension_seq.NEXTVAL INTO :new.goextension_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.goextension_id != :old.goextension_id) THEN    
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

END Goextension_BIUR;
/
SHOW ERROR
