from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
import evaluate
import torch
from peft import get_peft_model, LoraConfig

def get_model(config: dict, peft_config: LoraConfig = None):
    """
    사전학습된 분류 모델을 불러오고 필요 시 PEFT(LoRA)를 적용합니다.
    선택적으로 특정 레이어만 학습되도록 설정할 수 있습니다.

    Args:
        config (dict): 모델 구성 설정
            - "model_name" (str): 사전학습 모델 이름
            - "train_layers" (list of str, optional): 학습할 레이어 이름 패턴 목록
        peft_config (LoraConfig, optional): LoRA 설정 객체

    Returns:
        transformers.PreTrainedModel: 분류용 모델 객체
    """
    model = AutoModelForSequenceClassification.from_pretrained(
        config["model_name"],
        num_labels=3,  # 또는 len(set(df["label"]))
    )

    # 선택적 layer unfreeze
    if "train_layers" in config:
        # 전체 파라미터 freeze
        for name, param in model.named_parameters():
            param.requires_grad = False
        # 지정된 레이어만 unfreeze
        for name, param in model.named_parameters():
            if any(target in name for target in config["train_layers"]):
                param.requires_grad = True

    # PEFT 적용
    if peft_config:
        model = get_peft_model(model, peft_config)

    return model


def get_training_args(config):
    """
    Hugging Face Trainer에 필요한 학습 인자를 생성합니다.

    Args:
        config (dict): 학습 설정
            - output_dir, batch_size, num_epochs, eval/save/logging steps 등 포함

    Returns:
        transformers.TrainingArguments: 학습 인자 객체
    """
    return TrainingArguments(
        output_dir=config["output_dir"],
        per_device_train_batch_size=config["batch_size"],
        per_device_eval_batch_size=config["batch_size"],
        gradient_accumulation_steps=config.get("grad_accum", 2),
        num_train_epochs=config["num_epochs"],
        report_to="wandb",
        run_name=config["output_dir"].split("/")[-1],  # 디렉토리명 = 실험명

        # CPU 최적화를 위한 변경
        eval_strategy="steps",
        save_strategy="steps",
        eval_steps=config.get("eval_steps", 500),
        save_steps=config.get("save_steps", 500),
        logging_steps=config.get("logging_steps", 100),

        load_best_model_at_end=True,
        metric_for_best_model="accuracy",

        remove_unused_columns=False,
        dataloader_num_workers=0
    )


def create_trainer(model, training_args, tokenized_datasets, mode='train'):
    """
    Hugging Face Trainer 객체를 생성합니다. 평가 모드도 지원합니다.

    Args:
        model (transformers.PreTrainedModel): 학습 혹은 평가할 모델
        training_args (TrainingArguments): 학습 인자
        tokenized_datasets (dict): train/val/test Dataset 딕셔너리
        mode (str): "train" or "eval"

    Returns:
        transformers.Trainer: Trainer 객체
    """
    accuracy_metric = evaluate.load("accuracy")
    precision_metric = evaluate.load("precision")
    recall_metric = evaluate.load("recall")
    f1_metric = evaluate.load("f1")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = torch.argmax(torch.tensor(logits), dim=1)

        acc = accuracy_metric.compute(predictions=preds, references=labels)
        prec = precision_metric.compute(predictions=preds, references=labels, average="macro")
        rec = recall_metric.compute(predictions=preds, references=labels, average="macro")
        f1 = f1_metric.compute(predictions=preds, references=labels, average="macro")

        return {
            "accuracy": acc["accuracy"],
            "precision": prec["precision"],
            "recall": rec["recall"],
            "f1": f1["f1"],
        }
    if mode == 'train':
        return Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["val"],
            compute_metrics=compute_metrics
        )
    elif mode == 'eval':
        return Trainer(
                model=model,
                args=training_args,
                compute_metrics=compute_metrics,
                eval_dataset=tokenized_datasets["test"]
        )
    else:
        raise ValueError(f"Invalid mode: {mode}")


def get_device():
    """
    현재 실행 환경에서 사용 가능한 디바이스를 반환합니다.

    Returns:
        torch.device: "cuda" 또는 "cpu"
    """
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")