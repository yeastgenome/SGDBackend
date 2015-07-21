CREATE OR REPLACE TRIGGER Straindbentity_BUR
--
-- Before update trigger for the straindbentity table
--
  BEFORE UPDATE ON straindbentity
  FOR EACH ROW
BEGIN

  	IF (:new.dbentity_id != :old.dbentity_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

END Straindbentity_BUR;
/
SHOW ERROR
