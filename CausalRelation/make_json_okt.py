import json      
from konlpy.tag import Okt

okt = Okt()

# 인과관계 추론을 위해 텍스트 파일을 불러와 Json 형식으로 변환 
total_json = []

# dict_data 안의 tokens의 값으로 토큰 정보 넣기 
# text 데이터 한 줄씩 불러와 끊어 읽기 단위로 자르기 
# try :
    
f = open("/home/xaiplanet/xai_workspace/nlp_integrate/out_puts/01. 충주 화학공장 화재.txt", "r") # out_puts 폴더에 요약된 .txt 파일이 저장 됨 

# 요약된 파일을 불러와 토큰화 시키기 위해서 vocab 생성 및 적용 

contents = f.readlines()
# print("-------------------요약 된 텍스트 파일 그대로 출력 ---------------------")
print(contents)

# kkma = Kkma()
# print(kkma.nouns(str(contents)))




token_data_all = []
dict_data = [{ "vertexSet": [],
        "labels":[],
        "title" :"",
        "sents" : token_data_all }]

for content in contents :
    # print("==================")
    # print(content)

    token_data = okt.morphs(content)
    
    # token_data = content.split()
    token_data_all.append(token_data)

    
    # json 형식으로 변환하기 
    # json_data = json.dumps(dict_data, ensure_ascii=False)
    # token_data_all.append(token_data)
    # token_data_all.append(',')
    # total_json.append(dict_data)
token_data_all = token_data_all[:-1]
# print(token_data_all)


#---------
# contents = f.readlines()
# # print(contents)
# token_data_total_all = []

# for content in contents :
#     # print("----")
#     # print(content)
    
#     token_data = content.split()
#     # print(token_data)

    
#     token_data_all = []
#     dict_data = { "vertexSet": [],
#             "labels":[],
#             "title" :"",
#             "sents" : token_data }

#     # print("=================DICT_DATA===============")
    

#     token_data_total_all.append(dict_data)   
# # token_data_all = token_data_all[:-1]
# print(token_data_total_all)


    
# 파일쓰기
with open("/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/datasets/docred_joint/TEST.json",'w') as f :
    json.dump(token_data_all, f, ensure_ascii=False)
# print("========================최종===========================")
# print(dict_data)

# except : 
#     print("파일 존재하지 않음")
#     print("이 파일의 경우 분석 가능하지 않습니다.")
#     ## SampleData folder 에 존재하지 않는 것이더라도 분석이 가능하도록 수정이 필요함 

