CREATE OR REPLACE TRIGGER Pathwaydbentity_AUDR
--
--  After a row in the pathwaydbentity table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON pathwaydbentity
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.biocyc_id != :new.biocyc_id)
    THEN
        AuditLog.InsertUpdateLog('PATHWAYDBENTITY', 'BIOCYC_ID', :old.dbentity_id, :old.biocyc_id, :new.biocyc_id, USER);
    END IF;

  ELSE

    v_row := :old.dbentity_id || '[:]' || :old.biocyc_id;

    AuditLog.InsertDeleteLog('PATHWAYDBENTITY', :old.dbentity_id, v_row, USER);

  END IF;

END Pathwaydbentity_AUDR;
/
SHOW ERROR
