import torch
import torch.nn as nn

def get_optimizer(config, model):
    if config["optimizer"] == "Adam":
        return torch.optim.Adam(
            model.parameters(),
            lr=config["learning_rate"],
            weight_decay=config.get("weight_decay", 0.0)
        )
    elif config["optimizer"] == "SGD":
        return torch.optim.SGD(
            model.parameters(),
            lr=config["learning_rate"],
            weight_decay=config.get("weight_decay", 0.0)
        )
    elif config["optimizer"] == "AdamW":
        return torch.optim.AdamW(
            model.parameters(),
            lr=config["learning_rate"],
            weight_decay=config.get("weight_decay", 0.0)
        )
    else:
        raise ValueError(f"Unsupported optimizer: {config['optimizer']}")


def get_scheduler(config, optimizer):
    if config["scheduler"] == "ReduceLROnPlateau":
        return torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode="max",
            patience=config.get("lr_scheduler_patience", 2),
            factor=config.get("lr_scheduler_factor", 0.5),
        )
    elif config["scheduler"] is None:
        return None
    else:
        raise ValueError(f"Unsupported scheduler: {config['scheduler']}")


def get_loss_fn(config):
    loss_type = config.get("loss_fn", "CrossEntropyLoss")

    if loss_type == "CrossEntropyLoss":
        return nn.CrossEntropyLoss()
    elif loss_type == "MSELoss":
        return nn.MSELoss()
    elif loss_type == "BCEWithLogitsLoss":
        return nn.BCEWithLogitsLoss()
    else:
        raise ValueError(f"Unsupported loss function: {loss_type}")


from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def compute_metrics(preds, labels):
    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="weighted")
    return acc, precision, recall, f1


