from src.train import run_train_and_eval
from peft import LoraConfig, TaskType
from datetime import datetime

# 공통 설정
data_config = {
    # df
    "data_dir": "/teamspace/studios/this_studio/Codeit_Sprint_AI01/13/data/review_data/쇼핑몰/05. 생활",

    # dataset
    "seed": 42,
    "test_size": 0.2,
    "val_size": 0.1,

    # tokenizer
    "model_name": "beomi/KcELECTRA-base",
    "max_length": 128,
    "input_column": "text",
    "label_column": "label",
    "text_output": True,    # True면 원문 포함

    # model
    "train_layers": [
        "encoder.layer.11",
        "classifier"
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
    "eval_steps": 643,
    "save_steps": 643,
    "logging_steps": 643,
    "gradient_accumulation_steps": 4,
}

from peft import LoraConfig, TaskType

peft_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,
    inference_mode=False,
    r=4,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["key", "query", "value"]
)

import wandb
wandb.login(key="d96360caa2ca3fa72006523172f7c3e30085f64c")


# 실행 진입점
if __name__ == "__main__":
    model = run_train_and_eval(data_config, trainer_config)