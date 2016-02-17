CREATE OR REPLACE TRIGGER Dbentity_BIUDR
--
-- Before insert, update or delete trigger for dbentity table
--
  BEFORE INSERT OR UPDATE OR DELETE ON dbentity
  FOR EACH ROW
DECLARE
  v_IsValidUser   dbuser.username%TYPE;
  v_IsSgdidValid  sgdid.display_name%TYPE;
  v_LowerSubclass  dbentity.subclass%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.dbentity_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.dbentity_id FROM DUAL;
    END IF;

    IF (:new.sgdid IS NULL) THEN
        :new.sgdid := MakeSgdid;
    ELSE
        :new.sgdid := UPPER(:new.sgdid);
         v_IsSgdidValid := ManageSgdid.CheckSgdid(:new.sgdid);
    END IF;

   IF (:new.obj_url is NULL) THEN
        v_LowerSubclass := LOWER(:new.subclass);
        :new.obj_url := CONCAT('/'||v_LowerSubclass||'/', :new.sgdid);
   END IF;

    IF (:new.subclass = 'LOCUS') THEN
        IF (:new.dbentity_status = 'Archived') THEN
		    RAISE_APPLICATION_ERROR
                 (-20039, 'Allowable values are Active, Merged, Deleted.');
        END IF;
    ELSIF (:new.subclass = 'FILE') THEN
        IF (:new.dbentity_status = 'Merged') OR (:new.dbentity_status = 'Deleted') THEN
            RAISE_APPLICATION_ERROR
                 (-20040, 'Allowable values are Active or Archived.');
        END IF;
    ELSIF (:new.subclass = 'STRAIN') OR (:new.subclass = 'REFERENCE') OR (:new.subclass = 'PATHWAY') THEN
        IF (:new.dbentity_status != 'Active') THEN
            RAISE_APPLICATION_ERROR
                 (-20041, 'Only allowable value is Active.');
      	END IF;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSIF UPDATING THEN

    IF (:new.dbentity_id != :old.dbentity_id) THEN
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF (:new.sgdid != :old.sgdid) THEN
        RAISE_APPLICATION_ERROR
            (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.subclass = 'LOCUS') THEN
	    IF (:new.dbentity_status = 'Archived') THEN
            RAISE_APPLICATION_ERROR
                 (-20039, 'Allowable values are Active, Merged, Deleted.');
		END IF;
    ELSIF (:new.subclass = 'FILE') THEN
	    IF (:new.dbentity_status = 'Merged') OR (:new.dbentity_status = 'Deleted') THEN
            RAISE_APPLICATION_ERROR
                 (-20040, 'Allowable values are Active or Archived.');
	    END IF;
    ELSIF (:new.subclass = 'STRAIN') OR (:new.subclass = 'REFERENCE') OR (:new.subclass = 'PATHWAY') THEN
	    IF (:new.dbentity_status != 'Active') THEN
            RAISE_APPLICATION_ERROR
                 (-20041, 'Only allowable value is Active.');
		END IF;
    END IF;

    IF (:new.date_created != :old.date_created) THEN
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

    IF (:new.created_by != :old.created_by) THEN
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

  ELSE

    IF ((:new.subclass = 'LOCUS') OR (:new.subclass = 'STRAIN')) THEN
       RAISE_APPLICATION_ERROR
                 (-20042, 'This dbentity subclass can not be deleted.');
    END	IF;

  END IF;

END Dbentity_BIUDR;
/
SHOW ERROR
