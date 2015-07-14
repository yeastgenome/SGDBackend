Create OR REPLACE TRIGGER Chemical_BIUR
--
-- Before insert or update trigger for chemical table
--
  BEFORE INSERT OR UPDATE ON chemical
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.chemical_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.chemical_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.chemical_id != :old.chemical_id) THEN    
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

END Chemical_BIUR;
/
SHOW ERROR
