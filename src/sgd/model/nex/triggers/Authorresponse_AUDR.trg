CREATE OR REPLACE TRIGGER Authorresponse_AUDR
--
--  After a Curation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON authorresponse
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
    v_part       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.reference_id != :new.reference_id)
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'REFERENCE_ID', :old.curation_id, :old.reference_id, :new.reference_id, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'SOURCE_ID', :old.curation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'BUD_ID', :old.curation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (((:old.colleague_id IS NULL) AND (:new.colleague_id IS NOT NULL)) OR ((:old.colleague_id IS NOT NULL) AND (:new.colleague_id IS NULL)) OR (:old.colleague_id != :new.colleague_id))
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'COLLEAGUE_ID', :old.curation_id, :old.colleague_id, :new.colleague_id, USER);
    END IF;

    IF (:old.author_email != :new.author_email) 
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'AUTHOR_EMAIL', :old.curation_id, :old.author_email, :new.author_email, USER);
    END IF;

    IF (((:old.has_novel_research IS NULL) AND (:new.has_novel_research IS NOT NULL)) OR ((:old.has_novel_research IS NOT NULL) AND (:new.has_novel_research IS NULL)) OR (:old.has_novel_research != :new.has_novel_research))
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'HAS_NOVEL_RESEARCH', :old.curation_id, :old.has_novel_research, :new.has_novel_research, USER);
    END IF;

    IF (((:old.has_large_scale_data IS NULL) AND (:new.has_large_scale_data IS NOT NULL)) OR ((:old.has_large_scale_data IS NOT NULL) AND (:new.has_large_scale_data IS NULL)) OR (:old.has_large_scale_data != :new.has_large_scale_data))
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'HAS_LARGE_SCALE_DATA', :old.curation_id, :old.has_large_scale_data, :new.has_large_scale_data, USER);
    END IF;

    IF (((:old.has_fast_track_tag IS NULL) AND (:new.has_fast_track_tag IS NOT NULL)) OR ((:old.has_fast_track_tag IS NOT NULL) AND (:new.has_fast_track_tag IS NULL)) OR (:old.has_fast_track_tag != :new.has_fast_track_tag))
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'HAS_FAST_TRACK_TAG', :old.curation_id, :old.has_fast_track_tag, :new.has_fast_track_tag, USER);
    END IF;

    IF (((:old.curator_checked_datasets IS NULL) AND (:new.curator_checked_datasets IS NOT NULL)) OR ((:old.curator_checked_datasets IS NOT NULL) AND (:new.curator_checked_datasets IS NULL)) OR (:old.curator_checked_datasets != :new.curator_checked_datasets))
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'CURATOR_CHECKED_DATASETS', :old.curation_id, :old.curator_checked_datasets, :new.curator_checked_datasets, USER);
    END IF;

    IF (((:old.curator_checked_genelist IS NULL) AND (:new.curator_checked_genelist IS NOT NULL)) OR ((:old.curator_checked_genelist IS NOT NULL) AND (:new.curator_checked_genelist IS NULL)) OR (:old.curator_checked_genelist != :new.curator_checked_genelist))
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'CURATOR_CHECKED_GENELIST', :old.curation_id, :old.curator_checked_genelist, :new.curator_checked_genelist, USER);
    END IF;

    IF (((:old.no_action_required IS NULL) AND (:new.no_action_required IS NOT NULL)) OR ((:old.no_action_required IS NOT NULL) AND (:new.no_action_required IS NULL)) OR (:old.no_action_required != :new.no_action_required))
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'NO_ACTION_REQUIRED', :old.curation_id, :old.no_action_required, :new.no_action_required, USER);
    END IF;

    IF (((:old.research_results IS NULL) AND (:new.research_results IS NOT NULL)) OR ((:old.research_results IS NOT NULL) AND (:new.research_results IS NULL)) OR (:old.research_results != :new.research_results))
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'RESEARCH_RESULTS', :old.curation_id, :old.research_results, :new.research_results, USER);
    END IF;

    IF (((:old.gene_list IS NULL) AND (:new.gene_list IS NOT NULL)) OR ((:old.gene_list IS NOT NULL) AND (:new.gene_list IS NULL)) OR (:old.gene_list != :new.gene_list))
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'GENE_LIST', :old.curation_id, :old.gene_list, :new.gene_list, USER);
    END IF;

    IF (((:old.dataset_description IS NULL) AND (:new.dataset_description IS NOT NULL)) OR ((:old.dataset_description IS NOT NULL) AND (:new.dataset_description IS NULL)) OR (:old.dataset_description != :new.dataset_description))
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'DATASET_DESCRIPTION', :old.curation_id, :old.dataset_description, :new.dataset_description, USER);
    END IF;

    IF (((:old.other_description IS NULL) AND (:new.other_description IS NOT NULL)) OR ((:old.other_description IS NOT NULL) AND (:new.other_description IS NULL)) OR (:old.other_description != :new.other_description))
    THEN
        AuditLog.InsertUpdateLog('AUTHORRESPONSE', 'OTHER_DESCRIPTION', :old.curation_id, :old.other_description, :new.other_description, USER);
    END IF;

  ELSE

    v_part := :old.curation_id || '[:]' || :old.reference_id || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.colleague_id || '[:]' || :old.author_email || '[:]' ||
             :old.has_novel_research || '[:]' || :old.has_large_scale_data || '[:]' ||
             :old.has_fast_track_tag || '[:]' || :old.curator_checked_datasets || '[:]' ||
             :old.curator_checked_genelist || '[:]' || :old.no_action_required || '[:]' ||
             :old.gene_list || '[:]' ||
             :old.dataset_description || '[:]' || :old.other_description || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    v_row := concat(concat(v_part, '[:]'), :old.research_results);

    AuditLog.InsertDeleteLog('AUTHORRESPONSE', :old.curation_id, v_row, USER);

  END IF;

END Authorresponse_AUDR;
/
SHOW ERROR
