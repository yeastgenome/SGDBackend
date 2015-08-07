Create OR REPLACE TRIGGER ReferenceDeleted_BIUR
--
-- Before insert or update trigger for reference_deleted table
--
  BEFORE INSERT OR UPDATE ON reference_deleted
  FOR EACH ROW
DECLARE
  v_IsPubmedUsed        referencedbentity.pmid%TYPE;
  v_IsSgdidUsed         sgdid.display_name%TYPE;
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.reference_deleted_id IS NULL) THEN
        SELECT reference_deleted_seq.NEXTVAL INTO :new.reference_deleted_id FROM DUAL;
    END IF; 

    v_IsPubmedUsed := CheckPubmed(:new.pmid);

    IF (:new.sgdid IS NOT NULL) THEN
      v_IsSgdidUsed := ManageSgdid.CheckSgdid(:new.sgdid);
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.reference_deleted_id != :old.reference_deleted_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    v_IsPubmedUsed := CheckPubmed(:new.pmid);

    IF (:new.sgdid IS NOT NULL) THEN
      v_IsSgdidUsed := ManageSgdid.CheckSgdid(:new.sgdid);
    END IF;

    IF (:new.date_created != :old.date_created) THEN    
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

    IF (:new.created_by != :old.created_by) THEN    
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

  END IF;

END ReferenceDeleted_BIUR;
/
SHOW ERROR
