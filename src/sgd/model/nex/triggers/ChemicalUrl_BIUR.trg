Create OR REPLACE TRIGGER ChemicalUrl_BIUR
--
-- Before insert or update trigger for chemical_url table
--
  BEFORE INSERT OR UPDATE ON chemical_url
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.url_id IS NULL) THEN
        SELECT url_seq.NEXTVAL INTO :new.url_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.url_id != :old.url_id) THEN    
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

END ChemicalUrl_BIUR;
/
SHOW ERROR
