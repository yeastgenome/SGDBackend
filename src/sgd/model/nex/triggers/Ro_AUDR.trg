CREATE OR REPLACE TRIGGER Ro_AUDR
--
--  After a row in the ro table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON ro
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('RO', 'FORMAT_NAME', :old.relation_ontology_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('RO', 'DISPLAY_NAME', :old.relation_ontology_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (((:old.obj_url IS NULL) AND (:new.obj_url IS NOT NULL)) OR ((:old.obj_url IS NOT NULL) AND (:new.obj_url IS NULL)) OR (:old.obj_url != :new.obj_url))
    THEN
        AuditLog.InsertUpdateLog('RO', 'OBJ_URL', :old.relation_ontology_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('RO', 'SOURCE_ID', :old.relation_ontology_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('RO', 'BUD_ID', :old.relation_ontology_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.ro_id != :new.ro_id)
    THEN
        AuditLog.InsertUpdateLog('RO', 'RO_ID', :old.relation_ontology_id, :old.ro_id, :new.ro_id, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('RO', 'DESCRIPTION', :old.relation_ontology_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.relation_ontology_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.ro_id || '[:]' || :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('RO', :old.relation_ontology_id, v_row, USER);

  END IF;

END Ro_AUDR;
/
SHOW ERROR
