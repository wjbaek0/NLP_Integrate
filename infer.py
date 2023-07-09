import sys,os,subprocess
import time
sys.path.append("Classification")
from Classification.Classification_model import Classificaion_predict
sys.path.append("NER")
from NER.inference import ner_inference
sys.path.append("CausalRelation")
from CausalRelation._03_causal_test import casual_inference
from CausalRelation._03_causal_keyword import return_cause_result
import pymysql
import run
import argparse
import datetime
import random ## 임시 
sys.path.append("utils")
from utils.utils import *
from grade import compute_total_risk

# mysql database와 app.py(server) 연결
db = pymysql.connect(
    host = '211.115.91.45',
    port = 3306,
    user = 'xai_root',
    password = 'xai123$%',
    db = 'mois_safety'
)
# JDBC_Driver = os.path.join("/datadrive", "ojdbc8.jar")
# args = "-Djava.class.path=%s" % JDBC_Driver
# jvm_path = jpype.getDefaultJVMPath()
# jpype.startJVM(jvm_path, args)
# conn = jp.connect('oracle.jdbc.driver.OracleDriver','jdbc:oracle:thin:dsdp/ds1q2w3e4r@14.63.58.105:1521/ORCL', jars=JDBC_Driver)'

SUM_PATH = '/home/xaiplanet/xai_workspace/nlp_integrate/out_puts/{}.txt'  # out_puts : 요약된 텍스트 파일 저장
FONT_PATH = "/home/xaiplanet/xai_workspace/nlp_integrate/Noto_Sans_KR/NotoSansKR-Medium.otf"


def inference(file_name,sum_txt,file_id):
    file_wo = os.path.splitext(file_name)[0]
    log_message = "Inference Starting..."
    update_status(file_id, 1)
    update_log(file_id, 1, log_message)

    global wordcloud
    wordcloud = keyword(data_path = SUM_PATH.format(file_wo), font_path = FONT_PATH)
    
    global summary 
    with open(SUM_PATH.format(file_wo), 'r') as f:
        summary = f.read()

    global top5_keyword
    top5_keyword = top_keyword(data_path = SUM_PATH.format(file_wo), font_path = FONT_PATH)
    top5_keyword = ','.join(top5_keyword)


    file = os.path.splitext(file_name)[0] + ".txt"
    # 분류모델 & bar_data
    class_log, pred , bardata = Classificaion_predict(file)
    step = 2
    update_status(file_id, step)
    class_log = class_log.replace("'","")
    log_2 = "classification prediction start...."
    update_log(file_id, step, log_2 + class_log)
    
    # 개체명 모델

        
    ner_log, ner_word_list, ner_sentence_list = ner_inference(sum_txt)
        
    step = 3
    update_status(file_id, step)
    ner_log = ner_log.replace("'","")
    log_3 = "\nner extraction start...."
    
    update_log(file_id, step, log_3 + ner_log)
    
    print("=================NER_WORD_LIST====================")
    print(ner_word_list)
    
    
    
    
    # 인과관계 모델------------------------------------------
    
    relation_log ="....."
    
    file = os.path.splitext(file_name)[0] + ".txt"
    print("======================PRINT FILE =====================")
    print(file)
    # relation_result_dict, relation_log = casual_inference(file) 
    
    # relation_result_dict= casual_inference(file) 
    relation_result_dict= return_cause_result(file) 
    # step = 4
    # update_status(file_id, step)
    relation_log = relation_log.replace("'","")
    log_4 = "causal prediction start....\n"
    step = 4

    #-------------------------------------------------------
    # output data  --- >> DB 적재

    result = [ pred, ner_word_list, relation_result_dict, bardata, ner_sentence_list ]
    
    print("============pred============\n", pred, "\n============pred============")
    print("============ner_word_list============\n", ner_word_list, "\n============ner_word_list============")
    print("============relation_result_dict============\n", relation_result_dict, "\n============relation_result_dict============")
    print("============bardata============\n", bardata, "\n============bardata============")
    print("============ner_sentence_list============\n", ner_sentence_list, "\n============ner_sentence_list============")
    print("============result============\n", result, "\n============result============")
    
    
    analyze(file_id,result)
    time.sleep(1.2)
    update_status(file_id, step)
    update_log(file_id, step, log_4 + relation_log + '\ncausal prediction done')

    # update_risk(file_id)


    # update_log(file_id,str(class_log),str(ner_log),str(relation_log))
    return step
    
    

