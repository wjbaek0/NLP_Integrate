#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

from typing import Any
import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf

from CausalRelation.configs import TrainConfig, TestConfig


#from CausalRelation.configs import TrainConfig, TestConfig
from jerex import model, util
import json
import os
import yaml
from typing import overload
import time
import datetime
import torch
from torch import nn
import pytorch_lightning as pl

from hydra.experimental import compose
from hydra.experimental import initialize

import transformers
from transformers import AdamW, BertConfig, BertTokenizer
from jerex import models, util, datasets
from jerex.data_module import DocREDDataModule
from jerex.model import JEREXModel

from CausalRelation.configs import TestConfig
from jerex import model, util

from apscheduler.schedulers.background import BackgroundScheduler
from konlpy.tag import Okt
okt = Okt()
from ckonlpy.tag import Twitter
twitter = Twitter()
# from konlpy.tag import Kkma  
# kkma=Kkma() 
# from konlpy.tag import Komoran
# komoran=Komoran() 
# from konlpy.tag import Hannanum
# hannanum=Hannanum()  
# from eunjeon import Mecab
# mecab= Mecab()

cs = ConfigStore.instance()
cs.store(name="test_kcbert", node=TestConfig)


twitter.add_dictionary('전기적', 'Noun')
twitter.add_dictionary('전기합선', 'Noun')
twitter.add_dictionary('사고', 'Noun')
twitter.add_dictionary('적극적', 'Noun')
twitter.add_dictionary('내화', 'Noun')
twitter.add_dictionary('위치한', 'Noun')
twitter.add_dictionary('자동', 'Noun')
twitter.add_dictionary('화재', 'Noun')
twitter.add_dictionary('적정성', 'Noun')
twitter.add_dictionary('주기적', 'Noun')
twitter.add_dictionary('기동용', 'Noun')
twitter.add_dictionary('세일', 'Noun')
twitter.add_dictionary('전기적인', 'Noun')
twitter.add_dictionary('형식적', 'Noun')
twitter.add_dictionary('내장재', 'Noun')
twitter.add_dictionary('전자식', 'Noun')
twitter.add_dictionary('착화', 'Noun')
twitter.add_dictionary('리모델링', 'Noun')
twitter.add_dictionary('공사비', 'Noun')
twitter.add_dictionary('설명서', 'Noun')
twitter.add_dictionary('내역서', 'Noun')
twitter.add_dictionary('설계 도서', 'Noun')
twitter.add_dictionary('거치대', 'Noun')
twitter.add_dictionary('클라이밍', 'Noun')
twitter.add_dictionary('케이지', 'Noun')
twitter.add_dictionary('슈거치대', 'Noun')
twitter.add_dictionary('아래로', 'Noun')
twitter.add_dictionary('붐대', 'Noun')
twitter.add_dictionary('회전하는', 'Noun')
twitter.add_dictionary('양중', 'Noun')
twitter.add_dictionary('사업주', 'Noun')
twitter.add_dictionary('구성', 'Noun')
twitter.add_dictionary('준수', 'Noun')




def write_json(file):
   
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
        content = content.replace("전 기적", "전기적")  

        
        # print(content)
        # print("========TOKEN_DATA==========")
        # print(content.split())
        # print(content.split()[-1])
        # print(content.split()[-1][-1])
        
        # 문장으로 끝나지 않는 구절 모두 삭제 
        if content.split()[-1][-1] == '다' or content.split()[-1][-1] == '.' or content.split()[-1][-1] == '음' or content.split()[-1][-1] == '정' or content.split()[-1][-1] == '됨': 
            print(content)
            token_data = okt.morphs(content)
      
            # token_data = twitter.morphs(content)
            print("토큰 데이터 값 확인하기!!!!!!!!")
            print(token_data)    
                                        
            token_data_all.append(token_data) 
        
        
        else :
            continue
        
        
    token_data_all = token_data_all[:-1]

        
    # 파일쓰기
    with open("/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/datasets/docred_joint/TEST.json",'w') as f :
        json.dump(dict_data, f, ensure_ascii=False)
    print(dict_data)

    return



def causal_test() -> Any:
  
    
    initialize(config_path='config/docred_joint')
    cfg = compose(config_name="test_kcbert")

    print(OmegaConf.to_yaml(cfg))

    util.config_to_abs_paths(cfg.dataset, 'test_path')
    util.config_to_abs_paths(cfg.model, 'model_path', 'tokenizer_path', 'encoder_config_path')
    util.config_to_abs_paths(cfg.misc, 'cache_path')

    model.test(cfg)
       
    return 




