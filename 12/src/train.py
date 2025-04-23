import torch
import torch.nn as nn
import wandb
from tqdm import tqdm
import os
from time import time
from src.utils import get_optimizer, get_scheduler, get_criterion
from src.model import get_model
import torch
import torch.nn as nn
import wandb
from tqdm import tqdm
import os
from time import time

def train_one_epoch(model, dataloader, optimizer, criterion, config, epoch):
    model.train()
    total_loss = 0
    total_tokens = 0
    correct_tokens = 0
    start_time = time()

    pbar = tqdm(dataloader, desc=f"[Train] Epoch {epoch+1}", leave=False)

    for batch in pbar:
        src = batch["input_ids"].to(config["device"])         # (B, S)
        src_mask = batch["input_mask"].to(config["device"])   # (B, S), bool
        tgt = batch["target_ids"].to(config["device"])        # (B, T)

        tgt_in = tgt[:, :-1]   # decoder input
        tgt_out = tgt[:, 1:]   # decoder output (label)

        optimizer.zero_grad()
        logits = model(src, tgt_in, src_mask)  # (B, T, vocab_size)

        if config["criterion"] == "NLLLoss":
            import torch.nn.functional as F
            logits = F.log_softmax(logits.clamp(min=-10, max=10), dim=-1)

        num_tokens = (tgt_out != config["pad"]).sum().item()
        if num_tokens == 0:
            print(f"[DEBUG - Train] All tokens are PAD.")
            print(f"[DEBUG] tgt_out unique tokens: {torch.unique(tgt_out)}")
            print(f"[DEBUG] pad token: {config['pad']}")
            continue

        loss = criterion(
            logits.contiguous().view(-1, logits.size(-1)),
            tgt_out.contiguous().view(-1)
        )
        loss.backward()

        if config.get("grad_clip", 0.0) > 0.0:
            nn.utils.clip_grad_norm_(model.parameters(), config["grad_clip"])

        optimizer.step()

        total_loss += loss.item() * num_tokens
        total_tokens += num_tokens

        pred = logits.argmax(dim=-1)
        correct = ((pred == tgt_out) * (tgt_out != config["pad"]))
        correct_tokens += correct.sum().item()

        pbar.set_postfix({
            "loss": f"{loss.item():.4f}",
            "acc": f"{correct.sum().item() / num_tokens:.4f}",
            "lr": f"{optimizer.param_groups[0]['lr']:.7f}"
        })

    avg_loss = total_loss / total_tokens
    avg_acc = correct_tokens / total_tokens
    ppl = torch.exp(torch.tensor(avg_loss)).item()
    elapsed_time = time() - start_time

    if config.get("use_wandb", False):
        wandb.log({
            "train/loss": avg_loss,
            "train/acc": avg_acc,
            "train/ppl": ppl,
            "train/lr": optimizer.param_groups[0]["lr"],
            "train/time": elapsed_time
        })

    # print(f"[Epoch {epoch+1:02d}] Train Loss: {avg_loss:.4f} | Acc: {avg_acc:.4f} | PPL: {ppl:.2f} | Time: {elapsed_time:.1f}s")
    return avg_loss, avg_acc, ppl, elapsed_time


