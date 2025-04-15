import torch
from torch import nn
from tqdm import tqdm
import wandb
import os
import random
from src.utils import init_wandb, get_scheduler
from time import time

def train_one_epoch(train_loader, encoder, decoder, criterion, encoder_optimizer, decoder_optimizer, config, epoch=None):
    encoder.train()
    decoder.train()
    total_loss = 0
    desc = f"[Epoch {epoch:02d}] Training" if epoch is not None else "Training"
    pbar = tqdm(train_loader, desc=desc, leave=False)

    for input_tensor, target_tensor in pbar:
        input_tensor = input_tensor.to(config["device"]).long()
        target_tensor = target_tensor.to(config["device"]).long()

        decoder_input = target_tensor[:, :-1]           # <sos>부터 시작
        target_label = target_tensor[:, 1:]             # <eos> 전까지가 정답

        encoder_optimizer.zero_grad()
        decoder_optimizer.zero_grad()

        encoder_outputs, encoder_hidden = encoder(input_tensor)
        decoder_outputs, _, _ = decoder(encoder_outputs, encoder_hidden, decoder_input)

        loss = criterion(
            decoder_outputs.view(-1, decoder_outputs.size(-1)),
            target_label.contiguous().view(-1)
        )
        loss.backward()

        encoder_optimizer.step()
        decoder_optimizer.step()

        total_loss += loss.item()
        pbar.set_postfix({"batch_loss": f"{loss.item():.4f}"})

    return total_loss / len(train_loader)

def evaluate_one_epoch(valid_loader, encoder, decoder, criterion, config, epoch=None):
    encoder.eval()
    decoder.eval()
    total_loss = 0
    desc = f"[Epoch {epoch:02d}] Validation" if epoch is not None else "Validation"
    pbar = tqdm(valid_loader, desc=desc, leave=False)

    with torch.no_grad():
        for input_tensor, target_tensor in pbar:
            input_tensor = input_tensor.to(config["device"]).long()
            target_tensor = target_tensor.to(config["device"]).long()

            decoder_input = target_tensor[:, :-1]
            target_label = target_tensor[:, 1:]

            encoder_outputs, encoder_hidden = encoder(input_tensor)
            decoder_outputs, _, _ = decoder(encoder_outputs, encoder_hidden, decoder_input)

            loss = criterion(
                decoder_outputs.view(-1, decoder_outputs.size(-1)),
                target_label.contiguous().view(-1)
            )
            total_loss += loss.item()
            pbar.set_postfix({"batch_loss": f"{loss.item():.4f}"})

    return total_loss / len(valid_loader)

def train_model(train_loader, valid_loader, encoder, decoder, optimizer_enc, optimizer_dec, criterion, config):
    best_loss = float("inf")
    scheduler = get_scheduler(config, optimizer_enc) if config.get("scheduler") == "ReduceLROnPlateau" else None
    early_stop_counter = 0

    os.makedirs(os.path.dirname(config["checkpoint_path"]), exist_ok=True)

    if config["use_wandb"]:
        init_wandb(config)

    for epoch in range(1, config["num_epochs"] + 1):
        start_time = time()

        train_loss = train_one_epoch(train_loader, encoder, decoder, criterion, optimizer_enc, optimizer_dec, config, epoch)
        valid_loss = evaluate_one_epoch(valid_loader, encoder, decoder, criterion, config, epoch)

        epoch_time = time() - start_time
        current_lr = optimizer_enc.param_groups[0]['lr']
        print(f"Epoch {epoch:02d}/{config['num_epochs']:02d} - Train Loss: {train_loss:.4f} | Valid Loss: {valid_loss:.4f} | Time: {epoch_time:.2f}s | LR: {current_lr:.6f} | EarlyStop: {early_stop_counter}")

        if config["use_wandb"]:
            wandb.log({
                "train_loss": train_loss,
                "valid_loss": valid_loss,
                "train_time": epoch_time,
                "learning_rate": current_lr,
                "early_stop_counter": early_stop_counter,
                "epoch": epoch
            })

        if scheduler:
            previous_lr = current_lr
            scheduler.step(valid_loss)
            new_lr = optimizer_enc.param_groups[0]['lr']
            if new_lr != previous_lr:
                print(f"Learning rate changed: {previous_lr:.6f} → {new_lr:.6f}")

        if valid_loss < best_loss:
            best_loss = valid_loss
            early_stop_counter = 0
            config_to_save = config.copy()
            checkpoint_path = config["checkpoint_path"]

            torch.save({
                "encoder": encoder.state_dict(),
                "decoder": decoder.state_dict(),
                "config": config_to_save
            }, checkpoint_path)
            print(f"{config['model_type']} model checkpoint saved at {checkpoint_path}")

            if config.get("use_wandb", False):
                wandb.log({
                    "best_valid_loss": best_loss,
                    "checkpoint_epoch": epoch,
                })
                # wandb.save(checkpoint_path)
        else:
            early_stop_counter += 1
            if early_stop_counter >= config.get("patience", float("inf")):
                print(f"Early stopping triggered at epoch {epoch:02d}.")
                break

