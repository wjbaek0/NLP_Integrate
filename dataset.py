import os
import random
import time
from glob import glob
from utils.conversion import Conversion
from utils.utils import Params, LexRanking, keyword
from tqdm import tqdm


class Dataset:
    def __init__(self, file_path):
        
        self.file_path = file_path
        self.data_list = list()
        self.params = Params(f'config/config.yml')
        self.data_path = self.params.data_path

    def prepare_data(self):
        # for ext in ('pdf', 'txt', 'doc', 'docx', 'hwp'):
        self.data_list.append(self.file_path)

        # random.shuffle(self.data_list)  # Use to shuffle the name of the extension of the data

    def multi_processing(self):

        for file in tqdm(self.data_list):
            time.sleep(0.1)
            name = os.path.splitext(os.path.basename(file))[0] + '.txt'

            conversion = Conversion(file)
            extension = os.path.splitext(file)[1] 

            if extension == ".pdf":
                print('Extracting pdf text...')
                
                conversion.get_pdf_text()
                print('PDF converted to text')
                
                conversion.report_prep(os.path.join(self.params.save_path, name), self.params.save_path_plumber, self.params.save_path)
                
                keyword(data_path=os.path.join(self.params.save_path, name), font_path=self.params.font_path)

                print('pdf text extraction complete')

            elif extension == ".hwp":
                print('Extracting hwp text... ')

                print(file)
                print(conversion)
                conversion.get_hwp_text()
                print('hwp converted to text')

                conversion.report_prep(os.path.join(self.params.save_path, name), self.params.save_path_plumber, self.params.save_path)

                keyword(data_path=os.path.join(self.params.save_path, name), font_path=self.params.font_path)

                print('text preprocessing completion')

            elif extension == ".docx" or extension == ".doc":
                print('Extracting docx text... ')

                conversion.get_docx_text()
                print('docx converted to text')

                conversion.report_prep(os.path.join(self.params.save_path, name), self.params.save_path_plumber, self.params.save_path)

                keyword(data_path=os.path.join(self.params.save_path, name), font_path=self.params.font_path)

                print('docx preprocessing completion')

            elif extension == ".txt":
                print('News Summarizing and Normalizing... ')

                with open(file, 'r', encoding='utf-8') as f:
                    txt = f.read()
                    txt = "".join(txt)
                    txt = LexRanking(txt)
                print(os.path.join(self.params.save_path, name))
                with open(os.path.join(self.params.save_path, name), 'w', encoding='utf-8') as f:
                    f.writelines('\n'.join(txt.summary['text']))
                
                print('News summary and normalization complete ')

                keyword(data_path=os.path.join(self.params.save_path, name), font_path=self.params.font_path)

            else:
                raise Exception('Unused extension. We only use pdf and txt.')
