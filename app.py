"""
# 파일명 : app.py
# 설명   : 
# 개정이력 :
#    버젼    수정일자                   수정자              내용
#    1.0    2022-10-12                              
"""
import random
import signal
import time
import flask
from flask import Flask, render_template, request, redirect, jsonify, Response, send_from_directory, url_for
from flask_cors import CORS
import pymysql
# import run
import sql_func
import sys
# import subprocess
sys.path.append("utils/utils")
from utils import *
import json
import os
import shutil
from datetime import datetime
# import base64
# from infer import inference
from multiprocessing import Process, Pipe, active_children, current_process, parent_process

parent_conn, child_conn = Pipe()  # default is duplex!

# import Linux

now = datetime.now()

app = Flask(__name__, static_url_path='/')
# cors = CORS(app, resources={r"/postUpload/*": {"origins": "*"}})
cors = CORS(app, supports_credentials=True, resources={r"*": {"origins": ['http://3.36.134.175:3200', 'http://localhost:3000']}})
app.debug = True
app.config['JSON_AS_ASCII'] = False
# APP_PATH='/home/xaiplanet/xai_workspace/nlp_integrate'
UPLOAD_FOLDER = "/home/xaiplanet/xai_workspace/nlp_integrate/tmp/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# mysql database와 app.py(server) 연결
db = pymysql.connect(
    host = '211.115.91.45',
    port = 3306,
    user = 'xai_root',
    password = 'xai123$%',
    db = 'mois_safety'
)

"""
# 함수명   : 
# 설명     : 
# return   : 
# 특이사항  : 
"""
# PPT 3
@app.route('/getList')
def get_list():
    print(request.args, "args========================================")
    dtype = request.args['dtype']
    ttype = request.args['ttype']
    startDate = request.args['startDate']
    endDate = request.args['endDate']
    keyword = request.args['keyword']
    offset = request.args['offset']
    limit = request.args['limit']
    print(dtype)
    
    try:
        main_json = sql_func.page_main(dtype, ttype, startDate, endDate, keyword, offset, limit)
        return_status = "ok"
        return {"ret":return_status, "data":main_json}
          
    except Exception as e:
        print(f"errort at /getList:{e}")
        return_status = "error"
        return jsonify({"ret":return_status})
    

@app.route('/getFilter')
def get_filter():
    try:
        filter_json = {
            'dtype': [
                    {'key': 0, 'label': '사업장대규모인적사고'},
                    {'key': 1, 'label': '다중밀집시설대형화재'},
                    {'key': 2, 'label': '철도교통사고'},
                    {'key': 3, 'label': '해양선박사고'},
                    {'key': 4, 'label': '항공기사고'},
                    {'key': 5, 'label': '도로교통사고'},
                    {'key': 6, 'label': '유해화학물질사고'},
                    {'key': 7, 'label': '감염병'},
                    {'key': 8, 'label': '공연장안전사고'},
                    {'key': 9, 'label': '등산레저사고'},
                    {'key': 10, 'label': '물놀이사고'},
                    {'key': 11, 'label': '산불'},
                    {'key': 12, 'label': '다중밀집시설붕괴'}
                    ],
            'ttype': [
                    {'key': 0, 'label': '보고서'},
                    {'key': 1, 'label': '웹뉴스'},
                    {'key': 2, 'label': '시스템'},
                    {'key': 3, 'label': 'NDMS'},
                    {'key': 4, 'label': '기타자료'}
                    ]
        }
        return_status = "ok"
        return {"data": filter_json, "ret": return_status}
    
    except Exception as e:
        print(f"errort at /getFilter:{e}")
        return_status = "error"
        return {"ret":return_status}
    

@app.route('/infoSave', methods=['POST', 'GET'])
def info_save():
    try:
        file_id = request.json['file_id']
        
        input_json = json.loads(request.data.decode())
        title = input_json["title"]
        # mdate = input_json["mdate"]
        data_src = input_json["dsource"]
        ttype = input_json["ttype"]
        idate = input_json["idate"]
        
        input = [title, data_src, ttype, idate]
        
        sql_func.info_save(file_id, input)
        
        return 'ok'

    except Exception as e:
        print(f"errort at /infoSave:{e}")
        return_status = "error"
        return {"ret": return_status}
    

