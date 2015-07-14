CREATE OR REPLACE TRIGGER TaxonomyRelation_AUDR
--
--  After a row in the taxonomy_relation table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON taxonomy_relation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('TAXONOMY_RELATION', 'SOURCE_ID', :old.relation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('TAXONOMY_RELATION', 'BUD_ID', :old.relation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

	 IF (:old.parent_id != :new.parent_id)
    THEN
        AuditLog.InsertUpdateLog('TAXONOMY_RELATION', 'PARENT_ID', :old.relation_id, :old.parent_id, :new.parent_id, USER);
    END IF;

     IF (:old.child_id != :new.child_id)
    THEN
        AuditLog.InsertUpdateLog('TAXONOMY_RELATION', 'CHILD_ID', :old.relation_id, :old.child_id, :new.child_id, USER);
    END IF;

    IF (:old.relation_type != :new.relation_type)
    THEN
        AuditLog.InsertUpdateLog('TAXONOMY_RELATION', 'RELATION_TYPE', :old.relation_id, :old.relation_type, :new.relation_type, USER);
    END IF;

  ELSE

    v_row := :old.relation_id || '[:]' || :old.source_id || '[:]' ||
		  	 :old.bud_id || '[:]' || :old.parent_id || '[:]' ||
             :old.child_id || '[:]' || :old.relation_type || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('TAXONOMY_RELATION', :old.relation_id, v_row, USER);

  END IF;

END TaxonomyRelation_AUDR;
/
SHOW ERROR