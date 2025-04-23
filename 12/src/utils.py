import wandb

def wandb_login():
    wandb.login(key="d96360caa2ca3fa72006523172f7c3e30085f64c")
    print("W&B logged in!")

import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler

def get_optimizer(model, config):
    opt_name = config["optimizer"]
    lr = config["lr"]
    weight_decay = config.get("weight_decay", 0.0)

    if opt_name == "Adam":
        return optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif opt_name == "AdamW":
        return optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif opt_name == "RMSprop":
        return optim.RMSprop(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif opt_name == "SGD":
        return optim.SGD(model.parameters(), lr=lr, momentum=config.get("momentum", 0.9), weight_decay=weight_decay)
    else:
        raise ValueError(f"Unsupported optimizer: {opt_name}")



def get_scheduler(optimizer, config):
    name = config["scheduler"]
    
    if name == "ROP":
        return lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode="min",
            factor=config.get("factor", 0.5),
            patience=config.get("patience", 3),
            min_lr=config.get("min_lr", 1e-6)
        )
    elif name == "CosineAnnealingLR":
        return lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=config["epochs"],
            eta_min=config.get("min_lr", 1e-6)
        )
    elif name == "CosineAnnealingWarmRestarts":
        return lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer,
            T_0=config.get("T_0", 3),
            T_mult=config.get("T_mult", 1),
            eta_min=config.get("min_lr", 1e-6)
        )
    else:
        raise ValueError(f"Unsupported scheduler: {name}")

import torch.nn as nn

def get_criterion(config):
    if config["criterion"] == "CrossEntropyLoss":
        return nn.CrossEntropyLoss(
            ignore_index=config["pad"],
            label_smoothing=config.get("label_smoothing", 0.0)
        )
    elif config["criterion"] == "NLLLoss":
        return nn.NLLLoss(ignore_index=config["pad"])
    else:
        raise ValueError(f"Unsupported criterion: {config['criterion']}")