def validate_one_epoch(model, dataloader, criterion, config, epoch):
    model.eval()
    total_loss = 0
    total_tokens = 0
    correct_tokens = 0
    start_time = time()

    pbar = tqdm(dataloader, desc=f"[Valid] Epoch {epoch+1}", leave=False)

    with torch.no_grad():
        for batch in pbar:
            src = batch["input_ids"].to(config["device"])         # (B, S)
            src_mask = batch["input_mask"].to(config["device"])   # (B, S)
            tgt = batch["target_ids"].to(config["device"])        # (B, T)

            tgt_in = tgt[:, :-1]
            tgt_out = tgt[:, 1:]

            logits = model(src, tgt_in, src_mask)

            if config["criterion"] == "NLLLoss":
                import torch.nn.functional as F
                logits = F.log_softmax(logits.clamp(min=-10, max=10), dim=-1)

            num_tokens = (tgt_out != config["pad"]).sum().item()
            if num_tokens == 0:
                print(f"[DEBUG - Valid] All tokens are PAD.")
                print(f"[DEBUG] tgt_out unique tokens: {torch.unique(tgt_out)}")
                print(f"[DEBUG] pad token: {config['pad']}")
                continue

            loss = criterion(
                logits.contiguous().view(-1, logits.size(-1)),
                tgt_out.contiguous().view(-1)
            )

            total_loss += loss.item() * num_tokens
            total_tokens += num_tokens

            pred = logits.argmax(dim=-1)
            correct = ((pred == tgt_out) * (tgt_out != config["pad"]))
            correct_tokens += correct.sum().item()

            pbar.set_postfix({
                "loss": f"{loss.item():.4f}",
                "acc": f"{correct.sum().item() / num_tokens:.4f}",
            })

    avg_loss = total_loss / total_tokens
    accuracy = correct_tokens / total_tokens
    ppl = torch.exp(torch.tensor(avg_loss)).item()  # perplexity
    elapsed_time = time() - start_time

    if config.get("use_wandb", False):
        wandb.log({
            "valid/loss": avg_loss,
            "valid/acc": accuracy,
            "valid/ppl": ppl,
            "valid/time": elapsed_time,
        })

    # print(f"[Epoch {epoch+1:02d}] Valid Loss: {avg_loss:.4f} | Acc: {accuracy:.4f} | PPL: {ppl:.2f} | Time: {elapsed_time:.1f}s")
    if total_tokens == 0:
        print(f"[Epoch {epoch+1}] Warning: No valid tokens in validation set — skipping loss/accuracy computation.")
        return float("inf"), 0.0, float("inf"), elapsed_time

    return avg_loss, accuracy, ppl, elapsed_time


def safe_validate_one_epoch(model, dataloader, criterion, config, epoch):
    model.eval()
    total_loss = 0
    total_tokens = 0
    correct_tokens = 0
    start_time = time()

    pbar = tqdm(dataloader, desc=f"[Valid-Safe] Epoch {epoch+1}", leave=False)

    with torch.no_grad():
        for batch in pbar:
            src = batch["input_ids"].to(config["device"])
            src_mask = batch["input_mask"].to(config["device"])
            tgt = batch["target_ids"].to(config["device"])

            tgt_in = tgt[:, :-1]
            tgt_out = tgt[:, 1:]

            logits = model(src, tgt_in, src_mask)

            if config["criterion"] == "NLLLoss":
                import torch.nn.functional as F
                logits = F.log_softmax(logits.clamp(min=-10, max=10), dim=-1)

            num_tokens = (tgt_out != config["pad"]).sum().item()
            if num_tokens == 0:
                if config.get("verbose", 1) > 0:
                    print(f"[DEBUG] [Valid-Safe] Skipping batch with all PAD tokens.")
                continue

            loss = criterion(
                logits.contiguous().view(-1, logits.size(-1)),
                tgt_out.contiguous().view(-1)
            )

            loss_val = loss.item()
            if not torch.isfinite(torch.tensor(loss_val)) or torch.isnan(torch.tensor(loss_val)):
                if config.get("verbose", 1) > 0:
                    print(f"[WARNING] [Valid-Safe] Skipping batch due to invalid loss: {loss_val}")
                    print(f" - logits has NaN: {torch.isnan(logits).any().item()}")
                    print(f" - logits has Inf: {(logits == float('inf')).any().item()}")
                    print(f" - tgt_out has NaN: {torch.isnan(tgt_out).any().item()}")
                    print(f" - tgt_out unique: {torch.unique(tgt_out)}")
                continue

            total_loss += loss_val * num_tokens
            total_tokens += num_tokens

            pred = logits.argmax(dim=-1)
            correct = ((pred == tgt_out) * (tgt_out != config["pad"]))
            correct_tokens += correct.sum().item()

            pbar.set_postfix({
                "loss": f"{loss_val:.4f}",
                "acc": f"{correct.sum().item() / num_tokens:.4f}",
            })

    if total_tokens == 0:
        if config.get("verbose", 1) > 0:
            print(f"[WARNING] [Valid-Safe] No valid tokens found in epoch {epoch+1}.")
        return float("inf"), 0.0, float("inf"), time() - start_time

    avg_loss = total_loss / total_tokens
    accuracy = correct_tokens / total_tokens
    ppl = torch.exp(torch.tensor(avg_loss)).item()
    elapsed_time = time() - start_time

    if config.get("use_wandb", False):
        wandb.log({
            "valid/loss": avg_loss,
            "valid/acc": accuracy,
            "valid/ppl": ppl,
            "valid/time": elapsed_time,
        })

    if config.get("verbose", 1) > 0:
        print(f"\n[Safe Validation Summary]")
        print(f"- Loss       : {avg_loss:.4f}")
        print(f"- Accuracy   : {accuracy:.4f}")
        print(f"- Perplexity : {ppl:.2f}")
        print(f"- Time       : {elapsed_time:.1f}s")

    return avg_loss, accuracy, ppl, elapsed_time


