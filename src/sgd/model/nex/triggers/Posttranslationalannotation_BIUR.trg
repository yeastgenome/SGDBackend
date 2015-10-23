CREATE OR REPLACE TRIGGER Posttranslationalannotation_BIUR
--
-- Before insert or update trigger for the posttranslationalannotation table
--
  BEFORE INSERT OR UPDATE ON posttranslationalannotation
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.annotation_id IS NULL) THEN
        SELECT annotation_seq.NEXTVAL INTO :new.annotation_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.annotation_id != :old.annotation_id) THEN    
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

END Posttranslationalannotation_BIUR;
/
SHOW ERROR
