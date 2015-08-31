CREATE OR REPLACE TRIGGER Phenotype_AUDR
--
--  After a row in the phenotype table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON phenotype
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPE', 'FORMAT_NAME', :old.phenotype_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPE', 'DISPLAY_NAME', :old.phenotype_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (((:old.obj_url IS NULL) AND (:new.obj_url IS NOT NULL)) OR ((:old.obj_url IS NOT NULL) AND (:new.obj_url IS NULL)) OR (:old.obj_url != :new.obj_url))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPE', 'OBJ_URL', :old.phenotype_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPE', 'SOURCE_ID', :old.phenotype_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPE', 'BUD_ID', :old.phenotype_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.observable_id != :new.observable_id)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPE', 'OBSERVABLE_ID', :old.phenotype_id, :old.observable_id, :new.observable_id, USER);
    END IF;

    IF (((:old.qualifier_id IS NULL) AND (:new.qualifier_id IS NOT NULL)) OR ((:old.qualifier_id IS NOT NULL) AND (:new.qualifier_id IS NULL)) OR (:old.qualifier_id != :new.qualifier_id))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPE', 'QUALIFIER_ID', :old.phenotype_id, :old.qualifier_id, :new.qualifier_id, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPE', 'DESCRIPTION', :old.phenotype_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.phenotype_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.observable_id || '[:]' || :old.qualifier_id || '[:]' ||
             :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PHENOTYPE', :old.phenotype_id, v_row, USER);

  END IF;

END Phenotype_AUDR;
/
SHOW ERROR
