CREATE OR REPLACE TRIGGER Taxonomy_AUDR
--
--  After a row in the taxonomy table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON taxonomy
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('TAXONOMY', 'FORMAT_NAME', :old.taxonomy_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('TAXONOMY', 'DISPLAY_NAME', :old.taxonomy_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (((:old.obj_url IS NULL) AND (:new.obj_url IS NOT NULL)) OR ((:old.obj_url IS NOT NULL) AND (:new.obj_url IS NULL)) OR (:old.obj_url != :new.obj_url))
    THEN
        AuditLog.InsertUpdateLog('TAXONOMY', 'OBJ_URL', :old.taxonomy_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('TAXONOMY', 'SOURCE_ID', :old.taxonomy_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.taxid IS NULL) AND (:new.taxid IS NOT NULL)) OR ((:old.taxid IS NOT NULL) AND (:new.taxid IS NULL)) OR (:old.taxid != :new.taxid))
    THEN
        AuditLog.InsertUpdateLog('TAXONOMY', 'TAXID', :old.taxonomy_id, :old.taxid, :new.taxid, USER);
    END IF;

    IF (((:old.common_name IS NULL) AND (:new.common_name IS NOT NULL)) OR ((:old.common_name IS NOT NULL) AND (:new.common_name IS NULL)) OR (:old.common_name != :new.common_name))
    THEN
        AuditLog.InsertUpdateLog('TAXONOMY', 'COMMON_NAME', :old.taxonomy_id, :old.common_name, :new.common_name, USER);
    END IF;

    IF (:old.rank != :new.rank)
    THEN
        AuditLog.InsertUpdateLog('TAXONOMY', 'RANK', :old.taxonomy_id, :old.rank, :new.rank, USER);
    END IF;

  ELSE

    v_row := :old.taxonomy_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.taxid || '[:]' ||
             :old.common_name || '[:]' || :old.rank || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('TAXONOMY', :old.taxonomy_id, v_row, USER);

  END IF;

END Taxonomy_AUDR;
/
SHOW ERROR
