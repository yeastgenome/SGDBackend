Create OR REPLACE TRIGGER Psimod_BIUR
--
-- Before insert or update trigger for psimod table
--
  BEFORE INSERT OR UPDATE ON psimod
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.psimod_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.psimod_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.psimod_id != :old.psimod_id) THEN    
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

END Psimod_BIUR;
/
SHOW ERROR
