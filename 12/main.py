import torch
from src.data_utils import prepare_data_and_tokenizer
from src.loader import get_all_loaders
from src.model import get_model, get_sp
from src.train import run


def print_config(config):
    print("\nConfig Summary")
    print("────────────────────────────")
    for k, v in config.items():
        print(f"{k}: {v}")
    print("────────────────────────────\n")


if __name__ == "__main__":
    config = {
        "base_path": "C:/Users/user/Desktop/PythonWorkspace/Codeit_Sprint_AI01/12/data",
        "category": "law",      # "news", "editorial", "law"

        # SentencePiece 설정
        "sp_vocab_size": 32000,
        "coverage_ratio": 0.95,
    }
    train_law_df, valid_law_df, config = prepare_data_and_tokenizer(config)

    config.update({
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "train_val_ratio": 0.8,
        "seed": 42,
        "verbose": 0,
        "train_sample_size": None,    
        "test_sample_size": 1000,
        "batch_size": 4,
    })

    train_loader, valid_loader, test_loader = get_all_loaders(train_law_df, valid_law_df, config)

    config.update({
        "model_name": "EnhancedMiniBART",
        "d_model": 192,
        "nhead": 3,
        "num_layers": 1,
        "dropout": 0.3,
                
        "optimizer": "AdamW",
        "scheduler": "CosineAnnealingLR",    
        "ROP_patience": 3,
        "criterion": "CrossEntropyLoss",
        "label_smoothing": 0.1,

        "lr": 5e-4,
        "weight_decay": 1e-4,
        "epochs": 7,
        "patience": 3,

        "use_wandb": True,
        "save_dir": "./checkpoints",
        "grad_clip": 1.0,
    })
    print_config(config)

    sp = get_sp(config)
    model = get_model(config)

    results = run(model, train_loader, valid_loader, test_loader, sp, config)