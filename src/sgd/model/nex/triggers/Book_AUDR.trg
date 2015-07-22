CREATE OR REPLACE TRIGGER Book_AUDR
--
--  After a row in the book table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON book
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.format_name != :new.format_name)
    THEN
        AuditLog.InsertUpdateLog('BOOK', 'FORMAT_NAME', :old.book_id, :old.format_name, :new.format_name, USER);
    END IF;

     IF (:old.display_name != :new.display_name)
    THEN
        AuditLog.InsertUpdateLog('BOOK', 'DISPLAY_NAME', :old.book_id, :old.display_name, :new.display_name, USER);
    END IF;

    IF (:old.obj_url != :new.obj_url)
    THEN
        AuditLog.InsertUpdateLog('BOOK', 'OBJ_URL', :old.book_id, :old.obj_url, :new.obj_url, USER);
    END IF;

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('BOOK', 'SOURCE_ID', :old.book_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('BOOK', 'BUD_ID', :old.book_id, :old.bud_id, :new.bud_id, USER);
    END IF;

    IF (:old.title != :new.title)
    THEN
        AuditLog.InsertUpdateLog('BOOK', 'TITLE', :old.book_id, :old.title, :new.title, USER);
    END IF;

    IF (((:old.volume_title IS NULL) AND (:new.volume_title IS NOT NULL)) OR ((:old.volume_title IS NOT NULL) AND (:new.volume_title IS NULL)) OR (:old.volume_title != :new.volume_title))
    THEN
        AuditLog.InsertUpdateLog('BOOK', 'VOLUME_TITLE', :old.book_id, :old.volume_title, :new.volume_title, USER);
    END IF;

    IF (((:old.isbn IS NULL) AND (:new.isbn IS NOT NULL)) OR ((:old.isbn IS NOT NULL) AND (:new.isbn IS NULL)) OR (:old.isbn != :new.isbn))
    THEN
        AuditLog.InsertUpdateLog('BOOK', 'ISBN', :old.book_id, :old.isbn, :new.isbn, USER);
    END IF;

    IF (((:old.total_pages IS NULL) AND (:new.total_pages IS NOT NULL)) OR ((:old.total_pages IS NOT NULL) AND (:new.total_pages IS NULL)) OR (:old.total_pages != :new.total_pages))
    THEN
        AuditLog.InsertUpdateLog('BOOK', 'TOTAL_PAGES', :old.book_id, :old.total_pages, :new.total_pages, USER);
    END IF;

    IF (((:old.publisher IS NULL) AND (:new.publisher IS NOT NULL)) OR ((:old.publisher IS NOT NULL) AND (:new.publisher IS NULL)) OR (:old.publisher != :new.publisher))
    THEN
        AuditLog.InsertUpdateLog('BOOK', 'PUBLISHER', :old.book_id, :old.publisher, :new.publisher, USER);
    END IF;

  ELSE

    v_row := :old.book_id || '[:]' || :old.format_name || '[:]' ||
             :old.display_name || '[:]' || :old.obj_url || '[:]' ||
             :old.source_id || '[:]' || :old.bud_id || '[:]' ||
             :old.title || '[:]' || :old.volume_title || '[:]' || 
             :old.isbn || '[:]' || :old.total_pages || '[:]' ||
             :old.publisher || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('BOOK', :old.book_id, v_row, USER);

  END IF;

END Book_AUDR;
/
SHOW ERROR
