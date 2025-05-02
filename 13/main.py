from src.train import run_train_and_eval
from peft import LoraConfig, TaskType
from datetime import datetime

# 공통 설정
data_config = {
    # df
    "data_dir": "C:/Users/user/Desktop/PythonWorkspace/Codeit_Sprint_AI01/13/data/review_data/쇼핑몰/05. 생활",

    # task
    "task_type": "aspect",  # 또는 "general"


    # dataset
    "seed": 42,
    "test_size": 0.2,
    "val_size": 0.1,

    # tokenizer
    # "model_name": "beomi/KcELECTRA-base",
    # "model_name": "google/electra-base-discriminator",
    # "model_name": "google-bert/bert-base-multilingual-cased",
    "model_name": "beomi/KcELECTRA-small-v2022",
    # "model_name": "distilbert-base-multilingual-cased",
    "max_length": 128,
    "input_column": "text",
    "label_column": "label",
    "text_output": True,    # True면 원문 포함

    # model
    "train_layers": [
        "electra",
        "classifier",
    ],
}


def get_timestamped_output_dir(model_name, base_dir="./results"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{base_dir}/{model_name}_{timestamp}"

output_dir = get_timestamped_output_dir(data_config["model_name"])


trainer_config = {
    "num_epochs": 1,
    "batch_size": 2,
    "output_dir": output_dir,
    "save_path": output_dir,
    "eval_steps": 1722,
    "save_steps": 1722,
    "logging_steps": 1722,
    "gradient_accumulation_steps": 2,

    # "resume_from_checkpoint": "C:/Users/user/Desktop/PythonWorkspace/Codeit_Sprint_AI01/13/results/beomi/KcELECTRA-base_20250426_1730/checkpoint-4501",
}

from peft import LoraConfig, TaskType, PromptTuningConfig, PrefixTuningConfig, AdaLoraConfig, PromptEncoderConfig, IA3Config

# peft_config = LoraConfig(
#     task_type=TaskType.SEQ_CLS,
#     inference_mode=False,
#     r=2,
#     lora_alpha=8,
#     lora_dropout=0.05,
#     target_modules=["key", "query", "value"]
# )

# peft_config = PromptTuningConfig(
#     task_type=TaskType.SEQ_CLS,
#     num_virtual_tokens=10,  # 가벼운 설정. (5~20개 사이 추천)
#     tokenizer_name_or_path="beomi/KcELECTRA-base"  # 사용하는 모델의 토크나이저
# )

# peft_config = PrefixTuningConfig(
#     task_type=TaskType.SEQ_CLS,
#     num_virtual_tokens=10,  # 프리픽스 길이 (가볍게 10~20 추천)
#     encoder_hidden_size=768,  # ELECTRA-base의 hidden_size는 768
# )

peft_config = AdaLoraConfig(
    task_type=TaskType.SEQ_CLS,
    inference_mode=False,
    init_r=4,
    target_r=2,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["key", "query", "value"],
    beta1=0.85,
    beta2=0.85,
    tinit=50,
    tfinal=300,
    deltaT=10,
    orth_reg_weight=0.5,
    total_step=17720,
)

# peft_config = PromptEncoderConfig(
#     task_type=TaskType.SEQ_CLS,
#     num_virtual_tokens=20,
#     encoder_hidden_size=128,
#     token_dim=768,  # beomi/KcELECTRA-base의 hidden size
#     num_layers=2,
#     inference_mode=False
# )

# peft_config = IA3Config(
#     task_type=TaskType.SEQ_CLS,
#     inference_mode=False,
#     target_modules=["query", "key", "value", "dense"],
#     feedforward_modules=["dense"],  # Electra의 FFN 구조에 맞춤
#     init_ia3_weights=True
# )


import wandb
wandb.login()


# 실행 진입점
if __name__ == "__main__":
    model = run_train_and_eval(data_config, trainer_config, peft_config)