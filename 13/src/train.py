from datetime import datetime
import wandb
from peft import LoraConfig
from src.loader import get_df, get_datasets, get_tokenizer, tokenize_datasets
from src.model import get_model, get_training_args, create_trainer
from src.uitils import get_predictions_and_labels, print_acc_and_confusion_matrix, print_samples

def run_train_and_eval(data_config: dict, trainer_config: dict, module_config=None):
    """
    전체 학습 및 평가 파이프라인을 실행합니다.

    Args:
        data_config (dict): 데이터 및 모델 관련 설정
        trainer_config (dict): 학습 관련 설정
        module_config (dict or LoraConfig or any): PEFT 또는 기타 확장 설정 (W&B 로깅에 포함됨)
    """
    # 데이터 준비
    df = get_df(data_config["data_dir"])
    datasets = get_datasets(df, data_config)
    tokenizer = get_tokenizer(data_config)
    tokenized_datasets = tokenize_datasets(datasets, tokenizer, data_config)

    # W&B 초기화 및 설정 기록
    wandb.init(
        project="peft-classification",
        name=f"{data_config['model_name'].replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}"
    )

    wandb.config.update({
        "data_config": data_config,
        "trainer_config": trainer_config,
        "module_config": (
            module_config.__dict__ if hasattr(module_config, "__dict__") else module_config
        )
    })

    # 모델 및 학습
    model = get_model(data_config, module_config)

    # LoRA 적용 모델인 경우만 trainable 파라미터 출력
    if hasattr(model, "print_trainable_parameters"):
        model.print_trainable_parameters()
    else:
        total, trainable = 0, 0
        for param in model.parameters():
            total += param.numel()
            if param.requires_grad:
                trainable += param.numel()
        print(f"trainable params: {trainable:,} || all params: {total:,} || trainable%: {100 * trainable / total:.4f}")

    training_args = get_training_args(trainer_config)
    trainer = create_trainer(model, training_args, tokenized_datasets, mode='train')
    trainer.train()

    # 평가
    eval_trainer = create_trainer(model, training_args, tokenized_datasets, mode='eval')
    pred_labels, true_labels = get_predictions_and_labels(eval_trainer, tokenized_datasets["test"])

    print_acc_and_confusion_matrix(true_labels, pred_labels)
    print_samples(datasets["test"], true_labels, pred_labels, num_samples=5)

    return model