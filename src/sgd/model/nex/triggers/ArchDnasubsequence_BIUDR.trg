Create OR REPLACE TRIGGER ArchDnasubsequence_BIUDR
--
-- Before insert, update or delete trigger for arch_dnasubsequence table
--
  BEFORE INSERT OR UPDATE OR DELETE ON arch_dnasubsequence
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

    IF (:new.dnasubsequence_id != :old.dnasubsequence_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.annotation_id != :old.annotation_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.dbentity_id != :old.dbentity_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.display_name != :old.display_name) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.bud_id != :old.bud_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.so_id != :old.so_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.relative_start_index != :old.relative_start_index) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.relative_end_index != :old.relative_end_index) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.contig_start_index != :old.contig_start_index) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.contig_end_index != :old.contig_end_index) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.seq_version != :old.seq_version) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.coord_version != :old.coord_version) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.genomerelease_id != :old.genomerelease_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.file_header != :old.file_header) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.download_filename != :old.download_filename) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.file_id != :old.file_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.residues != :old.residues) THEN
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

    v_CanDelete := CheckDelete.CheckTableDelete('ARCH_DNASUBSEQUENCE');  

  END IF;

END ArchDnasubsequence_BIUDR;
/
SHOW ERROR
