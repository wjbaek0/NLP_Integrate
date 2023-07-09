#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf

from CausalRelation.configs import TestConfig
from jerex import model, util

import threading

cs = ConfigStore.instance()
cs.store(name="test_kcbert", node=TestConfig)
count = 0

@hydra.main(config_name='test_kcbert', config_path='config/docred_joint')
def test(cfg: TestConfig) -> None:
    
    print(OmegaConf.to_yaml(cfg))

    try :
        
        util.config_to_abs_paths(cfg.dataset, 'test_path')
        util.config_to_abs_paths(cfg.model, 'model_path', 'tokenizer_path', 'encoder_config_path')
        util.config_to_abs_paths(cfg.misc, 'cache_path')

        print(cfg)
        model.test(cfg)
    except :

        print("except error")
        
    return 


if __name__ == '__main__':
    test()
    

