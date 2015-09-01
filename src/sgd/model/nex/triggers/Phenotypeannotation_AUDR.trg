CREATE OR REPLACE TRIGGER Phenotypeannotation_AUDR
--
--  After a Phenotypeannotation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON phenotypeannotation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.locus_id != :new.locus_id)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'LOCUS_ID', :old.annotation_id, :old.locus_id, :new.locus_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'SOURCE_ID', :old.annotation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'BUD_ID', :old.annotation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF  (((:old.strain_id IS NULL) AND (:new.strain_id IS NOT NULL)) OR ((:old.strain_id IS NOT NULL) AND (:new.strain_id IS NULL)) OR (:old.strain_id != :new.strain_id))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'STRAIN_ID', :old.annotation_id, :old.strain_id, :new.strain_id, USER);
    END IF;

    IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'REFERENCE_ID', :old.annotation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

    IF (:old.phenotype_id != :new.phenotype_id) 
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'PHENOTYPE_ID', :old.annotation_id, :old.phenotype_id, :new.phenotype_id, USER);
    END IF;

    IF (:old.experiment_id != :new.experiment_id)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'EXPERIMENT_ID', :old.annotation_id, :old.experiment_id, :new.experiment_id, USER);
    END IF;

    IF (:old.mutant_id != :new.mutant_id)
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'MUTANT_ID', :old.annotation_id, :old.mutant_id, :new.mutant_id, USER);
    END IF;

    IF  (((:old.allele_id IS NULL) AND (:new.allele_id IS NOT NULL)) OR ((:old.allele_id IS NOT NULL) AND (:new.allele_id IS NULL)) OR (:old.allele_id != :new.allele_id))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'ALLELE_ID', :old.annotation_id, :old.allele_id, :new.allele_id, USER);
    END IF;

    IF  (((:old.reporter_id IS NULL) AND (:new.reporter_id IS NOT NULL)) OR ((:old.reporter_id IS NOT NULL) AND (:new.reporter_id IS NULL)) OR (:old.reporter_id != :new.reporter_id))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'REPORTER_ID', :old.annotation_id, :old.reporter_id, :new.reporter_id, USER);
    END IF;

    IF  (((:old.chebi_id IS NULL) AND (:new.chebi_id IS NOT NULL)) OR ((:old.chebi_id IS NOT NULL) AND (:new.chebi_id IS NULL)) OR (:old.chebi_id != :new.chebi_id))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'CHEBI_ID', :old.annotation_id, :old.chebi_id, :new.chebi_id, USER);
    END IF;

    IF  (((:old.assay_id IS NULL) AND (:new.assay_id IS NOT NULL)) OR ((:old.assay_id IS NOT NULL) AND (:new.assay_id IS NULL)) OR (:old.assay_id != :new.assay_id))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'ASSAY_ID', :old.annotation_id, :old.assay_id, :new.assay_id, USER);
    END IF;

    IF  (((:old.analysis_id IS NULL) AND (:new.analysis_id IS NOT NULL)) OR ((:old.analysis_id IS NOT NULL) AND (:new.analysis_id IS NULL)) OR (:old.analysis_id != :new.analysis_id))
    THEN
        AuditLog.InsertUpdateLog('PHENOTYPEANNOTATION', 'ANALYSIS_ID', :old.annotation_id, :old.analysis_id, :new.analysis_id, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.locus_id || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.reference_id || '[:]' || :old.analysis_id || '[:]' ||
             :old.phenotype_id || '[:]' || :old.experiment_id || '[:]' ||
             :old.mutant_id || '[:]' || :old.allele_id || '[:]' ||
             :old.reporter_id || '[:]' || :old.chebi_id || '[:]' ||
             :old.assay_id || '[:]' || :old.analysis_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PHENOTYPEANNOTATION', :old.annotation_id, v_row, USER);

  END IF;

END Phenotypeannotation_AUDR;
/
SHOW ERROR
