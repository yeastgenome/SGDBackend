CREATE OR REPLACE TRIGGER StrainSummaryReference_AUDR
--
--  After a row in the strain_summary_reference table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON strain_summary_reference
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.summary_id != :new.summary_id)
    THEN
        AuditLog.InsertUpdateLog('SUMMARY_REFERENCE', 'SUMMARY_ID', :old.summary_reference_id, :old.summary_id, :new.summary_id, USER);
    END IF;

     IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('SUMMARY_REFERENCE', 'REFERENCE_ID', :old.summary_reference_id, :old.reference_id, :new.reference_id, USER);
    END IF;

     IF (:old.reference_order != :new.reference_order)
    THEN
        AuditLog.InsertUpdateLog('SUMMARY_REFERENCE', 'REFERENCE_ORDER', :old.summary_reference_id, :old.reference_order, :new.reference_order, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('SUMMARY_REFERENCE', 'SOURCE_ID', :old.summary_reference_id, :old.source_id, :new.source_id, USER);
    END IF;

  ELSE

    v_row := :old.summary_reference_id || '[:]' || :old.summary_id || '[:]' ||
             :old.reference_id || '[:]' || :old.reference_order || '[:]' || 
             :old.source_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('SUMMARY_REFERENCE', :old.summary_reference_id, v_row, USER);

  END IF;

END StrainSummaryReference_AUDR;
/
SHOW ERROR
