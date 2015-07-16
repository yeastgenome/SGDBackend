CREATE OR REPLACE TRIGGER Dbentity_BIUDR
--
-- Before insert or update trigger for dbentity table
--
  BEFORE INSERT OR UPDATE ON dbentity
  FOR EACH ROW
DECLARE
  v_IsValidUser     dbuser.userid%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.dbentity_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.dbentity_id FROM DUAL;
    END IF;

    IF (:new.sgdid IS NULL) THEN
        :new.sgdid := MakeSgdid;
    ELSE
        :new.sgdid := UPPER(:new.sgdid);
    END IF;

     v_IsValidUser := CheckUser(:new.created_by);

  ELSIF UPDATING THEN

    IF (:new.dbentity_id != :old.dbentity_id) THEN
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF (:new.sgdid != :old.sgdid) THEN
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

  ELSE

	v_CanDelete := CheckDelete.CheckTableDelete('DBENTITY'); 

  END IF;

END Dbentity_BIUDR;
/
SHOW ERROR
