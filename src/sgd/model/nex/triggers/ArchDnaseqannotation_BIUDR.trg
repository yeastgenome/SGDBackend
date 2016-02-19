Create OR REPLACE TRIGGER ArchDnaseqannotation_BIUDR
--
-- Before insert, update or delete trigger for arch_dnaseqannotation table
--
  BEFORE INSERT OR UPDATE OR DELETE ON arch_dnaseqannotation
  FOR EACH ROW
DECLARE
  v_IsValidUser     dbuser.username%TYPE;
  v_CanDelete       NUMBER;
BEGIN
  IF INSERTING THEN

    v_IsValidUser := CheckUser(:new.created_by);

  ELSIF UPDATING THEN

    IF (:new.annotation_id != :old.annotation_id) THEN
        RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.dbentity_id != :old.dbentity_id) THEN
        RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.source_id != :old.source_id) THEN
        RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.reference_id != :old.reference_id) THEN
        RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.taxonomy_id != :old.taxonomy_id) THEN
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

    IF (:new.dna_type != :old.dna_type) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.contig_id != :old.contig_id) THEN
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

    IF (:new.start_index != :old.start_index) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.end_index != :old.end_index) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.strand != :old.strand) THEN
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

    v_CanDelete := CheckDelete.CheckTableDelete('ARCH_DNASEQANNOTATION');  

  END IF;

END ArchDnaseqannotation_BIUDR;
/
SHOW ERROR
