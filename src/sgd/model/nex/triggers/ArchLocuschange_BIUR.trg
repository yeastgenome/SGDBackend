Create OR REPLACE TRIGGER ArchLocuschange_BIUR
--
-- Before insert or update trigger for arch_locuschange table
--
  BEFORE INSERT OR UPDATE ON arch_locuschange
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.change_id IS NULL) THEN
        SELECT change_seq.NEXTVAL INTO :new.change_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.changed_by);

  ELSE

    IF (:new.change_id != :old.change_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF (:new.date_archived != :old.date_archived) THEN    
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

  END IF;

END ArchLocuschange_BIUR;
/
SHOW ERROR
