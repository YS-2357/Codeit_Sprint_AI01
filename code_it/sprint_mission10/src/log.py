import wandb
import datetime

def init_wandb(config=None, project_name="text-classification"):
    wandb.finish()

    run_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"{config['embedding']}_{config['model']}_{run_time}"

    wandb.init(
        project=project_name,
        name=run_name,
        reinit=True,
    )

    if config:
        wandb.config.update(config)

def log_metrics(epoch, train_loss, train_acc, val_acc, val_precision, val_recall, val_f1, lr):
    wandb.log({
        "epoch": epoch,
        "train_loss": train_loss,
        "train_acc": train_acc,
        "val_acc": val_acc,
        "val_precision": val_precision,
        "val_recall": val_recall,
        "val_f1": val_f1,
        "learning_rate": lr
    })

def log_test_metrics(test_acc, test_precision, test_recall, test_f1):
    wandb.log({
        "test_acc": test_acc,
        "test_precision": test_precision,
        "test_recall": test_recall,
        "test_f1": test_f1
    })

def save_model(path):
    wandb.save(path)