def json_format():
    try :
        
        json_path = "/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/runs/infer_result/"
        
        with open(f"{json_path}predictions.json", "r", encoding="utf-8") as f :
            read_caual_json = json.load(f) 
            print("===================PREDICTIONS.JSON=============================")
            print(read_caual_json)

        # relation type json
        with open(f"/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/datasets/docred_joint/types.json", "r", encoding="utf-8") as f :
            types_json = json.load(f) # type : dict ==> dict_keys(['entities', 'relations'])
            # print("================TYPES_JSON================")
            # print(types_json)
            
            # dict_keys(['tokens', 'mentions', 'entities', 'relations'])
            # confidence score 높은 걸로 뽑던지 아니면 for loop 태워서
            
            
            print("=================================================")
            relation_text = read_caual_json[0]['relations']
            print(relation_text)
            print(relation_text[0]['type'])

            
            # tokens
            print("===================PRINT_TOKENS==================")
            print(read_caual_json[0]['tokens'])
            tokens = read_caual_json[0]['tokens']
            print(tokens)
            
                  
                
            print("==========read_caual_json==========")
            print(read_caual_json) # tokens, mentions, entities, relations, 
            head_mentions = read_caual_json[0]["entities"]
            print("entities확인하기!!! head_mentions")
            print(head_mentions)
            
            cause_list = []
            result_list = []
            
            for i in range(len(head_mentions)) :
                if head_mentions[i]['type'] == 'cause' :
                    cause_list.append(head_mentions[i]['mentions'])
                elif head_mentions[i]['type'] == 'result' :
                    result_list.append(head_mentions[i]['mentions'])
                else :
                    print("not found entities info")       
            
            print("-----CAUSAL_LIST_INFO-----")
            print(*cause_list)  # mentions의 인덱스 리스트가 담김
            print("-----RESULT_LIST_INFO-----")
            print(*result_list)  # mentions의 인덱스 리스트가 담김 
            
            print("==============HEAD_MENTIONS=================")
            mentions = read_caual_json[0]["mentions"]
            print("==========mentions================")
            print(mentions) # [{'start': 26, 'end': 27}, {'start': 22, 'end': 24}, {'start': 35, 'end': 36}]
            
            
            relation_result_dict = {
                "entities" :{
                    "cause"  : [],
                    "result" : [],
                }
            }


            
            for j in cause_list :
                print(j) #type : list
                for l in j :
                    print(l)
                    cause_mention = mentions[l]
                    a = cause_mention['start']
                    b = cause_mention['end']
                    print(tokens[a:b])
                    relation_result_dict["entities"]["cause"].append(tokens[a:b]) #type list
                                
            for k in result_list :
                print(k)
                
                for m in k :
                    print(m)
                    result_mention = mentions[m]
                    c = result_mention['start']
                    d = result_mention['end']
                    print(tokens[c:d])
                    relation_result_dict["entities"]["result"].append(tokens[c:d]) #type list
                    



            
            
            relation_result_dict["relation"] = relation_text[0]['type']
            print("====================== RELATION=========================")
            print(relation_result_dict["relation"])
            print("=-=======원인, 결과 값 확인-========= ")
            print(relation_result_dict["entities"]["cause"])
            print(relation_result_dict["entities"]["result"])
            
            
            # 만약 원인에 화재가 들어가 있을경우 삭제 
            remove_words = [['화재'],['발화'],['피난']] 
            
            for remove_word in remove_words :
                print("잘 출력되는지 확인 중 ")
                print(remove_word)
                if remove_word in relation_result_dict["entities"]["cause"] :
                    print('원인 값에 화재가 포함됨') 
                    
                    relation_result_dict["entities"]["cause"].remove(remove_word)
                
            
            # 만약 원인에 중복되는 값이 있을 경우 삭제
            print("-------------------------------원인값 확인")
            cause = []
            for value in relation_result_dict["entities"]["cause"] :
                if value not in cause:
                    cause.append(value)
            relation_result_dict["entities"]["cause"] = cause
            print(cause)
            
            
            # 만약 결과에 중복되는 값이 있을 경우 삭제 
            print("-------------------------------결과값 확인")
            result = []
            for value in relation_result_dict["entities"]["result"] :
                if value not in result:
                    result.append(value)
            relation_result_dict["entities"]["result"] = result

            print(result)
            
            
            
    except :
        print("pass")    
        relation_result_dict = "pass"
    return relation_result_dict



def casual_inference(file) :
    try :
        
        print("--------------------------1----------------------------")    
        write_json(file)
        
            
        print("========== TEST.JSON 파일로 인과관계 추론 진행 ==========")
        
        print("--------------------------2----------------------------")    
        
        
        
        # jerex_test 
        cs = ConfigStore.instance()
        cs.store(name="test_kcbert", node=TestConfig)      
        causal_test()
  
        relation_result_dict = json_format() 
        
    except :
        relation_result_dict = "인과 추출 불가1"
    return relation_result_dict


#---------------------------------------------------------------------------------------------
if __name__=='__main__':
    file = "20171221_제천_스포츠센터_화재.txt"    
    # file = "02. 서산 화학공장 화재.txt" # 가스, 폭발 / 화재
    # file = "01. 충주 화학공장 화재.txt"  # 전기적 요인 / 화재, 발화 
    # file = "20171221_제천_스포츠센터_화재.txt"  #  [['연기', '유입'], ['방화', '문'], ['스포츠', '센터'], ['실화']] / 화재 
    relation_result_dict = casual_inference(file)
    print("main===============", relation_result_dict)