import os
from dataset import Dataset 
from utils.utils import Params


class RunMain:
    def __init__(self, file_path):
        
        self.file_path = file_path
        self.params = Params(f'config/config.yml')
        self.data_path = self.params.data_path
        self.save_path = self.params.save_path
        self.save_path_plumber = self.params.save_path_plumber

    def run(self):
        os.makedirs(self.save_path, exist_ok=True)
        os.makedirs(self.save_path_plumber, exist_ok=True)

        dataset = Dataset(self.file_path)

        print('Data load...')

        dataset.prepare_data()
        dataset.multi_processing()

        print('◻️◻️◻️◻️◻️◻️◻️◻️◻️◻️◻️◻️ Finish ◻️◻️◻️◻️◻️◻️◻️◻️◻️◻️◻️◻️')


if __name__ == "__main__":
    # RunMain('/home/xaiplanet/xai_workspace/nlp_integrate/SampleData/파일이름.pdf').run()
    
    PATH = '/home/xaiplanet/xai_workspace/nlp_integrate/all_data'
    with os.scandir(PATH) as entries:
        file_list = [entry for entry in entries if entry.is_file()]
    # print(file_list)
    for f in file_list:
        try :
            RunMain(f.path).run()
        except :
            continue