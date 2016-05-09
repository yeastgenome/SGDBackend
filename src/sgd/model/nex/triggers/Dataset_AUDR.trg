CREATE OR REPLACE TRIGGER Dataset_AUDR
--
--  After a row in the dataset table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON dataset
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'FORMAT_NAME', :old.dataset_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'DISPLAY_NAME', :old.dataset_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'OBJ_URL', :old.dataset_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'SOURCE_ID', :old.dataset_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'BUD_ID', :old.dataset_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (((:old.dbxref_id IS NULL) AND (:new.dbxref_id IS NOT NULL)) OR ((:old.dbxref_id IS NOT NULL) AND (:new.dbxref_id IS NULL)) OR (:old.dbxref_id != :new.dbxref_id))
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'DBXREF_ID', :old.dataset_id, :old.dbxref_id, :new.dbxref_id, USER);
    END IF;

    IF (((:old.dbxref_type IS NULL) AND (:new.dbxref_type IS NOT NULL)) OR ((:old.dbxref_type IS NOT NULL) AND (:new.dbxref_type IS NULL)) OR (:old.dbxref_type != :new.dbxref_type))
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'DBXREF_TYPE', :old.dataset_id, :old.dbxref_type, :new.dbxref_type, USER);
    END IF;

    IF (:old.assay_id != :new.assay_id)
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'ASSAY_ID', :old.dataset_id, :old.assay_id, :new.assay_id, USER);
    END IF;

    IF (((:old.taxonomy_id IS NULL) AND (:new.taxonomy_id IS NOT NULL)) OR ((:old.taxonomy_id IS NOT NULL) AND (:new.taxonomy_id IS NULL)) OR (:old.taxonomy_id != :new.taxonomy_id))
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'TAXONOMY_ID', :old.dataset_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF (((:old.channel_count IS NULL) AND (:new.channel_count IS NOT NULL)) OR ((:old.channel_count IS NOT NULL) AND (:new.channel_count IS NULL)) OR (:old.channel_count != :new.channel_count))
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'CHANNEL_COUNT', :old.dataset_id, :old.channel_count, :new.channel_count, USER);
    END IF;

    IF (:old.sample_count != :new.sample_count)
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'SAMPLE_COUNT', :old.dataset_id, :old.sample_count, :new.sample_count, USER);
    END IF;

    IF (:old.is_in_spell != :new.is_in_spell)
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'IS_IN_SPELL', :old.dataset_id, :old.is_in_spell, :new.is_in_spell, USER);
    END IF;

    IF (:old.is_in_browser != :new.is_in_browser)
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'IS_IN_BROWSER', :old.dataset_id, :old.is_in_browser, :new.is_in_browser, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('DATASET', 'DESCRIPTION', :old.dataset_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.dataset_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.dbxref_id || '[:]' || :old.dbxref_type || '[:]' ||
             :old.assay_id || '[:]' || :old.taxonomy || '[:]' || 
             :old.channel_count || '[:]' || :old.sample_count || '[:]' || 
             :old.is_in_spell || '[:]' || :old.is_in_browser || '[:]' || 
             :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DATASET', :old.dataset_id, v_row, USER);

  END IF;

END Dataset_AUDR;
/
SHOW ERROR
