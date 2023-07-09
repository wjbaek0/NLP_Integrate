import ast
import random
import re
import sys
from typing import final
import pymysql
from pymysql.constants import CLIENT
import os
import time
from collections import OrderedDict

PATH = r'/home/xaiplanet/new_workspace/nlp_integrate/SampleData'

# print(sys.executable)
class MySQLConnect:
    def __init__(self):
        self.db = pymysql.connect(
            host = '211.115.91.45',
            port = 3306,
            user = 'xai_root',
            password = 'xai123$%',
            db = 'mois_safety',
            # charset='utf8',
            client_flag= CLIENT.MULTI_STATEMENTS,
        )
# class JDBCConnect():
#     def __init__(self):
#         self.JDBC_Driver = os.path.join("/home/xaiplanet/new_workspace", "ojdbc8.jar")
#         self.conn = jp.connect('oracle.jdbc.driver.OracleDriver','jdbc:oracle:thin:dsdp/ds1q2w3e4r@14.63.58.105:1521/ORCL', jars=self.JDBC_Driver)

"""
# 함수명  : upload_db
# 설명    : PATH에 가지고 있는 파일들의 기본 정보를 DB에 업로드
# return  : None / SQL 쿼리만 실행
# 특이사항 : 현재는 API에 사용되지 않음
def upload_db():
    db = MySQLConnect().db
    with os.scandir(PATH) as entries:
        files = [entry for entry in entries if entry.is_file()]
        f_docs = []
        for f in files:
            f_title = os.path.splitext(f.name)[0]
            f_date = time.strftime('%Y-%m-%d', time.gmtime(os.path.getctime(f)))
            f_path = f.path
            f_format = os.path.splitext(f.name)[1][1:].upper()
            f_docs.append((f_title, f_date, f_path, f_format))
            
        try:
            with db.cursor() as cur:
                doc_values = ''
                for f in f_docs:
                    doc_values += f'{f[0], f[1], f[2], f[3]},'
                sql = 'INSERT INTO document (title, date, path) VALUES ' + doc_values[:-1] + ';'
                cur.execute(sql)
                db.commit()
        except Exception as e:
            print(e)
        finally:
            cur.close()
            db.close()
"""


"""
# 함수명  : page_main
# 설명    : DB 항목들을 페이지에 보여주는 기능
# return  : dict
# 특이사항 : 
"""
def page_main(dtype='', ttype='', startDate='', endDate='', keyword='', offset='0', limit='10'):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = 'SELECT file_id, ttype, source, format, dtype, date, idate, file, title FROM document '\
                'WHERE file_id in '\
                '(SELECT file_id FROM job_status WHERE step = 4) '\
                'AND summary IS NOT NULL '\
                ';'
            if dtype != '':
                sql = sql[:-1] + f'AND dtype LIKE "%{dtype}%"' + ';'
            if ttype != '':
                sql = sql[:-1] + f'AND ttype LIKE "%{ttype}%"' + ';'
            if keyword != '':
                sql = sql[:-1] + f'AND (keyword LIKE "%{keyword}%" or title LIKE "%{keyword}%")' + ';'
            if startDate != '':
                sql = sql[:-1] + f'AND idate >= "{startDate}"' + ';'
            if endDate != '':
                sql = sql[:-1] + f'AND idate <= "{endDate}"' + ';'
            cur.execute(sql)
            all_data = cur.fetchall()
            totalCount = len(all_data)
            
            sql = sql[:-1] + f' ORDER BY idate DESC LIMIT {offset}, {limit} ' + ';'
            cur.execute(sql)
            data = cur.fetchall()
            table_json = []
            for d in data:
                d_json = {'file_id': d[0], 'ttype': d[1], 'dsource': d[2], 'ftype': d[3], 'dtype': d[4], 'mdate': d[5], 'idate': d[6]}
                d_json['title'] = d[8] if d[8] != "" else d[7]
                # d_json['mdate'] = d[-2].strftime('%Y-%m-%d') if d[-2] != None else d[2].strftime('%Y-%m-%d')
                table_json.append(d_json)
            # order_json = []
            # for t in table_json:
            #     dict_order = OrderedDict()
            #     for k, v in t.items():
            #         dict_order[k] = v
            #     order_json.append(dict_order)
            #     order_json.reverse()
            # table_json.reverse()
        return {'totalCount': totalCount, 'list': table_json}
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


