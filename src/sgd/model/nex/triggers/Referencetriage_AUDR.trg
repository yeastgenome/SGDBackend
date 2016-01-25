CREATE OR REPLACE TRIGGER Referencetriage_AUDR
--
--  After a Curation row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON referencetriage
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
    v_part       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.pmid != :new.pmid)
    THEN
        AuditLog.InsertUpdateLog('REFERENCETRIAGE', 'PMID', :old.curation_id, :old.pmid, :new.pmid, USER);
    END IF;

     IF (:old.citation != :new.citation)
    THEN
        AuditLog.InsertUpdateLog('REFERENCETRIAGE', 'CITATION', :old.curation_id, :old.citation, :new.citation, USER);
    END IF;

    IF (((:old.fulltext_url IS NULL) AND (:new.fulltext_url IS NOT NULL)) OR ((:old.fulltext_url IS NOT NULL) AND (:new.fulltext_url IS NULL)) OR (:old.fulltext_url != :new.fulltext_url))
    THEN
        AuditLog.InsertUpdateLog('REFERENCETRIAGE', 'FULLTEXT_URL', :old.curation_id, :old.fulltext_url, :new.fulltext_url, USER);
    END IF;

    IF (((:old.abstract IS NULL) AND (:new.abstract IS NOT NULL)) OR ((:old.abstract IS NOT NULL) AND (:new.abstract IS NULL)) OR (:old.abstract != :new.abstract))
    THEN
        AuditLog.InsertUpdateLog('REFERENCETRIAGE', 'ABSTRACT', :old.curation_id, :old.abstract, :new.abstract, USER);
    END IF;

  ELSE

    v_part := :old.curation_id || '[:]' || :old.pmid || '[:]' ||
             :old.citation || '[:]' || :old.fulltext_url || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    v_row := concat(concat(v_part, '[:]'), :old.abstract);

    AuditLog.InsertDeleteLog('REFERENCETRIAGE', :old.curation_id, v_row, USER);

  END IF;

END Referencetriage_AUDR;
/
SHOW ERROR
