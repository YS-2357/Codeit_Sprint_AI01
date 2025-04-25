from datetime import datetime
import wandb
import torch
import os
from src.loader import get_df, get_datasets, get_tokenizer, tokenize_datasets
from src.model import get_model, get_training_args, create_trainer
from src.uitils import get_predictions_and_labels, print_acc_and_confusion_matrix, print_samples

def run_train_and_eval(data_config: dict, trainer_config: dict, module_config=None):
    """
    전체 학습 및 평가 파이프라인을 실행합니다. 모델 저장 및 체크포인트 로드를 지원합니다.

    Args:
        data_config (dict): 데이터 및 모델 관련 설정
        trainer_config (dict): 학습 관련 설정
        module_config (dict or LoraConfig or any): PEFT 또는 기타 layer freeze 설정
    """
    # 데이터 준비
    df = get_df(data_config["data_dir"])
    datasets = get_datasets(df, data_config)
    tokenizer = get_tokenizer(data_config)
    tokenized_datasets = tokenize_datasets(datasets, tokenizer, data_config)

    # output_dir 기반 자동 경로 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    model_name_sanitized = data_config["model_name"].replace("/", "_")
    output_dir = trainer_config.get("output_dir", f"./results/{model_name_sanitized}_{timestamp}")
    save_path = trainer_config.get("save_path", os.path.join(output_dir, "checkpoint"))
    resume_from_checkpoint = trainer_config.get("resume_from_checkpoint", None)

    os.makedirs(save_path, exist_ok=True)

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

    # 모델 준비
    model = get_model(data_config, module_config)

    # 체크포인트에서 모델 파라미터만 로드 (옵티마이저 상태 등은 불러오지 않음)
    if resume_from_checkpoint:
        model_path_bin = os.path.join(resume_from_checkpoint, "pytorch_model.bin")
        model_path_safe = os.path.join(resume_from_checkpoint, "model.safetensors")

        if os.path.exists(model_path_bin):
            print(f"[✓] Loading model weights from {model_path_bin}")
            model.load_state_dict(torch.load(model_path_bin, map_location=torch.device("cuda" if torch.cuda.is_available() else "cpu")))
        elif os.path.exists(model_path_safe):
            print(f"[✓] Loading model weights from {model_path_safe}")
            from safetensors.torch import load_file
            device_str = "cuda" if torch.cuda.is_available() else "cpu"
            model.load_state_dict(load_file(model_path_safe, device=device_str))
        else:
            raise FileNotFoundError("No valid model weight file found in checkpoint directory.")
        

    # 학습 파라미터 출력
    if hasattr(model, "print_trainable_parameters"):
        model.print_trainable_parameters()
    else:
        total, trainable = 0, 0
        for param in model.parameters():
            total += param.numel()
            if param.requires_grad:
                trainable += param.numel()
        print(f"trainable params: {trainable:,} || all params: {total:,} || trainable%: {100 * trainable / total:.4f}")

    # 학습 인자 및 트레이너 설정
    training_args = get_training_args(trainer_config)
    trainer = create_trainer(model, training_args, tokenized_datasets, mode='train')

    # 학습 수행 (체크포인트)
    if resume_from_checkpoint:
        print(f"[✓] Resuming training from checkpoint: {resume_from_checkpoint}")
    else:
        print("[✗] Starting training from scratch")
    trainer.train()

    # 모델 저장
    save_path = trainer_config.get("save_path", training_args.output_dir)
    trainer.save_model(save_path)

    # 평가
    eval_trainer = create_trainer(model, training_args, tokenized_datasets, mode='eval')
    pred_labels, true_labels = get_predictions_and_labels(eval_trainer, tokenized_datasets["test"])

    print_acc_and_confusion_matrix(true_labels, pred_labels)
    print_samples(datasets["test"], true_labels, pred_labels, num_samples=5)

    return model