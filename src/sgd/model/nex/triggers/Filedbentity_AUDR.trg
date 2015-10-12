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

    IF (:old.md5sum != :new.md5sum)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'MD5SUM', :old.dbentity_id, :old.md5sum, :new.md5sum, USER);
    END IF;

    IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'TAXONOMY_ID', :old.dbentity_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

     IF (((:old.reference_id IS NULL) AND (:new.reference_id IS NOT NULL)) OR ((:old.reference_id IS NOT NULL) AND (:new.reference_id IS NULL)) OR (:old.reference_id != :new.reference_id))
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'REFERENCE_ID', :old.dbentity_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (:old.file_status != :new.file_status)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'FILE_STATUS', :old.dbentity_id, :old.file_status, :new.file_status, USER);
    END IF;

    IF (:old.file_data_type != :new.file_data_type)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'FILE_DATA_TYPE', :old.dbentity_id, :old.file_data_type, :new.file_data_type, USER);
    END IF;

    IF (:old.file_operation != :new.file_operation)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'FILE_OPERATION', :old.dbentity_id, :old.file_operation, :new.file_operation, USER);
    END IF;

    IF (:old.file_version != :new.file_version)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'FILE_VERSION', :old.dbentity_id, :old.file_version, :new.file_version, USER);
    END IF;

    IF (:old.file_format != :new.file_format)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'FILE_FORMAT', :old.dbentity_id, :old.file_format, :new.file_format, USER);
    END IF;

    IF (:old.file_extension != :new.file_extension)
    THEN
        AuditLog.InsertUpdateLog('FILEDBENTITY', 'FILE_EXTENSION', :old.dbentity_id, :old.file_extension, :new.file_extension, USER);
    END IF;

  ELSE

    v_row := :old.dbentity_id || '[:]' || :old.md5sum || '[:]' ||
             :old.taxonomy_id || '[:]' || :old.reference_id || '[:]' ||
             :old.previous_file_name || '[:]' || :old.status || '[:]' || 
             :old.file_file_data_type || '[:]' || :old.operation || '[:]' || 
             :old.file_version || '[:]' || :old.file_format || '[:]' || 
             :old.file_extension;

    AuditLog.InsertDeleteLog('FILEDBENTITY', :old.dbentity_id, v_row, USER);

  END IF;

END Filedbentity_AUDR;
/
SHOW ERROR
