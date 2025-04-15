from torch.utils.data import Dataset
from konlpy.tag import Okt
import nltk
from nltk.tokenize import word_tokenize


class K2EDataset(Dataset):
    def __init__(self, df, input_lang, output_lang, config):
        self.pairs = list(zip(df["ko"], df["en"]))
        self.input_lang = input_lang
        self.output_lang = output_lang
        self.tokenizer_ko = Okt().morphs
        self.tokenizer_en = word_tokenize
        self.max_length = config["MAX_LENGTH"]
        self.SOS_token = config["SOS_token"]
        self.EOS_token = config["EOS_token"]
        self.PAD_token = config["PAD_token"]
        self.UNK_token = config["UNK_token"]

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        ko_sent, en_sent = self.pairs[idx]
        input_tensor = self.tensor_from_sentence(self.input_lang, ko_sent, self.tokenizer_ko)
        target_tensor = self.tensor_from_sentence(self.output_lang, en_sent, self.tokenizer_en)
        return input_tensor, target_tensor

    def tensor_from_sentence(self, lang, sentence, tokenizer):
        tokens = tokenizer(sentence)[:self.max_length - 2]
        ids = [self.SOS_token] + [lang.word2index.get(tok, self.UNK_token) for tok in tokens] + [self.EOS_token]
        ids += [self.PAD_token] * (self.max_length - len(ids))
        return torch.tensor(ids[:self.max_length], dtype=torch.long)

from torch.utils.data import DataLoader, WeightedRandomSampler
from sklearn.model_selection import train_test_split
import numpy as np
import random
import torch

def split_train_val(df, config):
    return train_test_split(
        df,
        test_size=config["train_val_size"],
        random_state=config["random_seed"],
        stratify=df[config["stratify_col"]],
    )

def get_weighted_sampler(df, config):
    seed = config["random_seed"]
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)

    verbose = config.get("verbose", 0)

    print("\n" + "=" * 50)
    print("[STEP] 가중치 샘플링: 클래스 빈도 및 스케일링")
    print("=" * 50)

    # 1. 조합 컬럼 생성
    df = df.copy()
    df["combined_class"] = df["domain"] + "_" + df["subdomain"]

    # 2. 클래스별 빈도 계산
    class_counts = df["combined_class"].value_counts()
    if verbose > 0:
        print("▶ 클래스 조합 빈도 (상위 10개):")
        print(class_counts.head(10))
        print("")

    # 3. Soft scaling: 1 / log(freq + 1)
    raw_weights = 1.0 / np.log1p(class_counts)
    if verbose > 0:
        print("▶ Soft scaling 적용 (1 / log(freq + 1)) (상위 5개):")
        print(raw_weights.head())
        print("")

    # 4. Normalize (optional)
    if config.get("normalize_weights", True):
        min_w, max_w = raw_weights.min(), raw_weights.max()
        scaled_weights = (raw_weights - min_w) / (max_w - min_w + 1e-6)
        scaled_weights = np.clip(scaled_weights, a_min=0.05, a_max=1.0)
        if verbose > 0:
            print("▶ Min-max normalize 적용 (0~1) (상위 5개):")
            print(scaled_weights.head())
            print("")
    else:
        scaled_weights = raw_weights

    # 5. 각 샘플에 weight 매핑
    class_weight_dict = scaled_weights.to_dict()
    sample_weights = df["combined_class"].map(class_weight_dict).values

    if verbose > 0:
        print("▶ 샘플 가중치 통계:")
        print(f"  전체 샘플 수: {len(sample_weights)}")
        print(f"  평균: {sample_weights.mean():.4f}, 최대: {sample_weights.max():.4f}, 최소: {sample_weights.min():.4f}")
        print("")

        class_weight_dict_sorted = sorted(class_weight_dict.items(), key=lambda x: x[1], reverse=True)
        print("▶ 상위 가중치 클래스 (상위 5개):")
        for c, w in class_weight_dict_sorted[:5]:
            print(f"  {c}: {w:.4f}")
        print("")

    return WeightedRandomSampler(sample_weights, len(df), replacement=True)

def print_class_balance(df, column, name=""):
    print(f"\n[{name}] 클래스 분포 (상위 10개):")
    print(df[column].value_counts(normalize=True).head(10))

def get_dataloaders(train_df, valid_df, input_lang, output_lang, config):
    verbose = config.get("verbose", 0)
    batch_size = config["batch_size"]
    stratify_col = config["stratify_col"]

    print("\n" + "=" * 50)
    print("[STEP] 학습/검증 분할 및 클래스 분포 확인")
    print("=" * 50)

    # 1. train_df → train_split, val_split
    train_split, valid_split = split_train_val(train_df, config)

    if verbose > 0:
        print_class_balance(train_split, stratify_col, name="train_split")
        print_class_balance(valid_split, stratify_col, name="valid_split")

    # 2. Sampler 적용
    sampler = get_weighted_sampler(train_split, config) if config.get("use_weighted_sampler") else None

    print("\n" + "=" * 50)
    print("[STEP] Dataset 및 DataLoader 생성")
    print("=" * 50)

    # 3. Dataset 생성
    train_dataset = K2EDataset(train_split, input_lang, output_lang, config)
    valid_dataset = K2EDataset(valid_split, input_lang, output_lang, config)
    test_dataset  = K2EDataset(valid_df, input_lang, output_lang, config)

    # 4. DataLoader
    train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=sampler or None, shuffle=(sampler is None))
    valid_loader = DataLoader(valid_dataset, batch_size=batch_size)
    test_loader  = DataLoader(test_dataset, batch_size=batch_size)

    if verbose > 0:
        print(f"DataLoader 준비 완료 (batch_size: {batch_size})")

        print("[INFO] DataLoader 샘플 배치 정보 확인")
        # 첫 번째 배치만 확인
        sample_batch = next(iter(train_loader))
        input_tensor, target_tensor = sample_batch

        print(f"- 입력 텐서 shape: {input_tensor.shape}")   # (batch, seq_len)
        print(f"- 출력 텐서 shape: {target_tensor.shape}") # (batch, seq_len)
        print(f"- 입력 vocab size: {input_lang.n_words}")
        print(f"- 출력 vocab size: {output_lang.n_words}")
        print(f"- 사용 MAX_LENGTH: {config['MAX_LENGTH']}")

    return train_loader, valid_loader, test_loader

def calc_oov_ratio(df, lang, tokenizer, column, name=""):
    total, oov = 0, 0
    for sent in df[column]:
        for tok in tokenizer(sent):
            total += 1
            if tok not in lang.word2index:
                oov += 1
    ratio = 100 * oov / total if total > 0 else 0
    print(f"[{name}] OOV 비율: {ratio:.2f}% ({oov}/{total})")