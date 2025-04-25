from src.data_utils import get_df
from src.loader import get_datasets, get_tokenizer, tokenize_datasets
from src.model import get_training_args, get_model, create_trainer
from src.uitils import get_predictions_and_labels, print_acc_and_confusion_matrix, print_samples


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
}

from datetime import datetime

def get_timestamped_output_dir(model_name, base_dir="./results"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{base_dir}/{model_name}_{timestamp}"

output_dir = get_timestamped_output_dir(data_config["model_name"])

trainer_config = {
    "num_epochs": 1,
    "batch_size": 2,
    "output_dir": output_dir,
    "eval_steps": 500,
    "save_steps": 500,
    "logging_steps": 500,
    "gradient_accumulation_steps": 4,
}

from peft import LoraConfig, TaskType

peft_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,
    inference_mode=False,
    r=2,
    lora_alpha=8,
    lora_dropout=0.05,
    target_modules=["query", "value"]
)

import wandb
wandb.login(key="d96360caa2ca3fa72006523172f7c3e30085f64c")

if __name__ == "__main__":
    df = get_df(data_config["data_dir"])
    datasets = get_datasets(df, data_config)
    tokenizer = get_tokenizer(data_config)
    tokenized_datasets = tokenize_datasets(datasets, tokenizer, data_config)

    # wandb
    wandb.init(
        project="peft-classification",
        name = f"{data_config['model_name'].replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    )

    model_peft = get_model(data_config, peft_config)
    model_peft.print_trainable_parameters()
    # print(model_peft)/

    training_args = get_training_args(trainer_config)

    trainer = create_trainer(model_peft, training_args, tokenized_datasets, mode='train')
    trainer.train()
    
    from transformers import Trainer
    # Trainer 재생성
    eval_trainer = create_trainer(model_peft, training_args, tokenized_datasets, mode='eval')

    # 평가 실행
    pred_labels, true_labels = get_predictions_and_labels(eval_trainer, tokenized_datasets["test"])
    print_acc_and_confusion_matrix(true_labels, pred_labels)
    print_samples(datasets["test"], true_labels, pred_labels, num_samples=5)