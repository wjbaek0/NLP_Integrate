import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf
from CausalRelation.configs import TestConfig
from jerex import model, util

import threading
import time

from apscheduler.schedulers.background import BackgroundScheduler

cs = ConfigStore.instance()
cs.store(name="test_kcbert", node=TestConfig)

count = 0

@hydra.main(config_name='test_kcbert', config_path='config/docred_joint')
def test(cfg: TestConfig) -> None:
        
    print(OmegaConf.to_yaml(cfg))

    util.config_to_abs_paths(cfg.dataset, 'test_path')
    util.config_to_abs_paths(cfg.model, 'model_path', 'tokenizer_path', 'encoder_config_path')
    util.config_to_abs_paths(cfg.misc, 'cache_path')

    print(cfg)
    model.test(cfg)
    
    return

if __name__ == '__main__':
    sched = BackgroundScheduler()
    sched.start()
    sched.add_job(test, id="test_func")

    count = 0
    while True:
        print("Running main process...............")
        time.sleep(1)
        count += 1
        if count == 20:
            # sched.remove_job("test_func")
            break 

 
        
         
         
    