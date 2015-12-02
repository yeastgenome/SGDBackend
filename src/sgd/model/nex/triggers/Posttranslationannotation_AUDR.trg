CREATE OR REPLACE TRIGGER Posttranslationannotation_AUDR
--
--  After a Posttranslationannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON posttranslationannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('POSTTRANSLATIONANNOTATION', 'DBENTITY_ID', :old.annotation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('POSTTRANSLATIONANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('POSTTRANSLATIONANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('POSTTRANSLATIONANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('POSTTRANSLATIONANNOTATION', 'BUD_ID', :old.annotation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.site_index != :new.site_index) 
    THEN
        AuditLog.InsertUpdateLog('POSTTRANSLATIONANNOTATION', 'SITE_INDEX', :old.annotation_id, :old.site_index, :new.site_index, USER);
    END IF;

    IF (:old.site_residue != :new.site_residue)
    THEN
        AuditLog.InsertUpdateLog('POSTTRANSLATIONANNOTATION', 'SITE_RESIDUE', :old.annotation_id, :old.site_residue, :new.site_residue, USER);
    END IF;

    IF (:old.psimod_id != :new.psimod_id)
    THEN
        AuditLog.InsertUpdateLog('POSTTRANSLATIONANNOTATION', 'PSIMOD_ID', :old.annotation_id, :old.psimod_id, :new.psimod_id, USER);
    END IF;

    IF (((:old.modifier_id IS NULL) AND (:new.modifier_id IS NOT NULL)) OR ((:old.modifier_id IS NOT NULL) AND (:new.modifier_id IS NULL)) OR (:old.modifier_id != :new.modifier_id))
    THEN
        AuditLog.InsertUpdateLog('POSTTRANSLATIONANNOTATION', 'MODIFIER_ID', :old.annotation_id, :old.modifier_id, :new.modifier_id, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.dbentity_id || '[:]' ||
             :old.source_id || '[:]' || :old.taxonomy_id || '[:]' ||
             :old.reference_id || '[:]' || :old.bud_id || '[:]' ||
             :old.site_index || '[:]' || :old.site_residue || '[:]' ||
             :old.psimod_id || '[:]' || :old.modifier_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('POSTTRANSLATIONANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Posttranslationannotation_AUDR;
/
SHOW ERROR