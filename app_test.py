from flask import Flask, render_template, request, redirect, jsonify, Response
import pymysql
import run
import sql_func
import sys
sys.path.append("utils/utils")
from utils import *
import json
import os
import shutil
from datetime import datetime
import base64

now = datetime.now()

app = Flask(__name__)
app.debug = True
app.config['JSON_AS_ASCII'] = False

# mysql database와 app.py(server) 연결
db = pymysql.connect(
    host = '127.0.0.1',
    port = 3306,
    user = 'xai_root',
    password = 'xai123$%',
    db = 'mois_safety'
)


# p10 해당 페이지 정보 가져오기 - PPT3 내용
# @app.route('/getDIList')
# def getDIList():
#     # pagesize = request.args.get('10', default = 10, type = int)
#     # page = request.args.get('1', default = '*', type = int)

#     # http://127.0.0.1:5000/getDIList?pagesize=10&page=3
#     ## return 값에 각각 해당페이지의 내용 보여주기 
#     return jsonify({"file_id":12345, "수정일":now.date(), "유형":"실시간", "자료소스":"NDMS", "파일형식":"txt", "재난유형":"가스사고", "제목":"프로판가스"})


# PPT 3
@app.route('/getDIList')
def get_list():
    
    # cursor = db.cursor()
    # sql = '''SELECT * FROM document;'''
    # cursor.execute(sql)
    # row = cursor.fetchall()
    # data_list = []  
    
    # for d in row :
    #     data_dic = {
    #         'id' : d[0],  
    #         'name' : d[1], run
    #         'path' : d[2] 
    #     }
    #     data_list.append(data_dic)
    # resultJSON = json.dumps(data_list) 
    # db.close()
    # return Response(resultJSON, status=200)
    
    
    try:
        main_json = sql_func.page_main()
        return_status = "ok"
        return jsonify({"ret":return_status, "data":main_json})
      
        
    except Exception as e:
        print(e)
        return_status = "error"
        return jsonify({"ret":return_status})



# 등록 분석 - PPT4내용  
# p10 등록 버튼을 누른후, p11 수집데이터 정보 입력 받아 등록 분석수행 버튼을 눌러 수행할 경우 
@app.route('/monitoring/input')
def input():
    ## 수집 데이터 정보를 입력하여 등록분석 버튼을 누를경우 수집 데이터 정보에 해당하는 DB에 입력 정보 저장 
    # global doc_id
    # file_id = request.args.get("10", default = 10, type = int)
    with db.cursor() as cur:
        cur.execute("SELECT id FROM document;")
        ids = [id[0] for id in cur.fetchall()]
        file_id = max(ids) + 1
        cur.close()
        db.commit()

    resultJSON = [{"file_id":file_id, "status":"Starting"}]
    # resultJSON = json.dumps(resultJSON, ensure_ascii=False)
    
    ## 파일을 서버로 업로드하는 수행 필요
    
    return_status = "ok"
    
    return jsonify({"ret": return_status, "data": resultJSON})
    ## 자료소스 , 자료형식, 수집일, 자료파일(경로), 분석수행 입력 받는 부분의 DB 테이블도 필요할 것 같음.


@app.route('/getStatus')
def getStatus():
    
    # http://127.0.0.1:5000/getStatus?file_id=10
    
    file_id = request.args.get("file_id", default = 10, type = int)
    ## file_id 에 해당하는 DB정보 가져온 후, 
    resultJSON = [{"status":12, "message":"log infomation~"}]
    # resultJSON = json.dumps(resultJSON, ensure_ascii=False)
    return jsonify({"ret" : "ok", "data":resultJSON})



