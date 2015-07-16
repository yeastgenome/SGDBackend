CREATE OR REPLACE FUNCTION MakeSgdid RETURN VARCHAR2
--
-- Constructs and returns a SGDID  
--
IS
    v_Sgdid	    dbentity.sgdid%TYPE;
    v_SgdidNo   NUMBER;  
BEGIN

   SELECT sgdid_seq.NEXTVAL INTO v_SgdidNo FROM DUAL;

   IF (LENGTH(v_SgdidNo) = 9) THEN
        v_Sgdid := CONCAT('S',v_SgdidNo);
        RETURN (v_Sgdid);
   ELSIF (LENGTH(v_SgdidNo) = 8) THEN
        v_Sgdid := CONCAT('S0',v_SgdidNo);
        RETURN (v_Sgdid);
   ELSIF (LENGTH(v_SgdidNo) = 7) THEN
        v_Sgdid := CONCAT('S00',v_SgdidNo);
        RETURN (v_Sgdid);
   ELSIF (LENGTH(v_SgdidNo) = 6) THEN
        v_Sgdid := CONCAT('S000',v_SgdidNo);
        RETURN (v_Sgdid);
   ELSIF (LENGTH(v_SgdidNo) = 5) THEN
        v_Sgdid := CONCAT('S0000',v_SgdidNo);
        RETURN (v_Sgdid);
   ELSIF (LENGTH(v_SgdidNo) = 4) THEN
        v_Sgdid := CONCAT('S00000',v_SgdidNo);
        RETURN (v_Sgdid);
   ELSIF (LENGTH(v_SgdidNo) = 3) THEN
        v_Sgdid := CONCAT('S000000',v_SgdidNo);
        RETURN (v_Sgdid);
   ELSIF (LENGTH(v_SgdidNo) = 2) THEN
        v_Sgdid := CONCAT('S0000000',v_SgdidNo);
        RETURN (v_Sgdid);
   ELSIF (LENGTH(v_SgdidNo) = 1) THEN
        v_Sgdid := CONCAT('S00000000',v_SgdidNo);
        RETURN (v_Sgdid);
   ELSE
        RAISE_APPLICATION_ERROR
            (-20026, 'Invalid Sequence No: "' || v_SgdidNo || '"');
   END IF;

END MakeSgdid;
/
GRANT EXECUTE ON MakeSgdid to PUBLIC
/
SHOW ERROR