"""
# 함수명   : 
# 설명     : 
# return   : 
# 특이사항  : 
"""
@app.route('/postUpload', methods=['POST', 'GET']) 
def input():

    # UPLOAD_FOLDER = "/home/xaiplanet/xai_workspace/nlp_integrate/tmp/"
    # app = Flask(__name__)
    # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # print('*************', request.files.keys())

    File_1 = request.files['file']
    file_name = File_1.filename

    title = request.form["title"]
    mdate = request.form["mdate"]
    data_src = request.form["dsource"]
    ttype = request.form["ttype"]
    idate = request.form["idate"]
    
    print(request.form)
    print("File_1 ================",file_name)
    print("Data Src ================",data_src)
    print("Date ================",mdate)
    print("File Type ================",ttype)
    
    File_1.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
    # 수집 데이터 정보를 입력하여 등록분석 버튼을 누를경우 수집 데이터 정보에 해당하는 DB에 입력 정보 저장 

    print("Data Src:", data_src)
    
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file_info = [file_name, mdate, file_path, ttype, data_src, title, idate]
    
    file_id = sql_func.init_analyze(file_info)  # DB에서 다음 차례의 인덱스를 file_id로 부여
    print('*********** FILE ID **************', file_id)
            
    ## 자료소스 , 자료형식, 수집일, 자료파일(경로), 분석수행 입력 받는 부분의 DB 테이블에 입력
    shutil.copyfile(file_path, file_path.replace('tmp', 'Sample_Data'))
    shutil.copyfile(file_path, file_path.replace('tmp', 'SampleData'))
                
    # sql_func.analyze(insert_record_list) # db에 저장만 

    sql_func.init_status(file_id)
    send_req(file_name, file_id)
        
    resultJSON = {"file_id":file_id, "status": 0}
    return jsonify({"ret" : "ok", "data":resultJSON})
    
    # try :
    #     result_json = sql_func.upload_file(file_path, result_json)
    #     resultJSON = [{"file_id":file_id, "status":0}]
    #     resultJSON = json.dumps(resultJSON, ensure_ascii=False)
    
    #     return_status = "ok"
    #     return jsonify({"ret": return_status, "data": result_json})

    # except Exception as e :
    #     print(e)
    #     return_status = "error"
    #     return jsonify({"ret":return_status})

    #else: # 요약 , 추출 , 모델추론 
    #    # shutdown_func = request.environ.get('werkzeug.server.shutdown')
    #   # if shutdown_func is None:
    #    #     raise RuntimeError('Not running werkzeug')
    #    # shutdown_func()
    #    print("---------- 모델 추론 시작   ") 
    #    inference_main(file_name,file_id) 
    #   exit(0)
    
    
def inference_main(file_name,file_id):

    f = '/home/xaiplanet/xai_workspace/nlp_integrate/Sample_Data/{}'.format(file_name)
    #모델함수 시작 - 결과 DB 저장 
    print("log----------------------------------------\n",file_name,f,file_id)
    os.system(f"{sys.executable} infer.py '{file_name}' '{f}' {file_id}")

    
"""
# 함수명   : getStatus
# 설명     : 
# return   : 
# 특이사항  : 
"""
@app.route('/getStatus')
def getStatus():
    
    file_id = request.args['file_id']
    status = sql_func.get_record_status(file_id)
    # print("========= FILE_ID :  ", file_id)
    log = sql_func.get_log_msg(file_id)
    if len(log) < 1:
        msg = '==========================\nAnalization Starting...\n=========================='
    else:
        start = '==========================\nAnalization Starting...\n==========================\n'
        # msg = ['\n'.join([str(l[0]), l[1], l[2]]) + '\n==========================' for l in log]
        msg = [l[2] for l in log]
        msg = '\n'.join(msg)
        msg = start + msg
    time.sleep(1)

    return jsonify({"ret" : "ok", "data":{'status': status, 'msg': msg}})


"""
# 함수명   : 
# 설명     : 
# return   : 
# 특이사항  : 
"""
@app.route('/getDIItem')
def getDIItem():
    host_url = flask.request.host_url[:-1]
    file_id = request.args['file_id']

    # 위의 file_id를 이용해서 상세보기 페이지에 필요한 항목들 가져오기
    record_json = sql_func.get_record_getDIItem(file_id)
    file_name = record_json['file_name']
    record_json['file_url'] = host_url + url_for('get_document', file_name = file_name)
    print(file_id)
    resultJSON = record_json

    return {"ret" : "ok", "data": resultJSON}
     



"""
# 함수명   : getWordCloud
# 설명     : 
# return   : 
# 특이사항  : 
"""
# 워드 클라우드 출력 및 워드 클라우드 저장 경로를 DB에 저장
@app.route('/getWordCloud')
def wordcloud():
    file_id = request.args['file_id'] 

    resultJSON = sql_func.get_record_getWordCloud(file_id)
    
    return {"ret" : "ok", "data": resultJSON}


