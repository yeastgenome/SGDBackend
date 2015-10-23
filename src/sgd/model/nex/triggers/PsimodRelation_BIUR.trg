Create OR REPLACE TRIGGER PsimodRelation_BIUR
--
-- Before insert or update trigger for psimod_relation table
--
  BEFORE INSERT OR UPDATE ON psimod_relation
  FOR EACH ROW
DECLARE
  v_IsValidUser         dbuser.username%TYPE;
BEGIN
  IF INSERTING THEN

    IF (:new.relation_id IS NULL) THEN
        SELECT relation_seq.NEXTVAL INTO :new.relation_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSE

    IF (:new.relation_id != :old.relation_id) THEN    
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

END PsimodRelation_BIUR;
/
SHOW ERROR
