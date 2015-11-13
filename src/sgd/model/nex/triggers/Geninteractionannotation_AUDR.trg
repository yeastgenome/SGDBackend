CREATE OR REPLACE TRIGGER Geninteractionannotation_AUDR
--
--  After a Geninteractionannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON geninteractionannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity1_id != :new.dbentity1_id)
    THEN
        AuditLog.InsertUpdateLog('GENINTERACTIONANNOTATION', 'DBENTITY1_ID', :old.annotation_id, :old.dbentity1_id, :new.dbentity1_id, USER);
    END IF;

    IF (:old.dbentity2_id != :new.dbentity2_id)
    THEN
        AuditLog.InsertUpdateLog('GENINTERACTIONANNOTATION', 'DBENTITY2_ID', :old.annotation_id, :old.dbentity2_id, :new.dbentity2_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('GENINTERACTIONANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('GENINTERACTIONANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

     IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('GENINTERACTIONANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('GENINTERACTIONANNOTATION', 'BUD_ID', :old.annotation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.phenotype_id != :new.phenotype_id) 
    THEN
        AuditLog.InsertUpdateLog('GENINTERACTIONANNOTATION', 'PHENOTYPE_ID', :old.annotation_id, :old.phenotype_id, :new.phenotype_id, USER);
    END IF;

    IF (:old.biogrid_experimental_system != :new.biogrid_experimental_system)
    THEN
        AuditLog.InsertUpdateLog('GENINTERACTIONANNOTATION', 'BIOGRID_EXPERIMENTAL_SYSTEM', :old.annotation_id, :old.biogrid_experimental_system, :new.biogrid_experimental_system, USER);
    END IF;

    IF (:old.annotation_type != :new.annotation_type)
    THEN
        AuditLog.InsertUpdateLog('GENINTERACTIONANNOTATION', 'ANNOTATION_TYPE', :old.annotation_id, :old.annotation_type, :new.annotation_type, USER);
    END IF;

    IF (:old.bait_hit != :new.bait_hit)
    THEN
        AuditLog.InsertUpdateLog('GENINTERACTIONANNOTATION', 'BAIT_HIT', :old.annotation_id, :old.bait_hit, :new.bait_hit, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description))
    THEN
        AuditLog.InsertUpdateLog('GENINTERACTIONANNOTATION', 'DESCRIPTION', :old.annotation_id, :old.description, :new.description, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.dbentity1_id || '[:]' ||
             :old.dbentity2_id || '[:]' || :old.source_id || '[:]' ||
             :old.reference_id || '[:]' || :old.taxonomy_id || '[:]' ||
             :old.bud_id || '[:]' || :old.phenotype_id || '[:]' ||
             :old.biogrid_experimental_system || '[:]' || :old.annotation_type || '[:]' ||
             :old.bait_hit || '[:]' || :old.description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('GENINTERACTIONANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Geninteractionannotation_AUDR;
/
SHOW ERROR
