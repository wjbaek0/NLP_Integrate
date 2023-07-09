import json
import pickle
import torch
import sys
import os
from net import KobertBiLSTMCRF

from gluonnlp.data import SentencepieceTokenizer
from data_utils.utils import Config
from data_utils.vocab_tokenizer import Tokenizer
from data_utils.pad_sequence import keras_pad_fn
from pathlib import Path


class DecoderFromNamedEntitySequence():
    def __init__(self, tokenizer, index_to_ner):
        self.tokenizer = tokenizer
        self.index_to_ner = index_to_ner

    def __call__(self, list_of_input_ids, list_of_pred_ids):
        input_token = self.tokenizer.decode_token_ids(list_of_input_ids)[0]
        # print(self.tokenizer.decode_token_ids(list_of_input_ids))
        pred_ner_tag = [self.index_to_ner[pred_id] for pred_id in list_of_pred_ids[0]]

        print("len: {}, input_token:{}".format(len(input_token), input_token))
        print("len: {}, pred_ner_tag:{}".format(len(pred_ner_tag), pred_ner_tag))

        # ----------------------------- parsing list_of_ner_word ----------------------------- #
        list_of_ner_word = []
        entity_word, entity_tag, prev_entity_tag = "", "", ""
        for i, pred_ner_tag_str in enumerate(pred_ner_tag):
            if "LOC" in pred_ner_tag_str:
                if "B-" in pred_ner_tag_str:
                    if prev_entity_tag == pred_ner_tag_str:
                        list_of_ner_word.append({"word": entity_word.replace("▁", " "), "tag": prev_entity_tag[-3:]})
                    entity_word = input_token[i]
                    prev_entity_tag = pred_ner_tag_str
                    entity_tag = prev_entity_tag[-3:]
                elif "I-"+prev_entity_tag[-3:] in pred_ner_tag_str:
                    entity_word += input_token[i]
                else:
                    print(entity_word, prev_entity_tag)
                    if entity_word != "" and prev_entity_tag[-3:] != "":
                        list_of_ner_word.append({"word": entity_word.replace("▁", " "), "tag": prev_entity_tag[-3:]})
                    entity_word, entity_tag, prev_entity_tag = "", "", ""
                        
            else:
                if "B-" in pred_ner_tag_str:
                    entity_tag = pred_ner_tag_str[-3:]

                    if prev_entity_tag != entity_tag and prev_entity_tag != "":
                        list_of_ner_word.append({"word": entity_word.replace("▁", " "), "tag": prev_entity_tag})

                    entity_word = input_token[i]
                    prev_entity_tag = entity_tag
                elif "I-"+entity_tag in pred_ner_tag_str:
                    entity_word += input_token[i]
                else:
                    if entity_word != "" and entity_tag != "":
                        list_of_ner_word.append({"word":entity_word.replace("▁", " "), "tag":entity_tag})
                    entity_word, entity_tag, prev_entity_tag = "", "", ""

        dth_inj_ner_word = ''
        for i in list_of_ner_word:
            if i['tag'] == 'VIC' or i['tag'] == 'DTH' or i['tag'] == 'INJ':
              dth_inj_ner_word += i['word'] + ' '

        # ----------------------------- parsing decoding_ner_sentence ----------------------------- #
        decoding_ner_sentence = ""
        is_prev_entity = False
        prev_entity_tag = ""
        is_there_B_before_I = False

        for token_str, pred_ner_tag_str in zip(input_token, pred_ner_tag):
            token_str = token_str.replace('▁', ' ')  # '▁' 토큰을 띄어쓰기로 교체

            if 'B-' in pred_ner_tag_str:
                if is_prev_entity is True:
                    decoding_ner_sentence += ':' + prev_entity_tag+ '>'

                if token_str[0] == ' ':
                    token_str = list(token_str)
                    token_str[0] = ' <'
                    token_str = ''.join(token_str)
                    decoding_ner_sentence += token_str
                else:
                    decoding_ner_sentence += '<' + token_str
                is_prev_entity = True
                prev_entity_tag = pred_ner_tag_str[-3:] # 첫번째 예측을 기준으로 하겠음
                is_there_B_before_I = True

            elif 'I-' in pred_ner_tag_str:
                decoding_ner_sentence += token_str

                if is_there_B_before_I is True: # I가 나오기전에 B가 있어야하도록 체크
                    is_prev_entity = True
            else:
                if is_prev_entity is True:
                    decoding_ner_sentence += ':' + prev_entity_tag+ '>' + token_str
                    is_prev_entity = False
                    is_there_B_before_I = False
                else:
                    decoding_ner_sentence += token_str
        return dth_inj_ner_word, decoding_ner_sentence[6:-5]

