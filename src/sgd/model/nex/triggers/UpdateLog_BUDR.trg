CREATE OR REPLACE TRIGGER UpdateLog_BUDR
--
-- Before update or delete trigger for the update_log table
-- Only allow the description column to be updated
--
  BEFORE UPDATE OR DELETE ON update_log
  FOR EACH ROW
DECLARE
    v_CanDelete     NUMBER;
BEGIN

  IF UPDATING THEN

    IF (:new.update_log_id != :old.update_log_id) THEN    
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

    IF (:new.col_name != :old.col_name) THEN 
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

    IF (((:old.old_value IS NULL) AND (:new.old_value IS NOT NULL)) OR ((:old.old_value IS NOT NULL) AND (:new.old_value IS NULL)) OR (:new.old_value != :old.old_value)) THEN 
        RAISE_APPLICATION_ERROR
            (-20027, 'No columns in this table can be updated.');
    END IF;

    IF (((:old.new_value IS NULL) AND (:new.new_value IS NOT NULL)) OR ((:old.new_value IS NOT NULL) AND (:new.new_value IS NULL)) OR (:new.new_value != :old.new_value)) THEN 
        RAISE_APPLICATION_ERROR
            (-20027, 'No columns in this table can be updated.');
    END IF;

  ELSE

    v_CanDelete := CheckDelete.CheckTableDelete('UPDATE_LOG');  

  END IF;

END UpdateLog_BUDR;
/
SHOW ERROR
