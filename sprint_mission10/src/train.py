from tqdm import tqdm
import wandb
import torch
import torch.nn as nn
from src.utils import compute_metrics
from src.log import log_metrics

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Now using device: {device}")

def train(model, train_loader, val_loader, criterion, optimizer, scheduler=None,
          num_epochs=10, save_path='best_model.pt'):

    best_val_acc = 0.0

    for epoch in range(1, num_epochs + 1):
        # Train
        model.train()
        total_loss, total_correct, total_samples = 0, 0, 0

        train_loop = tqdm(train_loader, desc=f"[Epoch {epoch}/{num_epochs}] Training", leave=False)
        for texts, labels in train_loop:
            texts, labels = texts.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(texts)
            loss = criterion(outputs, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            preds = torch.argmax(outputs, dim=1)
            correct = (preds == labels).sum().item()

            total_loss += loss.item()
            total_correct += correct
            total_samples += labels.size(0)

            train_loop.set_postfix(loss=loss.item(), acc=correct / labels.size(0))

        train_loss = total_loss / len(train_loader)
        train_acc = total_correct / total_samples

        # Validation
        model.eval()
        all_val_preds, all_val_labels = [], []
        val_loop = tqdm(val_loader, desc=f"[Epoch {epoch}/{num_epochs}] Validation", leave=False)
        with torch.no_grad():
            for texts, labels in val_loop:
                texts, labels = texts.to(device), labels.to(device)
                outputs = model(texts)
                preds = torch.argmax(outputs, dim=1)

                all_val_preds.extend(preds.cpu().numpy())
                all_val_labels.extend(labels.cpu().numpy())

        val_acc, val_precision, val_recall, val_f1 = compute_metrics(all_val_preds, all_val_labels)
        lr = optimizer.param_groups[0]['lr']

        # Scheduler
        if scheduler:
            scheduler.step(val_acc)

        # Logging
        log_metrics(epoch, train_loss, train_acc, val_acc, val_precision, val_recall, val_f1, lr)

        # 모델 저장
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), save_path)
            # wandb.save(save_path)     # offline에서는 생략
            print(f"Epoch {epoch}: Val Acc improved to {val_acc:.4f} → model saved.")

        else:
            print(f"Epoch {epoch}: Val Acc = {val_acc:.4f} (Best: {best_val_acc:.4f})")

        # 로그 요약
        print(f"[Summary] Epoch {epoch} | Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | Val Acc: {val_acc:.4f}")

def evaluate(model, loader):
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for texts, labels in tqdm(loader, leave=False):
            texts, labels = texts.to(device), labels.to(device)
            outputs = model(texts)
            preds = torch.argmax(outputs, dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    acc, precision, recall, f1 = compute_metrics(all_preds, all_labels)
    return acc, precision, recall, f1