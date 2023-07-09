"""
# 파일명 : preprocess_common.py
# 설명   : 전처리를 위한 common
# 개정이력 :
#    버젼    수정일자                   수정자              내용
#    1.0    2022-05-03                  김종완            신규 작성
""" 
import pathlib
import os
import datetime


"""
# 함수명   : createFolder
# 설명    : 디렉터리가 없으면 디렉터리를 생성한다.
# return  : None
# 특이사항 :
"""    
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            path = pathlib.Path(directory)
            if len(path.suffix) == 0 :
                os.makedirs(directory)
            else : 
                os.makedirs(os.path.dirname(directory))
            # logger.warning("Directory was created because directory dose not exist %s", os.path.abspath(directory))
            print("Directory was created because directory dose not exist %s", os.path.abspath(directory))
    except OSError:
        return



"""
# Class  : Paths
# 설명   : default path 정의
"""
class Paths :
    LOG_DIR        = os.path.abspath("./log/casual_log.log")
    TSV_SAVE_DIR   = os.path.abspath("./data/result_tsv")
    INTEG_JSON_DIR = os.path.abspath("./data/integrated_json/integrated_relation_{}.json") 
    PROCESSED_DATA_DIR  = os.path.abspath("./data/processed_train_test_test_0620")
    # PROCESSED_DATA_DIR  = os.path.abspath("./data/processed_train_test_test_0620_1")
    METADATA_FILE_NAME  = os.path.join(PROCESSED_DATA_DIR, "metadata.json")
    CHECKPOINT_DIR      = os.path.abspath("./checkpoint")
    RAW_DATA_DIR        = os.path.abspath("./data_kaggle") # in local environment #FIXME
    CAUSAL_DATA_DIR     = os.path.join(RAW_DATA_DIR, "causal_data")               #FIXME
    CONFIG_FILE_DIR     = os.path.abspath("./processor/config/config.yaml")   #config file path
    TRAIN_VAL_TEST_PATH = {
        "train" : os.path.join(PROCESSED_DATA_DIR, "causal_relation_train.json"),
        "val"   : os.path.join(PROCESSED_DATA_DIR, "causal_relation_val.json"),
        "test"  : os.path.join(PROCESSED_DATA_DIR, "causal_relation_test.json"),
    }

    # joint
    JOINT_SAVE_DIR       = "./data/joint_{}"
    JOINT_SAVE_JSON_PATH = {
        "train" : "joint_train.json",
        "test"  : "joint_test.json",
        "val"   : "joint_val.json",
    }
    


"""
# Class  : Params
# 설명   : default param 정의
"""
class Params : 
    CUSTOM_LOG_FILE       = False # log 파일 생성 유무
    REDIFINE_POSITION_VAL = 9     # NIA 표준 json 생성시 조정할 위치값
    


class RegExpObject:
    E1 = r"\<e1\>"
    E2 = r"\<e2\>"
    E1_SLASH     = r"\<\/e1\>"
    E2_SLASH     = r"\<\/e2\>"
    E_OR_SLASH   = r"\<\/e\d\>|\<e\d\>"
    SEARCH_TOKEN = r"\<\/*e\d\>"

        
"""
# Class  : PreprocessJsonData
# 설명   : jsonl 데이터 token 추가 및 tsv형식으로 전처리
"""
class DefineEntitiesName:
    CAUSE  = "사고원인"
    RESULT = "결과"
    CAUSE_TOKEN  = "e1"
    RESULT_TOKEN = "e2"
    
    INIT_DICT    = {
            "type"   : [],
            "cause"  : [],
            "result" : [],
            "text"   : [],
            "joint"  : [],
            "doc_id" : [],
        }

    INTEGRATED_DATA_DICT = {
        "create_date" : "",
        "data"        : [],
        }

    INTEGRATED_DICT = {
        "id"         : "", #데이터별 고유ID 설정 
        "doc_loc"    : "", # 원래 데이터 정보
        "relation"   : "", # 정의한 관계
        "sentence"   : "", # 전체문장
        "subj_start" : "", # subject(entity1)의 단어 시작 위치
        "subj_end"   : "", # subject(entity1)의 단어 끝 위치
        "obj_start"  : "", # object(entity2)의 시작 단어 위치
        "obj_end"    : "", # object(entity2)의 끝 단어 위치
        "subj_word"  : "", # subject(entity1) 전체 단어
        "obj_word"   : "", # object(entity2) 전체 단어
        } 
 
        
    CAUSAL_TOKEN_DICT = {
        "사고원인" : "e1",
        "결과" : "e2",
        }

    CAUSAL_KEY_DICT = {
        "사고원인" : "cause",
        "결과" : "result",
        }

    # INTEGRATED_KEY_DICT = {
    #     "화재" : "scd:fire",
    #     "폭발" : "scd:explosion",
    #     "폭발 및 화재" : "scd:fire/explosion"
    #     }
    # INTEGRATED_KEY_DICT = {
    #     "화재:발화열원"   : "scd:fire_ignition_heat_source",
    #     "화재:최초착화물" : "scd:fire_initial_ignition_objects",
    #     "화재:발화요인"   : "scd:fire_ignition factor",
    #     "화재:발화기기"   : "scd:fire_ignition_objects",
    #     }
    INTEGRATED_KEY_DICT = {
        "화재:물적사고"   : "scd_fire_physical_accident",
        "화재:인적사고"   : "scd_fire_personnel_accident",
        "공사장:물적사고" : "scd_construction_physical_accident",
        "공사장:인적사고" : "scd_construction_personnel_accident",
        }

    INTEGRATED_SUB_OBJ_KEY = {
        "사고원인" : ["subj_word", "subj_start", "subj_end"],
        "결과" : ["obj_word",  "obj_start",  "obj_end" ],
    }



"""
# Class  : 
# 설명   : 
"""
class DefineJointEntities :
    JOINT_INIT_DICT = {
        "vertexSet" : [],
        "labels"    : [],
        "title"     : "",
        "sents"     : [],
    }

    # 이건 리스트로 append 된다.
    VERTEX_DICT = {
        "name" : "",
        "pos"  : [],
        "sent_id" : 0, #int
        "type"    : "",
    }

    LABELS_DICT = {
        "r": "",        # relation
        "h": 0,         # head (int)
        "t": 1,         # tail (int)
        "evidence": [] # sentenc id (list)
    }

    JOINT_CAUSAL_TOKEN_DICT = {
        "e1" : "cause",
        "e2" : "result",
        }

    ENTITY_POSISION_DICT = {
            "e1" : {
                "start" : 0,
                "end"   : 0,
            },
            "e2" : {
                "start" : 0,
                "end"   : 0,
            }
    }

    REGEXP_DICT = {
    "cause"    : r"(\<e\d\>)",
    "result"   : r"(\</e\d\>)",
    "both"     : r"(\<\/*e\d\>)",
    "separate" : r"[\<\/>]"
    }

    DOC_SENTENCE_DICT = {
        "search_sentence" : {
            "text" : "",
            "search_idx" : 0
        },
        "all_sentence"   : [],
    }