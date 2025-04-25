from peft import get_peft_model, LoraConfig, TaskType
from transformers import AutoModelForSequenceClassification

peft_config = LoraConfig(
    task_type=TaskType.SEQ_CLS,
    inference_mode=False,
    r=4,
    lora_alpha=16,
    lora_dropout=0.1,
)

model_name = "beomi/KcELECTRA-base"

model_peft = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)
model_peft = get_peft_model(model_peft, peft_config)
model_peft.print_trainable_parameters()