import os
import json
import pandas as pd
import numpy as np
import re
import sentencepiece as spm

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    data = []
    max_col_len = 0

    for doc in json_data["documents"]:
        sentences = []
        for sublist in doc["text"]:
            for item in sublist:
                sentences.append(item.get("sentence", ""))

        sent_len = len(sentences)
        max_col_len = max(max_col_len, sent_len)

        summary = doc["abstractive"][0] if doc["abstractive"] else ""

        entry = {i: s for i, s in enumerate(sentences)}
        entry["max_len"] = sent_len
        entry["full"] = " ".join(sentences)
        entry["summary"] = summary
        data.append(entry)

    df = pd.DataFrame(data)
    columns = list(range(max_col_len)) + ["max_len", "full", "summary"]
    df = df.reindex(columns=columns)

    return df


def load_category_dataset(config):
    train_json = f"train_original_{config['category']}.json"
    valid_json = f"valid_original_{config['category']}.json"
    train_path = os.path.join(config["base_path"], train_json)
    valid_path = os.path.join(config["base_path"], valid_json)

    train_df = load_json(train_path)
    valid_df = load_json(valid_path)

    config.update({
        "train_json_path": train_path,
        "valid_json_path": valid_path,
    })
    print(f"1. config updated with JSON paths!")
    return train_df, valid_df, config


def save_dataset_as_csv(train_df, valid_df, config):
    data_dir = os.path.join(config["base_path"], "data")
    os.makedirs(data_dir, exist_ok=True)

    train_path = os.path.join(data_dir, f"train_{config['category']}.csv")
    valid_path = os.path.join(data_dir, f"valid_{config['category']}.csv")

    if os.path.exists(train_path) and os.path.exists(valid_path):
        print(f"    - CSVs already exist. Skipping save.")
    else:
        train_df.to_csv(train_path, index=False)
        valid_df.to_csv(valid_path, index=False)
        print(f"    - Saved CSVs →\n  train: {train_path}\n  valid: {valid_path}")

    config.update({
        "train_csv_path": train_path,
        "valid_csv_path": valid_path,
    })
    print(f"2. Saved CSVs and updated config paths!")
    return config


def save_text_for_spm(train_df, config):
    bpe_dir = os.path.join(config["base_path"], "bpe")
    os.makedirs(bpe_dir, exist_ok=True)

    corpus_path = os.path.join(bpe_dir, f"corpus_{config['category']}.txt")

    if os.path.exists(corpus_path):
        print(f"    - Corpus file already exists. Skipping save.")
    else:
        with open(corpus_path, "w", encoding="utf-8") as f:
            for _, row in train_df.iterrows():
                f.write(str(row["full"]).strip() + "\n")
                f.write(str(row["summary"]).strip() + "\n")
        print(f"    - Saved corpus → {corpus_path}")

    config.update({"sp_corpus_path": corpus_path})
    print(f"3. Saved corpus and updated config!")
    return config


def train_sp_model(config):
    corpus_path = config["sp_corpus_path"]
    model_prefix = os.path.join(config["base_path"], "bpe", f"spm_{config['category']}")
    model_path = f"{model_prefix}.model"
    vocab_path = f"{model_prefix}.vocab"

    if os.path.exists(model_path) and os.path.exists(vocab_path):
        print(f"    - SentencePiece model already exists. Skipping training.")
    else:
        spm.SentencePieceTrainer.Train(
            input=config["sp_corpus_path"],
            model_prefix=model_prefix,
            vocab_size=config["sp_vocab_size"],
            character_coverage=1.0,
            model_type="bpe",
            pad_id=0,
            unk_id=1,
            bos_id=2,
            eos_id=3,
            user_defined_symbols=["[MASK]", "[CLS]", "[SEP]"]
        )
        print(f"    - Trained SentencePiece model → {model_path}")

    sp = spm.SentencePieceProcessor(model_file=f"{model_prefix}.model")
    actual_vocab_size = sp.get_piece_size()

    config.update({
        "sp_model_path": model_path,
        "sp_vocab_path": vocab_path,
        "sp_vocab_size": actual_vocab_size,
        "pad": 0,
        "unk": 1,
        "bos": 2,
        "eos": 3,
    })
    print(f"4. Trained SentencePiece and updated config!")
    return config


def get_max_len(train_df, config):
    sp = spm.SentencePieceProcessor()
    sp.load(config["sp_model_path"])

    # 각 문장의 토큰 개수만 수집
    token_lengths = [len(sp.encode_as_ids(str(text).strip())) for text in train_df["full"]]

    # 원하는 커버리지에 해당하는 토큰 길이 계산
    coverage_percentile = config.get("coverage_ratio", 0.95) * 100
    max_len = int(np.percentile(token_lengths, coverage_percentile))
    print(f"    - {coverage_percentile:.1f}% of samples are <= {max_len} tokens")

    config.update({"max_len": max_len})
    print(f"5. Updated config with SentencePiece token coverage length.")
    return config
    


def prepare_data_and_tokenizer(config):
    train_df, valid_df, config = load_category_dataset(config)
    config = save_dataset_as_csv(train_df, valid_df, config)
    config = save_text_for_spm(train_df, config)
    config = train_sp_model(config)
    config = get_max_len(train_df, config)
    print(f"6. All preparation steps completed.")
    return train_df, valid_df, config