model_config = Config(json_path='/home/xaiplanet/xai_workspace/nlp_integrate/NER/config.json')

# Vocab & Tokenizer
tok_path = '/home/xaiplanet/xai_workspace/nlp_integrate/NER/tokenizer_78b3253a26.model'
ptr_tokenizer = SentencepieceTokenizer(tok_path)

# load vocab & tokenizer
with open("/home/xaiplanet/xai_workspace/nlp_integrate/NER/vocab.pkl", 'rb') as f:
    vocab = pickle.load(f)

tokenizer = Tokenizer(vocab=vocab, split_fn=ptr_tokenizer, pad_fn=keras_pad_fn, maxlen=model_config.maxlen)

# load ner_to_index.json
with open("/home/xaiplanet/xai_workspace/nlp_integrate/NER/ner_to_index.json", 'rb') as f:
    ner_to_index = json.load(f)
    index_to_ner = {v: k for k, v in ner_to_index.items()}

# Model
# KoBERT + bi-lstm + crf
model = KobertBiLSTMCRF(config=model_config, num_classes=len(ner_to_index), time_distribute=False)
model_dict = model.state_dict()
checkpoint = torch.load("/home/xaiplanet/xai_workspace/nlp_integrate/NER/best-epoch-217-step-25600-acc-0.979-loss-664.879.pth", map_location=torch.device('cpu'))

convert_keys = {}
for k, v in checkpoint['model_state_dict'].items():
    new_key_name = k.replace("module.", '')
    if new_key_name not in model_dict: 
        print("{} is not int model_dict".format(new_key_name))
        continue
    convert_keys[new_key_name] = v

model.load_state_dict(convert_keys)
model.eval()



#device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
device = torch.device('cpu')
# n_gpu = torch.cuda.device_count()
# if n_gpu > 1:
#     model = torch.nn.DataParallel(model)
model.to(device)

decoder_from_res = DecoderFromNamedEntitySequence(tokenizer=tokenizer, index_to_ner=index_to_ner)

def ner_inference(sum_txt):
    txt_list = sum_txt.split('\n')
    ner_word_list = []
    ner_sentence_list = []
    log =""
    for txt in txt_list:
        # try:
        list_of_input_ids = tokenizer.list_of_string_to_list_of_cls_sep_token_ids([txt])
        x_input = torch.tensor(list_of_input_ids).long()

        ## for bert bilstm crf & bert bigru crf
        list_of_pred_ids = model(x_input, using_pack_sequence=False)

        dth_inj_ner_word, decoding_ner_sentence = decoder_from_res(list_of_input_ids=list_of_input_ids, list_of_pred_ids=list_of_pred_ids)
        # print("list_of_ner_word:", dth_inj_ner_word)
        # print("decoding_ner_sentence:", decoding_ner_sentence)
        if not dth_inj_ner_word == '':
            ner_word_list.append(dth_inj_ner_word)
            ner_sentence_list.append(decoding_ner_sentence)
        else:
            ner_sentence_list.append(decoding_ner_sentence)

        log += str(dth_inj_ner_word) + "\n"
        log += str(decoding_ner_sentence) + "\n"
        # except Exception as e:
        #     print(e)
        #     pass
        
    return log, ner_word_list, ner_sentence_list




if __name__=='__main__':
    # sum_txt = str(sys.argv[1])
    SUM_PATH = r'/home/xaiplanet/xai_workspace/nlp_integrate/out_puts'
    SUM_FILE = r'아시아나항공 991편 사고조사보고서.txt'
    INPUT_PATH = os.path.join(SUM_PATH, SUM_FILE)
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        sum_txt = f.read() 
    # print(type(sum_txt),sum_txt)
    log, ner_word_list, ner_sentence_list = ner_inference(sum_txt)
    print()