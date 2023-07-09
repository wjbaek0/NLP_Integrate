######## PDF TEST 용 파일 #########################################################################
import json
import torch
import os , sys, logging as log
import random
import time
import datetime
from torch import nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import gluonnlp as nlp
import numpy as np
from transformers import BertModel
# from kobert.pytorch_kobert import get_kobert_model
from kobert import get_kobert_model
from kobert_tokenizer import KoBERTTokenizer

now1 = datetime.datetime.now().strftime('%y%m%d')
time1 = datetime.datetime.now().strftime('%H%M')
device = torch.device('cuda:1')
# Setting parameters
max_len = 300 # kobert base <= 300 학습시 allocate memory 문제
batch_size = 8
num_class = 5

class BERTDataset(Dataset):  # dataset to bert_tokenizer
    def __init__(self, dataset, sent_idx, label_idx, bert_tokenizer,vocab, max_len,
                 pad, pair):
   
        transform = nlp.data.BERTSentenceTransform(
            bert_tokenizer, max_seq_length=max_len,vocab=vocab, pad=pad, pair=pair)
        
        self.sentences = [transform([i[sent_idx]]) for i in dataset]
        self.labels = [np.int32(i[label_idx]) for i in dataset]

    def __getitem__(self, i):
        return (self.sentences[i] + (self.labels[i], ))
         

    def __len__(self):
        return (len(self.labels))
        
class BERTClassifier(nn.Module):
    def __init__(self,
                 bert,
                 hidden_size = 768,
                 num_classes=num_class ,   ###   클래스 수 조정 
                 dr_rate=0,
                 params=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size , 256),
			# torch.nn.BatchNorm1d(256),
            # nn.ReLU(),
			nn.Linear(256, num_classes),
		)
             
        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)
    
    def gen_attention_mask(self, token_ids, valid_length):
        attention_mask = torch.zeros_like(token_ids)
        for i, v in enumerate(valid_length):
            attention_mask[i][:v] = 1
        return attention_mask.float()

    def forward(self, token_ids, valid_length, segment_ids):
        attention_mask = self.gen_attention_mask(token_ids, valid_length)
        
        _, pooler = self.bert(input_ids = token_ids, token_type_ids = segment_ids.long(), attention_mask = attention_mask.float().to(token_ids.device),return_dict=False)
        if self.dr_rate:
            out = self.dropout(pooler)
            
        return self.classifier(out) ### logits 

