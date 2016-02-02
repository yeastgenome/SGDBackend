CREATE OR REPLACE TRIGGER Filedbentity_AUDR
--
--  After a row in the filedbentity table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON filedbentity
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.topic_id != :new.topic_id)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'TOPIC_ID', :old.dbentity_id, :old.topic_id, :new.topic_id, USER);
    END IF;

    IF (:old.format_id != :new.format_id)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'FORMAT_ID', :old.dbentity_id, :old.format_id, :new.format_id, USER);
    END IF;

    IF (:old.extension_id != :new.extension_id)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'EXTENSION_ID', :old.dbentity_id, :old.extension_id, :new.extension_id, USER);
    END IF;

    IF (:old.file_date != :new.file_date)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'FILE_DATE', :old.dbentity_id, :old.file_date, :new.file_date, USER);
    END IF;

    IF (:old.is_public != :new.is_public)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'IS_PUBLIC', :old.dbentity_id, :old.is_public, :new.is_public, USER);
    END IF;

    IF (:old.used_for_spell != :new.used_for_spell)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'USED_FOR_SPELL', :old.dbentity_id, :old.used_for_spell, :new.used_for_spell, USER);
    END IF;

    IF (:old.used_for_jbrowse != :new.used_for_jbrowse)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'USED_FOR_JBROWSE', :old.dbentity_id, :old.used_for_jbrowse, :new.used_for_jbrowse, USER);
    END IF;

    IF (:old.file_version != :new.file_version)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'FILE_VERSION', :old.dbentity_id, :old.file_version, :new.file_version, USER);
    END IF;

     IF (((:old.md5sum IS NULL) AND (:new.md5sum IS NOT NULL)) OR ((:old.md5sum IS NOT NULL) AND (:new.md5sum IS NULL)) OR (:old.md5sum != :new.md5sum))
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'MD5SUM', :old.dbentity_id, :old.md5sum, :new.md5sum, USER);
    END IF;

     IF (((:old.filepath_id IS NULL) AND (:new.filepath_id IS NOT NULL)) OR ((:old.filepath_id IS NOT NULL) AND (:new.filepath_id IS NULL)) OR (:old.filepath_id != :new.filepath_id))
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'FILEPATH_ID', :old.dbentity_id, :old.filepath_id, :new.filepath_id, USER);
    END IF;

     IF (((:old.previous_file_name IS NULL) AND (:new.previous_file_name IS NOT NULL)) OR ((:old.previous_file_name IS NOT NULL) AND (:new.previous_file_name IS NULL)) OR (:old.previous_file_name != :new.previous_file_name))
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'PREVIOUS_FILE_NAME', :old.dbentity_id, :old.previous_file_name, :new.previous_file_name, USER);
    END IF;

     IF (((:old.readme_url IS NULL) AND (:new.readme_url IS NOT NULL)) OR ((:old.readme_url IS NOT NULL) AND (:new.readme_url IS NULL)) OR (:old.readme_url != :new.readme_url))
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'README_URL', :old.dbentity_id, :old.readme_url, :new.readme_url, USER);
    END IF;

  ELSE

    v_row := :old.dbentity_id || '[:]' || :old.topic_id || '[:]' ||
             :old.format_id || '[:]' || :old.extension_id || '[:]' ||
             :old.file_date || '[:]' || :old.is_public || '[:]' || 
             :old.used_for_spell || '[:]' || :old.used_for_jbrowse || '[:]' || 
             :old.file_version || '[:]' || :old.md5sum || '[:]' || 
             :old.filepath_id || '[:]' || :old.previous_file_name || '[:]' ||
             :old.readme_url;

    AuditLog.InsertDeleteLog('FILEDBENTITY', :old.dbentity_id, v_row, USER);

  END IF;

END Filedbentity_AUDR;
/
SHOW ERROR
