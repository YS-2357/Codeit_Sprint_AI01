from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
import evaluate
import torch
from peft import get_peft_model, LoraConfig, TaskType

def get_model(config, peft_config=None):
    model = AutoModelForSequenceClassification.from_pretrained(
        config["model_name"],
        num_labels=3,  # 또는 len(set(df["label"]))
        # quantization_config=get_quatization_config(),     # cpu에서는 불가능
    )
    if peft_config:
        model = get_peft_model(model, peft_config)
    return model


def get_training_args(config):
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
        raise ValueError