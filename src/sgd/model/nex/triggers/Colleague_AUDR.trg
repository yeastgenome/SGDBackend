CREATE OR REPLACE TRIGGER Colleague_AUDR
--
--  After a Colleague row is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON colleague
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'FORMAT_NAME', :old.colleague_id, :old.format_name, :new.format_name, USER);
    END IF;

         IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'DISPLAY_NAME', :old.colleague_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (((:old.obj_url IS NULL) AND (:new.obj_url IS NOT NULL)) OR ((:old.obj_url IS NOT NULL) AND (:new.obj_url IS NULL)) OR (:old.obj_url != :new.obj_url))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'OBJ_URL', :old.colleague_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'SOURCE_ID', :old.colleague_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'BUD_ID', :old.colleague_id, :old.bud_id, :new.bud_id, USER);
    END IF;

     IF (((:old.orcid IS NULL) AND (:new.orcid IS NOT NULL)) OR ((:old.orcid IS NOT NULL) AND (:new.orcid IS NULL)) OR (:old.orcid != :new.orcid))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'ORCID', :old.colleague_id, :old.orcid, :new.orcid, USER);
    END IF;

    IF (:old.last_name != :new.last_name) 
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'LAST_NAME', :old.colleague_id, :old.last_name, :new.last_name, USER);
    END IF;

    IF (:old.first_name != :new.first_name) 
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'FIRST_NAME', :old.colleague_id, :old.first_name, :new.first_name, USER);
    END IF;

    IF  (((:old.suffix IS NULL) AND (:new.suffix IS NOT NULL)) OR ((:old.suffix IS NOT NULL) AND (:new.suffix IS NULL)) OR (:old.suffix != :new.suffix))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'SUFFIX', :old.colleague_id, :old.suffix, :new.suffix, USER);
    END IF;

    IF (((:old.other_last_name IS NULL) AND (:new.other_last_name IS NOT NULL)) OR ((:old.other_last_name IS NOT NULL) AND (:new.other_last_name IS NULL)) OR (:old.other_last_name != :new.other_last_name)) 
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'OTHER_LAST_NAME', :old.colleague_id, :old.other_last_name, :new.other_last_name, USER);
    END IF;

    IF (((:old.profession IS NULL) AND (:new.profession IS NOT NULL)) OR ((:old.profession IS NOT NULL) AND (:new.profession IS NULL)) OR (:old.profession != :new.profession))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'PROFESSION', :old.colleague_id, :old.profession, :new.profession, USER);
    END IF;

    IF (((:old.job_title IS NULL) AND (:new.job_title IS NOT NULL)) OR ((:old.job_title IS NOT NULL) AND (:new.job_title IS NULL)) OR (:old.job_title != :new.job_title))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'JOB_TITLE', :old.colleague_id, :old.job_title, :new.job_title, USER);
    END IF;

    IF (((:old.institution IS NULL) AND (:new.institution IS NOT NULL)) OR ((:old.institution IS NOT NULL) AND (:new.institution IS NULL)) OR (:old.institution != :new.institution))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'INSTITUTION', :old.colleague_id, :old.institution, :new.institution, USER);
    END IF;

    IF (((:old.address1 IS NULL) AND (:new.address1 IS NOT NULL)) OR ((:old.address1 IS NOT NULL) AND (:new.address1 IS NULL)) OR (:old.address1 != :new.address1))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'ADDRESS1', :old.colleague_id, :old.address1, :new.address1, USER);
    END IF;

    IF (((:old.address2 IS NULL) AND (:new.address2 IS NOT NULL)) OR ((:old.address2 IS NOT NULL) AND (:new.address2 IS NULL)) OR (:old.address2 != :new.address2))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'ADDRESS2', :old.colleague_id, :old.address2, :new.address2, USER);
    END IF;

    IF (((:old.address3 IS NULL) AND (:new.address3 IS NOT NULL)) OR ((:old.address3 IS NOT NULL) AND (:new.address3 IS NULL)) OR (:old.address3 != :new.address3))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'ADDRESS3', :old.colleague_id, :old.address3, :new.address3, USER);
    END IF;

    IF (((:old.city IS NULL) AND (:new.city IS NOT NULL)) OR ((:old.city IS NOT NULL) AND (:new.city IS NULL)) OR (:old.city != :new.city))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'CITY', :old.colleague_id, :old.city, :new.city, USER);
    END IF;

    IF (((:old.state IS NULL) AND (:new.state IS NOT NULL)) OR ((:old.state IS NOT NULL) AND (:new.state IS NULL)) OR (:old.state != :new.state))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'STATE', :old.colleague_id, :old.state, :new.state, USER);
    END IF;

    IF (((:old.country IS NULL) AND (:new.country IS NOT NULL)) OR ((:old.country IS NOT NULL) AND (:new.country IS NULL)) OR (:old.country != :new.country))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'COUNTRY', :old.colleague_id, :old.country, :new.country, USER);
    END IF;

    IF (((:old.postal_code IS NULL) AND (:new.postal_code IS NOT NULL)) OR ((:old.postal_code IS NOT NULL) AND (:new.postal_code IS NULL)) OR (:old.postal_code != :new.postal_code))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'POSTAL_CODE', :old.colleague_id, :old.postal_code, :new.postal_code, USER);
    END IF;

    IF (((:old.work_phone IS NULL) AND (:new.work_phone IS NOT NULL)) OR ((:old.work_phone IS NOT NULL) AND (:new.work_phone IS NULL)) OR (:old.work_phone != :new.work_phone))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'WORK_PHONE', :old.colleague_id, :old.work_phone, :new.work_phone, USER);
    END IF;

    IF (((:old.other_phone IS NULL) AND (:new.other_phone IS NOT NULL)) OR ((:old.other_phone IS NOT NULL) AND (:new.other_phone IS NULL)) OR (:old.other_phone != :new.other_phone))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'OTHER_PHONE', :old.colleague_id, :old.other_phone, :new.other_phone, USER);
    END IF;

    IF (((:old.fax IS NULL) AND (:new.fax IS NOT NULL)) OR ((:old.fax IS NOT NULL) AND (:new.fax IS NULL)) OR (:old.fax != :new.fax))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'FAX', :old.colleague_id, :old.fax, :new.fax, USER);
    END IF;

    IF (((:old.email IS NULL) AND (:new.email IS NOT NULL)) OR ((:old.email IS NOT NULL) AND (:new.email IS NULL)) OR (:old.email != :new.email))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'EMAIL', :old.colleague_id, :old.email, :new.email, USER);
    END IF;

    IF (((:old.research_interest IS NULL) AND (:new.research_interest IS NOT NULL)) OR ((:old.research_interest IS NOT NULL) AND (:new.research_interest IS NULL)) OR (:old.research_interest != :new.research_interest))
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'RESEARCH_INTEREST', :old.colleague_id, :old.research_interest, :new.research_interest, USER);
    END IF;

    IF (:old.is_pi != :new.is_pi)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'IS_PI', :old.colleague_id, :old.is_pi, :new.is_pi, USER);
    END IF;

    IF (:old.is_contact != :new.is_contact)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'IS_CONTACT', :old.colleague_id, :old.is_contact, :new.is_contact, USER);
    END IF;

    IF (:old.display_email != :new.display_email) 
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'DISPLAY_EMAIL', :old.colleague_id, :old.display_email, :new.display_email, USER);
    END IF;

    IF (:old.date_last_modified != :new.date_last_modified)
    THEN
        AuditLog.InsertUpdateLog('COLLEAGUE', 'DATE_LAST_MODIFIED', :old.colleague_id, :old.date_last_modified, :new.date_last_modified, USER);
    END IF;

  ELSE

    v_row := :old.colleague_id || '[:]' || :old.format_name || '[:]' ||
             :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.orcid || '[:]' ||
             :old.last_name || '[:]' || :old.first_name || '[:]' || 
             :old.suffix || '[:]' || :old.other_last_name || '[:]' || 
             :old.profession || '[:]' || :old.job_title || '[:]' || 
             :old.institution || '[:]' || :old.address1 || '[:]' || 
             :old.address2 || '[:]' || :old.address3 || '[:]' || 
             :old.city || '[:]' || :old.state || '[:]' || 
             :old.country || '[:]' || 
             :old.postal_code || '[:]' || :old.work_phone || '[:]' ||
             :old.other_phone || '[:]' || :old.fax || '[:]' ||
             :old.email || '[:]' || :old.research_interest || '[:]' ||
             :old.is_pi || '[:]' || :old.is_contact || '[:]' ||
             :old.display_email || '[:]' || :old.date_last_modified || '[:]' || 
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('COLLEAGUE', :old.colleague_id, v_row, USER);

  END IF;

END Colleague_AUDR;
/
SHOW ERROR