# 분석 수행 
# doc_id 를 전달하여 분석할 보고서 파일을 선택하는 경우 
@app.route('/monitoring/predict/<int:file_id>', methods=["GET","POST"])
def predict(file_id):
    record_json = sql_func.get_record('document', 'id', file_id)
    # 파일 받기   
    file_path = "Sample_Data/test.pdf" ## file_path
    with open(file_path, 'r') as input_file:
        coded_string = input_file.read()
        decoded = base64.b64decode(coded_string)
    with open('out_puts/test.txt', 'w', encoding="utf-8") as output_file: ## file_path 
        output_file.write(decoded.decode("utf-8"))
    
    
    # 서버에 파일을 sample data 로 복사하기
    try:
        with db.cursor() as cur:
            cur.execute(f'SELECT * FROM document WHERE id = {doc_id};')
            data = cur.fetchone()
            db_json = {'id': data[0], 'title': data[1], 'date': data[2].strftime('%Y-%m-%d'), 'path': r'{0}'.format(data[3])}
            cur.execute(sql)
            cur.close()
            db.commit()
            # return db_json
    except Exception as e:
        print(e)
        
        
    shutil.copyfile(db_json['path'], db_json['path'].replace('SampleData', 'Sample_Data'))
    global run
    run = run.RunMain()
    run.run()
    from_data = request.args.get('from')
    to_data = request.args.get('to')
    print("Success")
    f = open(db_json['path'].replace('SampleData', 'out_puts'), 'r', encoding='utf-8')
    summary = f.read()
    print(summary) # 요약 텍스트 
    
    try:
        with db.cursor() as cur:
            # 요약 모델 실행
            # 분류 모델 실행
            category = 'category'
            sql = f"UPDATE document\
                    SET category = '{category}', summary = '{summary}'\
                    WHERE id = {doc_id};"
            cur.execute(sql)
            cur.close()
            db.commit()
    except Exception as e:
        print(e)
            
    os.remove(db_json['path'].replace('SampleData', 'Sample_Data'))
            
            
    ## 키워드 추출 + 추론로직  + 재난위험도 공식 + 융합위험도 공식 + 로깅 + 스텝 
    global casualties
    casualties = "사망 4명 부상 3명 , 재산피해 360억"
    
    global risk
    risk = "88"
    
    resultJSON = [{"file_id":12345, "status":"Start"}]
    resultJSON = json.dumps(resultJSON, ensure_ascii=False)
    
    ## 빈공간 채우기용 

    return jsonify({"ret" : "ok", "data":resultJSON})


@app.route('/getDIItem')
def getDIItem():
    
    file_id = request.args.get("10", default = 10, type = int)
    
    resultJSON = [{"source":"text_source", "format":"PDF", "재난유형":"재난유형", "키워드":"화재", "사고내용":"content"}]
    # "file_id":12345, "수정일":now.date(), "유형":"실시간", "자료소스":"NDMS", "파일형식":"txt", "재난유형":"가스사고", "제목":"프로판가스"
    resultJSON = json.dumps(resultJSON, ensure_ascii=False)
    
    return jsonify({"ret" : "ok", "data":resultJSON})



# 워드 클라우드 출력 및 워드 클라우드 저장 경로를 DB에 저장
@app.route('/getWordCloud')
def wordcloud():
    ## DB에 경로 저장
    file_id = request.args.get("10", default = 10, type = int)
    
    resultJSON = [{'text': "told", 'value':64},{'text':'mistake','value':11},{'text':'tought', 'value': 3}]
    resultJSON = json.dumps(resultJSON, ensure_ascii=False)
    
    return jsonify({"ret" : "ok", "data": resultJSON})


# 세부보기 버튼(분류-재난유형)
@app.route('/getDType')
def classification():
    file_id = request.args.get("10", default = 10, type = int)
    ## 버튼- URL 연결 
    ## 추론로직
    resultJSON = [{"bardata":" 4명 사망.. ~~ 재산피해"}]
    resultJSON = json.dumps(resultJSON, ensure_ascii=False)
    return jsonify({"ret":"ok","data":resultJSON})  


# p8
# 세부보기 버튼 (인명피해정보-개체명 인식)
@app.route('/getHDamageIngo', methods=["GET","POST"])
def detail():
    file_id = request.args.get("10", default = 10, type = int)
    ## 버튼- URL 연결 readlines
    ## 추론로직
    resultJSON = [{"msg":" 4명 사망.. ~~ 재산피해"}]
    resultJSON = json.dumps(resultJSON, ensure_ascii=False)
    return jsonify({"ret":"ok","data":resultJSON}) 


# 세부보기 버튼(재난위험도)
@app.route('/getFusionRisk')
def risk_detail(casualties): # casualties - 개체명인식 피해정보(ex: "사망 4명 부상 3명 , 재산피해 360억": )
    file_id = request.args.get("10", default = 10, type = int)
    ## 버튼- URL 연결 
    ## 추론로직
    return jsonify({"(risk/10)+재난취약성^2+사회취약성^2"}) 


global person_risk
person_risk = 2

# 세부보기 버튼(융합위험도)
@app.route('/getRisk')
def risk_detail2(person_risk):
    file_id = request.args.get("10", default = 10, type = int)
    ## 버튼- URL 연결                                                                                                                                                                           
    ## 추론로직
    return jsonify({"person_risk+alpha or person_risk-alpha"}) 


# 저장 버튼 
@app.route('/monitoring/save')
def save():
    ## 저장 버튼을 누르면 - DB에 수집일, 유형, 자료소스, 파일형식, 재난유형, 제목 이 들어간 테이블에 정보 저장 되어 p10에 업데이트 
    print("saved successfully")
    return 


# 목록 돌아가기 버튼, 등록 버튼은 routing 필요없을 것같음..

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)