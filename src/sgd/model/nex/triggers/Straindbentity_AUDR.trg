CREATE OR REPLACE TRIGGER Straindbentity_AUDR
--
--  After a row in the straindbentity table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON straindbentity
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.taxonomy_id != :new.taxonomy_id)
    THEN
        AuditLog.InsertUpdateLog('STRAINDBENTITY', 'TAXONOMY_ID', :old.dbentity_id, :old.taxonomy_id, :new.taxonomy_id, USER);
    END IF;

    IF (:old.strain_type != :new.strain_type)
    THEN
        AuditLog.InsertUpdateLog('STRAINDBENTITY', 'STRAIN_TYPE', :old.dbentity_id, :old.strain_type, :new.strain_type, USER);
    END IF;

	 IF (((:old.genotype IS NULL) AND (:new.genotype IS NOT NULL)) OR ((:old.genotype IS NOT NULL) AND (:new.genotype IS NULL)) OR (:old.genotype != :new.genotype)) 
    THEN
        AuditLog.InsertUpdateLog('STRAINDBENTITY', 'GENOTYPE', :old.dbentity_id, :old.genotype, :new.genotype, USER);
    END IF;

    IF (((:old.genbank_id IS NULL) AND (:new.genbank_id IS NOT NULL)) OR ((:old.genbank_id IS NOT NULL) AND (:new.genbank_id IS NULL)) OR (:old.genbank_id != :new.genbank_id)) 
    THEN
        AuditLog.InsertUpdateLog('STRAINDBENTITY', 'GENBANK_ID', :old.dbentity_id, :old.genbank_id, :new.genbank_id, USER);
    END IF;

    IF (((:old.assembly_size IS NULL) AND (:new.assembly_size IS NOT NULL)) OR ((:old.assembly_size IS NOT NULL) AND (:new.assembly_size IS NULL)) OR (:old.assembly_size != :new.assembly_size)) 
    THEN
        AuditLog.InsertUpdateLog('STRAINDBENTITY', 'ASSEMBLY_SIZE', :old.dbentity_id, :old.assembly_size, :new.assembly_size, USER);
    END IF;

    IF (((:old.fold_coverage IS NULL) AND (:new.fold_coverage IS NOT NULL)) OR ((:old.fold_coverage IS NOT NULL) AND (:new.fold_coverage IS NULL)) OR (:old.fold_coverage != :new.fold_coverage)) 
    THEN
        AuditLog.InsertUpdateLog('STRAINDBENTITY', 'FOLD_COVERAGE', :old.dbentity_id, :old.fold_coverage, :new.fold_coverage, USER);
    END IF;

    IF (((:old.scaffold_number IS NULL) AND (:new.scaffold_number IS NOT NULL)) OR ((:old.scaffold_number IS NOT NULL) AND (:new.scaffold_number IS NULL)) OR (:old.scaffold_number != :new.scaffold_number)) 
    THEN
        AuditLog.InsertUpdateLog('STRAINDBENTITY', 'SCAFFOLD_NUMBER', :old.dbentity_id, :old.scaffold_number, :new.scaffold_number, USER);
    END IF;

    IF (((:old.longest_scaffold IS NULL) AND (:new.longest_scaffold IS NOT NULL)) OR ((:old.longest_scaffold IS NOT NULL) AND (:new.longest_scaffold IS NULL)) OR (:old.longest_scaffold != :new.longest_scaffold)) 
    THEN
        AuditLog.InsertUpdateLog('STRAINDBENTITY', 'LONGEST_SCAFFOLD', :old.dbentity_id, :old.longest_scaffold, :new.longest_scaffold, USER);
    END IF;

    IF (((:old.scaffold_nfifty IS NULL) AND (:new.scaffold_nfifty IS NOT NULL)) OR ((:old.scaffold_nfifty IS NOT NULL) AND (:new.scaffold_nfifty IS NULL)) OR (:old.scaffold_nfifty != :new.scaffold_nfifty))
    THEN
        AuditLog.InsertUpdateLog('STRAINDBENTITY', 'SCAFFOLD_NFIFTY', :old.dbentity_id, :old.scaffold_nfifty, :new.scaffold_nfifty, USER);
    END IF;

    IF (((:old.feature_count IS NULL) AND (:new.feature_count IS NOT NULL)) OR ((:old.feature_count IS NOT NULL) AND (:new.feature_count IS NULL)) OR (:old.feature_count != :new.feature_count))
    THEN
        AuditLog.InsertUpdateLog('STRAINDBENTITY', 'FEATURE_COUNT', :old.dbentity_id, :old.feature_count, :new.feature_count, USER);
    END IF;

  ELSE

    v_row := :old.dbentity_id || '[:]' ||
             :old.taxonomy_id || '[:]' || :old.strain_type || '[:]' ||
             :old.genotype || '[:]' || :old.genbank_id || '[:]' || 
             :old.assembly_size || '[:]' || :old.fold_coverage || '[:]' || 
             :old.scaffold_number || '[:]' || :old.longest_scaffold || '[:]' || 
             :old.scaffold_nfifty || '[:]' || :old.feature_count;

    AuditLog.InsertDeleteLog('STRAINDBENTITY', :old.dbentity_id, v_row, USER);

  END IF;

END Straindbentity_AUDR;
/
SHOW ERROR
