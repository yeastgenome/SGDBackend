Create OR REPLACE TRIGGER SoAlias_BIUR
--
-- Before insert or update trigger for so_alias table
--
  BEFORE INSERT OR UPDATE ON so_alias
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.alias_id IS NULL) THEN
        SELECT alias_seq.NEXTVAL INTO :new.alias_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.alias_id != :old.alias_id) THEN    
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

END SoAlias_BIUR;
/
SHOW ERROR
