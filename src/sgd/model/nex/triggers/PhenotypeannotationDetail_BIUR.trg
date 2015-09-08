CREATE OR REPLACE TRIGGER PhenotypeannotationDetail_BIUR
--
-- Before insert or update trigger for the phenotypeannotation_detail table
--
  BEFORE INSERT OR UPDATE ON phenotypeannotation_detail
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.detail_id IS NULL) THEN
        SELECT detail_seq.NEXTVAL INTO :new.detail_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.detail_id != :old.detail_id) THEN    
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

END PhenotypeannotationDetail_BIUR;
/
SHOW ERROR
