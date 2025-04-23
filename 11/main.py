import torch
import os
from konlpy.tag import Okt
from nltk.tokenize import word_tokenize
import datetime
from src import download  # 초기화
from src.preprocess import load_or_build_dataframe
from src.lang import load_or_build_lang
from src.loader import get_dataloaders, calc_oov_ratio
from src.model import EncoderRNN, AttnDecoderRNN
from src.utils import get_loss_fn, get_optimizer
from src.train import run_training_pipeline

# 자바 환경변수
os.environ["JAVA_HOME"] = "C:\\Program Files\\Java\\jdk-24"
os.environ["JAVA_TOOL_OPTIONS"] = "--enable-native-access=ALL-UNNAMED"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
MODEL_DIR = os.path.join(ROOT_DIR, "model")

config = {
    # 데이터 경로
    "train_json_path": "C:/Users/user/Desktop/PythonWorkspace/Codeit_Sprint_AI01/sprint_mission11/data/train.json",
    "valid_json_path": "C:/Users/user/Desktop/PythonWorkspace/Codeit_Sprint_AI01/sprint_mission11/data/valid.json",

    # 데이터 로딩
    "max_train_samples": 1000,   # None: 전체 데이터
    "max_valid_samples": 500,   # None: 전체 데이터
    "remove_missing": True,
    "remove_duplicates": True,
    "df_log": True,

    # 데이터 로더
    "train_val_size": 0.2,
    "stratify_col": "subdomain",
    "use_weighted_sampler": True,  # 또는 False
    "normalize_weights": True,

    # DataFrame 저장 위치
    "train_df_path": "data/train_df.pkl",
    "valid_df_path": "data/valid_df.pkl",
    "force_reload_df": False,   # False일 경우 기존 DataFrame 로드

    # Lang 저장 위치
    "input_lang_path": "data/input_lang.pkl",
    "output_lang_path": "data/output_lang.pkl",
    "force_rebuild_vocab": False,  # False일 경우 기존 vocab 로드

    # 길이 분석
    "MAX_LENGTH": 29,
    "length_sample_size": None,
    "length_percentile": 98,
    "length_padding": 2,
    "batch_size": 32,
    "save_vocab": True,


    # 특수 토큰
    "SOS_token": 0,
    "EOS_token": 1,
    "PAD_token": 2,
    "UNK_token": 3,

    # 기타
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "random_seed": 42,
    "verbose": 1,
}

run_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

config.update({
    # 학습 하이퍼파라미터
    "num_epochs": 100,
    "learning_rate": 0.025979870010903847,
    "weight_decay": 1e-5,
    "dropout": 0.3798667697931237,
    "optimizer": "Adam",
    "patience": 10,

    # 손실 함수 및 스케줄러
    "loss_fn": "CrossEntropyLoss",
    "scheduler": "ReduceLROnPlateau",
    "lr_scheduler_patience": 3,
    "lr_scheduler_factor": 0.5,

    # 모델 설정
    "model_type": "attn_seq2seq",           # 현재 사용 중인 모델 유형
    "use_attention": True,                  # 어텐션 사용 여부

    # RNN 기반 모델 공통 설정
    "embedding_dim": 256,
    "hidden_size": 128,
    "gru_num_layers": 1,

    # 체크포인트 및 vocab 저장
    "checkpoint_path": f"checkpoints/attn_seq2seq_{run_time}.pt",
    "save_vocab": True,

    # wandb 로깅 설정
    "use_wandb": True,
    "project_name": "k2e_translation",
    "experiment_name": "attn_seq2seq_trial"
})

import os

def loader_main(config):
    verbose = config.get("verbose", 0)

    print("=" * 50)
    print("[STEP 1] 데이터 로딩 및 결측/중복 제거")
    print("=" * 50)
    train_df, valid_df = load_or_build_dataframe(config)

    print("\n" + "=" * 50)
    print("[STEP 2] Vocab 구축 또는 로딩")
    print("=" * 50)
    os.makedirs(os.path.dirname(config["input_lang_path"]), exist_ok=True)
    os.makedirs(os.path.dirname(config["output_lang_path"]), exist_ok=True)

    ko_tokenizer = Okt().morphs
    en_tokenizer = word_tokenize

    input_lang = load_or_build_lang(train_df, "ko", ko_tokenizer, config["input_lang_path"], config)
    output_lang = load_or_build_lang(train_df, "en", en_tokenizer, config["output_lang_path"], config)

    print(f"Vocab 크기 (ko): {input_lang.n_words}, (en): {output_lang.n_words}")

    print("\n" + "=" * 50)
    print("[STEP 3] DataLoader 준비 및 클래스 분포 확인")
    print("=" * 50)
    train_loader, valid_loader, test_loader = get_dataloaders(train_df, valid_df, input_lang, output_lang, config)
    print(f"DataLoader 생성 완료 - batch_size: {config['batch_size']}")

    if verbose > 0:
        def show_loader_info(name, loader):
            sample_batch = next(iter(loader))
            src, tgt = sample_batch
            print(f"[{name}] 샘플 수: {len(loader.dataset):,}, 배치 수: {len(loader):,}")
            print(f"[{name}] 입력 shape: {src.shape}, 출력 shape: {tgt.shape}")

        print("\n" + "=" * 50)
        print("[INFO] DataLoader 상세 정보")
        print("=" * 50)
        show_loader_info("Train", train_loader)
        show_loader_info("Valid", valid_loader)
        show_loader_info("Test ", test_loader)

        print(f"- Batch size: {config['batch_size']}")
        print(f"- MAX_LENGTH: {config['MAX_LENGTH']}")
        print(f"- Vocab 크기 (ko): {input_lang.n_words}, (en): {output_lang.n_words}")


    print("\n" + "=" * 50)
    print("[STEP 4] OOV 비율 확인")
    print("=" * 50)
    if verbose > 0:
        ko_tokenizer = Okt().morphs
        en_tokenizer = word_tokenize
        calc_oov_ratio(valid_df, input_lang, ko_tokenizer, "ko", name="ko")
        calc_oov_ratio(valid_df, output_lang, en_tokenizer, "en", name="en")

    return train_df, valid_df, train_loader, valid_loader, test_loader, input_lang, output_lang


if __name__ == "__main__":
    train_df, valid_df, train_loader, valid_loader, test_loader, input_lang, output_lang = loader_main(config)

    encoder = EncoderRNN(
        input_size=input_lang.n_words,
        embedding_dim=config["embedding_dim"],
        hidden_size=config["hidden_size"],
        num_layers=config["gru_num_layers"],
        dropout=config["dropout"]
    ).to(config["device"])
    decoder = AttnDecoderRNN(
        output_size=output_lang.n_words,
        embedding_dim=config["embedding_dim"],
        hidden_size=config["hidden_size"],
        num_layers=config["gru_num_layers"],
        dropout=config["dropout"],
        sos_token=config["SOS_token"],
        max_len=config["MAX_LENGTH"]
    ).to(config["device"])
    criterion = get_loss_fn(config)

    encoder_optimizer = get_optimizer(config, encoder)
    decoder_optimizer = get_optimizer(config, decoder)
    tokenizer_ko = Okt().morphs

    run_training_pipeline(
        train_loader, valid_loader, test_loader, valid_df,
        encoder, decoder,
        encoder_optimizer, decoder_optimizer,
        criterion, config,
        input_lang, output_lang, tokenizer_ko,
        n_samples=5
    )