def analyze(file_id: int, result: list):
    # columns = ['category', 'ner_word', 'ner_sentence', 'cause']
    # result = [category, ner_word, cause , bar_json, ner_sentence]
    
    risk_json = get_risk_table()
    dtype = result[0]
    for i in risk_json:
        print(i)
        if i['dtype'] == dtype:
            risk_score = i['risk_score']
    
    if len(result[4]) > 0:
        print("=================result[4]===================")
        print(result[4])
        # cas_pattern = re.compile(r'\d+')
        dth_pattern = re.compile(r'(\<\D+(?P<DTH>\d+\s*\d*\s*\d*\s*\d*)\D+:DTH\>)')
        inj_pattern = re.compile(r'(\<\D+(?P<INJ>\d+\s*\d*\s*\d*\s*\d*)\D+:INJ\>)')
        dth_total = dth_pattern.findall('\n'.join(result[4]))  # 1 파일 당 사망자 수 -> grade.py 로
        inj_total = inj_pattern.findall('\n'.join(result[4]))  # 1 파일 당 부상자 수 -> grade.py 로
        dth_cnt = dth_total[0][1].replace(' ', '') if len(dth_total) > 0 else 0
        inj_cnt = inj_total[0][1].replace(' ', '') if len(inj_total) > 0 else 0
            
        casualties = (int(dth_cnt), int(inj_cnt))
        # casualties = random.randint(1, 95 - risk_score)
    # else:
    #     casualties = (0, 0)
    ## 11.28 - 인명피해도 / 2 적용
    print(dth_total)
    print(inj_total)
    
    y = get_y(result[0])  # INT
    fusion_risk_score, grade, z = compute_total_risk(casualties[0], casualties[1],result[0], y) # 반환되는 total_risk 값 
    #fusion_risk_score = grade.compute_total_risk() # 반환되는 total_risk 값 
    #fusion_risk_score = risk_score + (casualties[0] * 1) + (casualties[1] * 0.2)
    # grade(casualties)
    
    ## 융합위험도 최대 95 
    if fusion_risk_score > 100 :
        fusion_risk_score = 100
    
    if result[4] != []:
        date_pattern = re.compile(r'[^\d](\d{2,4}\ {0,2}\년\ {0,2}\d{1,2}\ {0,2}\월\ {0,2}\d{1,2})[^\d]')
        print(date_pattern.search(' '.join(result[4])))
        idate = date_pattern.search(' '.join(result[4]))
        if idate:
            idate = idate.group(1).replace(' ', '')
            doa_pattern = re.compile(r'[^\d]')
            idate = doa_pattern.sub(r'-', idate)
            print(idate)
        else:
            idate = "NULL"
    else:
        idate = "NULL"

    # fusion_risk_score = 50 + random.randrange(1,10)
    # fusion_risk_score = risk_score + int(result[1])
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = f'UPDATE document '\
                    f'SET dtype = "{result[0]}", '\
                    f'ner_word = "사망: {casualties[0]}명, 부상: {casualties[1]}명", '\
                    f'cause = "{result[2]}", '\
                    f'bar_json = "{result[3]}", '\
                    f'ner_sentence = "{result[4]}", '\
                    f'keyword = "{top5_keyword}",'\
                    f'wordcloud = "{wordcloud}",'\
                    f'summary = "{summary}", '\
                    f'risk = {risk_score}, '\
                    f'fusion_risk = {fusion_risk_score}, '\
                    f'grade = {grade}, '\
                    f'z = {z} '\
                    f'WHERE file_id = {file_id};'
            cur.execute(sql)
            db.commit()
            if idate == "NULL":
                sql = f'UPDATE document SET idate = {idate} WHERE file_id = {file_id};'
            else:
                sql = f'UPDATE document SET idate = "{idate}" WHERE file_id = {file_id};'
            cur.execute(sql)
            db.commit()
            print(">>>>>>>>>>>>>  DB 저장 완료 ")
    except Exception as e:
        print(e)   # 확인완료
    finally:
        cur.close()
        db.close()