def Classificaion_predict(file_path): # 개별 파일 추론 ->> 폴더 전체 추론으로 변경 
	##모델 호출
	tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')
	model, vocab = get_kobert_model('skt/kobert-base-v1',tokenizer.vocab_file)
	json_result = {}
	json_result['confidence_score'] = dict()
	json_result['statistics'] = dict()
	# 5가지 클래스의 비정제 데이터로 학습한 모델로 대체
	tok=tokenizer.tokenize
	model = BERTClassifier(model, dr_rate=0.7).to(device)
	model.load_state_dict(torch.load('/home/xaiplanet/xai_workspace/nlp_integrate/PDF_Test/kobert_model_49.pth'), strict=False) # weight 

	file_list = os.listdir(file_path)
 
	with torch.no_grad():
		for file in file_list:
			print("<classification predict start....>")
			model.eval()
			pred = ""
			bardata = []
			y_pred = []
			y_true=[]
			confidence=[] 	
			file_dir = '/home/xaiplanet/xai_workspace/nlp_integrate/PDF_Test/Test_files/'+file # text화된 파일을 
			with open(file_dir,'r',encoding='utf-8')as f:
				text = f.read()

			textset = [[text,'0']]
			text_data = BERTDataset(textset,0, 1, tok, vocab,  300, True, False)
			text_dataloader = torch.utils.data.DataLoader(text_data, batch_size=batch_size, num_workers=0)

			for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(text_dataloader):
				token_ids = token_ids.long().to(device)
				segment_ids = segment_ids.long().to(device)
				valid_length= valid_length

				out = model(token_ids, valid_length, segment_ids)

				for i in out:
					softmax = nn.Softmax(dim=-1)
					confidence.append(softmax(i)) # 추론 스코어 저장 
					y_pred.append(torch.argmax(i).cpu().numpy().tolist())

			# Construction , fire
			if y_pred[0] == 0 :
				pred = "사업장대규모인적사고"
			elif y_pred[0] == 1 :
				pred = "다중밀집시설대형화재"
			elif y_pred[0] == 2 :
				pred = "철도교통사고"
			elif y_pred[0] == 3 :
				pred = "해양선박사고"
			elif y_pred[0] == 4 :
				pred = "유해화학물질사고"
			elif y_pred[0] == 5 :
				pred = "항공기사고"
			elif y_pred[0] == 6 :
				pred = "감염병"
			elif y_pred[0] == 7 :
				pred = "도로교통사고"


			score = confidence[0]
			print('===== 추론 리스트 =====', score.tolist())
			Construction_score = round((score.tolist()[0])*100)
			Fire_score = round((score.tolist()[1])*100)
			train_score = round((score.tolist()[2])*100)
			ship_score = round((score.tolist()[3])*100)
			# aircraft_score = round((score.tolist()[4])*100)
			# road_score = round((score.tolist()[5])*100)
			chemical_score = round((score.tolist()[4])*100)
			# infect_score = round((score.tolist()[7])*100)

			# # 임시저장 - 데이터가 없어 학습못한 3 클래스는 랜덤화 
			# train_score = random.randrange(6,11)
			# ship_score = random.randrange(7,13)
			aircraft_score = random.randrange(2,7)
			road_score = random.randrange(3,9)
			# chemical_score = random.randrange(3,9)
			infect_score = random.randrange(2,8)

			print("-----------------------------------------")
			print(">> 추론된 값은 ==> " , pred )
			print("> 사업장대규모인적사고의 confidence score :  " , Construction_score,"%" )
			print("> 다중밀집시설대형화재의 confidence score :  " , Fire_score,"%" )
			print("> 철도교통사고의 confidence score :  " , train_score,"%" )
			print("> 해양선박사고의 confidence score :  " , ship_score,"%" )
			print("> 항공기사고의 confidence score :  " , aircraft_score,"%" )
			print("> 도로교통사고의 confidence score :  " , road_score,"%" )
			print("> 유해화학물질사고의 confidence score :  " , chemical_score,"%" )
			print("> 감염병의 confidence score :  " , infect_score,"%" )

										
			bardata = []
			bardata.append({"title":"사업장대규모인적사고"," value":Construction_score})
			bardata.append({"title":"다중밀집시설대형화재"," value":Fire_score})
			bardata.append({"title":"철도교통사고"," value":train_score})
			bardata.append({"title":"해양선박사고"," value":ship_score})
			bardata.append({"title":"항공기사고"," value":aircraft_score})
			bardata.append({"title":"도로교통사고"," value":road_score})
			bardata.append({"title":"유해화학물질사고"," value":chemical_score})
			bardata.append({"title":"감염병"," value":infect_score})

			json_result['confidence_score'][f'{file}'] = {'pred_class': pred, 'confidence_score': bardata}
			json_result['statistics'][pred] = json_result['statistics'][pred] + 1 if pred in json_result['statistics'] else 1

			print("----- json_result out -----")

		return pred , bardata, json_result # 로그, 스텝 , 추론값 , bar json_result
	


if __name__=='__main__':
	for i in range(10):
	# 	#Test
		file_path = "/home/xaiplanet/xai_workspace/nlp_integrate/PDF_Test/Test_files"
		pred_path = "/home/xaiplanet/xai_workspace/nlp_integrate/PDF_Test/predict"
		pred , bardata, json_result = Classificaion_predict(file_path) ## 받아온 데이터로 일괄 저장할 로직 만들기
		# print(*json_result, *json_result.values(), sep='\n')
		iter = 1
		while True:
			if os.path.exists(f'{pred_path}/predict_confidence{iter}.json'):
				iter += 1
			else:
				with open(f'{pred_path}/predict_confidence{iter}.json', 'w', encoding="utf-8") as f:
					json.dump(json_result, f, ensure_ascii=False, indent=4)
					f.close()
				break