"""
# 함수명  : init_analyze
# 설명    : 처음 분석 시작 시 파일의 기본 정보들을 DB에 업로드 및 그 ID를 가져와 file_id로 반환
# return  : int (ID(=PK) 반환)
# 특이사항 : 
"""
def init_analyze(result: list):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            file_name_split = os.path.splitext(result[0])
            f_format = file_name_split[1][1:].upper()
            if result[6] == '':
                sql = f"INSERT INTO document (file, date, path, ttype, source, title, format) VALUES ('{file_name_split[0]}', '{result[1]}', '{result[2]}', '{result[3]}', '{result[4]}', '{result[5]}', '{f_format}');"
            else:
                sql = f"INSERT INTO document (file, date, path, ttype, source, title, format, idate) VALUES ('{file_name_split[0]}', '{result[1]}', '{result[2]}', '{result[3]}', '{result[4]}', '{result[5]}', '{f_format}', '{result[6]}');"
            print(sql)
            cur.execute(sql)
            sql = "SELECT @@IDENTITY;"
            cur.execute(sql)
            file_id = cur.fetchone()[0]
            db.commit()
        return file_id
    except Exception as e:
        print("INIT_ANALYZE ERROR")
        print(e)
    finally:
        cur.close()
        db.close()


"""
# 함수명  : re_anaylze
# 설명    : 처음 분석 시작 시 파일의 기본 정보들을 DB에 업로드 및 그 ID를 가져와 file_id로 반환
# return  : int (ID(=PK) 반환)
# 특이사항 : 
"""
def re_anaylze(file_id:int, result: list):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            file_name_split = os.path.splitext(result[0])
            f_format = file_name_split[1][1:].upper()
            if result[3] == '':
                sql = f"UPDATE document SET ttype = '{result[0]}', source = '{result[1]}', title = '{result[2]}', idate = '{result[3]}' WHERE file_id = {file_id};"
            else:
                sql = f"UPDATE document SET ttype = '{result[0]}', source = '{result[1]}', title = '{result[2]}' WHERE file_id = {file_id};"
            print(sql)
            cur.execute(sql)
            db.commit()
        return file_id
    except Exception as e:
        print("RE_ANALYZE ERROR")
        print(e)
    finally:
        cur.close()
        db.close()


"""
# 함수명  : analyze
# 설명    : 분석이 완료된 후 분석 결과들을 한번에 인자로 받아 DB에 업데이트
# return  : None / SQL 쿼리만 실행
# 특이사항 : 
"""
def analyze(file_id: int, result: list):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = f"UPDATE document SET category = '{result[0]}', ner_word = '{result[1]}',\
                    cause = '{result[2]}', bar_json = '{result[3]}', ner_sentence = '{result[4]}',\
                    WHERE file_id = {file_id};"
            cur.execute(sql)
            db.commit()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


"""
# 함수명  : get_record
# 설명    : 테이블, 칼럼, ID를 파라미터로 받아 일치하는 1개 레코드 전부를 {칼럼: 값, 칼럼: 값}의 딕셔너리로 반환
# return  : dict
# 특이사항 : 딕셔너리 내의 Key들은 실제 칼럼명, 현재는 API에 사용되지 않음
"""
# def get_record(table, id_column: str, id: int):
#     db = MySQLConnect().db
#     try:
#         with db.cursor() as cur:
#             cur.execute(f"SELECT COLUMN_NAME FROM information_schema.columns WHERE TABLE_NAME = '{table}';")
#             columns = cur.fetchall()
#             cur.execute(f"SELECT * FROM {table} WHERE {id_column} = {id};")
#             data = cur.fetchone()
#             record_json = {columns[i][0]: data[i] for i in range(len(columns))}
#         return record_json
#     except Exception as e:
#         print(e)
#     finally:
#         cur.close()
#         db.close()


"""
# 함수명  : get_record_status
# 설명    : 
# return  : 
# 특이사항 : 
"""
def get_record_status(file_id: int):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            # print('*******************START STATUS***********************')
            sql = f"SELECT step FROM job_status WHERE file_id = {file_id};"
            cur.execute(sql)
            data = cur.fetchone()
            db.commit()
            step = data[0]
            # print('***** MODEL STEP =', step, '*****')
        return step
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


