Create OR REPLACE TRIGGER Sgdid_BIUDR
--
-- Before insert, update or delete trigger for sgdid table
--
  BEFORE INSERT OR UPDATE OR DELETE ON sgdid
  FOR EACH ROW
DECLARE
  v_IsValidUser   dbuser.username%TYPE;
  v_CanDelete     NUMBER;
BEGIN
  IF INSERTING THEN

    IF (:new.sgdid IS NULL) THEN
		RAISE_APPLICATION_ERROR
            (-20038, 'SGDIDs can only be inserted via inserts to the DBENTITY table.');
    END IF; 

  ELSIF UPDATING THEN

    IF (:new.sgdid != :old.sgdid) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF (:new.display_name != :old.display_name) THEN
        RAISE_APPLICATION_ERROR
           (-20028, 'SGDID cannot be updated.');
    END IF;

    IF (:new.obj_url != :old.obj_url) THEN
        RAISE_APPLICATION_ERROR
           (-20028, 'SGDID cannot be updated.');
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

    v_CanDelete := CheckDelete.CheckTableDelete('SGDID'); 

  END IF;

END Sgdid_BIUDR;
/
SHOW ERROR
