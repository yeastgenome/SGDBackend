CREATE OR REPLACE TRIGGER Proteinexptannotation_AUDR
--
--  After a Proteinexptannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON proteinexptannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.dbentity_id != :new.dbentity_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION', 'DBENTITY_ID', :old.annotation_id, :old.dbentity_id, :new.dbentity_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION', 'TAXONOMY_ID', :old.annotation_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF  (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION', 'BUD_ID', :old.annotation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.experiment_type != :new.experiment_type)
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION', 'EXPERIMENT_TYPE', :old.annotation_id, :old.experiment_type, :new.experiment_type, USER);
    END IF;

    IF (:old.data_value != :new.data_value)
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION', 'DATA_VALUE', :old.annotation_id, :old.data_value, :new.data_value, USER);
    END IF;

    IF (:old.data_unit != :new.data_unit)
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION', 'DATA_UNIT', :old.annotation_id, :old.data_unit, :new.data_unit, USER);
    END IF;

    IF (((:old.assay_id IS NULL) AND (:new.assay_id IS NOT NULL)) OR ((:old.assay_id IS NOT NULL) AND (:new.assay_id IS NULL)) OR (:old.assay_id != :new.assay_id))
    THEN
        AuditLog.InsertUpdateLog('PROTEINEXPTANNOTATION', 'ASSAY_ID', :old.annotation_id, :old.assay_id, :new.assay_id, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.dbentity_id || '[:]' ||
             :old.source_id || '[:]' || :old.taxonomy_id || '[:]' ||
             :old.reference_id || '[:]' || :old.bud_id || '[:]' ||
             :old.experiment_type || '[:]' || :old.data_value || '[:]' || 
             :old.data_unit || '[:]' || :old.assay_id || '[:]' || 
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PROTEINEXPTANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Proteinexptannotation_AUDR;
/
SHOW ERROR
