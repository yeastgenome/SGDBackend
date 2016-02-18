CREATE OR REPLACE TRIGGER ArchLiteratureannotation_BIUDR
--
-- Before insert, update or delete trigger for the arch_literatureannotation table
--
  BEFORE INSERT OR UPDATE OR DELETE ON arch_literatureannotation
  FOR EACH ROW
DECLARE
  v_IsValidUser     dbuser.username%TYPE;
  v_CanDelete       NUMBER;
BEGIN
  IF INSERTING THEN

    IF (:new.archive_id IS NULL) THEN
        SELECT archive_seq.NEXTVAL INTO :new.archive_id FROM DUAL;
    END IF; 

    v_IsValidUser := CheckUser(:new.created_by);

  ELSIF UPDATING THEN

    IF (:new.archive_id != :old.archive_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF (:new.reference_id != :old.reference_id) THEN
        RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.source_id != :old.source_id) THEN
        RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.taxonomy_id != :old.taxonomy_id) THEN
        RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.locus_id != :old.locus_id) THEN
        RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.bud_id != :old.bud_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.topic != :old.topic) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.date_created != :old.date_created) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.created_by != :old.created_by) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.date_archived != :old.date_archived) THEN    
        RAISE_APPLICATION_ERROR
            (-20001, 'Audit columns cannot be updated.');
    END IF;

  ELSE

    v_CanDelete := CheckDelete.CheckTableDelete('ARCH_LITERATUREANNOTATION');  

  END IF;

END ArchLiteratureannotation_BIUDR;
/
SHOW ERROR
