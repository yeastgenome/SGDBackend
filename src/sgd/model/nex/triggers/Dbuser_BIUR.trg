CREATE OR REPLACE TRIGGER Dbuser_BIUR
--
-- Before insert or update trigger for the dbuser table
--
  BEFORE INSERT OR UPDATE ON dbuser
  FOR EACH ROW
DECLARE
  v_IsValidCode        code.code_value%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.dbuser_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.dbuser_id FROM DUAL;
    END IF;

    :new.username := UPPER(:new.username);

  ELSE

    IF (:new.dbuser_id != :old.dbuser_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF (:new.date_created != :old.date_created) THEN    
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;
    
   END IF;

END Dbuser_BIUR;
/
SHOW ERROR