def update_status(file_id: int, step: int):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            ## step = {'pre': 0, 'sum': 1, 'class': 2, 'ner': 3, 'cause': 4}
            sql = f"UPDATE job_status SET step = {step} WHERE file_id = {file_id}"  # job_status.doc_id 중복 불가
            cur.execute(sql)
            db.commit()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def update_log(file_id: int, step, log):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            # log_split = log.split('\n')
            # for log_i in log_split:
            if step == 0:
                sql = f"DELETE FROM mois_safety.job_log WHERE file_id = {file_id};"
                cur.execute(sql)
                db.commit()
            now = datetime.datetime.now().replace(microsecond=0)
            sql = "INSERT INTO job_log (file_id, step , log_time, log_message) VALUES "\
                + f"({file_id}, {step}, '{now}', '{log}')" + ';'
            cur.execute(sql)
            db.commit()
            print(file_id, step, ">>>>>>>>>>>>>  로그 저장 완료  ")
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def init_status(file_id):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = f"INSERT INTO job_status (file_id) VALUES (f'{file_id}');"
            cur.execute(sql)
            db.commit()
            print(file_id)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def get_risk_table():
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = "SELECT dtype, risk_score, risk_level FROM risk"
            cur.execute(sql)
            rs = cur.fetchall()
            result_json = [{'dtype': r[0], 'risk_score': r[1], 'risk_level': r[2]} for r in rs]
        print(result_json)
        return result_json
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()
        

def get_y(category):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = f"SELECT SUM(z) FROM mois_safety.document WHERE dtype = '{category}';"
            cur.execute(sql)
            data = cur.fetchone()
            data = data[0]
            if data == None:
                data = 0
            # data = (0) tuple
        print(data)
        return data
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


"""
# 함수명  : parse_args
# 설명    : input parameter 
# return  : args
# 특이사항 : 
"""
class MySQLConnect:
    def __init__(self):
        self.db = pymysql.connect(
            host = '211.115.91.45',
            port = 3306,
            user = 'xai_root',
            password = 'xai123$%',
            db = 'mois_safety',
            # charset='utf8',
        )

def parse_args():
    parser = argparse.ArgumentParser(
        description='Preprocess data input params')
                        
    parser.add_argument("--file_name", required=False, type=str, default=None, help="File Nme")
    parser.add_argument("--file_path", required=False, type=str, default=None, help="File Path")
    parser.add_argument("--file_id",   required=False, type=int, default=None, help="File ID")
    args = parser.parse_args()

    return args


if __name__=='__main__':
    #Test
    file_name = sys.argv[1]
    file_path = sys.argv[2]
    file_id   = sys.argv[3]
    
    print(file_name)
    print(file_path)
    print(file_id)
    
    run.RunMain(file_path).run() # 통합 전처리 모듈
    
    update_log(file_id, 0, 'FILE NAME:  ' + file_name)
    
    # print(sys.executable)

    # test
    # args = parse_args()
    # file_name = args.file_name
    # file_path = args.file_path
    # file_id   = args.file_id
    
    # print("\nfile_name==", file_name ,"\nfile_path==", file_path , "\nfile_id==",file_id  )
    with open(SUM_PATH.format(os.path.splitext(file_name)[0]),'r',encoding='utf-8')as f:
        sum_txt = f.read()
        f.close()
    print("================ TEXT SUMMARIZATION RESULT ================\n", sum_txt)

    inference(file_name,sum_txt,file_id)

    # get_risk_table()
    
    # os.remove(file_path.replace('out_puts', 'Sample_Data'))
    # os.remove(file_path)


