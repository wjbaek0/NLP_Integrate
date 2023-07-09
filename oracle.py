import os
import jaydebeapi as jp

JDBC_Driver = os.path.join("/home/xaiplanet/new_workspace", "ojdbc8.jar")
conn = jp.connect('oracle.jdbc.driver.OracleDriver','jdbc:oracle:thin:dsdp/ds1q2w3e4r@14.63.58.105:1521/ORCL', jars=JDBC_Driver)

# Query
try:
    with conn.cursor() as curs:
        sql = "select HAZOP_ID \
            ,   DSD_TY_CLS \
            ,   DSD_TY_CD \
            ,   FN_CODENM(DSD_TY_CLS, DSD_TY_CD)   DSDNM \
            ,   HM_DMG_RANK \
            ,   DIS_VLNTY \
            ,   SOC_VLNTY \
            ,   TRY_RDC \
            ,   RISK_SCORE \
            ,   RISK_GRD \
            ,   FUSN_HM_DMG \
            ,   FUSN_SCORE \
            ,   FUSN_RISK_GRD \
            ,   SENS_TXT \
            ,   SENS_MSG_ID \
            ,   SENS_MSG_YN \
            ,   ACT_TXT \
            ,   ACT_MSG_ID \
            ,   ACT_MSG_YN \
            from TB_ANL_HAZOP AH"
        # sql = "select \
        #         FN_CODENM(DSD_TY_CLS, DSD_TY_CD) DSDNM \
        #     ,   RISK_SCORE \
        #     ,   RISK_GRD \
        #     ,   FUSN_SCORE \
        #     ,   FUSN_RISK_GRD \
        #     from TB_ANL_HAZOP AH"
        curs.execute(sql)
        rs = curs.fetchall()
        for row in rs:
            print(row)
            
        # sql_ = "select * from TB_ANL_HAZOP AH"
        # curs.execute(sql_)
        # fs = curs.fetchall()
        # for f in fs:
        #     print(f)

finally:
    conn.close()