from datetime import datetime

def train(model, train_loader, valid_loader, config):
    if not os.path.exists(config["save_dir"]):
        os.makedirs(config["save_dir"])

    optimizer = get_optimizer(model, config)
    scheduler = get_scheduler(optimizer, config)
    criterion = get_criterion(config)

    train_dict = {}
    valid_dict = {}

    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    best_valid_loss = float("inf")
    best_valid_acc = 0.0
    patience = 0
    model_name = f"{config['model_name']}_best_{timestamp}.pt"
    best_model_path = os.path.join(config["save_dir"], model_name)



    for epoch in range(config["epochs"]):
        start_time = time()

        train_loss, train_acc, train_ppl, train_time = train_one_epoch(
            model, train_loader, optimizer, criterion, config, epoch
        )
        valid_loss, valid_acc, valid_ppl, valid_time = safe_validate_one_epoch(
            model, valid_loader, criterion, config, epoch
        )

        elapsed_time = time() - start_time
        lr = optimizer.param_groups[0]["lr"]

        train_dict[epoch+1] = {"loss": train_loss, "acc": train_acc, "ppl": train_ppl,
                               "lr": lr, "time": train_time}
        valid_dict[epoch+1] = {"loss": valid_loss, "acc": valid_acc, "ppl": valid_ppl,
                               "time": valid_time, "early_stop": False}

        if scheduler is not None:
            if config["scheduler"] == "ROP":
                scheduler.step(valid_loss)
            else:
                scheduler.step()

        if config.get("verbose", 0) >= 0:
            print(f"Epoch {epoch+1:02d}")
            print(f"├─ Train | Loss: {train_loss:.4f} | Acc: {train_acc:.4f} | PPL: {train_ppl:.2f} | LR: {lr:.1e} | Time: {train_time:.1f}s")
            print(f"├─ Valid | Loss: {valid_loss:.4f} | Acc: {valid_acc:.4f} | PPL: {valid_ppl:.2f} | Time: {valid_time:.1f}s")

        # 모델 저장 (loss 우선 기준, acc는 동률 시 참고)
        eps = 1e-4  # 작은 값: 손실 차이 임계값

        if (best_valid_loss - valid_loss > eps) or (
            abs(best_valid_loss - valid_loss) <= eps and valid_acc > best_valid_acc
        ):
            best_valid_loss = valid_loss
            best_valid_acc = valid_acc
            patience = 0

            torch.save(model.state_dict(), best_model_path)
            # if config.get("use_wandb", False):
            #     wandb.save(best_model_path)
            if config.get("verbose", 0) >= 0:
                print(f"└─ Best Model Updated at {best_model_path}!")
        else:
            patience += 1
            valid_dict[epoch+1]["early_stop"] = True
            if config.get("verbose", 0) >= 0:
                print(f"└─ Patience {patience}/{config['patience']}")

        if patience >= config["patience"]:
            if config.get("verbose", 0) >= 0:
                print(f"\nEarly Stopping at Epoch {epoch+1:02d}")
                print(f"-> Best Loss: {best_valid_loss:.4f} | Acc: {best_valid_acc:.4f}")
            break

    return train_dict, valid_dict, best_model_path


