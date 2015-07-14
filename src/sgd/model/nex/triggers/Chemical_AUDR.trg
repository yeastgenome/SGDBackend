CREATE OR REPLACE TRIGGER Chemical_AUDR
--
--  After a row in the chemical table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON chemical
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('CHEMICAL', 'FORMAT_NAME', :old.chemical_id, :old.format_name, :new.format_name, USER);
    END IF;

	 IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('CHEMICAL', 'DISPLAY_NAME', :old.chemical_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (((:old.obj_url IS NULL) AND (:new.obj_url IS NOT NULL)) OR ((:old.obj_url IS NOT NULL) AND (:new.obj_url IS NULL)) OR (:old.obj_url != :new.obj_url))
    THEN
        AuditLog.InsertUpdateLog('CHEMICAL', 'OBJ_URL', :old.chemical_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('CHEMICAL', 'SOURCE_ID', :old.chemical_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('CHEMICAL', 'BUD_ID', :old.chemical_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.chebi_id != :new.chebi_id)
    THEN
        AuditLog.InsertUpdateLog('CHEMICAL', 'CHEBI_ID', :old.chemical_id, :old.chebi_id, :new.chebi_id, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('CHEMICAL', 'DESCRIPTION', :old.chemical_id, :old.description, :new.description, USER);
    END IF;


  ELSE

    v_row := :old.chemical_id || '[:]' || :old.format_name || '[:]' ||
		  	 :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.chebi_id || '[:]' || :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('CHEMICAL', :old.chemical_id, v_row, USER);

  END IF;

END Chemical_AUDR;
/
SHOW ERROR
