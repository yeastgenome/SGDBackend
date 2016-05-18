CREATE OR REPLACE TRIGGER Doannotation_AUDR
--
--  After a Doannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON doannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('DOANNOTATION', 'DBENTITY_ID', :old.annotation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('DOANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('DOANNOTATION', 'BUD_ID', :old.annotation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

     IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('DOANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('DOANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (:old.do_id != :new.do_id) 
    THEN
        AuditLog.InsertUpdateLog('DOANNOTATION', 'DO_ID', :old.annotation_id, :old.do_id, :new.do_id, USER);
    END IF;

    IF (:old.eco_id != :new.eco_id)
    THEN
        AuditLog.InsertUpdateLog('DOANNOTATION', 'ECO_ID', :old.annotation_id, :old.eco_id, :new.eco_id, USER);
    END IF;

    IF (:old.annotation_type != :new.annotation_type)
    THEN
        AuditLog.InsertUpdateLog('DOANNOTATION', 'ANNOTATION_TYPE', :old.annotation_id, :old.annotation_type, :new.annotation_type, USER);
    END IF;

    IF (:old.do_qualifier != :new.do_qualifier)
    THEN
        AuditLog.InsertUpdateLog('DOANNOTATION', 'DO_QUALIFIER', :old.annotation_id, :old.do_qualifier, :new.do_qualifier, USER);
    END IF;

    IF (:old.date_assigned != :new.date_assigned)
    THEN
        AuditLog.InsertUpdateLog('DOANNOTATION', 'DATE_ASSIGNED', :old.annotation_id, :old.date_assigned, :new.date_assigned, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.dbentity_id || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.taxonomy_id || '[:]' || :old.reference_id || '[:]' ||
             :old.do_id || '[:]' || :old.eco_id || '[:]' ||
             :old.annotation_type || '[:]' || :old.do_qualifier || '[:]' ||
             :old.date_assigned || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('DOANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Doannotation_AUDR;
/
SHOW ERROR