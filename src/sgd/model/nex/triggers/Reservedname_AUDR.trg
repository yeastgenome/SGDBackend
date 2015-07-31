CREATE OR REPLACE TRIGGER Reservedname_AUDR
--
--  After a row in the reservedname table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON reservedname
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('RESERVEDNAME', 'FORMAT_NAME', :old.reservedname_id, :old.format_name, :new.format_name, USER);
    END IF;

     IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('RESERVEDNAME', 'DISPLAY_NAME', :old.reservedname_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('RESERVEDNAME', 'OBJ_URL', :old.reservedname_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('RESERVEDNAME', 'SOURCE_ID', :old.reservedname_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('RESERVEDNAME', 'BUD_ID', :old.reservedname_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (((:old.locus_id IS NULL) AND (:new.locus_id IS NOT NULL)) OR ((:old.locus_id IS NOT NULL) AND (:new.locus_id IS NULL)) OR (:old.locus_id != :new.locus_id))
    THEN
        AuditLog.InsertUpdateLog('RESERVEDNAME', 'LOCUS_ID', :old.reservedname_id, :old.locus_id, :new.locus_id, USER);
    END IF;

    IF (((:old.reference_id IS NULL) AND (:new.reference_id IS NOT NULL)) OR ((:old.reference_id IS NOT NULL) AND (:new.reference_id IS NULL)) OR (:old.reference_id != :new.reference_id))
    THEN
        AuditLog.InsertUpdateLog('RESERVEDNAME', 'REFERENCE_ID', :old.reservedname_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (:old.colleague_id != :new.colleague_id)
    THEN
        AuditLog.InsertUpdateLog('RESERVEDNAME', 'COLLEAGUE_ID', :old.reservedname_id, :old.colleague_id, :new.colleague_id, USER);
    END IF;

    IF (:old.reservation_date != :new.reservation_date)
    THEN
        AuditLog.InsertUpdateLog('RESERVEDNAME', 'RESERVATION_DATE', :old.reservedname_id, :old.reservation_date, :new.reservation_date, USER);
    END IF;

    IF (:old.expiration_date != :new.expiration_date)
    THEN
        AuditLog.InsertUpdateLog('RESERVEDNAME', 'EXPIRATION_DATE', :old.reservedname_id, :old.expiration_date, :new.expiration_date, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('RESERVEDNAME', 'DESCRIPTION', :old.reservedname_id, :old.description, :new.description, USER);
    END IF;

  ELSE

    v_row := :old.reservedname_id || '[:]' || :old.format_name || '[:]' ||
             :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.locus_id || '[:]' || :old.reference_id || '[:]' || 
             :old.colleague_id || '[:]' || :old.reservation_date || '[:]' ||
             :old.expiration_date || '[:]' || :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('RESERVEDNAME', :old.reservedname_id, v_row, USER);

  END IF;

END Reservedname_AUDR;
/
SHOW ERROR
