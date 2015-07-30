CREATE OR REPLACE TRIGGER ReferenceDeleted_AUDR
--
--  After a row from the reference_deleted table is updated or deleted, 
--  write the record to delete_log table
--
  AFTER UPDATE OR DELETE ON reference_deleted
  FOR EACH ROW
DECLARE
  v_row		delete_log.deleted_row%TYPE;
BEGIN

  IF UPDATING THEN

    IF (:old.pubmed_id != :new.pubmed_id) 
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_DELETED', 'PUBMED_ID', :old.reference_deleted_id, :old.pubmed_id, :new.pubmed_id, USER);
    END IF;

    IF (((:old.sgdid IS NULL) AND (:new.sgdid IS NOT NULL)) OR ((:old.sgdid IS NOT NULL) AND (:new.sgdid IS NULL)) OR (:old.sgdid != :new.sgdid))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_DELETED', 'SGDID', :old.reference_deleted_id, :old.sgdid, :new.sgdid, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id)) 
    THEN
        AuditLog.InsertUpdateLog('REFERENCE_DELETED', 'BUD_ID', :old.reference_deleted_id, :old.bud_id, :new.bud_id, USER);
    END IF;

  ELSE

     v_row := :old.reference_deleted_id || '[:]' || :old.pubmed_id || '[:]' || 
              :old.sgdid || '[:]' || :old.bud_id || '[:]' ||
              :old.date_created || '[:]' || :old.created_by;

     AuditLog.InsertDeleteLog('REFERENCE_DELETED', :old.reference_deleted_id, v_row, USER);

  END IF;

END ReferenceDeleted_AUDR;
/
SHOW ERROR
