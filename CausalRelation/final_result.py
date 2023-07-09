import os 
import json

def json_format():
    # json_path = "/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/runs/infer_result/"
    json_path = "/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/runs/infer_result/"
    with open(f"{json_path}predictions.json", "r", encoding="utf-8") as f :
        read_caual_json = json.load(f) 
        print("===================PREDICTIONS.JSON=============================")
        # print(read_caual_json) # 전체 PREDICTIONS.JSON 데이터 

    # relation type json
    with open(f"/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/datasets/docred_joint/types.json", "r", encoding="utf-8") as f :
        types_json = json.load(f) # type : dict ==> dict_keys(['entities', 'relations'])
        print("==================TYPES_JSON==================")
        print(types_json)
    # dict_keys(['tokens', 'mentions', 'entities', 'relations'])
    # print("길이!!!!")
    # print(len(read_caual_json))
        
    try : 
            
        print("==========read_caual_json==========")
        head_mentions = read_caual_json[0]["entities"]
        print(head_mentions)

        print("==============HEAD_MENTIONS=================")
        mentions = read_caual_json[0]["mentions"]
        cause_mentions = mentions[1]
        result_mentions = mentions[0]
        print(cause_mentions, result_mentions)


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

        # make dict 
        relation_result_dict = {
            "entities" :{
                "cause"  : [],
                "result" : [],
            },
            "relaltion" : {},
        }
        relation_result_dict["entities"]["cause"].append(tokens[a:b]) #type list
        relation_result_dict["entities"]["result"].append(tokens[c:d]) #type list
        relation_result_dict["relaltion"] = relation_text[0]['type']
    
    except :
        print("명확한 원인과 결과가 명시 되어있지 않음.")
        relation_result_dict = "명확한 원인과 결과가 명시 되어있지 않음."
        
        
    

    # file_path = "/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/runs/infer_result/predictions.json"

    # if os.path.isfile(file_path):
    #     os.remove(file_path)

    
    return relation_result_dict





if __name__=='__main__':
    relation_result_dict = json_format()
    print("======RELATION_RESULT_DICT=========\n", relation_result_dict)