from nltk.translate.bleu_score import corpus_bleu

def evaluate_model(test_loader, encoder, decoder, criterion, config, output_lang):
    # 체크포인트
    if os.path.exists(config["checkpoint_path"]):
        checkpoint = torch.load(config["checkpoint_path"], map_location=config["device"])
        encoder.load_state_dict(checkpoint["encoder"])
        decoder.load_state_dict(checkpoint["decoder"])
        print(f"Model loaded from {config['checkpoint_path']}")
    else:
        print("Checkpoint not found. Proceeding with current model parameters.")

    encoder.eval()
    decoder.eval()
    total_loss = 0
    pbar = tqdm(test_loader, desc="Testing", leave=False)
    all_references = []
    all_candidates = []

    with torch.no_grad():
        for input_tensor, target_tensor in pbar:
            input_tensor = input_tensor.to(config["device"])
            target_tensor = target_tensor.to(config["device"])

            encoder_outputs, encoder_hidden = encoder(input_tensor)
            decoder_outputs, _, _ = decoder(encoder_outputs, encoder_hidden, target_tensor)

            loss = criterion(
                decoder_outputs.view(-1, decoder_outputs.size(-1)),
                target_tensor.view(-1)
            )
            total_loss += loss.item()
            pbar.set_postfix({"batch_loss": f"{loss.item():.4f}"})

            # === BLEU 계산을 위한 후처리 ===
            _, topi = decoder_outputs.topk(1)  # [B, T, 1]
            pred_ids = topi.squeeze(-1).tolist()  # [B, T]
            true_ids = target_tensor.tolist()     # [B, T]

            for pred_seq, ref_seq in zip(pred_ids, true_ids):
                pred_words = [
                    output_lang.index2word.get(tok, "<unk>")
                    for tok in pred_seq if tok not in [config["PAD_token"], config["EOS_token"], config["SOS_token"]]
                ]
                ref_words = [
                    output_lang.index2word.get(tok, "<unk>")
                    for tok in ref_seq if tok not in [config["PAD_token"], config["EOS_token"], config["SOS_token"]]
                ]
                all_candidates.append(pred_words)
                all_references.append([ref_words])  # bleu는 다중 참조를 받기 때문에 [[]]

    final_loss = total_loss / len(test_loader)
    bleu_score = corpus_bleu(all_references, all_candidates) * 100
    print(f"Final Test Loss: {final_loss:.4f} | BLEU: {bleu_score:.2f}")
    return final_loss, bleu_score


def tensorFromSentence(lang, sentence, tokenizer, config):
    tokens = tokenizer(sentence)[:config["MAX_LENGTH"] - 2]
    ids = [config["SOS_token"]] + [lang.word2index.get(tok, config["UNK_token"]) for tok in tokens] + [config["EOS_token"]]
    ids += [config["PAD_token"]] * (config["MAX_LENGTH"] - len(ids))
    return torch.tensor(ids[:config["MAX_LENGTH"]], dtype=torch.long)

