CREATE OR REPLACE TRIGGER ProteinsequenceDetail_AUDR
--
--  After a row in the proteinsequence_detail table is updated or deleted,
--  write record to update_log or delete_log table
--
    AFTER UPDATE OR DELETE ON proteinsequence_detail
    FOR EACH ROW
DECLARE
    v_row       delete_log.deleted_row%TYPE;
BEGIN
  IF UPDATING THEN

    IF (:old.annotation_id != :new.annotation_id)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'ANNOTATION_ID', :old.detail_id, :old.ANNOTATION_ID, :new.annotation_id, USER);
    END IF;

    IF (((:old.bud_id IS NULL) AND (:new.bud_id IS NOT NULL)) OR ((:old.bud_id IS NOT NULL) AND (:new.bud_id IS NULL)) OR (:old.bud_id != :new.bud_id))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'BUD_ID', :old.detail_id, :old.BUD_ID, :new.bud_id, USER);
    END IF;

    IF (:old.molecular_weight != :new.molecular_weight)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'MOLECULAR_WEIGHT', :old.detail_id, :old.MOLECULAR_WEIGHT, :new.molecular_weight, USER);
    END IF;

    IF (:old.protein_length != :new.protein_length)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'PROTEIN_LENGTH', :old.detail_id, :old.PROTEIN_LENGTH, :new.protein_length, USER);
    END IF;

    IF (:old.n_term_seq != :new.n_term_seq)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'N_TERM_SEQ', :old.detail_id, :old.N_TERM_SEQ, :new.n_term_seq, USER);
    END IF;

    IF (:old.c_term_seq != :new.c_term_seq)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'C_TERM_SEQ', :old.detail_id, :old.C_TERM_SEQ, :new.c_term_seq, USER);
    END IF;

    IF (((:old.pi IS NULL) AND (:new.pi IS NOT NULL)) OR ((:old.pi IS NOT NULL) AND (:new.pi IS NULL)) OR (:old.pi != :new.pi))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'PI', :old.detail_id, :old.PI, :new.pi, USER);
    END IF;

    IF (((:old.cai IS NULL) AND (:new.cai IS NOT NULL)) OR ((:old.cai IS NOT NULL) AND (:new.cai IS NULL)) OR (:old.cai != :new.cai))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'CAI', :old.detail_id, :old.CAI, :new.cai, USER);
    END IF;

    IF (((:old.codon_bias IS NULL) AND (:new.codon_bias IS NOT NULL)) OR ((:old.codon_bias IS NOT NULL) AND (:new.codon_bias IS NULL)) OR (:old.codon_bias != :new.codon_bias))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'CODON_BIAS', :old.detail_id, :old.CODON_BIAS, :new.codon_bias, USER);
    END IF;

    IF (((:old.fop_score IS NULL) AND (:new.fop_score IS NOT NULL)) OR ((:old.fop_score IS NOT NULL) AND (:new.fop_score IS NULL)) OR (:old.fop_score != :new.fop_score))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'FOP_SCORE', :old.detail_id, :old.FOP_SCORE, :new.fop_score, USER);
    END IF;

    IF (((:old.gravy_score IS NULL) AND (:new.gravy_score IS NOT NULL)) OR ((:old.gravy_score IS NOT NULL) AND (:new.gravy_score IS NULL)) OR (:old.gravy_score != :new.gravy_score))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'GRAVY_SCORE', :old.detail_id, :old.GRAVY_SCORE, :new.gravy_score, USER);
    END IF;

    IF (((:old.aromaticity_score IS NULL) AND (:new.aromaticity_score IS NOT NULL)) OR ((:old.aromaticity_score IS NOT NULL) AND (:new.aromaticity_score IS NULL)) OR (:old.aromaticity_score != :new.aromaticity_score))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'AROMATICITY_SCORE', :old.detail_id, :old.AROMATICITY_SCORE, :new.aromaticity_score, USER);
    END IF;

    IF (((:old.aliphatic_index IS NULL) AND (:new.aliphatic_index IS NOT NULL)) OR ((:old.aliphatic_index IS NOT NULL) AND (:new.aliphatic_index IS NULL)) OR (:old.aliphatic_index != :new.aliphatic_index))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'ALIPHATIC_INDEX', :old.detail_id, :old.ALIPHATIC_INDEX, :new.aliphatic_index, USER);
    END IF;

    IF (((:old.instability_index IS NULL) AND (:new.instability_index IS NOT NULL)) OR ((:old.instability_index IS NOT NULL) AND (:new.instability_index IS NULL)) OR (:old.instability_index != :new.instability_index))
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'INSTABILITY_INDEX', :old.detail_id, :old.INSTABILITY_INDEX, :new.instability_index, USER);
    END IF;

    IF (:old.ala != :new.ala)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'ALA', :old.detail_id, :old.ALA, :new.ala, USER);
    END IF;

    IF (:old.arg != :new.arg)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'ARG', :old.detail_id, :old.ARG, :new.arg, USER);
    END IF;

    IF (:old.asn != :new.asn)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'ASN', :old.detail_id, :old.ASN, :new.asn, USER);
    END IF;

    IF (:old.asp != :new.asp)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'ASP', :old.detail_id, :old.ASP, :new.asp, USER);
    END IF;

    IF (:old.cys != :new.cys)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'CYS', :old.detail_id, :old.CYS, :new.cys, USER);
    END IF;

    IF (:old.gln != :new.gln)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'GLN', :old.detail_id, :old.GLN, :new.gln, USER);
    END IF;

    IF (:old.glu != :new.glu)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'GLU', :old.detail_id, :old.GLU, :new.glu, USER);
    END IF;

    IF (:old.gly != :new.gly)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'GLY', :old.detail_id, :old.GLY, :new.gly, USER);
    END IF;

    IF (:old.his != :new.his)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'HIS', :old.detail_id, :old.HIS, :new.his, USER);
    END IF;

    IF (:old.ile != :new.ile)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'ILE', :old.detail_id, :old.ILE, :new.ile, USER);
    END IF;

    IF (:old.leu != :new.leu)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'LEU', :old.detail_id, :old.LEU, :new.leu, USER);
    END IF;

    IF (:old.lys != :new.lys)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'LYS', :old.detail_id, :old.LYS, :new.lys, USER);
    END IF;

    IF (:old.met != :new.met)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'MET', :old.detail_id, :old.MET, :new.met, USER);
    END IF;

    IF (:old.phe != :new.phe)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'PHE', :old.detail_id, :old.PHE, :new.phe, USER);
    END IF;

    IF (:old.pro != :new.pro)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'PRO', :old.detail_id, :old.PRO, :new.pro, USER);
    END IF;

    IF (:old.ser != :new.ser)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'SER', :old.detail_id, :old.SER, :new.ser, USER);
    END IF;

    IF (:old.thr != :new.thr)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'THR', :old.detail_id, :old.THR, :new.thr, USER);
    END IF;

    IF (:old.trp != :new.trp)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'TRP', :old.detail_id, :old.TRP, :new.trp, USER);
    END IF;

    IF (:old.tyr != :new.tyr)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'TYR', :old.detail_id, :old.TYR, :new.tyr, USER);
    END IF;

    IF (:old.val != :new.val)
    THEN
        AuditLog.InsertUpdateLog('PROTEINSEQUENCE_DETAIL', 'VAL', :old.detail_id, :old.VAL, :new.val, USER);
    END IF;

  ELSE

    v_row := :old.annotation_id || '[:]' || :old.bud_id || '[:]' ||
             :old.molecular_weight || '[:]' || :old.protein_length || '[:]' ||
             :old.n_term_seq || '[:]' || :old.c_term_seq || '[:]' || 
             :old.pi || '[:]' || :old.cai || '[:]' || 
             :old.codon_bias || '[:]' || :old.fop_score || '[:]' || 
             :old.gravy_score || '[:]' || :old.aromaticity_score || '[:]' || 
             :old.aliphatic_index || '[:]' || :old.instability_index || '[:]' ||
             :old.ala || '[:]' || :old.arg || '[:]' || :old.asn || '[:]' || 
             :old.asp || '[:]' || :old.cys || '[:]' || :old.gln || '[:]' || 
             :old.glu || '[:]' || :old.gly || '[:]' || :old.his || '[:]' || 
             :old.ile || '[:]' || :old.leu || '[:]' || :old.lys || '[:]' || 
             :old.met || '[:]' || :old.phe || '[:]' || :old.pro || '[:]' || 
             :old.ser || '[:]' || :old.thr || '[:]' || :old.trp || '[:]' || 
             :old.tyr || '[:]' || :old.val || '[:]' ||
             :old.hydrogen || '[:]' || :old.sulfur || '[:]' || 
             :old.nitrogen || '[:]' || :old.oxygen || '[:]' || 
             :old.carbon || '[:]' || :old.no_cys_ext_coeff || '[:]' || 
             :old.all_cys_ext_coeff || '[:]' || 
             :old.date_created || '[:]' || :old.created_by;

    AuditLog.InsertDeleteLog('PROTEINSEQUENCE_DETAIL', :old.detail_id, v_row, USER);

  END IF;

END ProteinsequenceDetail_AUDR;
/
SHOW ERROR
