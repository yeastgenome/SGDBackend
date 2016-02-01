CREATE OR REPLACE TRIGGER Filepath_AUDR
--
--  After a row in the filepath table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON filepath
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('FILEPATH', 'SOURCE_ID', :old.filepath_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (:old.filepath != :new.filepath)
    THEN
        AuditLog.InsertUpdateLog('FILEPATH', 'FILEPATH', :old.filepath_id, :old.filepath, :new.filepath, USER);
    END IF;

  ELSE

    v_row := :old.filepath_id || '[:]' || :old.source_id || '[:]' ||
		  	 :old.filepath || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('FILEPATH', :old.filepath_id, v_row, USER);

  END IF;

END Filepath_AUDR;
/
SHOW ERROR