"""
# 함수명  : get_record_getDIItem
# 설명    : 
# return  : 
# 특이사항 : 
"""
def get_record_getDIItem(file_id: int):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = f"SELECT ttype, source, dtype, keyword, ner_word, cause, risk, fusion_risk, summary, title, date, idate, path FROM document WHERE file_id = {file_id};"
            cur.execute(sql)
            data = cur.fetchone()
            record_json = {
                'ttype': data[0],
                'dsource': data[1],
                'type': data[2],
                'keyword': data[3],
                'casualties': data[4],
                'cause': data[5],
                'risk': data[6],
                'fusion_risk': data[7],
                'text': data[8],
                'file_name': os.path.basename(data[12]),
                'file_url': "http://211.115.91.45:5000/tmp/{}".format(os.path.basename(data[12])),
                'title': data[9],
                'mdate': data[10],
                'idate': data[11]
                }
            # if data[-2] is not None:
            #     record_json['mdate'] = data[-2].strftime('%Y-%m-%d')
            # else:
            #     record_json['mdate'] = data[2].strftime('%Y-%m-%d')
            sql = f"SELECT step FROM job_status WHERE file_id = {file_id};"
            cur.execute(sql)
            status = cur.fetchone()
            if status is not None and status[0] == 4:
                record_json['status'] = status[0]
            else:
                pass  ## 0
        return record_json
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def info_save(file_id, input):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = "UPDATE document "\
                f"SET title = '{input[0]}', source = '{input[1]}', ttype = '{input[2]}', idate = '{input[3]}' "\
                f"WHERE file_id = {file_id};"
            cur.execute(sql)
            db.commit()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def get_record_getDType(file_id: int):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = f"SELECT bar_json FROM document WHERE file_id = {file_id};"
            cur.execute(sql)
            data = cur.fetchone()
            record_json = data[0]
            record_json = ast.literal_eval(record_json)
            for i in range(len(record_json)):
                record_json[i]["text"] = record_json[i].pop("title")
                record_json[i]["value"] = record_json[i].pop(" value")
        return record_json
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def get_record_getHDamageInfo(file_id: int):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            cur.execute(f"SELECT ner_sentence FROM document WHERE file_id = {file_id};")
            data = cur.fetchone()
            record_json = data[0]
            record_json = ast.literal_eval(record_json)
            record_json = [record for record in record_json if 'DTH' in record or 'INJ' in record]
            record_json = '\n'.join(record_json)            
        return record_json
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def get_record_getWordCloud(file_id: int):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = f"SELECT wordcloud FROM document WHERE file_id = {file_id};"
            cur.execute(sql)
            data = cur.fetchone()
            record_json = data[0]
            record_json = ast.literal_eval(record_json)
        return record_json
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def get_record_getRisk(file_id: int):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            cur.execute(f"SELECT * FROM document WHERE file_id = {file_id};")
            data = cur.fetchone()
            record_json = data[7]
        return record_json
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def get_record_getFusionRisk(file_id):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            cur.execute(f"SELECT dtype, z, fusion_risk, grade FROM document WHERE file_id = {file_id};")
            data = cur.fetchone()
            record_json = [{'dtype': data[0], 'human_damage': data[1],
                                'score': data[2], 'risk': data[3]}]
        return record_json
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def get_only_file_path(file_id: int):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            cur.execute(f"SELECT path FROM document WHERE file_id = {file_id};")
            data = cur.fetchone()
            record_json = data[0]
        return record_json
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def get_log_msg(file_id: int):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = f"SELECT step, log_time, log_message FROM job_log WHERE file_id = {file_id};"
            cur.execute(sql)
            data = cur.fetchall()
            record_json = data
        return record_json
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()
        
def get_file_path(file_id: int):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = f"SELECT path FROM document WHERE file_id = {file_id};"
            cur.execute(sql)
            data = cur.fetchone()
            record_json = data[0]
        return record_json
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def delete_record(file_id: int):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = f"DELETE FROM mois_safety.document WHERE file_id = {file_id};"
            cur.execute(sql)
            db.commit()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


def init_status(file_id):
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            del_sql = f"DELETE FROM job_status WHERE file_id = {file_id}"
            cur.execute(del_sql)
            db.commit()
            sql = f"INSERT INTO job_status (file_id, step) VALUES ({file_id}, 0);"
            cur.execute(sql)
            db.commit()
    except Exception as e:
        print(e)
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


def fill_ttype():
    db = MySQLConnect().db
    try:
        with db.cursor() as cur:
            sql = "SELECT file_id, ttype from document"
            cur.execute(sql)
            rs = cur.fetchall()
            for r in rs:
                words = ['PDF', 'TXT', 'HWP', '.txt']
                if r[1] in words:
                    sql = f"UPDATE document SET ttype = '보고서' WHERE file_id = {r[0]}"
                    cur.execute(sql)
                    db.commit()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        db.close()


if __name__ == "__main__":
    # page_main(dtype, ttype, startDate, endDate, keyword, offset, limit=10)
    # test = page_main(dtype = '사업장대규모인적사고')
    result = page_main()

    print()