CREATE OR REPLACE TRIGGER ColleagueLocus_BIUR
--
-- Before insert or update trigger for colleague_locus table
--
  BEFORE INSERT OR UPDATE ON colleague_locus
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.colleague_locus_id IS NULL) THEN
        SELECT colleague_locus_seq.NEXTVAL INTO :new.colleague_locus_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);
 
  ELSE

    IF (:new.colleague_locus_id != :old.colleague_locus_id) THEN    
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

END ColleagueLocus_BIUR;
/
SHOW ERROR
