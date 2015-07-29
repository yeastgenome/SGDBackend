Create OR REPLACE TRIGGER ReferenceDocument_BIUR
--
-- Before insert or update trigger for reference_document table
--
  BEFORE INSERT OR UPDATE ON reference_document
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.reference_document_id IS NULL) THEN
        SELECT reference_document_seq.NEXTVAL INTO :new.reference_document_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);
 
  ELSE

    IF (:new.reference_document_id != :old.reference_document_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
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

END ReferenceDocument_BIUR;
/
SHOW ERROR
