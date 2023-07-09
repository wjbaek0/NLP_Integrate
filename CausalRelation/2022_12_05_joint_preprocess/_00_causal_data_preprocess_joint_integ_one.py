"""
# 파일명 : preprocess_data.py
# 설명   : 레이블링된 데이터 전처리 후 학습위한 tsv 파일 생성
# 개정이력 :
#    버젼    수정일자                   수정자              내용
#    1.0    2022-05-03                  김종완            신규 작성
""" 
import os
import re
import glob
import copy
import json
import datetime
import argparse
import jsonlines
import traceback
import pandas as pd
import numpy as np
from typing import List
from pandas import DataFrame
from tqdm import tqdm  # processbar
from sklearn.model_selection import train_test_split

# common
from common import DefineEntitiesName
from common import Params
from common import Paths
from common import createFolder
# joint 
from common import DefineJointEntities

#logging setting
from common import Logging_config
logging_instance = Logging_config(Params.CUSTOM_LOG_FILE, Paths.LOG_DIR)
logger = logging_instance.logging_setting()



"""
# Class  : PreprocessJsonData
# 설명   : jsonl 데이터 token 추가 및 tsv형식으로 전처리
"""
class PreprocessJsonData(DefineEntitiesName, DefineJointEntities):
    def __init__(self):
        self.process_ele_dict  = self.INIT_DICT                      # common의 초기 빈값의 dictionary
        self.token_key_list    = list(self.CAUSAL_TOKEN_DICT.keys()) # ['원인', '결과']
        return 
    

    """
    # 함수명  : read_jsonl
    # 설명    : jsonl파일을 읽어온다.
    # return  : jsonl_element_list
    # 특이사항 : jsonl 파일 읽어서 리스트 반환
    """
    def read_jsonl(self, jsonl_path):
        jsonl_element_list = []  # jsonl 요소담을 빈 list
        # read jsonl 
        with jsonlines.open(jsonl_path) as f :
            for line in f:        
                jsonl_element_list.append(line)

        logger.info(f" ======== Labeling Text Data Count : {len(jsonl_element_list)}")

        return jsonl_element_list


    """
    # 함수명  : create_str_sentence
    # 설명    : 인과관계 토큰이 있는 문장만 만든다.
    # return  : sentence_str
    # 특이사항 : 정규식 사용
    """
    def create_str_sentence(self, ele_text_list):
        # TODO 문장은 이제 무조건 한문장이 되고 문장 나눔은 개행문자("\n")으로 바꾸는 작업
        # sentence_list = "".join(ele_text_list).split(".")
        # logger.debug("create_str_sentence")
        doc_sentence_dict = copy.deepcopy(self.DOC_SENTENCE_DICT) #MEMO deep copy로 해야 초기화됨!

        sentence_list = "".join(ele_text_list).split("\n")

        regex = re.compile(r"\<\/*e\d\>") # 인과관계 토큰 정규식
        
        for no, sentence in enumerate(sentence_list) :
            if regex.search(sentence) :
                # sentence_str = f'{sentence.strip()}.' # dot 추가
                sentence_str = f'{sentence.strip()}' # dot 추가 X
                # sentence_str = f'{sentence_list}' # dot 추가
                # pass  # 토큰이 있는 문장을 찾았으니 pass
                doc_sentence_dict["search_sentence"]["text"]       = sentence_str
                doc_sentence_dict["search_sentence"]["search_idx"] = no

            # doc_sentence_dict["all_sentence"].append([sentence])
            doc_sentence_dict["all_sentence"].append(sentence.split(" ")) # 아예 split해서 넣는다?

        return sentence_str, doc_sentence_dict


    """
    # 함수명  : __search_entity
    # 설명    : 원인과 결과 entity를 dictionary에 추가
    # return  : None
    # 특이사항 : 
    """
    def __search_entity(self, copy_text_list, entities_list):
        for causal_dict in entities_list : 
            causal_str = "".join(copy_text_list[causal_dict["start_offset"] : causal_dict["end_offset"]]).strip() # 원인 또는 결과 entity 생성
            temp_key   = self.CAUSAL_KEY_DICT[causal_dict['label']] # dictionary 리스트에 넣기 위해 key찾아줌 caus or result
           
            # entity append
            self.process_ele_dict[temp_key].append(causal_str)

        return None


    """
    # 함수명  : __insert_token
    # 설명    : entities 추가 및 토큰 위치 조정하여 추가
    # return  : copy_text_list
    # 특이사항 : 토큰 추가시 위치에 따른 index추가 조정이 된다.
    """
    def __insert_token(self, copy_text_list, entities_list):
        # 원인과 결과 entity string append
        self.__search_entity(copy_text_list, entities_list)

        start_offset_list = [ele['start_offset'] for ele in entities_list] # start_offset list

        # 위치를 조정하여 토큰 추가
        add_index = 0 # 토큰 추가시 밀려나는 index 초기값
        for no, (offset, casual_dict) in enumerate(zip(start_offset_list, entities_list)) : 
            # 첫번째가 아닌데 start_offset이 이전에 것 보다 클때
            if (no > 0) and (offset > start_offset_list[0]) :
                add_index = 2
            
            # 원인 토큰 insert e1 or e2
            copy_text_list.insert(casual_dict['start_offset'] + add_index,     f"<{self.CAUSAL_TOKEN_DICT[casual_dict['label']]}>")
            copy_text_list.insert(casual_dict['end_offset']   + add_index + 1, f"</{self.CAUSAL_TOKEN_DICT[casual_dict['label']]}>")

        return copy_text_list


    """
    # 함수명  : insert_causal_token_df
    # 설명    : 원인과 결과에 토큰을 추가하고 tsv를 만들기 위한 dictionary를 만든다.
    # return  : doc_sentence_dict
    # 특이사항 : DataFrame화 후 해당 entity정보 찾아서 다시 dictionary화
    """
    def insert_causal_token_df(self, jsonl_element_list):
        pbar = tqdm(total=len(jsonl_element_list)) # processbar setting

        for element in jsonl_element_list : 
            ele_text_list = list(element['text'])              # 리스트화해서 한글자마다 인덱싱
            relations_df  = pd.DataFrame(element['relations']) # relations를 dataframe으로 만든다.
            entities_df   = pd.DataFrame(element['entities'])  # entities를 dataframe으로 만든다.
            doc_id        = element["id"]

            # 현재 relation에 대한 원인과 결과의 dict을 만들어주기 위해 반복문
            for _, val in relations_df.iterrows():
                self.process_ele_dict['type'].append(val['type'])  # relation으로 레이블링된 재난 종류 append
                copy_text_list = ele_text_list.copy()              # text를 list화한 것을 copy하여 다시 만들어줌 
               
                # 원인
                cause_dict  = entities_df[entities_df['id'] == val['from_id']].to_dict("records")[0] # Dataframe to dictionay 
                # 결과
                result_dict = entities_df[entities_df['id'] == val['to_id']].to_dict("records")[0]   # Dataframe to dictionay 
                
                entities_list  = [cause_dict, result_dict]                          # 해당 relation에 대한 원인 결과 dicationary 리스트
                copy_text_list = self.__insert_token(copy_text_list, entities_list) # 토큰이 추가된 리스트 만들기

                # 리스트로 만들어 둔 sentence를
                # 인과관계 토큰이 있는 sentence만 하나의 str로 만든다
                sentence_str, doc_sentence_dict = self.create_str_sentence(copy_text_list) #MEMO joint에 대한 dict 추가
                self.process_ele_dict['text'].append(sentence_str)       # "text" list에 추가
                self.process_ele_dict['joint'].append(doc_sentence_dict) #MEMO joint "joint" list에 추가
                self.process_ele_dict['doc_id'].append(doc_id)           #MEMO joint "doc_id" list에 추가

            pbar.update(1) # processbar update

        logger.info(f"======== Total Causal Count : {len(self.process_ele_dict['text'])}")

        return doc_sentence_dict # joint 위한


    """
    # 함수명  : parse_args
    # 설명    : input parameter 
    # return  : args
    # 특이사항 : 
    """
    def parse_args(self):
        parser = argparse.ArgumentParser(
            description='Preprocess data input params')
                            
        parser.add_argument("-p","--data_path", required=False, type=str, default=None, help="Data path")
        parser.add_argument("-s","--save_path", required=False, type=str, default=None, help="result save path")
        args = parser.parse_args()

        return args


    """
    # 함수명  : main
    # 설명    : 데이터를 읽어서 전처리 후에 tsv를 저장한다.
    # return  : None
    # 특이사항 : 
    """
    def main(self):
        try : 
            # argument setting
            args = self.parse_args()

            # data_path = "./data/oka1313@xaiplanet.com.jsonl" # 한개 짜리
            # data_path = "./data/oka1313@xaiplanet.com_원인n.jsonl" # 여러개 짜리
            # save_path = "./data/test19_여러개.tsv"

            # data_path = "./data/2022_11_04/test_position_ll_l.jsonl" # 여러개 짜리
            # save_path = "./data/2022_10_13_new/인과관계분석_1차_건설사고사례집x.tsv"
            # data_path = "./data/2022_10_13_new/인과관계분석_1차_건설사고사례집.jsonl" # 여러개 짜리
            # save_path = "./data/2022_11_04//2022_11_304_test.tsv"

            # # 1118
            data_path = "./data/2022_11_18_데이터통합/인과관계분석_all.jsonl" # 여러개 짜리
            save_path = "./data/2022_11_18_데이터통합/2022_11_18_all_causal.tsv"

            # 1214
            # data_path = "./data/2022_11_18_데이터통합/json_test.jsonl" 
            # save_path = "./data/2022_11_18_데이터통합/2022_12_15_all_causal.tsv"

            # argument가 있을때 없을때를 구분!
            if args.data_path :
                data_path = args.data_path
                logger.info(f"======== Input data_path Argument : {data_path}")
            if args.save_path :
                save_path = args.save_path
                logger.info(f"======== Input save_path Argument : {save_path}")

            logger.info(f"======== Start Preprocessing ========")
            data_lists = self.read_jsonl(data_path) # read jsonl and 리스트화
            doc_sentence_dict = self.insert_causal_token_df(data_lists) # 전처리 하여 tsv 만들기 위한 dictionary 생성 # 이 과정에서 self.process_ele_dict 생성
            
            # 전처리결과 DataFrame화
            processed_df = pd.DataFrame(self.process_ele_dict)
            # tsv 저장
            processed_df[list(self.INIT_DICT)[:-2]].to_csv(save_path, sep="\t", header=None, index=None)

            logger.info(f"======== End Preprocess & Save TSV : {os.path.abspath(save_path)} ========")
            

        except Exception : 
            err = traceback.format_exc(limit=4)
            logger.error(err)


        # return split_data_df_list
        return processed_df


