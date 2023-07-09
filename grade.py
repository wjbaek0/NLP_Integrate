# 재난 유형별 융합 위험도 공식 구상 

#from infer import analyze
'''
1. NER 인명피해 정보를 통해서 사망과 부상 글자를 통해 숫자 추출

2. 재난 유형별 추가 위험도 Z 값 구상  

3. 융합 위험도 반환 

'''
## [1] 
# 인명피해 부상 명수 : hurt_count 
# 인명피해 사망 명수 : die_count 

#hurt_count = analyze.dth_total
#die_count =  analyze.inj_total 


## [2] - 1
# 사망 0명 이 부상 2등급 
# 감염병, 해양선박, 철도교통, 항공교통, 산불, 다중밀집시설화재, 
# 유해화학물질, 다중밀집시설붕괴, 경기장 및 공연장 안전사고, 등산레저
# case2 = ['infectious', 'marine', 'railroad','aircraft', 'forest', 'fire','chemical','collapse','theater','leisure']

# 사망 1명 이 부상 2등급 
# 도로교통, 사업장 대규모 인적사고, 물놀이 
# case1 = ['road','construction','water']

## 현 들어온 파일의 위험도 등급 파악
# 현재 들어온 사고의  Grade 계산 
def compute_total_risk(die_count,hurt_count,pred,y):
    
    
    disaster_risk_dict = {
        "해양선박사고" : ["marine",2,52,3],
        "철도교통사고" : ["railroad",1,46,2],
        "항공기사고" : ["aircraft",2,42,2],
        "산불" : ["forest",2,84,5],
        "다중밀집시설대형화재" : ["fire",2,65,3],
        "유해화학물질사고" : ["chemical",2,59,3],
        "다중밀집시설붕괴" :["collapse",2,38,1],
        "공연장" : ["theater",2,43,2],
        "등산레저" : ["leisure", 2,70,4],
        "도로교통사고" : ["road",1,51,3],
        "사업장대규모인적사고" : ["construction",1,66,3],
        "물놀이" : ["water",1,50,3]
                       }
    

    
    global case
    
    case = disaster_risk_dict[pred][1] # case 유형 1 또는 2가 반환됨 
    
    
    ## grade 확인 
    if case == 1 :
        grade = count_case1(die_count,hurt_count)
    elif case == 2:
        grade = count_case2(die_count,hurt_count)
    else :
        grade = count_case1(die_count,hurt_count) 
        
    grade = int(grade)
    
    ## Grade 기준으로 현 사고의 추가 위험도 z (-1, 0, 1) 가 결정 
    # 현 사고의 추가 위험도 z 
    
    if grade > disaster_risk_dict[pred][3] :
        z = 1
    elif grade == disaster_risk_dict[pred][3] :
        z = 0
    elif grade < disaster_risk_dict[pred][3] :
        z = -1
    else : 
        z = 0 
    
    
    
    # 융합 위험도 계산 
    # total_risk = "disaster_risk_dict 's value" + "(값 y : 누적 z값)" + "현 사고의 추가 위험도 z" 
    total_risk = disaster_risk_dict[pred][2] + z + y  
    print("--------------------------융합위험도-------------------------")
    
    print(disaster_risk_dict[pred][2])
    print(y)
    print(total_risk)

    ## 융합 위험도  = (x + y + z) mod 100    
    
    return  total_risk, grade, z

#----------------------------------------------------

#-----------------------------------------------------
##  case2 의 경우 
def count_case2(die_count,hurt_count) :
    
    if die_count == 0 :
        if hurt_count == 0 :
            Grade = "1"
            print("1_Grade")
            
        elif hurt_count >= 1 and hurt_count <= 4 :
            Grade = "2"
            print("2_Grade")

        elif hurt_count >= 5 :
            Grade = "3"
            print("3_Grade")

        else :
            Grade = "3"
            print("3_Grade")
            
            

    elif die_count >= 1 and die_count < 10 :
        Grade = "4"
        print("4_Grade")
    elif die_count >=10 :
        Grade = "5"
        print("5_Grade")
    else :
        Grade = "5"
        print("5_Grade")
        
    
    return Grade    
    

    
# case 1 의 경우 
def count_case1(die_count,hurt_count) :
    
    if die_count == 0 :
        if hurt_count == 0 :
            Grade = "1"
            print("1_Grade")

        elif hurt_count >= 1 and hurt_count <= 4 :
            Grade = "2"
            print("2_Grade")
            
        elif hurt_count >= 5 :
            Grade = "3"
            print("3_Grade")
        
        else :
            Grade = "3"
            print("3_Grade")
            
            

    elif die_count == 1 :
        if hurt_count >= 0 and hurt_count <=4 :
            Grade = "2"
            print("2_Grade")
            
        elif hurt_count >=5 :
            Grade = "3"
            print("3_Grade")
            
        else :
            Grade = "3"
            print("3_Grade")
            
        
    elif die_count >= 2 and die_count < 10 :
        Grade = "4"
        print("4_Grade")
        
    elif die_count >= 10 :
        Grade = "5" 
        print("5_Grade")
    else :
        Grade = "5"
        print("5_Grade")
    
    return Grade

#--------------------------------------------------

    



     
