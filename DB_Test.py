
import pymysql
import datetime


db = pymysql.connect(
    host = '127.0.0.1',
    port = 3306,
    user = 'xai_root',
    password = 'xai123$%',
    db = 'mois_safety'
)



def update_log(file_id: int,class_log,ner_log,relation_log):
    print("----로그 저장 ")
    now = datetime.datetime.now()
    try:
        with db.cursor() as cur:
            sql = "INSERT INTO job_log (file_id, step , log_time, log_message) VALUES "\
                + f"({file_id}, {2}, '{now}', '{class_log}')" + ';'
            cur.execute(sql)
            sql2 = "INSERT INTO job_log (file_id, step , log_time, log_message) VALUES "\
                + f"({file_id}, {3}, '{now}', '{ner_log}')" + ';'
            cur.execute(sql2)
            sql3 = "INSERT INTO job_log (file_id, step , log_time, log_message) VALUES "\
                + f"({file_id}, {4}, '{now}', '{relation_log}')" + ';'
            cur.execute(sql3)
            db.commit()
            # return db_json
    except Exception as e:
        print(e)
        
        
        
if __name__=='__main__': 
    class_log = "classificated"
    ner_log = "ner"
    relation_log = "relation"
    
    update_log(11,class_log ,ner_log ,relation_log)