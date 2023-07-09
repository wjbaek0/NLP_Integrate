from attr import dataclass
from omegaconf import MISSING
from typing import List, Optional

# from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard


@dataclass
class DatasetsConfig:
    # path to train dataset
    # train_path: str = 'data/datasets/docred_joint/train_joint.json'
    train_path: str = '/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/datasets/docred_joint/train_joint.json'
    # path to validation dataset
    # valid_path: str = 'data/datasets/docred_joint/val_joint.json'
    valid_path: str = '/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/datasets/docred_joint/val_joint.json'  ## 현 경로에 존재 하지 않음 
    # path to test dataset
    # test_path: Optional[str] = 'data/datasets/docred_joint/test_joint.json'
    test_path: Optional[str] = '/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/datasets/docred_joint/test_joint.json'
    types_path: str = MISSING


@dataclass
class ModelConfig:
    # model type (joint_multi_instance, joint_global, mention_classify, coref_classify, entity_classify,
    # relation_classify_multi_instance, relation_classify_global) ...
    model_type: str = 'joint_multi_instance'

    # path to or name of encoder model (HuggingFace BERT, e.g. bert-base-cased or bert-large-cased or ...)
    encoder_path: str = MISSING

    # path to tokenizer (HuggingFace BERT, e.g. bert-base-cased or bert-large-cased or ...)
    tokenizer_path: str = MISSING

    # task-specific thresholds
    mention_threshold: float = 0.85
    coref_threshold: float = 0.85
    rel_threshold: float = 0.6

    # probability of neuron dropout in selected model
    prop_drop: float = 0.1

    # dimensionality of meta data embedding
    meta_embedding_size: int = 25

    # size of meta embedding layers. Currently not calculated based on dataset, just set it to something
    # reasonably high
    size_embeddings_count: int = 30
    ed_embeddings_count: int = 300
    # token_dist_embeddings_count: int = 2000  #MEMO token_dist_embeddings_count 수정
    token_dist_embeddings_count: int = 3000  #MEMO token_dist_embeddings_count 수정
    sentence_dist_embeddings_count: int = 50

    # size of position embedding layer
    position_embeddings_count: int = 2000 #MEMO position_embeddings_count 수정


@dataclass
class SamplingConfig:
    # number of negative entity spans per document
    neg_mention_count: int = 200
    # number of negative (not coreferent) coreference pairs  per document
    neg_coref_count: int = 200
    # number of negative (unrelated) entity pairs per document
    neg_relation_count: int = 200
    # maximum size of spans
    max_span_size: int = 10
    # number of sampling processes. 0 = no multiprocessing for sampling
    sampling_processes: int = 4
    # ratio of negative mention spans that partially overlap with ground truth mention spans
    neg_mention_overlap_ratio: float = 0.5
    # if true, input is lowercased during preprocessing
    lowercase: bool = False


@dataclass
class LossConfig:
    # loss weights of respective task
    mention_weight: float = 1
    coref_weight: float = 1
    entity_weight: float = 0.25
    relation_weight: float = 1


@dataclass
class TrainingConfig:
    # batch size used for training
    batch_size: int = 1
    # min number of epochs
    min_epochs: int = 20
    # max number of epochs
    max_epochs: int = 20
    # learning rate
    lr: float = 5e-5
    # proportion of total train iterations to warmup in linear increase/decrease schedule
    lr_warmup: float = 0.1
    # weight decay to apply
    weight_decay: float = 0.01
    # maximum gradient norm
    max_grad_norm: float = 1.0
    # accumulate gradients over n batches
    accumulate_grad_batches: int = 1
    # maximum spans to process simultaneously during training
    # Only needed in case of insufficient memory
    max_spans: Optional[int] = None  #MEMO max max_spans 수정
    # max_spans: Optional[int] = 10  #MEMO max max_spans 수정

    # maximum mention pairs for coreference resolution
    # to process simultaneously during training
    # Only needed in case of insufficient memory
    max_coref_pairs: Optional[int] = None #MEMO max_coref_pairs 수정
    # max_coref_pairs: Optional[int] = 10 #MEMO max_coref_pairs 수정

    # maximum mention pairs for multi-instance relation classification
    # to process simultaneously during training
    # Only needed in case of insufficient memory
    max_rel_pairs: Optional[int] = None  #MEMO max_rel_pairs 수정
    # max_rel_pairs: Optional[int] = 10  #MEMO max_rel_pairs 수정


