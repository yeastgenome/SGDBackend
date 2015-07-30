CREATE OR REPLACE TRIGGER Colleague_BIUR
--
-- Before insert or update trigger for the colleague table
--
  BEFORE INSERT OR UPDATE ON colleague
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.colleague_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.colleague_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);

    IF ((:new.address1 IS NULL) AND (:new.address2 IS NOT NULL)) THEN
        RAISE_APPLICATION_ERROR
            (-20005, 'Lines of address must be entered consecutively');
    ELSE 
        IF ((:new.address2 IS NULL) AND (:new.address3 IS NOT NULL)) THEN
           RAISE_APPLICATION_ERROR
               (-20005, 'Lines of address must be entered consecutively');
        END IF;
    END IF;

    IF (:new.postal_code IS NOT NULL) THEN
        :new.postal_code := UPPER(:new.postal_code);
    END IF;

  ELSE

    IF (:new.colleague_id != :old.colleague_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF ((:new.address1 IS NULL) AND (:new.address2 IS NOT NULL)) THEN
        RAISE_APPLICATION_ERROR
            (-20005, 'Lines of address must be entered consecutively');
    ELSE
        IF ((:new.address2 IS NULL) AND (:new.address3 IS NOT NULL)) THEN
           RAISE_APPLICATION_ERROR
               (-20005, 'Lines of address must be entered consecutively');
        END IF;
    END IF;

    IF (:new.postal_code IS NOT NULL) THEN
        :new.postal_code := UPPER(:new.postal_code);
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

END Colleague_BIUR;
/
SHOW ERROR
