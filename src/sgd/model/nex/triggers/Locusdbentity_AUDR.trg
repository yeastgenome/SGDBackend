CREATE OR REPLACE TRIGGER Locusdbentity_AUDR
--
--  After a row in the locusdbentity table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON locusdbentity
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.systematic_name != :new.systematic_name)
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'SYSTEMATIC_NAME', :old.dbentity_id, :old.systematic_name, :new.systematic_name, USER);
    END IF;

	 IF (((:old.gene_name IS NULL) AND (:new.gene_name IS NOT NULL)) OR ((:old.gene_name IS NOT NULL) AND (:new.gene_name IS NULL)) OR (:old.gene_name != :new.gene_name)) 
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'GENE_NAME', :old.dbentity_id, :old.gene_name, :new.gene_name, USER);
--        InsertHistory.InsertHistory(:old.dbentity_id, 'SGD', SYSDATE, 'LOCUS', 'Gene name', :old.gene_name, :new.gene_name, 'Gene name change.', USER);
    END IF;

    IF (((:old.qualifier IS NULL) AND (:new.qualifier IS NOT NULL)) OR ((:old.qualifier IS NOT NULL) AND (:new.qualifier IS NULL)) OR (:old.qualifier != :new.qualifier)) 
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'QUALIFIER', :old.dbentity_id, :old.qualifier, :new.qualifier, USER);
--		InsertHistory.InsertHistory(:old.dbentity_id, 'SGD', SYSDATE, 'LOCUS', 'Feature qualifier', :old.qualifier, :new.qualifier, 'Feature qualifier change.', USER);
    END IF;

    IF (((:old.genetic_position IS NULL) AND (:new.genetic_position IS NOT NULL)) OR ((:old.genetic_position IS NOT NULL) AND (:new.genetic_position IS NULL)) OR (:old.genetic_position != :new.genetic_position)) 
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'GENETIC_POSITION', :old.dbentity_id, :old.genetic_position, :new.genetic_position, USER);
    END IF;

    IF (((:old.name_description IS NULL) AND (:new.name_description IS NOT NULL)) OR ((:old.name_description IS NOT NULL) AND (:new.name_description IS NULL)) OR (:old.name_description != :new.name_description)) 
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'NAME_DESCRIPTION', :old.dbentity_id, :old.name_description, :new.name_description, USER);
    END IF;

    IF (((:old.headline IS NULL) AND (:new.headline IS NOT NULL)) OR ((:old.headline IS NOT NULL) AND (:new.headline IS NULL)) OR (:old.headline != :new.headline)) 
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'HEADLINE', :old.dbentity_id, :old.headline, :new.headline, USER);
    END IF;

    IF (((:old.description IS NULL) AND (:new.description IS NOT NULL)) OR ((:old.description IS NOT NULL) AND (:new.description IS NULL)) OR (:old.description != :new.description)) 
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'DESCRIPTION', :old.dbentity_id, :old.description, :new.description, USER);
    END IF;

    IF (:old.has_summary != :new.has_summary)
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'HAS_SUMMARY', :old.dbentity_id, :old.has_summary, :new.has_summary, USER);
    END IF;

    IF (:old.has_sequence != :new.has_sequence)
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'HAS_SEQUENCE', :old.dbentity_id, :old.has_sequence, :new.has_sequence, USER);
    END IF;

    IF (:old.has_history != :new.has_history)
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'HAS_HISTORY', :old.dbentity_id, :old.has_history, :new.has_history, USER);
    END IF;

    IF (:old.has_literature != :new.has_literature)
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'HAS_LITERATURE', :old.dbentity_id, :old.has_literature, :new.has_literature, USER);
    END IF;

    IF (:old.has_go != :new.has_go)
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'HAS_GO', :old.dbentity_id, :old.has_go, :new.has_go, USER);
    END IF;

    IF (:old.has_phenotype != :new.has_phenotype)
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'HAS_PHENOTYPE', :old.dbentity_id, :old.has_phenotype, :new.has_phenotype, USER);
    END IF;

    IF (:old.has_interaction != :new.has_interaction)
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'HAS_INTERACTION', :old.dbentity_id, :old.has_interaction, :new.has_interaction, USER);
    END IF;

    IF (:old.has_expression != :new.has_expression)
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'HAS_EXPRESSION', :old.dbentity_id, :old.has_expression, :new.has_expression, USER);
    END IF;

    IF (:old.has_regulation != :new.has_regulation)
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'HAS_REGULATION', :old.dbentity_id, :old.has_regulation, :new.has_regulation, USER);
    END IF;

    IF (:old.has_protein != :new.has_protein)
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'HAS_PROTEIN', :old.dbentity_id, :old.has_protein, :new.has_protein, USER);
    END IF;

    IF (:old.has_sequence_section != :new.has_sequence_section)
    THEN
        AuditLog.InsertUpdateLog('LOCUSDBENTITY', 'HAS_SEQUENCE_SECTION', :old.dbentity_id, :old.has_sequence_section, :new.has_sequence_section, USER);
    END IF;

  ELSE

    v_row := :old.dbentity_id || '[:]' || :old.systematic_name || '[:]' ||
             :old.gene_name || '[:]' || :old.qualifier || '[:]' || 
             :old.genetic_position || '[:]' || :old.name_description || '[:]' || 
             :old.headline || '[:]' || :old.description || '[:]' || 
             :old.has_summary || '[:]' || :old.has_sequence || '[:]' ||
             :old.has_history || '[:]' || :old.has_literature || '[:]' ||
             :old.has_go || '[:]' || :old.has_phenotype || '[:]' ||
             :old.has_interaction || '[:]' || :old.has_expression || '[:]' ||
             :old.has_regulation || '[:]' || :old.has_protein || '[:]' ||
             :old.has_sequence_section;

    AuditLog.InsertDeleteLog('LOCUSDBENTITY', :old.dbentity_id, v_row, USER);

  END IF;

END Locusdbentity_AUDR;
/
SHOW ERROR