@dataclass
class InferenceConfig:
    # batch size used for validation
    valid_batch_size: int = 1
    # batch size used during testing
    test_batch_size: int = 1
    # maximum spans to process simultaneously during inference
    # only needed in case of insufficient memory
    # max_spans: Optional[int] = None
    max_spans: Optional[int] = 10  #MEMO max max_spans 수정

    # maximum mention pairs for coreference resolution
    # to process simultaneously during inference
    # only needed in case of insufficient memory
    # max_coref_pairs: Optional[int] = None
    max_coref_pairs: Optional[int] = 10 #MEMO max_coref_pairs 수정
    
    

    # maximum mention pairs for multi-instance relation classification
    # to process simultaneously during inference
    # only needed in case of insufficient memory
    # max_rel_pairs: Optional[int] = None
    max_rel_pairs: Optional[int] = 10  #MEMO max_rel_pairs 수정


@dataclass
class DistributionConfig:
    # gpus for training/inference
    gpus: List[int] = []
    # gpus: List[int] = field(default_factory=list)
    # used accelerator for multi gpu training/inference (supported: dp, ddp)
    accelerator: str = ''
    # prepares data per node when using ddp as accelerator
    prepare_data_per_node: bool = False


@dataclass
class MiscConfig:
    # if true, store predictions on disc (in log directory)
    store_predictions: bool = False
    # if true, store evaluation examples on disc (in log directory)
    store_examples: bool = False

    # logging
    flush_logs_every_n_steps: int = 1000
    log_every_n_steps: int = 1000

    # deterministic behaviour for experiment reproduction (also set seed in this case)
    deterministic: bool = False
    seed: Optional[int] = None

    # path to cache path of HuggingFace models
    cache_path: Optional[str] = None

    # precision to use (16 / 32)
    precision: int = 32

    # performance profiler to use
    profiler: Optional[str] = None

    # Test the best model on the validation set after training
    # also saves predictions and example visualizations (in case of joint model) files.
    # Should only be set to True if test_path is unset (if test_path is set, the dataset specified there is
    # used for final testing)
    final_valid_evaluate: bool = False


@dataclass
class LoggingConfig:
    # if true, store predictions on disc (in log directory)
    store_predictions: bool = False
    # if true, store evaluation examples on disc (in log directory)
    store_examples: bool = False

    # logging
    flush_logs_every_n_steps: int = 1000
    log_every_n_steps: int = 1000


@dataclass
class TrainConfig:
    datasets: DatasetsConfig = DatasetsConfig()
    model: ModelConfig = ModelConfig()
    sampling: SamplingConfig = SamplingConfig()
    loss: LossConfig = LossConfig()
    inference: InferenceConfig = InferenceConfig()
    training: TrainingConfig = TrainingConfig()
    distribution: DistributionConfig = DistributionConfig()
    misc: MiscConfig = MiscConfig()


@dataclass
class ModelTestConfig:
    # path to directory that containing model checkpoints
    
    # model_path: str = '/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/runs/2022-12-06/17-52-15/checkpoint/epoch=0-step=1479.ckpt'
    model_path: str = '/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/data/runs/2022-11-18/18-50-04/checkpoint/epoch=23-step=35519.ckpt'

    # path to tokenizer (HuggingFace BERT, e.g. bert-base-cased or bert-large-cased or ...)
    # tokenizer_path: str = MISSING
    tokenizer_path: str = 'bert-base-cased'

    # path to directory containing encoder configuration or name of configuration
    # (HuggingFace BERT, e.g. bert-base-cased or bert-large-cased or ...)
    # encoder_config_path: str = MISSING
    encoder_config_path: str = 'bert-base-cased'

    # task-specific thresholds
    # overrides values used for model training (validation step)
    mention_threshold: Optional[float] = None
    coref_threshold: Optional[float] = None
    rel_threshold: Optional[float] = None


@dataclass
class DatasetsTestConfig:
    # path to test dataset
    test_path: str = MISSING


@dataclass
# class TestConfig(YAMLWizard):
class TestConfig:
    dataset: DatasetsTestConfig = DatasetsTestConfig()
    model: ModelTestConfig = ModelTestConfig()
    inference: InferenceConfig = InferenceConfig()
    distribution: DistributionConfig = DistributionConfig()
    misc: MiscConfig = MiscConfig()
