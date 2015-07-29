CREATE OR REPLACE TRIGGER ReferenceDocument_AUDR
--
--  After a row in the reference_document table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON reference_document
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.document_type != :new.document_type)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_DOCUMENT', 'DOCUMENT_TYPE', :old.reference_document_id, :old.document_type, :new.document_type, USER);
    END IF;

     IF (:old.text != :new.text)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_DOCUMENT', 'TEXT', :old.reference_document_id, :old.text, :new.text, USER);
    END IF;

    IF (:old.html != :new.html)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_DOCUMENT', 'HTML', :old.reference_document_id, :old.html, :new.html, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_DOCUMENT', 'SOURCE_ID', :old.reference_document_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_DOCUMENT', 'BUD_ID', :old.reference_document_id, :old.bud_id, :new.bud_id, USER);
    END IF;

     IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_DOCUMENT', 'REFERENCE_ID', :old.reference_document_id, :old.reference_id, :new.reference_id, USER);
    END IF;

  ELSE

    v_row := :old.reference_document_id || '[:]' || :old.document_type || '[:]' ||
             :old.text || '[:]' || :old.html || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.reference_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('REFERENCE_DOCUMENT', :old.reference_document_id, v_row, USER);

  END IF;

END ReferenceDocument_AUDR;
/
SHOW ERROR
