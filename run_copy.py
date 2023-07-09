import os
from dataset_copy import Dataset 
from utils.utils import Params


class RunMain:
    def __init__(self):

        self.params = Params(f'config/config_copy.yml')
        self.data_path = self.params.data_path
        self.save_path = self.params.save_path
        self.save_path_plumber = self.params.save_path_plumber

    def run(self):
        os.makedirs(self.save_path, exist_ok=True)
        os.makedirs(self.save_path_plumber, exist_ok=True)

        dataset = Dataset(self.data_path)

        print('Data load...')

        dataset.prepare_data()
        dataset.multi_processing()

        print('◻️◻️◻️◻️◻️◻️◻️◻️◻️◻️◻️◻️ Finish ◻️◻️◻️◻️◻️◻️◻️◻️◻️◻️◻️◻️')


if __name__ == "__main__":
    run = RunMain()
    run.run()
