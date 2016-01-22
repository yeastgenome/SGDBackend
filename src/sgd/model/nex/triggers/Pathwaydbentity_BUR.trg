CREATE OR REPLACE TRIGGER Pathwaydbentity_BUR
--
-- Before update trigger for the pathwaydbentity table
--
  BEFORE UPDATE ON pathwaydbentity
  FOR EACH ROW
BEGIN

  	IF (:new.dbentity_id != :old.dbentity_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

END Pathwaydbentity_BUR;
/
SHOW ERROR
