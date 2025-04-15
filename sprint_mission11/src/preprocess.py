import os
import json
import pandas as pd

# 현재 파일 기준 경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")

# JSON 원본 경로
TRAIN_JSON = os.path.join(DATA_DIR, "train.json")
VALID_JSON = os.path.join(DATA_DIR, "valid.json")

# 캐시 파일 경로
TRAIN_CACHE = os.path.join(DATA_DIR, "train_df.parquet")
VALID_CACHE = os.path.join(DATA_DIR, "valid_df.parquet")



import json
import pandas as pd

import json
import pandas as pd

def load_json_data(file_path, max_samples=None):
    """JSON 파일에서 'data' 키에 해당하는 리스트를 반환"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data = data["data"]
    return data if max_samples is None else data[:max_samples]

import re

def clean_text(text):
    text = re.sub(r"[^\w\s.,?!가-힣a-zA-Z]", "", text)  # 특수 문자 제거
    text = re.sub(r"\s+", " ", text)                   # 다중 공백 제거
    return text.strip()                                # 양쪽 공백 제거


def extract_fields(data):
    """각 항목에서 필요한 필드를 리스트로 분리"""
    return {
        'ko': [clean_text(item["ko"]) for item in data],
        'en': [clean_text(item["en"]) for item in data],
        'ko_word_count': [item["word_count_ko"] for item in data],
        'en_word_count': [item["word_count_en"] for item in data],
        'domain': [item["domain"] for item in data],
        'subdomain': [item["subdomain"] for item in data],
    }

def create_dataframe(data, verbose=0):
    fields = extract_fields(data)
    df = pd.DataFrame(fields)
    if verbose > 0:
        print("- DataFrame 생성 완료")
        print("- 컬럼:", df.columns.tolist())
        print("- 타입 정보:\n", df.dtypes)
        print("- 첫 번째 샘플:\n", df.iloc[0].to_string())
    return df


def isna_dataframe(df, name=""):
    """결측치 제거 및 로그 출력"""
    print(f"[{name}] 결측치 개수 (제거 전):", df.isna().sum().sum())
    df = df.dropna().reset_index(drop=True)
    print(f"[{name}] 결측치 개수 (제거 후):", df.isna().sum().sum())
    return df

def deduplicate_dataframe(df, name=""):
    """중복 제거 및 로그 출력"""
    print(f"[{name}] 중복 개수 (제거 전):", df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"[{name}] 중복 개수 (제거 후):", df.duplicated().sum())
    return df

def load_and_prepare_data(config):
    verbose = config.get("verbose", 0)

    print("=" * 50)
    print("[STEP] JSON → DataFrame 변환 및 전처리")
    print("=" * 50)

    train_data = load_json_data(config["train_json_path"], max_samples=config["max_train_samples"])
    valid_data = load_json_data(config["valid_json_path"], max_samples=config["max_valid_samples"])

    if verbose > 0:
        print(f"훈련 샘플 수: {len(train_data):,}개, 검증 샘플 수: {len(valid_data):,}개")
        print(f"예시 항목 key 목록: {list(train_data[0].keys())}")

    train_df = create_dataframe(train_data, verbose)
    valid_df = create_dataframe(valid_data, verbose)

    if config.get("remove_missing", True):
        train_df = isna_dataframe(train_df, name="train" if config.get("df_log") else "")
        valid_df = isna_dataframe(valid_df, name="valid" if config.get("df_log") else "")

    if config.get("remove_duplicates", True):
        train_df = deduplicate_dataframe(train_df, name="train" if config.get("df_log") else "")
        valid_df = deduplicate_dataframe(valid_df, name="valid" if config.get("df_log") else "")

    return train_df, valid_df


import numpy as np
from tqdm import tqdm
from itertools import chain

def estimate_max_length(df, config):
    sample_size = config.get("length_sample_size", None)
    percentile = config.get("length_percentile", 98)
    padding = config.get("length_padding", 2)
    seed = config.get("random_seed", 42)

    # 샘플링
    if sample_size is None or sample_size >= len(df):
        sample_df = df
    else:
        sample_df = df.sample(n=sample_size, random_state=seed)

    ko_sentences = sample_df["ko"].tolist()
    en_sentences = sample_df["en"].tolist()

    # Tokenizer 정의 (1회 초기화)
    okt = Okt()
    ko_tokenized = list(map(okt.morphs, tqdm(ko_sentences, desc="Tokenizing Korean", leave=False)))
    en_tokenized = list(map(word_tokenize, tqdm(en_sentences, desc="Tokenizing English", leave=False)))

    # 전체 길이 계산
    ko_lengths = list(map(len, ko_tokenized))
    en_lengths = list(map(len, en_tokenized))

    all_lengths = ko_lengths + en_lengths
    max_len = int(np.percentile(all_lengths, percentile))

    result = max_len + padding
    print(f"MAX_LENGTH[{percentile}%] 설정됨: {result}")
    return result

from konlpy.tag import Okt
from nltk.tokenize import word_tokenize

def filter_by_length(df, config):
    max_len = config["MAX_LENGTH"]
    verbose = config.get("verbose", 0)

    okt = Okt()
    df["ko_len"] = df["ko"].map(lambda x: len(okt.morphs(x)))
    df["en_len"] = df["en"].map(lambda x: len(word_tokenize(x)))

    if verbose > 0:
        print(f"길이 분포(ko) - 평균: {df['ko_len'].mean():.2f}, 최대: {df['ko_len'].max()}")
        print(f"길이 분포(en) - 평균: {df['en_len'].mean():.2f}, 최대: {df['en_len'].max()}")

    before = len(df)
    df = df[(df["ko_len"] <= max_len) & (df["en_len"] <= max_len)].reset_index(drop=True)
    after = len(df)
    print(f"필터링: {before} → {after}개 (제거 {before - after}개)")

    return df


import os

def load_or_build_dataframe(config):
    if (
        not config.get("force_reload_df", False) and
        os.path.exists(config["train_df_path"]) and
        os.path.exists(config["valid_df_path"])
    ):
        if config.get("verbose", 0) > 0:
            print("저장된 DataFrame을 불러옵니다.")
        train_df = pd.read_pickle(config["train_df_path"])
        valid_df = pd.read_pickle(config["valid_df_path"])
    else:
        if config.get("verbose", 0) > 0:
            print("DataFrame을 새로 생성합니다.")
        train_df, valid_df = load_and_prepare_data(config)

        # 길이 필터링 포함
        max_len = estimate_max_length(train_df, config)
        config["MAX_LENGTH"] = max_len
        train_df = filter_by_length(train_df, config)
        valid_df = filter_by_length(valid_df, config)

        # 저장
        os.makedirs(os.path.dirname(config["train_df_path"]), exist_ok=True)
        train_df.to_pickle(config["train_df_path"])
        valid_df.to_pickle(config["valid_df_path"])
        if config.get("verbose", 0) > 0:
            print("DataFrame 저장 완료")

    return train_df, valid_df