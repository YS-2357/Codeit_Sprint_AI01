from datetime import datetime
import wandb
from src.loader import get_df, get_datasets, get_tokenizer, tokenize_datasets
from src.model import get_model, get_training_args, create_trainer
from src.uitils import get_predictions_and_labels, print_acc_and_confusion_matrix, print_samples

def run_train_and_eval(data_config: dict, trainer_config: dict, peft_config: LoraConfig):
    """
    전체 학습 및 평가 파이프라인을 실행합니다.

    Args:
        data_config (dict): 데이터 및 모델 관련 설정
        trainer_config (dict): 학습 관련 설정
        peft_config (LoraConfig): LoRA 기반 PEFT 설정
    """
    # 데이터 준비
    df = get_df(data_config["data_dir"])
    datasets = get_datasets(df, data_config)
    tokenizer = get_tokenizer(data_config)
    tokenized_datasets = tokenize_datasets(datasets, tokenizer, data_config)

    # W&B 초기화
    wandb.init(
        project="peft-classification",
        name=f"{data_config['model_name'].replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    )

    # 모델 준비 및 학습
    model = get_model(data_config, peft_config)
    model.print_trainable_parameters()
    training_args = get_training_args(trainer_config)
    trainer = create_trainer(model, training_args, tokenized_datasets, mode='train')
    trainer.train()

    # 평가 진행
    eval_trainer = create_trainer(model, training_args, tokenized_datasets, mode='eval')
    pred_labels, true_labels = get_predictions_and_labels(eval_trainer, tokenized_datasets["test"])

    print_acc_and_confusion_matrix(true_labels, pred_labels)
    print_samples(datasets["test"], true_labels, pred_labels, num_samples=5)

    return model