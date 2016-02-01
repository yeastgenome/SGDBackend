CREATE OR REPLACE TRIGGER FileKeyword_BIUR
--
-- Before insert or update trigger for file_keyword table
--
  BEFORE INSERT OR UPDATE ON file_keyword
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.file_keyword_id IS NULL) THEN
        SELECT link_seq.NEXTVAL INTO :new.file_keyword_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);
 
  ELSE

    IF (:new.file_keyword_id != :old.file_keyword_id) THEN    
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

END FileKeyword_BIUR;
/
SHOW ERROR