from nltk.translate.bleu_score import sentence_bleu

def generate_random_samples(valid_df, encoder, decoder, input_lang, output_lang, tokenizer_ko, config, n=10):
    pairs = list(zip(valid_df["ko"].tolist(), valid_df["en"].tolist()))

    encoder.eval()
    decoder.eval()
    for _ in range(n):
        pair = random.choice(pairs)
        print('>', pair[0])
        print('=', pair[1])

        input_tensor = tensorFromSentence(input_lang, pair[0], tokenizer_ko, config).unsqueeze(0).to(config["device"])
        with torch.no_grad():
            encoder_outputs, encoder_hidden = encoder(input_tensor)
            decoder_outputs, _, _ = decoder(encoder_outputs, encoder_hidden)

        _, topi = decoder_outputs.topk(1)
        decoded_ids = topi.squeeze().tolist()

        decoded_words = []
        for idx in decoded_ids:
            if idx == config["EOS_token"]:
                break
            word = output_lang.index2word.get(idx, '<UNK>')
            if word not in ["<sos>", "<eos>", "<pad>", "<unk>"]:
                decoded_words.append(word)
        
        bleu = sentence_bleu([pair[1].split()], decoded_words)
        print('<', ' '.join(decoded_words))
        print(f'[BLEU] {bleu * 100:.2f}')
        print()


def run_training_pipeline(
    train_loader, valid_loader, test_loader, valid_df,
    encoder, decoder,
    optimizer_enc, optimizer_dec,
    criterion, config,
    input_lang, output_lang, tokenizer_ko, n_samples=5
):
    # 학습
    train_model(
        train_loader=train_loader,
        valid_loader=valid_loader,
        encoder=encoder,
        decoder=decoder,
        optimizer_enc=optimizer_enc,
        optimizer_dec=optimizer_dec,
        criterion=criterion,
        config=config
    )

    # 테스트 평가
    test_loss, bleu_score = evaluate_model(
        test_loader=test_loader,
        encoder=encoder,
        decoder=decoder,
        criterion=criterion,
        config=config,
        output_lang=output_lang
    )

    # wandb 로그 (최종 테스트 성능)
    if config.get("use_wandb", False):
        wandb.log({
            "final_test_loss": test_loss,
            "final_test_bleu": bleu_score
        })

    # 랜덤 샘플 번역 결과
    print("=" * 60)
    print("랜덤 샘플 번역 결과:")
    print("=" * 60)
    samples = list(zip(valid_df["ko"].tolist(), valid_df["en"].tolist()))
    translated = []

    encoder.eval()
    decoder.eval()
    for _ in range(n_samples):
        ko, en = random.choice(samples)
        input_tensor = tensorFromSentence(input_lang, ko, tokenizer_ko, config).unsqueeze(0).to(config["device"])
        with torch.no_grad():
            encoder_outputs, encoder_hidden = encoder(input_tensor)
            decoder_outputs, _, _ = decoder(encoder_outputs, encoder_hidden)

        _, topi = decoder_outputs.topk(1)
        decoded_ids = topi.squeeze().tolist()

        decoded_words = []
        for idx in decoded_ids:
            if idx == config["EOS_token"]:
                break
            word = output_lang.index2word.get(idx, '<UNK>')
            if word not in ["<sos>", "<eos>", "<pad>", "<unk>"]:
                decoded_words.append(word)

        pred = " ".join(decoded_words)
        bleu = sentence_bleu([en.split()], decoded_words) * 100 
        print("> ", ko)
        print("= ", en)
        print("< ", pred)
        print(f"[BLEU] {bleu:.2f}")
        print()
        
        translated.append({
            "source": ko,
            "target": en,
            "prediction": pred,
            "bleu": bleu
        })

    # wandb에 번역 샘플 로깅
    if config.get("use_wandb", False):
        table = wandb.Table(columns=["Source", "Target", "Prediction", "BLEU"])
        for item in translated:
            table.add_data(item["source"], item["target"], item["prediction"], item["bleu"])
        wandb.log({"random_samples": table})
        wandb.finish()