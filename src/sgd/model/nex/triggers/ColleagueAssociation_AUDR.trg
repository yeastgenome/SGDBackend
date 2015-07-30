CREATE OR REPLACE TRIGGER ColleagueAssociation_AUDR
--
--  After a row in the colleague_association table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON colleague_association
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_ASSOCIATION', 'SOURCE_ID', :old.colleague_association_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_ASSOCIATION', 'BUD_ID', :old.colleague_association_id, :old.bud_id, :new.bud_id, USER);
    END IF;

	 IF (:old.colleague_id != :new.colleague_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_ASSOCIATION', 'COLLEAGUE_ID', :old.colleague_association_id, :old.colleague_id, :new.colleague_id, USER);
    END IF;

     IF (:old.associate_id != :new.associate_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_ASSOCIATION', 'ASSOCIATE_ID', :old.colleague_association_id, :old.associate_id, :new.associate_id, USER);
    END IF;

    IF (:old.association_type != :new.association_type)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE_ASSOCIATION', 'ASSOCIATION_TYPE', :old.colleague_association_id, :old.association_type, :new.association_type, USER);
    END IF;

  ELSE

    v_row := :old.colleague_association_id || '[:]' || :old.source_id || '[:]' ||
		  	 :old.bud_id || '[:]' || :old.colleague_id || '[:]' ||
             :old.associate_id || '[:]' || :old.association_type || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('COLLEAGUE_ASSOCIATION', :old.colleague_association_id, v_row, USER);

  END IF;

END ColleagueAssociation_AUDR;
/
SHOW ERROR
