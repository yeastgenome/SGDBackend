Create OR REPLACE TRIGGER ArchContig_BIUDR
--
-- Before insert, update or delete trigger for arch_contig table
--
  BEFORE INSERT OR UPDATE OR DELETE ON arch_contig
  FOR EACH ROW
DECLARE
  v_IsValidUser     dbuser.username%TYPE;
  v_CanDelete       NUMBER;
BEGIN
  IF INSERTING THEN

    IF (:new.contig_id IS NULL) THEN
        SELECT object_seq.NEXTVAL INTO :new.contig_id FROM DUAL;
    END IF;

    v_IsValidUser := CheckUser(:new.created_by);

  ELSIF UPDATING THEN

    IF (:new.contig_id != :old.contig_id) THEN
        RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.format_name != :old.format_name) THEN
        RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.display_name != :old.display_name) THEN
        RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.obj_url != :old.obj_url) THEN
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

    IF (:new.bud_id != :old.bud_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.so_id != :old.so_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.centromere_start != :old.centromere_start) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.centromere_end != :old.centromere_end) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.genbank_accession != :old.genbank_accession) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.gi_number != :old.gi_number) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.refseq_id != :old.refseq_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.reference_chromosome_id != :old.reference_chromosome_id) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.reference_start != :old.reference_start) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.reference_end != :old.reference_end) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.reference_percent_identity != :old.reference_percent_identity) THEN
    RAISE_APPLICATION_ERROR
             (-20029, 'This column cannot be updated.');
    END IF;

    IF (:new.reference_alignment_length != :old.reference_alignment_length) THEN
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

    IF (:new.description != :old.description) THEN
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

    v_CanDelete := CheckDelete.CheckTableDelete('ARCH_CONTIG');  

  END IF;

END ArchContig_BIUDR;
/
SHOW ERROR
