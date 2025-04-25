from datasets import Dataset

def get_datasets(df, config):
    # 전체 데이터셋
    dataset = Dataset.from_pandas(df)

    # 학습 시험 분리
    split_train_test = dataset.train_test_split(test_size=config["test_size"], seed=config["seed"])

    # 학습 검증 분리
    split_train_val = split_train_test['train'].train_test_split(test_size=config["val_size"], seed=config['seed'])

    datasets = {
        "train": split_train_val['train'],
        "val": split_train_val['test'],
        "test": split_train_test['test']
    }

    return datasets

from transformers import AutoTokenizer

def get_tokenizer(config):
    return AutoTokenizer.from_pretrained(config["model_name"])

def tokenize_datasets(datasets, tokenizer, config):
    def preprocess(example):
        tokenized = tokenizer(
            example[config["input_column"]],
            truncation=True,
            padding="max_length",
            max_length=config["max_length"]
        )
        if config.get("text_output"):
            tokenized["text"] = example[config["input_column"]]
        return tokenized

    tokenized_splits = {}
    for split in datasets:
        dataset = datasets[split]
        tokenized = dataset.map(preprocess, batched=True)
        tokenized = tokenized.rename_column(config["label_column"], "labels")
        tokenized.set_format(
            type="torch",
            columns=["input_ids", "attention_mask", "labels"] + (["text"] if config["text_output"] else [])
        )
        tokenized_splits[split] = tokenized

    return tokenized_splits
