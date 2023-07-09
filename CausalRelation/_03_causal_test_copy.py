#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any
import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf

from CausalRelation.configs import TrainConfig, TestConfig
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


def write_json(file):
   
    f = open("/home/xaiplanet/xai_workspace/nlp_integrate/SampleData/"+file, "r")   
    
    contents = f.readlines()

    token_data_all = []
    dict_data = [{ "vertexSet": [],
            "labels":[],
            "title" :"",
            "sents" : token_data_all }]

    for content in contents :
        print(content)
        print("========TOKEN_DATA==========")
        # print(content.split())
        # print(content.split()[-1])
        # print(content.split()[-1][-1])
        
        # 문장으로 끝나지 않는 구절 모두 삭제 
        # if content.split()[-1][-1] == '다' or content.split()[-1][-1] == '.' : 
            
            # token_data = content.split()
            # token_data = twitter.morphs(content) ## add
        token_data = okt.morphs(content) ## add

                    
        token_data_all.append(token_data)

        
    token_data_all = token_data_all[:-1]
    print(token_data_all)

        
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
        print(json_path)
        
        with open(f"{json_path}predictions.json", "r", encoding="utf-8") as f :
            read_caual_json = json.load(f) 
            print("===================PREDICTIONS.JSON=============================")
            print(read_caual_json)

        # relation type json
        with open(f"/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/datasets/docred_joint/types.json", "r", encoding="utf-8") as f :
            types_json = json.load(f) # type : dict ==> dict_keys(['entities', 'relations'])

            # dict_keys(['tokens', 'mentions', 'entities', 'relations'])
            # confidence score 높은 걸로 뽑던지 아니면 for loop 태워서
                
            print("==========read_caual_json==========")
            print(read_caual_json) # tokens, mentions, entities, relations, 
            head_mentions = read_caual_json[0]["entities"]
            print("entities확인하기!!! head_mentions")
            print(head_mentions)

            print("==============HEAD_MENTIONS=================")
            mentions = read_caual_json[0]["mentions"]
            print("!!!!!!값 확인중 ==========mentions================")
            print(mentions)
            cause_mentions = mentions[0]
            result_mentions = mentions[1]
            result2_mentions = mentions[2] #결과값
            print("=========CAUSAL_MENTION AND RESULT_MENTION=======")
            print(cause_mentions)
            print(result_mentions)
            print(result2_mentions)
             
            


            print("=================================================")
            relation_text = read_caual_json[0]['relations']
            print(relation_text)
            print(relation_text[0]['type'])

            
            # tokens
            print("===================PRINT_TOKENS==================")
            print(read_caual_json[0]['tokens'])
            tokens = read_caual_json[0]['tokens']


            print(cause_mentions['start'])
            a = cause_mentions['start']
            print(cause_mentions['end'])
            b = cause_mentions['end']
            print(tokens[a:b])


            c = result_mentions['start']
            d = result_mentions['end']
            print(tokens[c:d])

            relation_result_dict = {
                "entities" :{
                    "cause"  : [],
                    "result" : [],
                }
            }
            relation_result_dict["entities"]["cause"].append(tokens[a:b]) #type list
            relation_result_dict["entities"]["result"].append(tokens[c:d]) #type list
            relation_result_dict["relation"] = relation_text[0]['type']
            print("====================== RELATION=========================")
            print(relation_result_dict["relation"])
            print("=-=======원인, 결과 값 확인-========= ")
            print(relation_result_dict["entities"]["cause"])
            print(relation_result_dict["entities"]["result"])
            
            
            # 키워드 사전 형성하여 원인과 결과에 리스트 내부의 단어만 나오도록 지정 하기
            # causal_list = [[['발화']]]
            # result_list = [[['전기적','요인']]]
            
            # if relation_result_dict["entities"]["cause"] in causal_list :
            #     print("원인 키워드 존재함")
            # if relation_result_dict["entities"]["result"] in result_list :
            #     print("결과 키워드 존재함")


            
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
        relation_result_dict = "pass"
    return relation_result_dict


#---------------------------------------------------------------------------------------------
if __name__=='__main__':
    file = "01. 충주 화학공장 화재.txt"
    relation_result_dict = casual_inference(file)
    print("main===============", relation_result_dict)