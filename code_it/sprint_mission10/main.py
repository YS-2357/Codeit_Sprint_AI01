import wandb
import torch
from src.data import load_dataset, clean_texts, remove_empty, tokenize_texts, build_word2vec, build_fasttext, load_glove_embeddings, build_datasets, build_loaders
from src.model import get_model
from src.utils import get_optimizer, get_scheduler, get_loss_fn
from src.log import init_wandb, log_test_metrics
from src.train import train, evaluate
import os

def main(config):
    # 1. Load raw texts & labels
    train_texts, val_texts, test_texts, train_labels, val_labels, test_labels = load_dataset(config)

    # 2. Text preprocessing
    train_texts = clean_texts(train_texts)
    val_texts   = clean_texts(val_texts)
    test_texts  = clean_texts(test_texts)

    train_texts, train_labels = remove_empty(train_texts, train_labels)
    val_texts, val_labels     = remove_empty(val_texts, val_labels)
    test_texts, test_labels   = remove_empty(test_texts, test_labels)

    # 3. Tokenize and build embeddings
    train_tokens = tokenize_texts(train_texts)

    if config["embedding"] == "Word2Vec":
        _, word2idx, embedding_matrix = build_word2vec(train_tokens, config)
    elif config["embedding"] == "FastText":
        _, word2idx, embedding_matrix = build_fasttext(train_tokens, config)
    elif config["embedding"] == "GloVe":
        _, word2idx, embedding_matrix = load_glove_embeddings(config)
    else:
        raise ValueError(f"Unsupported embedding type: {config['embedding']}")

    # 4. Build datasets and dataloaders
    train_dataset, val_dataset, test_dataset = build_datasets(
        train_texts, val_texts, test_texts,
        train_labels, val_labels, test_labels,
        word2idx, config["max_len"]
    )
    train_loader, val_loader, test_loader = build_loaders(
        train_dataset, val_dataset, test_dataset, config
    )

    print(f"[Data Ready] Train: {len(train_dataset)} | Val: {len(val_dataset)} | Test: {len(test_dataset)}")

    # 5. Build model and training components
    model = get_model(config, embedding_matrix)
    optimizer = get_optimizer(config, model)
    scheduler = get_scheduler(config, optimizer)
    criterion = get_loss_fn(config)

    if config.get("log_wandb", False):
        init_wandb(config)

    # 6. Train
    train(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=criterion,
        optimizer=optimizer,
        scheduler=scheduler,
        num_epochs=config["num_epochs"],
        save_path=config["save_path"]
    )

    # 7. Final evaluation
    model.load_state_dict(torch.load(config["save_path"]))
    test_acc, test_precision, test_recall, test_f1 = evaluate(model, test_loader)
    print(f"[Final Evaluation] Test Acc: {test_acc:.4f} | Test Precision: {test_precision:.4f} | Test Recall: {test_recall:.4f} | Test F1: {test_f1:.4f}")

    # wandb 로깅 추가
    if config.get("log_wandb", False):
        log_test_metrics(test_acc, test_precision, test_recall, test_f1)

    if config.get("log_wandb", False):
        wandb.finish()

base_config = {
    "embedding_trainable": True,
    "embedding_dim": 200,
    "hidden_dim": 128,
    "output_dim": 20,
    "num_layers": 2,
    "dropout": 0.5,
    "bidirectional": True,
    "use_attention": True,

    "optimizer": "AdamW",
    "learning_rate": 1e-3,
    "weight_decay": 1e-5,
    "batch_size": 64,
    "num_epochs": 1,

    "loss_fn": "CrossEntropyLoss",
    "scheduler": "ReduceLROnPlateau",
    "lr_scheduler_patience": 2,
    "lr_scheduler_factor": 0.5,

    "dataset": "20Newsgroups",
    "remove_headers": True,
    "remove_footers": True,
    "remove_quotes": True,
    "val_split": 0.1,
    "test_split": 0.2,
    "max_len": 280,
    "data_dir": "data",

    "log_wandb": True,
}

if __name__ == "__main__":
    
    # 선택 가능한 임베딩
    # "Word2Vec", "FastText", "GloVe"
    embedding_name = "GloVe"

    # 선택 가능한 모델 구조
    # "EmbeddingLSTM", "AttnBiLSTM", "FinalBiLSTM"
    model_name = "AttnBiLSTM"

    # save_path는 자동으로 구성
    save_path = f"models/{embedding_name}_{model_name}_best.pt"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    base_config.update({
        "model": model_name,
        "embedding": embedding_name,
        "save_path": save_path
    })
    main(config=base_config)