CREATE OR REPLACE TRIGGER DeleteLog_BUDR
--
-- Before update or delete trigger for the delete_log table
-- Only allow the description column to be updated
--
  BEFORE UPDATE OR DELETE ON delete_log
  FOR EACH ROW
DECLARE
    v_CanDelete     NUMBER;
BEGIN

  IF UPDATING THEN

    IF (:new.delete_log_id != :old.delete_log_id) THEN    
        RAISE_APPLICATION_ERROR
			(-20027, 'No columns in this table can be updated.');
    END IF;

	 IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id)) THEN
	 	 RAISE_APPLICATION_ERROR
			(-20027, 'No columns in this table can be updated.');
    END IF;

    IF (:new.tab_name != :old.tab_name) THEN    
        RAISE_APPLICATION_ERROR
			(-20027, 'No columns in this table can be updated.');
    END IF;

    IF (:new.primary_key != :old.primary_key) THEN    
        RAISE_APPLICATION_ERROR
            (-20027, 'No columns in this table can be updated.');
    END IF;

    IF (:new.date_created != :old.date_created) THEN    
        RAISE_APPLICATION_ERROR
            (-20027, 'No columns in this table can be updated.');
    END IF;

    IF (:new.created_by != :old.created_by) THEN    
        RAISE_APPLICATION_ERROR
            (-20027, 'No columns in this table can be updated.');
    END IF;

    IF (:new.deleted_row != :old.deleted_row) THEN 
        RAISE_APPLICATION_ERROR
            (-20027, 'No columns in this table can be updated.');
    END IF;

  ELSE

    v_CanDelete := CheckDelete.CheckTableDelete('DELETE_LOG');  

  END IF;

END DeleteLog_BUDR;
/
SHOW ERROR
