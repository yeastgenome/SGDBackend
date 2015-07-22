CREATE OR REPLACE TRIGGER Referencdbeentity_BIUR
--
-- Before insert or update trigger for referencedbentity table
--
  BEFORE INSERT OR UPDATE ON referencedbentity
  FOR EACH ROW
BEGIN
  IF INSERTING THEN

    IF ((:new.journal_id IS NOT NULL) AND (:new.book_id IS NOT NULL)) THEN
        RAISE_APPLICATION_ERROR
            (-20018, 'journal_id and book_id can not both be NOT NULL.');
    END IF;

    IF ((:new.journal_id IS NOT NULL) AND (:new.method_obtained = 'Published') AND (:new.pubmed_id IS NOT NULL)) THEN
        IF (:new.title IS NULL) THEN
            RAISE_APPLICATION_ERROR
                (-20019, 'Reference title must be entered if there is a Pubmed_ID.');
        END IF;
    END IF;

  ELSE

    IF (:new.reference_id != :old.reference_id) THEN    
        RAISE_APPLICATION_ERROR
            (-20000, 'Primary key cannot be updated');
    END IF;

    IF ((:new.journal_id IS NOT NULL) AND (:new.book_id IS NOT NULL)) THEN
        RAISE_APPLICATION_ERROR
            (-20018, 'journal_id and book_id can not both be NOT NULL.');
    END IF;

    IF ((:new.journal_id IS NOT NULL) AND (:new.method_obtained = 'Published') AND (:new.pubmed_id IS NOT NULL)) THEN
        IF (:new.title IS NULL) THEN
            RAISE_APPLICATION_ERROR
                (-20019, 'Reference title must be entered if there is a Pubmed_ID.');
        END IF;
    END IF;

  END IF;

END Referencedbentity_BIUR;
/
SHOW ERROR
