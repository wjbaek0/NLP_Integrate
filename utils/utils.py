import yaml
import matplotlib.pyplot as plt
import os
import re
from konlpy.tag import Kkma, Komoran, Mecab
from wordcloud import WordCloud
from collections import Counter
from lexrankr import LexRank
from typing import List
from konlpy.tag import Mecab
import json



class Params:
    def __init__(self, project_file):
        self.params = yaml.safe_load(open(project_file).read())

    def __getattr__(self, item):
        return self.params.get(item, None)


class LexRanking:
    def __init__(self, txt):
        
        self.file = str(txt)
        # self.txt_str = self.open_file(file=self.file)
        self.lexrank = self.set_tokenizer()
        self.summary = self.generate_summary()
        self.sum_length, self.doc_length = self.summary['length'][0], self.summary['length'][1] 

    def open_file(self, file):
        with open(file, encoding='utf-8') as f:
            text = f.read()
        return text

    def set_tokenizer(self):
        tokenizer: MecabTokenizer = MecabTokenizer()
        lexrank: LexRank = LexRank(tokenizer)
        
        return lexrank

    def generate_summary(self):
        print('Summarizing files...')

        self.lexrank.summarize(self.file)
        len_file = self.lexrank.num_sentences

        if len_file > 500:
            k = 100 / len_file
            summary = self.lexrank.probe(k)
        else:
            summary = self.lexrank.probe(0.2)
            
        summary['length'].append(self.lexrank.num_sentences)
        for i in range(len(summary['text'])):
            input_string = summary['text'][i]
            
            time_pattern = re.compile(r'([^\d]\d{2}) {0,3}[\:\：] {0,3}(\d{2})([^\d])')
            date_pattern = re.compile(r'([^\d]\d{2,4})\ {0,2}\.\ {0,2}(\d{1,2})\ {0,2}\.\ {0,2}(\d{1,2})([^\d])')
            comma_pattern = re.compile(r'(\d{1,})\,(\d{3})')
            space_pattern = re.compile(r'[\(\)\․\,\:\/\\]')
            pattern_punctuation = re.compile(r'[^\w\s\㎞\ｍ\㎜\㎡\㎠\㎖\ℓ\㏁\℃\%\×\~\～\-]')

            result = time_pattern.sub(r'\1시 \2분\3', input_string)
            result = date_pattern.sub(r'\1년 \2월 \3일\4', result)
            result = comma_pattern.sub(r'\1\2', result)
            result = space_pattern.sub(r' ', result)
            output_string = pattern_punctuation.sub(r'', result)

            output_string = re.sub(r'[" "]+ ', " ", output_string)

            summary['text'][i] = output_string

        print('Summary complete')
        
        return summary

    # def print_summary(self):
    # print('======== Summary ========', *self.summary['text'], sep='\n')
    # print('\n======== Number of Sentences ========')
    # print(f'Summarized: {self.sum_length} sentences / Original: {self.doc_length} sentences')


class MecabTokenizer:
    mecab: Mecab = Mecab()

    def __call__(self, text: str) -> List[str]:
        pos = self.mecab.pos(text, join=True)
        tokens: List[str] = [
            w for w in pos if '/NN' in w or '/VV' in w or '/VA' in w or '/XR' in w]

        return tokens


def keyword(data_path, font_path):
    mecab = Mecab()
    with open(data_path, 'r', encoding='utf-8') as f:
        file = f.read()
        nouns = mecab.nouns(file)
        count = Counter(nouns)
        # print('=====================COUNT======================')
        # print(count)

        global cloud_list 

        cloud_list = []
        for key, val in count.items():
            cloud_list.append({"text": "{}".format(key), "value" : "{}".format(val)})
        print(cloud_list)
        print(type(cloud_list))

        most_common = count.most_common()
        
        print("===============COUNT===============")
        print(count)
        top5_keyword = [word[0] for idx in range(len(most_common)) for word in most_common]


        wc = WordCloud(font_path= font_path, background_color='white', max_font_size=60)
        cloud = wc.generate_from_frequencies(count)
        # wc.to_file(os.path.splitext(data_path)[0] + '.png')
        
        print('Wordcloud file saving completed...')
        

    # plt.figure(figsize=(10, 8))
    # plt.axis('off')
    # plt.imshow(cloud)
    # plt.show()

    return cloud_list    

# ================================================================================================
def top_keyword(data_path, font_path):
    mecab = Mecab()
    with open(data_path, 'r', encoding='utf-8') as f:
        file = f.read()
        nouns = mecab.nouns(file)
        count = Counter(nouns)

        cloud_list = []
        for key, val in count.items():
            cloud_list.append({"text": "{}".format(key), "value" : "{}".format(val)})

        most_common = count.most_common()
        top5_keyword = [word[0] for idx in range(len(most_common)) for word in most_common]

        print('====================KEYWORD=====================')

        
    print(f'top-5 keyword: {top5_keyword[:5]}')
    return top5_keyword[:5]   

