Create OR REPLACE TRIGGER Obinvestigation_BIUR
--
-- Before insert or update trigger for obinvestigation table
--
  BEFORE INSERT OR UPDATE ON obinvestigation
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.obinvestigation_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.obinvestigation_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.obinvestigation_id != :old.obinvestigation_id) THEN    
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

END Obinvestigation_BIUR;
/
SHOW ERROR
