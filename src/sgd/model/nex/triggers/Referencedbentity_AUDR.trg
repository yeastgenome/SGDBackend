CREATE OR REPLACE TRIGGER Referencedbentity_AUDR
--
--  After a row in the referencedbentity table is updated or deleted, 
--  execute a trigger or write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE  ON referencedbentity
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  If UPDATING THEN

    IF (:old.method_obtained != :new.method_obtained)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'METHOD_OBTAINED', :old.dbentity_id, :old.method_obtained, :new.method_obtained, USER);
    END IF;

    IF (:old.fulltext_status != :new.fulltext_status)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'FULLTEXT_STATUS', :old.dbentity_id, :old.fulltext_status, :new.fulltext_status, USER);
    END IF;

    IF (:old.citation != :new.citation)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'CITATION', :old.dbentity_id, :old.citation, :new.citation, USER);
    END IF;

    IF (:old.year != :new.year)
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'YEAR', :old.dbentity_id, :old.year, :new.year, USER);
    END IF;

    IF (((:old.pubmed_id IS NULL) AND (:new.pubmed_id IS NOT NULL)) OR ((:old.pubmed_id IS NOT NULL) AND (:new.pubmed_id IS NULL)) OR (:old.pubmed_id != :new.pubmed_id))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'PUBMED_ID', :old.dbentity_id, :old.pubmed_id, :new.pubmed_id, USER);
    END IF;

    IF (((:old.pubmed_central_id IS NULL) AND (:new.pubmed_central_id IS NOT NULL)) OR ((:old.pubmed_central_id IS NOT NULL) AND (:new.pubmed_central_id IS NULL)) OR (:old.pubmed_central_id != :new.pubmed_central_id))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'PUBMED_CENTRAL_ID', :old.dbentity_id, :old.pubmed_central_id, :new.pubmed_central_id, USER);
    END IF;

    IF (((:old.date_published IS NULL) AND (:new.date_published IS NOT NULL)) OR ((:old.date_published IS NOT NULL) AND (:new.date_published IS NULL)) OR (:old.date_published != :new.date_published))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'DATE_PUBLISHED', :old.dbentity_id, :old.date_published, :new.date_published, USER);
    END IF;

    IF (((:old.date_revised IS NULL) AND (:new.date_revised IS NOT NULL)) OR ((:old.date_revised IS NOT NULL) AND (:new.date_revised IS NULL)) OR (:old.date_revised != :new.date_revised))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'DATE_REVISED', :old.dbentity_id, :old.date_revised, :new.date_revised, USER);
    END IF;

    IF (((:old.issue IS NULL) AND (:new.issue IS NOT NULL)) OR ((:old.issue IS NOT NULL) AND (:new.issue IS NULL)) OR (:old.issue != :new.issue))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'ISSUE', :old.dbentity_id, :old.issue, :new.issue, USER);
    END IF;

    IF (((:old.page IS NULL) AND (:new.page IS NOT NULL)) OR ((:old.page IS NOT NULL) AND (:new.page IS NULL)) OR (:old.page != :new.page))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'PAGE', :old.dbentity_id, :old.page, :new.page, USER);
    END IF;

    IF (((:old.volume IS NULL) AND (:new.volume IS NOT NULL)) OR ((:old.volume IS NOT NULL) AND (:new.volume IS NULL)) OR (:old.volume != :new.volume))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'VOLUME', :old.dbentity_id, :old.volume, :new.volume, USER);
    END IF;

    IF (((:old.title IS NULL) AND (:new.title IS NOT NULL)) OR ((:old.title IS NOT NULL) AND (:new.title IS NULL)) OR (:old.title != :new.title))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'TITLE', :old.dbentity_id, :old.title, :new.title, USER);
    END IF;

    IF (((:old.doi IS NULL) AND (:new.doi IS NOT NULL)) OR ((:old.doi IS NOT NULL) AND (:new.doi IS NULL)) OR (:old.doi != :new.doi))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'DOI', :old.dbentity_id, :old.doi, :new.doi, USER);
    END IF;

    IF (((:old.journal_no IS NULL) AND (:new.journal_no IS NOT NULL)) OR ((:old.journal_no IS NOT NULL) AND (:new.journal_no IS NULL)) OR (:old.journal_no != :new.journal_no))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'JOURNAL_NO', :old.dbentity_id, :old.journal_no, :new.journal_no, USER);
    END IF;

    IF (((:old.book_no IS NULL) AND (:new.book_no IS NOT NULL)) OR ((:old.book_no IS NOT NULL) AND (:new.book_no IS NULL)) OR (:old.book_no != :new.book_no))
    THEN
        AuditLog.InsertUpdateLog('REFERENCE', 'BOOK_NO', :old.dbentity_id, :old.book_no, :new.book_no, USER);
    END IF;

  ELSE

  UPDATE dbentity SET dbentity_status = 'Deleted'
  WHERE dbentity_id = :old.dbentity_id;

  v_row := :old.dbentity_id || '[:]' || :old.method_obtained || '[:]' ||
           :old.fulltext_status || '[:]' || :old.citation || '[:]' || 
           :old.year || '[:]' || :old.pubmed_id || '[:]' ||
           :old.pubmed_central_id || '[:]' || :old.date_published || '[:]' || 
           :old.date_revised || '[:]' || :old.issue || '[:]' || 
           :old.page || '[:]' || :old.volume || '[:]' || 
           :old.title || '[:]' || :old.doi || '[:]' ||
           :old.journal_no || '[:]' || :old.book_no || '[:]' ||
           :old.date_created || '[:]' || :old.created_by;

  AuditLog.InsertDeleteLog('REFERENCE', :old.dbentity_id, v_row, USER);

  END IF;

END Referencedbentity_AUDR;
/
SHOW ERROR
