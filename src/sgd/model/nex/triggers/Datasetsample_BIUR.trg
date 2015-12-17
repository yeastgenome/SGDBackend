Create OR REPLACE TRIGGER Datasetsample_BIUR
--
-- Before insert or update trigger for datasetsample table
--
  BEFORE INSERT OR UPDATE ON datasetsample
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.datasetsample_id IS NULL) THEN
        SELECT datasetsample_seq.NEXTVAL INTO :new.datasetsample_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.datasetsample_id != :old.datasetsample_id) THEN    
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

END Datasetsample_BIUR;
/
SHOW ERROR
