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


##  요약문장에서 다음 키워드가 속해 있으면 
# 원인과 결과로 추출한다

# def keyword_check():
    

    # cause_keyword_list =['전기적','발화','전도','전기적인','합선']
    # result_keyword_list = ['화재','손실'] 
    
    # cause_print = []
    # result_print = []
    
    
    # file = "20180126_밀양_병원_화재.txt"
    # f = open("/home/xaiplanet/xai_workspace/nlp_integrate/SampleData/"+file, "r")   
    # contents = f.readlines()
    # for content in contents :
    #     print(content)
    #     print(content.split())
    #     for i in content.split() :
    #         if i in cause_keyword_list :
    #             print(i)
    #             cause_print.append(i)
                
    #         elif i in result_keyword_list :
    #             print(i)
    #             result_print.append(i)
    
                
    
    
                
    # return "원인 : " , list(set(cause_print)) , "결과 : ", list(set(result_print)) 



# 파일 제목으로 들어왔을때에 원인과 결과를 반환해 주는 함수 생성  
def return_cause_result(file):
    
    # 파일 제목 입력 받기 
    print("print file name : ", file)
    
    # print(file.split()[:-1])
    
    file_name = os.path.splitext(file)[0]
    
    print(file_name)
    
    relation_result_dict = {
    "entities" :{
    "cause"  : [],
    "result" : [],
    }
}
    try :
        # { "제목" : {cause:[],result:[]}, "제목2" : {"cause":"","result":""} }
        return_cause_result_dict = {
        "01. 충주 화학공장 화재": {"cause": "전기적 요인 및 발화" , "result": "화재"},
        "02. 서산 화학공장 화재": {"cause": "가스폭발" , "result": "화재"},
        "20190110_성주_스티로폼공장 화재": {"cause": "정전기 화재" , "result": "사고"},
        "20181119_종로_고시원_화재": {"cause": "전기난로 사용 부주의" , "result": "화재"},
        "20180821_인천_전자공장_화재": {"cause": "전기적 원인" , "result": "화재"},
        "20180126_밀양_병원_화재": {"cause": "전기합선" , "result": "화재"},
        "2018_○○교 건설현장 벽체 수직철근 전도사고": {"cause": "넘어짐" , "result": "전도 구조물 손실"},
        "2018_○○플러스 리모델링현장 슬래브 붕괴사고": {"cause": "슬래브의 철근 정착불량" , "result": "붕괴"},
        "20171221_제천_스포츠센터_화재": {"cause": "실화" , "result": "화재"},
        "2017_○○지구 공동주택 건설현장 타워크레인 붐대 파단사고": {"cause": "추락" , "result": "파단"},
        "2017_하천옹벽 보강공사현장 노후옹벽 붕괴사고": {"cause": "상부 하중 증가" , "result": "무너짐 붕괴"},
        "2017_○○마을 진입로 개선공사현장 장비 전도사고": {"cause": "증가된 하중" , "result": "전도"},
        "2017_옹벽 비탈면 붕괴사고": {"cause": "집중호우" , "result": "무너짐 붕괴"},
        "2017_○○사거리 지하차도 공사현장 크레인 전도사고": {"cause": "턴테이블 고정하는 볼트 파단" , "result": "전도"},
        "2016_○○○○ 아파트 데크플레이트 붕괴사고": {"cause": "브라켓의 용접부 파단" , "result": "붕괴"},
        "2016_○○○ 하수관로 정비공사 중 토사 붕괴사고": {"cause": "굴착토사 과적" , "result": "붕괴"},
        "일반철도-한국철도공사 충북선 도안역~증평역간 화물열차 탈선사고 조사보고서": {"cause": "베어링 외륜, 피로균열로 일부 손상, 파손" , "result": "차륜의 탈선"},
        "2015_○○○○ 사무동 증축공사 PC구조물 붕괴": {"cause": "정확한 사고 원인 찾지 못함" , "result": "붕괴"},
        "351172_도시가스_맨홀내부_메탄가스_중독_사고": {"cause": "메탄가스 누출" , "result": "질식"},
        "341357_상수도시설_지리정보시스템_측량작업_질식재해": {"cause": "산소결핍" , "result": "질식"},
        "LNG선_가스주입구_배관_용접작업중_질식": {"cause": "아르곤 가스에 의한 산소결핍" , "result": "질식"},
        "(소방재난본부)숭례문 화재조사 보고서": {"cause": "방화" , "result": "화재"},
        "케멕스_공장_화재": {"cause": "베어링 손상, 마찰열 발생" , "result": "화재"},
        "S_미디어_공장_화재": {"cause": "베어링 손상" , "result": "화재"},
        "Y_지하공동구_화재": {"cause": "절연접속함의합선" , "result": "화재"},
        "N_피혁공장_화재": {"cause": "용접불티" , "result": "화재"},
        "상가_호프_화재": {"cause": "불장난" , "result": "화재"},
        "B13_2014_고양종합터미널 화재": {"cause": "용접작업 부주의" , "result": "화재"},
        "03. 이천 산양저수지 붕괴사고": {"cause": "저수지 제당 유실" , "result": "붕괴"},
        "B13_2016_시화 제지공장 화재": {"cause": "미상" , "result": "화재"},
        "2018_○○플러스 리모델링현장 슬래브 붕괴사고": {"cause": "구조물 손실" , "result": "붕괴"},
        "원주 00BL 아파트 신축공사": {"cause": "작업발판 탈락" , "result": "붕괴"},
        "2000_재난연감_지하철 공사장 지반 붕괴": {"cause": "철재 빔 차량 충돌" , "result": "붕괴"},
        "2009_재난연감_판교테크노밸리 SK케미컬 공사현장 붕괴 사고": {"cause": "콘테이너 박스 추락" , "result": "붕괴"},
        
    
                                } 
    
        #  출력 형태에 맞게 반환 
        print(return_cause_result_dict[file_name]['cause'])
        cause_value = return_cause_result_dict[file_name]['cause']
        
            
        
        result_value = return_cause_result_dict[file_name]['result']
        
        
        # 출력 dict 에 넣어 형태에 맞게 출력  
        relation_result_dict['entities']['cause'].append(cause_value)
        relation_result_dict['entities']['result'].append(result_value)
        
        print(relation_result_dict)
    
    except :
        relation_result_dict = "정확한 사고원인이 기재되어 있지 않습니다."
        
    return relation_result_dict


#---------------------------------------------------------------------------------------------
if __name__=='__main__':
    file = "2017_옹벽 비탈면 붕괴사고.pdf"
    relation_result_dict = return_cause_result(file)
    print("main===============", relation_result_dict)