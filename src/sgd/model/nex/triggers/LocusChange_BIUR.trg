Create OR REPLACE TRIGGER LocusChange_BIUR
--
-- Before insert or update trigger for locus_change table
--
  BEFORE INSERT OR UPDATE ON locus_change
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.change_id IS NULL) THEN
        SELECT change_seq.NEXTVAL INTO :new.change_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.change_id != :old.change_id) THEN    
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

END LocusChange_BIUR;
/
SHOW ERROR
