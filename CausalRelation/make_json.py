import json      
import re 
from konlpy.tag import Kkma

from konlpy.tag import Okt
okt = Okt()
from ckonlpy.tag import Twitter
twitter = Twitter()

      
# 인과관계 추론을 위해 텍스트 파일을 불러와 Json 형식으로 변환 
total_json = []

# dict_data 안의 tokens의 값으로 토큰 정보 넣기 
# text 데이터 한 줄씩 불러와 끊어 읽기 단위로 자르기 
# try :
    
f = open("/home/xaiplanet/xai_workspace/nlp_integrate/out_puts/2018_○○교 건설현장 벽체 수직철근 전도사고.txt", "r") # out_puts 폴더에 요약된 .txt 파일이 저장 됨 

# 요약된 파일을 불러와 토큰화 시키기 위해서 vocab 생성 및 적용 

contents = f.readlines()


token_data_all = []
dict_data = [{ "vertexSet": [],
        "labels":[],
        "title" :"",
        "sents" : token_data_all }]


order = r'[0-9]'
    
for content in contents :
    # print(len(contents))
    content = re.sub(order,'',content)   # 숫자 제거 
    
    
    content = content.replace("인 명 피해", "인명 피해")
    content = content.replace("발생하 였다", "발생하였다")
    content = content.replace("발생하였 다", "발생하였다")
    content = content.replace("위치 한", "위치한")
    content = content.replace("구 조", "구조")
    content = content.replace("자 체", "자체")         
    content = content.replace("￭", "")         
    content = content.replace("-", "")         
    content = content.replace("(", "")         
    content = content.replace(")", "")         
    content = content.replace(",", "")         
    content = content.replace("  ", " ")  
    content = content.replace("❍", "")  
    content = content.replace(":", "")  
    content = content.replace("☞", "")  
    content = content.replace("발 화", "발화")  
    content = content.replace("자동화재탐지설비", "자동 화재 탐지 설비")  
    content = content.replace("주기적으 로", "주기적으로")  
    content = content.replace("'", "")  
    content = content.replace("실 내에", "실내에")  
    content = content.replace("사 망", "사망")  
    content = content.replace("소방종 합정밀검사", "소방 종합 정밀검사")  
    content = content.replace("‘", "")  
    content = content.replace("’", "")  
    content = content.replace("배출되었 다", "배출되었다")  
    content = content.replace("-", "")  
    content = content.replace("스포 츠센터", "스포츠 센터")          
    content = content.replace("화 재발생","화재 발생")
    content = content.replace("소 방","소방")

    # token_data = okt.morphs(content)     
    token_data = content.split()     
    # print(token_data)
    token_data_all.append(token_data)
    # print(type(token_data))

    
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
    json.dump(dict_data, f, ensure_ascii=False)
print("========================최종===========================")
print(dict_data)

# except : 
#     print("파일 존재하지 않음")
#     print("이 파일의 경우 분석 가능하지 않습니다.")
#     ## SampleData folder 에 존재하지 않는 것이더라도 분석이 가능하도록 수정이 필요함 








###########################################################################################################################

# f = open("/home/xaiplanet/xai_workspace/nlp_integrate/SampleData/"+file, "r")   
    f = open("/home/xaiplanet/xai_workspace/nlp_integrate/out_puts/"+file, "r")   
    
    contents = f.readlines()
    print("==========CONTENTS==========")
    print(contents)

    token_data_all = []
    dict_data = [{ "vertexSet": [],
            "labels":[],
            "title" :"",
            "sents" : token_data_all }]

    order = r'[0-9]'
    
    for content in contents :
        # print(len(contents))
        
        content = re.sub(order,'',content)   # 숫자 제거 
        
        
        content = content.replace("인 명 피해", "인명 피해")
        content = content.replace("발생하 였다", "발생하였다")
        content = content.replace("발생하였 다", "발생하였다")
        content = content.replace("위치 한", "위치한")
        content = content.replace("구 조", "구조")
        content = content.replace("자 체", "자체")         
        content = content.replace("￭", "")         
        content = content.replace("-", "")         
        content = content.replace("(", "")         
        content = content.replace(")", "")         
        content = content.replace(",", "")         
        content = content.replace("  ", " ")  
        content = content.replace("❍", "")  
        content = content.replace(":", "")  
        content = content.replace("☞", "")  
        content = content.replace("발 화", "발화")  
        content = content.replace("자동화재탐지설비", "자동 화재 탐지 설비")  
        content = content.replace("주기적으 로", "주기적으로")  
        content = content.replace("'", "")  
        content = content.replace("실 내에", "실내에")  
        content = content.replace("사 망", "사망")  
        content = content.replace("소방종 합정밀검사", "소방 종합 정밀검사")  
        content = content.replace("‘", "")  
        content = content.replace("’", "")  
        content = content.replace("배출되었 다", "배출되었다")  
        content = content.replace("-", "")  
        content = content.replace("스포 츠센터", "스포츠 센터")  
          
         
               
        
        
        print("=====================")
        
        # print(content)
        # print("========TOKEN_DATA==========")
        # print(content.split())
        # print(content.split()[-1])
        # print(content.split()[-1][-1])
        
        # 문장으로 끝나지 않는 구절 모두 삭제 
        if content.split()[-1][-1] == '다' or content.split()[-1][-1] == '.' or content.split()[-1][-1] == '음' or content.split()[-1][-1] == '정' or content.split()[-1][-1] == '됨': 
            print(content)
            token_data = okt.morphs(content)
            # token_data = content.split() #띄어쓰기 단위로 나누기 
            # token_data = twitter.morphs(content)
            print("토큰 데이터 값 확인하기!!!!!!!!")
            print(token_data)    
            
        # token_data = okt.morphs(content) ## add
                
                        
            token_data_all.append(token_data) ##
        
        
        else :
            continue
        
        
    token_data_all = token_data_all[:-1]

        
    # 파일쓰기
    with open("/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/datasets/docred_joint/TEST.json",'w') as f :
        json.dump(dict_data, f, ensure_ascii=False)
    print(dict_data)

    return
