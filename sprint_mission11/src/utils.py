from torch.optim import Adam, RMSprop, SGD, AdamW
import torch
import torch.nn as nn

def get_optimizer(config, model):
    optimizer_name = config.get("optimizer", "Adam")
    learning_rate = config.get("learning_rate", 1e-4)
    weight_decay = config.get("weight_decay", 0.0)

    if optimizer_name == "Adam":
        return Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    elif optimizer_name == "SGD":
        return SGD(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    elif optimizer_name == "AdamW":
        return AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    else:
        raise ValueError(f"Unsupported optimizer: {optimizer_name}")

def get_scheduler(config, optimizer):
    scheduler_name = config.get("scheduler", None)
    factor = config.get("lr_scheduler_factor", 0.5)
    patience = config.get("lr_scheduler_patience", 3)

    if scheduler_name == "ReduceLROnPlateau":
        return torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=factor,
            patience=patience,
        )
    elif scheduler_name is None:
        return None
    else:
        raise ValueError(f"Unsupported scheduler: {scheduler_name}")

def get_loss_fn(config):
    loss_type = config.get("loss_fn", "CrossEntropyLoss")

    if loss_type == "CrossEntropyLoss":
        return nn.CrossEntropyLoss(ignore_index=config["PAD_token"], label_smoothing=0.1)
    elif loss_type == "MSELoss":
        return nn.MSELoss()
    elif loss_type == "BCEWithLogitsLoss":
        return nn.BCEWithLogitsLoss()
    else:
        raise ValueError(f"Unsupported loss function: {loss_type}")

import wandb
import datetime

def init_wandb(config):
    wandb.finish()

    run_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"{config['model_type']}_{run_time}"

    wandb.init(
        project=config["project_name"],
        name=run_name,
        reinit=True,
        config=config
    )