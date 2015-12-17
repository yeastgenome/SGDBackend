Create OR REPLACE TRIGGER DatasetKeyword_AUDR
--
--  After a row in the dataset_keyword table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON dataset_keyword
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dataset_id != :new.dataset_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET_KEYWORD', 'DATASET_ID', :old.dataset_keyword_id, :old.dataset_id, :new.dataset_id, USER);
    END IF;

     IF (:old.keyword_id != :new.keyword_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET_KEYWORD', 'KEYWORD_ID', :old.dataset_keyword_id, :old.keyword_id, :new.keyword_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET_KEYWORD', 'SOURCE_ID', :old.dataset_keyword_id, :old.source_id, :new.source_id, USER);
    END IF;

  ELSE

    v_row := :old.dataset_keyword_id || '[:]' || :old.keyword_id || '[:]' ||
             :old.dataset_id || '[:]' || :old.source_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DATASET_KEYWORD', :old.dataset_keyword_id, v_row, USER);

  END IF;

END DatasetKeyword_AUDR;
/
SHOW ERROR
