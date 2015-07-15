Create OR REPLACE TRIGGER Sequencefeature_BIUR
--
-- Before insert or update trigger for sequencefeature table
--
  BEFORE INSERT OR UPDATE ON sequencefeature
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.sequencefeature_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.sequencefeature_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.sequencefeature_id != :old.sequencefeature_id) THEN    
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

END Sequencefeature_BIUR;
/
SHOW ERROR
