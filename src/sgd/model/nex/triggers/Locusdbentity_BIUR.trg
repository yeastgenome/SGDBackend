CREATE OR REPLACE TRIGGER Locusdbentity_BIUR
--
-- Before insert or update trigger for the locusdbentity table
--
  BEFORE INSERT OR UPDATE ON locusdbentity
  FOR EACH ROW
DECLARE
  v_IsValidUser     dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.gene_name IS NOT NULL) THEN
        :new.gene_name := UPPER(:new.gene_name);
    END IF;

  ELSE

    IF (:new.dbentity_id != :old.dbentity_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF (:new.gene_name IS NOT NULL) THEN
        :new.gene_name := UPPER(:new.gene_name);
    END IF;

   END IF;

END Locusdbentity_BIUR;
/
SHOW ERROR
