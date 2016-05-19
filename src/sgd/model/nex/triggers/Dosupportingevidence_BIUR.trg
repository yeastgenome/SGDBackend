Create OR REPLACE TRIGGER Dosupportingevidence_BIUR
--
-- Before insert or update trigger for dosupportingevidence table
--
  BEFORE INSERT OR UPDATE ON dosupportingevidence
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.dosupportingevidence_id IS NULL) THEN
        SELECT supportingevidence_seq.NEXTVAL INTO :new.dosupportingevidence_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.dosupportingevidence_id != :old.dosupportingevidence_id) THEN    
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

END Dosupportingevidence_BIUR;
/
SHOW ERROR
