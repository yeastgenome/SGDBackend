CREATE OR REPLACE TRIGGER Journal_BIUR
--
-- Before insert or update trigger for journal table
--
  BEFORE INSERT OR UPDATE ON journal
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.journal_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.journal_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.journal_id != :old.journal_id) THEN    
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

END Journal_BIUR;
/
SHOW ERROR
