CREATE OR REPLACE TRIGGER Goannotation_AUDR
--
--  After a Goannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON goannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.locus_id != :new.locus_id)
    THEN
        AuditLog.InsertUpdateLog('GOANNOTATION', 'LOCUS_ID', :old.annotation_id, :old.locus_id, :new.locus_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('GOANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('GOANNOTATION', 'BUD_ID', :old.annotation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

     IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('GOANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('GOANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (:old.go_id != :new.go_id) 
    THEN
        AuditLog.InsertUpdateLog('GOANNOTATION', 'GO_ID', :old.annotation_id, :old.go_id, :new.go_id, USER);
    END IF;

    IF (:old.eco_id != :new.eco_id)
    THEN
        AuditLog.InsertUpdateLog('GOANNOTATION', 'ECO_ID', :old.annotation_id, :old.eco_id, :new.eco_id, USER);
    END IF;

    IF (:old.annotation_type != :new.annotation_type)
    THEN
        AuditLog.InsertUpdateLog('GOANNOTATION', 'ANNOTATION_TYPE', :old.annotation_id, :old.annotation_type, :new.annotation_type, USER);
    END IF;

    IF (:old.go_qualifier != :new.go_qualifier)
    THEN
        AuditLog.InsertUpdateLog('GOANNOTATION', 'GO_QUALIFIER', :old.annotation_id, :old.go_qualifier, :new.go_qualifier, USER);
    END IF;

    IF (:old.date_assigned != :new.date_assigned)
    THEN
        AuditLog.InsertUpdateLog('GOANNOTATION', 'DATE_ASSIGNED', :old.annotation_id, :old.date_assigned, :new.date_assigned, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.locus_id || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.taxonomy_id || '[:]' || :old.reference_id || '[:]' ||
             :old.go_id || '[:]' || :old.eco_id || '[:]' ||
             :old.annotation_type || '[:]' || :old.go_qualifier || '[:]' ||
             :old.date_assigned || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('GOANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Goannotation_AUDR;
/
SHOW ERROR
