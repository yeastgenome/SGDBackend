CREATE OR REPLACE TRIGGER ObinvestigationRelation_AUDR
--
--  After a row in the obinvestigation_relation table is updated or deleted, 
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON obinvestigation_relation
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

     IF (:old.source_id != :new.source_id)
    THEN
        AuditLog.InsertUpdateLog('OBINVESTIGATION_RELATION', 'SOURCE_ID', :old.relation_id, :old.source_id, :new.source_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('OBINVESTIGATION_RELATION', 'BUD_ID', :old.relation_id, :old.bud_id, :new.bud_id, USER);
    END IF;

	 IF (:old.parent_id != :new.parent_id)
    THEN
        AuditLog.InsertUpdateLog('OBINVESTIGATION_RELATION', 'PARENT_ID', :old.relation_id, :old.parent_id, :new.parent_id, USER);
    END IF;

     IF (:old.child_id != :new.child_id)
    THEN
        AuditLog.InsertUpdateLog('OBINVESTIGATION_RELATION', 'CHILD_ID', :old.relation_id, :old.child_id, :new.child_id, USER);
    END IF;

    IF (:old.relation_ontology_id != :new.relation_ontology_id)
    THEN
        AuditLog.InsertUpdateLog('OBINVESTIGATION_RELATION', 'RELATION_ONTOLOGY_ID', :old.relation_id, :old.relation_ontology_id, :new.relation_ontology_id, USER);
    END IF;

  ELSE

    v_row := :old.relation_id || '[:]' || :old.source_id || '[:]' ||
		  	 :old.bud_id || '[:]' || :old.parent_id || '[:]' ||
             :old.child_id || '[:]' || :old.relation_ontology_id || '[:]' ||
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('OBINVESTIGATION_RELATION', :old.relation_id, v_row, USER);

  END IF;

END ObinvestigationRelation_AUDR;
/
SHOW ERROR