def evaluate(model, test_loader, config, sp, num_examples=5):
    model.eval()
    criterion = get_criterion(config)
    total_loss = 0
    total_tokens = 0
    correct_tokens = 0
    predictions = []

    device = config["device"]
    start_time = time()

    with torch.no_grad():
        for batch in tqdm(test_loader, desc="[Test]"):
            src = batch["input_ids"].to(device)
            src_mask = batch["input_mask"].to(device)
            tgt = batch["target_ids"].to(device)

            tgt_in = tgt[:, :-1]
            tgt_out = tgt[:, 1:]

            logits = model(src, tgt_in, src_mask)

            if config["criterion"] == "NLLLoss":
                import torch.nn.functional as F
                logits = F.log_softmax(logits.clamp(min=-10, max=10), dim=-1)

            num_tokens = (tgt_out != config["pad"]).sum().item()
            if num_tokens == 0:
                print("[Warning] Skipped batch with all pad tokens.")
                continue

            loss = criterion(
                logits.contiguous().view(-1, logits.size(-1)),
                tgt_out.contiguous().view(-1)
            )

            if not torch.isfinite(loss):
                print(f"[WARNING] Invalid loss (NaN or Inf) detected. Skipping batch.")
                continue

            if torch.isnan(loss):
                print(f"[WARNING] NaN loss in test batch. Skipping this batch.")
                print(f" - tgt_out shape: {tgt_out.shape}, num_tokens: {num_tokens}")
                print(f" - logits contains NaN: {torch.isnan(logits).any().item()}")
                print(f" - target contains NaN: {torch.isnan(tgt_out).any().item()}")
                continue


            total_loss += loss.item() * num_tokens
            total_tokens += num_tokens

            pred = logits.argmax(dim=-1)
            correct = ((pred == tgt_out) * (tgt_out != config["pad"]))
            correct_tokens += correct.sum().item()

            # 예시 수집
            if len(predictions) < num_examples:
                for i in range(min(len(pred), num_examples - len(predictions))):
                    src_ids = src[i].tolist()
                    tgt_ids = tgt[i].tolist()
                    pred_ids = pred[i].tolist()

                    src_text = sp.decode([t for t in src_ids if t not in {sp.pad_id(), sp.bos_id(), sp.eos_id()}])
                    tgt_text = sp.decode([t for t in tgt_ids if t not in {sp.pad_id(), sp.bos_id(), sp.eos_id()}])
                    pred_text = sp.decode([t for t in pred_ids if t not in {sp.pad_id(), sp.bos_id(), sp.eos_id()}])

                    predictions.append((src_text, tgt_text, pred_text))

    if total_tokens == 0:
        print("[Test] Warning: No valid tokens in test set — all batches may be fully padded.")
        return float("inf"), 0.0, float("inf")

    avg_loss = total_loss / total_tokens
    accuracy = correct_tokens / total_tokens
    ppl = torch.exp(torch.tensor(avg_loss)).item()
    elapsed_time = time() - start_time

    if config.get("use_wandb", False):
        wandb.log({
            "test/loss": avg_loss,
            "test/acc": accuracy,
            "test/ppl": ppl,
            "test/time": elapsed_time,
        })

        for i, (src, tgt, pred) in enumerate(predictions):
            wandb.log({
                f"sample/sample_{i+1}": wandb.Table(columns=["Input", "Target", "Output"],
                                                data=[[src, tgt, pred]])
            })

    if config.get("verbose", 0) >= 0:
        print("\n[Test Summary]")
        print(f"- Loss       : {avg_loss:.4f}")
        print(f"- Accuracy   : {accuracy:.4f}")
        print(f"- Perplexity : {ppl:.2f}")
        print(f"- Time       : {elapsed_time:.1f}s")

        print("\n[Sample Predictions]")
        for i, (src, tgt, pred) in enumerate(predictions):
            print(f"Sample {i+1}")
            print(f"  Input  : {src}")
            print(f"  Target : {tgt}")
            print(f"  Output : {pred}")
            print("-" * 50)

    return avg_loss, accuracy, ppl


def run(model, train_loader, valid_loader, test_loader, sp, config):
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")

    # 1. wandb 로그인 및 초기화
    if config.get("use_wandb", False):
        wandb.finish()
        wandb.init(
            project=config.get("wandb_project", "text-summary"),
            name=config.get("run_name", f"{config['model_name']}_{timestamp}"),
            config=config,
            reinit=True,
        )

    # 2. 모델 불러오기
    model = get_model(config).to(config["device"])

    # 3. 옵티마이저, 스케줄러, 손실함수 설정
    optimizer = get_optimizer(model, config)
    scheduler = get_scheduler(optimizer, config)
    criterion = get_criterion(config)

    # 4. 모델 학습
    train_result, valid_result, best_model_path = train(model, train_loader, valid_loader, config)

    # 5. 최적 모델 불러오기
    model.load_state_dict(torch.load(best_model_path, map_location=config["device"]))

    # 6. 평가 실행
    test_loss, test_acc, test_ppl = evaluate(model, test_loader, config, sp)

    # 7. wandb 종료
    if config.get("use_wandb", False):
        wandb.finish()

    return {
        "train": train_result,
        "valid": valid_result,
        "test": {
            "loss": test_loss,
            "acc": test_acc,
            "ppl": test_ppl
        },
        "best_model_path": best_model_path
    }