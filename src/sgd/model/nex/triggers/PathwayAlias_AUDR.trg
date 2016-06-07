CREATE OR REPLACE TRIGGER PathwayAlias_AUDR
--
--  After a row in the pathway_alias table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON pathway_alias
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('PATHWAY_ALIAS', 'DISPLAY_NAME', :old.alias_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (((:old.obj_url IS NULL) AND (:new.obj_url IS NOT NULL)) OR ((:old.obj_url IS NOT NULL) AND (:new.obj_url IS NULL)) OR (:old.obj_url != :new.obj_url))
    THEN
        AuditLog.InsertUpdateLog('PATHWAY_ALIAS', 'OBJ_URL', :old.alias_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('PATHWAY_ALIAS', 'SOURCE_ID', :old.alias_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('PATHWAY_ALIAS', 'BUD_ID', :old.alias_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.pathway_id != :new.pathway_id)
    THEN
        AuditLog.InsertUpdateLog('PATHWAY_ALIAS', 'PATHWAY_ID', :old.alias_id, :old.pathway_id, :new.pathway_id, USER);
    END IF;

    IF (:old.alias_type != :new.alias_type)
    THEN
        AuditLog.InsertUpdateLog('PATHWAY_ALIAS', 'ALIAS_TYPE', :old.alias_id, :old.alias_type, :new.alias_type, USER);
    END IF;

  ELSE

    v_row := :old.alias_id || '[:]' || 
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.pathway_id || '[:]' || :old.alias_type || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PATHWAY_ALIAS', :old.alias_id, v_row, USER);

  END IF;

END PathwayAlias_AUDR;
/
SHOW ERROR