import os
import json
import pandas as pd

def get_df(data_dir):
    """
    지정된 디렉토리에서 JSON 파일들을 탐색하여 감성 분석용 데이터프레임을 생성합니다.

    Args:
        data_dir (str): JSON 파일들이 저장된 상위 디렉토리 경로

    Returns:
        pd.DataFrame: text와 label 컬럼을 포함한 전처리된 데이터프레임
                      label은 [-1, 0, 1]을 각각 [0, 1, 2]로 변환합니다.
    """
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
    """
    데이터프레임을 학습/검증/테스트 세트로 분할하고 Hugging Face Dataset 객체로 반환합니다.

    Args:
        df (pd.DataFrame): 전체 데이터프레임
        config (dict): 분할 비율 및 시드 값을 포함하는 설정
            - "test_size" (float): 테스트 데이터 비율
            - "val_size" (float): 검증 데이터 비율 (train에서 분할)
            - "seed" (int): 시드 값

    Returns:
        dict: {"train": Dataset, "val": Dataset, "test": Dataset}
    """
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
    """
    Hugging Face 모델 이름에 해당하는 토크나이저를 불러옵니다.

    Args:
        config (dict): 모델 이름을 포함하는 설정 딕셔너리
            - "model_name" (str): 사전학습 모델 이름

    Returns:
        transformers.PreTrainedTokenizer: 불러온 토크나이저 객체
    """
    return AutoTokenizer.from_pretrained(config["model_name"])

def tokenize_datasets(datasets, tokenizer, config):
    """
    주어진 Dataset 객체를 토크나이즈하고 PyTorch 텐서 형식으로 변환합니다.

    Args:
        datasets (dict): {"train", "val", "test"} 키를 가진 Dataset 딕셔너리
        tokenizer (transformers.PreTrainedTokenizer): 사용할 토크나이저
        config (dict): 토크나이즈 설정
            - "input_column" (str): 입력 텍스트 컬럼명 (ex: "text")
            - "label_column" (str): 라벨 컬럼명 (ex: "label")
            - "max_length" (int): 최대 토큰 길이
            - "text_output" (bool): 원문 텍스트도 유지할지 여부

    Returns:
        dict: 토크나이즈된 Dataset 객체 딕셔너리
    """
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
