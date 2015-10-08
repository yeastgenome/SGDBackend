Create OR REPLACE TRIGGER Gosupportingevidence_BIUR
--
-- Before insert or update trigger for gosupportingevidence table
--
  BEFORE INSERT OR UPDATE ON gosupportingevidence
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.gosupportingevidence_id IS NULL) THEN
        SELECT gosupportingevidence_seq.NEXTVAL INTO :new.gosupportingevidence_id FROM DUAL;
    END IF;

   SELECT group_seq.NEXTVAL INTO :new.group_id FROM DUAL;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.gosupportingevidence_id != :old.gosupportingevidence_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF (:new.group_id != :old.group_id) THEN
        RAISE_APPLICATION_ERROR
            (-20029, 'This column cannot be updated.');
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

END Gosupportingevidence_BIUR;
/
SHOW ERROR
