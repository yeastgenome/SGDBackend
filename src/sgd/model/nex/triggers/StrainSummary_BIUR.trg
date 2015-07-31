CREATE OR REPLACE TRIGGER StrainSummary_BIUR
--
-- Before insert or update trigger for strain_summary table
--
  BEFORE INSERT OR UPDATE ON strain_summary
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.summary_id IS NULL) THEN
        SELECT summary_seq.NEXTVAL INTO :new.summary_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);
 
  ELSE

    IF (:new.summary_id != :old.summary_id) THEN    
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

END StrainSummary_BIUR;
/
SHOW ERROR
