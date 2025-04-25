import os
import json
import pandas as pd

def get_df(data_dir):
    # json 파일 모으기
    json_paths = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".json"):
                json_paths.append(os.path.join(root, file))

    # 제이슨 데이터에서 원하는 속성만 수집
    data = []
    for path in json_paths:
        with open(path, 'r', encoding='utf-8') as f:
            try:
                items = json.load(f)
                for item in items:
                    polarity = item.get("GeneralPolarity", None)
                    text = item.get("RawText", None)

                    if polarity is not None and text:  # 둘 다 있어야 추가
                        polarity = int(polarity)
                        if polarity in [-1, 0, 1]:
                            data.append({
                                "text": text,
                                "label": polarity + 1  # -1 → 0, 0 → 1, 1 → 2
                            })
            except Exception:
                continue  # 형식 이상한 파일은 무시하고 넘어감

    # 데이터프레임 만들기
    df = pd.DataFrame(data)
    df = df.dropna().drop_duplicates()
    return df

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
