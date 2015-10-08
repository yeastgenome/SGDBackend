CREATE OR REPLACE TRIGGER Genomerelease_AUDR
--
--  After a row in the genomerelease table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON genomerelease
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('GENOMERELEASE', 'FORMAT_NAME', :old.genomerelease_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('GENOMERELEASE', 'DISPLAY_NAME', :old.genomerelease_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (((:old.obj_url IS NULL) AND (:new.obj_url IS NOT NULL)) OR ((:old.obj_url IS NOT NULL) AND (:new.obj_url IS NULL)) OR (:old.obj_url != :new.obj_url))
    THEN
        AuditLog.InsertUpdateLog('GENOMERELEASE', 'OBJ_URL', :old.genomerelease_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('GENOMERELEASE', 'SOURCE_ID', :old.genomerelease_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('GENOMERELEASE', 'BUD_ID', :old.genomerelease_id, :old.bud_id, :new.bud_id, USER);
    END IF;

     IF (:old.file_id != :new.file_id)
    THEN
        AuditLog.InsertUpdateLog('GENOMERELEASE', 'FILE_ID', :old.genomerelease_id, :old.file_id, :new.file_id, USER);
    END IF;

     IF (:old.sequence_release != :new.sequence_release)
    THEN
        AuditLog.InsertUpdateLog('GENOMERELEASE', 'SEQUENCE_RELEASE', :old.genomerelease_id, :old.sequence_release, :new.sequence_release, USER);
    END IF;

     IF (:old.annotation_release != :new.annotation_release)
    THEN
        AuditLog.InsertUpdateLog('GENOMERELEASE', 'ANNOTATION_RELEASE', :old.genomerelease_id, :old.annotation_release, :new.annotation_release, USER);
    END IF;

     IF (:old.curation_release != :new.curation_release)
    THEN
        AuditLog.InsertUpdateLog('GENOMERELEASE', 'CURATION_RELEASE', :old.genomerelease_id, :old.curation_release, :new.curation_release, USER);
    END IF;

     IF (:old.release_date != :new.release_date)
    THEN
        AuditLog.InsertUpdateLog('GENOMERELEASE', 'RELEASE_DATE', :old.genomerelease_id, :old.release_date, :new.release_date, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('GENOMERELEASE', 'DESCRIPTION', :old.genomerelease_id, :old.description, :new.description, USER);
    END IF;

  ELSE

    v_row := :old.genomerelease_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.file_id || '[:]' ||
             :old.sequence_release || '[:]' || :old.annotation_release || '[:]' ||
             :old.curation_release || '[:]' || :old.release_date || '[:]' ||
             :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('GENOMERELEASE', :old.genomerelease_id, v_row, USER);

  END IF;

END Genomerelease_AUDR;
/
SHOW ERROR
