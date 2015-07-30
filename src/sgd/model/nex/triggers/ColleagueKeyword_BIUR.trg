CREATE OR REPLACE TRIGGER ColleagueKeyword_BIUR
--
-- Before insert or update trigger for colleague_keyword table
--
  BEFORE INSERT OR UPDATE ON colleague_keyword
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.colleague_keyword_id IS NULL) THEN
        SELECT colleague_keyword_seq.NEXTVAL INTO :new.colleague_keyword_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);
 
  ELSE

    IF (:new.colleague_keyword_id != :old.colleague_keyword_id) THEN    
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

END ColleagueKeyword_BIUR;
/
SHOW ERROR