"""
# Class  : PreprocessJsonData
# 설명   : jsonl 데이터 token 추가 및 tsv형식으로 전처리
"""
class JointPreprocess(PreprocessJsonData):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.joint_list = []
        
        return


    """
    # 함수명   : data_train_test_split
    # 설명     :     
    # return   :     
    # 특이사항 : 
    """
    def data_train_test_split(self, joint_list) -> List: 
        logger.info("Processing split train, test, val")
        # train test split
        split_train_list, split_test_list = train_test_split(joint_list,  shuffle=True, random_state=42, test_size=0.2)
        split_test_list, split_val_list   = train_test_split(split_test_list, shuffle=True, random_state=42, test_size=0.5)

        logger.debug(f"train count : {len(split_train_list)}")
        logger.debug(f"test  count : {len(split_test_list)}")
        logger.debug(f"val   count : {len(split_val_list)}")

        return [split_train_list, split_test_list, split_val_list]


    """
    # 함수명   : joint_search_entities_position
    # 설명     : e1 e2가 포함된 split된 text list에서 e1 e2위치를 찾고 지운다.
    # return   : re_make_list, temp_entities_dict
    # 특이사항 : 정규식 사용
    """
    def joint_search_entities_position(self, split_text : List):
        # local variable 선언
        re_make_list = []
        append_index = 0
        temp_entities_dict = copy.deepcopy(self.ENTITY_POSISION_DICT)

        for no, split_ele in enumerate(split_text) : 
            # append 
            # 가정은 e1 과 /e1은 서로 반대로 나오지 않는다.
            # re.split 
            # 둘다 가지고 있을 경우
            if re.search(self.REGEXP_DICT["cause"], split_ele) and re.search(self.REGEXP_DICT["result"], split_ele) :
                split_list = re.split(self.REGEXP_DICT["both"], split_ele) # e.g ['', '<e2>', '붕괴', '</e2>', '됨.']
                # logger.debug(f"both {split_ele}")
                re_make_list.append(split_list[2])
                
                entity_key = re.sub(self.REGEXP_DICT["separate"], "", split_list[1])
                temp_entities_dict[entity_key]["start"] = append_index
                append_index += 1
                
                re_make_list.append(split_list[4])
                entity_key = re.sub(self.REGEXP_DICT["separate"], "", split_list[1])
                temp_entities_dict[entity_key]["end"] = append_index
                append_index += 1
                
            # 앞에 것만
            elif re.search(self.REGEXP_DICT["cause"], split_ele) :
                # logger.debug(f"only cause : {split_ele}")
                split_list = re.split(self.REGEXP_DICT["cause"], split_ele) # e.g ['', '<e1>', '메인지브']
                re_make_list.append(split_list[2]) # text list에 append
                
                # e1 start index defind
                entity_key = re.sub(self.REGEXP_DICT["separate"],"",split_list[1]) # <, >, / 잘라냄
                temp_entities_dict[entity_key]["start"] = append_index
                append_index += 1
            
            # 뒤에 것만
            elif re.search(self.REGEXP_DICT["result"], split_ele) :
                # logger.debug(f"only result : {split_ele}")
                split_list = re.split(self.REGEXP_DICT["result"],split_ele) 
                
                # for search_ele in split_list :
                #     if not re.search(self.REGEXP_DICT["result"], search_ele) :
                #         if not search_ele == '' :  # 분리하면 ['제거', '</e1>', ''] 식으로 나오는 경우가 있는데 ''는 넣지 않는다.
                #             re_make_list.append(search_ele)
                        
                #             entity_key = re.sub(self.REGEXP_DICT["separate"], "", split_list[1]) # <, >, / 잘라냄
                #             temp_entities_dict[entity_key]["end"] = append_index
                #             append_index += 1
                
                split_list = list(filter(None, split_list)) # filter로 "" <--- 요거 없애버림
                for search_ele in split_list :
                    if not re.search(self.REGEXP_DICT["result"], search_ele) :
                        re_make_list.append(search_ele)

                        # '</e1>건물' <<-- 이런식으로 된 경우
                        # ['</e1>', '건물'] 이런식으로 split됨
                        # 그래서 위와 같이 split_list[1]로 했을시 key error 발생
                        # 그래서 리스트 안에 /e1 or e2 if로 꺼낸다.
                        sp_entity = [i for i in split_list if re.search(self.REGEXP_DICT["result"], i)][0]
                        entity_key = re.sub(self.REGEXP_DICT["separate"], "", sp_entity) # <, >, / 잘라냄
                        # entity_key = re.sub(self.REGEXP_DICT["separate"], "", split_list[1]) # <, >, / 잘라냄

                        temp_entities_dict[entity_key]["end"] = append_index
                        append_index += 1

                        # '전도</e1>되어' 일때 ['전도', '</e1>', '되어']로 분리 되고 뒤에 되어는 추가 되면서 end position이 하나더 추가 되서
                        # 들어가기 때문에 전도 까지 포함해서 인덱싱할수 있다.
                
                if re.search(self.REGEXP_DICT["result"], split_list[-1]) :
                    temp_entities_dict[entity_key]["end"] = append_index

                # 그러면 여기서 . 이 있으면 합쳐야 하나??

            # entitiy가 아닌 것들
            else :
                re_make_list.append(split_ele)
                append_index += 1

        return re_make_list, temp_entities_dict


    """
    # 함수명   : joint_create_element
    # 설명     :     
    # return   :     
    # 특이사항 : 
    """
    def joint_create_element(self, df_val):
        # logger.debug("joint_create_element")

        joint_process_dict = copy.deepcopy(self.JOINT_INIT_DICT)
        
        all_sentence_list  = df_val["joint"]["all_sentence"]

        no = 0 # 원인과 결과의 vertexSet의 위치를 표기해주는데 지금은 두개 밖에 없으니 no=0으로 상수화

        split_text = df_val["text"].split(" ")
        re_make_list, entities_dict = self.joint_search_entities_position(split_text) # re_make_list : split text list, # entities_dict : e1 e2의 위치
         
         # e1, e2 있는 리스트 교체
        sent_id = df_val["joint"]["search_sentence"]["search_idx"]
        all_sentence_list[sent_id] = re_make_list

        # 원인과 결과 vertext dict create & append
        joint_process_dict["vertexSet"].append([self._joint_create_vertex_dict(df_val, "cause", entities_dict, sent_id)])
        joint_process_dict["vertexSet"].append([self._joint_create_vertex_dict(df_val, "result", entities_dict, sent_id)])

        joint_process_dict["labels"].append(self._joint_create_labels_dict(df_val, no, sent_id))

        joint_process_dict["sents"] = all_sentence_list # sentence는 한개만 들어간다.
        joint_process_dict["title"] = " ".join(all_sentence_list[0]) # 문서의 첫번째 문장화 해서 제목으로 지정

        return joint_process_dict


    """
    # 함수명   : _joint_create_vertex_dict
    # 설명     :     
    # return   :     
    # 특이사항 : 
    """
    def _joint_create_vertex_dict(self, df_values, col_property, entities_dict, sent_id):
        joint_vertex_dict  = copy.deepcopy(self.VERTEX_DICT)
        e1_e2_token        = {v:k for k,v in self.JOINT_CAUSAL_TOKEN_DICT.items()}[col_property]

        joint_vertex_dict["name"]    = df_values[col_property] # e1 or e2 요소 (e.g 메인지브 등이 전도)
        joint_vertex_dict["type"]    = col_property            # entity type
        joint_vertex_dict["pos"]     = list(entities_dict[e1_e2_token].values())
        joint_vertex_dict["sent_id"] = sent_id

        return joint_vertex_dict


    """
    # 함수명   : 
    # 설명     :     
    # return   :     
    # 특이사항 : 
    """
    def _joint_create_labels_dict(self, df_values, no, sent_id):
        joint_lables_dict  = copy.deepcopy(self.LABELS_DICT)

        joint_lables_dict["r"] = self.INTEGRATED_KEY_DICT[df_values["type"]]
        joint_lables_dict["h"] = no   # cause의 위치
        joint_lables_dict["t"] = no+1 # tail은 result의 위치이기 때문에 1을 더해준다.
        joint_lables_dict["evidence"].append(sent_id)

        return joint_lables_dict


    #MEMO joint 전처리
    """
    # 함수명   : joint_vertex_create
    # 설명     : joint 전처리
    # return   : joint_list
    # 특이사항 : 
    """
    def joint_vertex_create(self, processed_df : DataFrame):
        logger.debug("joint_vertex_create")
        # 문장하나당 하는 version
        for _, df_val in processed_df.iterrows():
            joint_process_dict = self.joint_create_element(df_val)
            self.joint_list.append(joint_process_dict)

        return self.joint_list


    """
    # 함수명   : joint_main
    # 설명     :     
    # return   :     
    # 특이사항 : 
    """
    def joint_all_list_save(self, joint_list):
        temp_df = pd.DataFrame(joint_list)
        temp_df.to_csv("./data/2022_12_14_데이터통합/joint_all_통합_one.csv", encoding="utf-8", index=False)
        logger.debug("joint csv save")

        return



    """
    # 함수명   : joint_main
    # 설명     :     
    # return   :     
    # 특이사항 : 
    """
    def joint_main(self) :
        preprocessing = PreprocessJsonData()
        processed_df  = preprocessing.main() 
        joint_list    = self.joint_vertex_create(processed_df)

        self.joint_all_list_save(joint_list)

        split_joint_list = self.data_train_test_split(joint_list) # [split_train_list, split_test_list, split_val_list]
        
        save_time = datetime.datetime.now().strftime("%Y%m%d_%H_%M")
        # save_time = datetime.datetime.now().strftime("%Y%m%d")

        # json 저장
        for data_kind, sp_list in zip(Paths.JOINT_SAVE_JSON_PATH, split_joint_list) : # train, test, val 순이다.
            joint_save_dir = Paths.JOINT_SAVE_DIR.format(save_time)
            createFolder(joint_save_dir)
            save_joint_path = os.path.join(joint_save_dir, Paths.JOINT_SAVE_JSON_PATH[data_kind])
            with open(save_joint_path, 'w', encoding="utf-8") as f :
                json.dump(sp_list, f, ensure_ascii=False)

            logger.debug(f"save json {save_joint_path}")

        return None

    



if __name__ == "__main__" : 
    preprocessing = PreprocessJsonData()
    preprocessing.main()
    # preprocessing = JointPreprocess()
    # preprocessing.joint_main()
    
