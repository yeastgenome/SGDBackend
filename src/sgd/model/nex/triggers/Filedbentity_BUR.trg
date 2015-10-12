CREATE OR REPLACE TRIGGER Filedbentity_BUR
--
-- Before update trigger for the filedbentity table
--
  BEFORE UPDATE ON filedbentity
  FOR EACH ROW
BEGIN

  	IF (:new.dbentity_id != :old.dbentity_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

END Filedbentity_BUR;
/
SHOW ERROR