"""
# 함수명   : getDType
# 설명     : 
# return   : 
# 특이사항  : 
"""
@app.route('/getDType')
def classification():
    file_id = request.args['file_id']    
    resultJSON = sql_func.get_record_getDType(file_id)

    ## 버튼- URL 연결 
    ## 추론로직
    
    return jsonify({"ret":"ok","data":resultJSON})  


"""
# 함수명   : getHDamageInfo
# 설명     : 
# return   : 
# 특이사항  : 
"""
@app.route('/getHDamageInfo', methods=["GET","POST"])
def detail():
    file_id = request.args['file_id']
    resultJSON = sql_func.get_record_getHDamageInfo(file_id)
    return jsonify({"ret":"ok","data": {"msg": resultJSON}}) 


"""
# 함수명   : risk_detail
# 설명     : 
# return   : 
# 특이사항  : 
"""
@app.route('/getFusionRisk')
def risk_detail(): # casualties - 개체명인식 피해정보(ex: "사망 4명 부상 3명 , 재산피해 360억": )
    file_id = request.args['file_id']    
    resultJSON = sql_func.get_record_getFusionRisk(file_id)
    print(resultJSON)
    return jsonify({"ret":"ok","data":resultJSON}) 

@app.route('/tmp/<file_name>')
def get_document(file_name):
    return send_from_directory('tmp', file_name)

"""
# 함수명   : 
# 설명     : 
# return   : 
# 특이사항  : 
"""
@app.route('/getRisk')
def risk_detail2():
    # file_id = request.args['file_id']
    resultJSON = sql_func.get_risk_table()
    return jsonify({"ret":"ok","data": resultJSON})


@app.route('/delete/<int:file_id>', methods=['DELETE']) 
def delete(file_id):
    # file_id = request.args['file_id']   
    resultJSON = sql_func.delete_record(file_id)
    print(resultJSON)
    return jsonify({"ret":"ok"})





"""
# 함수명   : 
# 설명     : 
# return   : 
# 특이사항  : 
"""
@app.route('/reAnalyze', methods=['POST', 'GET']) 
def reAnalyze():

    file_id = request.json['file_id']
    sql_func.init_status(file_id)
    file_path = sql_func.get_only_file_path(file_id)

    global file_name
    file_name = os.path.split(file_path)[-1]
    # os.path.split(file_path)[-1]
    sample_file_path = '/home/xaiplanet/xai_workspace/nlp_integrate/SampleData/{}'.format(file_name)
    
    # title = request.form["title"]
    # mdate = request.form["mdate"]
    # data_src = request.form["dsource"]
    # ttype = request.form["ttype"]
    # idate = request.form["idate"]
    
    # file_info = [ttype, data_src, title, idate]
    # file_id = sql_func.re_anaylze(file_id, file_info)

    # 서버에 파일을 sample data 로 복사하기
    shutil.copyfile(file_path,sample_file_path)

    # FILE_ID 에 해당하는 FILE_PATH 들고오기 
    dir_name, file_name = os.path.split(file_path)

    print("==================FILE_NAME=================",file_name)


    # Fork 프로세스 
    # result_json = sql_func.analyze(file_id)
    # print("result_json >>>>>>>>>",result_json)
    
    #### 동일한 file_id로 수행한 후 결과가 덮어씌기 되지않을경우, 결과 모두 Delete 후 돌리도록 로직 필요  
    
    # inference_main(file_name,file_id)
    # Sample_Data 파일 지우기         
            
    # resultJSON = json.dumps(resultJSON, ensure_ascii=False)
    
    send_req(file_name, file_id)
        
    resultJSON = {"file_id":file_id, "status": 0}
    return jsonify({"ret" : "ok", "data":resultJSON})




def end_inference():
    write_msg("END_PROCESS")
def send_req(file_name, file_id):
    msg = []
    msg.append(file_name)
    msg.append(file_id)
    write_msg(msg)
    print(f"Main: send message to child({msg})")
    
def write_msg(msg):
    parent_conn.send(msg)
    
def child_func(conn):
    result = []
    while True:
        msg = conn.recv()
        print(f'{datetime.now()} child received {msg}')
        if msg[0] == "END_PROCESS":
            print(f'Child end......')
            conn.close()
            break
        print(f'{datetime.now()} Start Inference process........')
        inference_main(msg[0], msg[1])
        
child_processes = active_children()

def child_inter(signum, frame):
    for c in child_processes:
        # print(c.parent_process)
        c.terminate()
    raise KeyboardInterrupt
signal.signal(signal.SIGINT, child_inter)
signal.signal(signal.SIGTERM, child_inter)


if __name__ == '__main__':
    # os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
    # os.environ["CUDA_VISIBLE_DEVICES"]="1"
    child_process = Process(target=child_func, args=(child_conn,))
    child_process.start()
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)