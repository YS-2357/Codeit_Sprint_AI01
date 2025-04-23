import torch
from torch.utils.data import Dataset
import sentencepiece as spm

class Full2SummaryDataset(Dataset):
    def __init__(self, df, sp, max_len):
        self.df = df
        self.sp = sp
        self.max_len = max_len

    def __len__(self):
        return len(self.df)

    def pad_or_truncate(self, ids):
        ids = ids[:self.max_len]
        return ids + [0] * (self.max_len - len(ids))

    def __getitem__(self, idx):
        full = self.df.iloc[idx]["full"]
        summary = self.df.iloc[idx]["summary"]

        # 입력: BOS full EOS / BOS summary EOS
        input_ids = [self.sp.bos_id()] + self.sp.encode_as_ids(full) + [self.sp.eos_id()]
        target_ids = [self.sp.bos_id()] + self.sp.encode_as_ids(summary) + [self.sp.eos_id()]

        input_ids = self.pad_or_truncate(input_ids)
        target_ids = self.pad_or_truncate(target_ids)

        # 마스크
        input_mask = [t != 0 for t in input_ids]

        return torch.tensor(input_ids), torch.tensor(input_mask), torch.tensor(target_ids)


from sklearn.model_selection import train_test_split

def split_train_validation(train_df, config):
    test_size = 1 - config["train_val_ratio"]
    train_df, valid_df = train_test_split(
        train_df,
        test_size=test_size,
        random_state=config["seed"],
        shuffle=True
    )
    print(f"    - Train Val Ratio: {config['train_val_ratio']:.1f}: {test_size:.1f}")
    print(f"    - Train: {len(train_df)}, Valid: {len(valid_df)}")
    return train_df.reset_index(drop=True), valid_df.reset_index(drop=True)
    

def collate_fn(batch):
    input_ids, input_mask, target_ids = zip(*batch)
    
    input_ids = torch.stack(input_ids)
    input_mask = torch.stack(input_mask)
    target_ids = torch.stack(target_ids)
    
    return {
        "input_ids": input_ids,
        "input_mask": input_mask,
        "target_ids": target_ids,
    }


from torch.utils.data import DataLoader

def get_all_loaders(train_df, test_df, config):
    # 샘플 수 제한
    train_sample_size = config.get("train_sample_size", None)
    if train_sample_size:
        train_df = train_df[:train_sample_size]
    test_sample_size = config.get("test_sample_size", None)
    if test_sample_size:
        test_df = test_df[:test_sample_size]

    train_df, valid_df = split_train_validation(train_df, config)
    sp = spm.SentencePieceProcessor(model_file=config["sp_model_path"])
    
    train_loader = DataLoader(
        Full2SummaryDataset(train_df, sp, config["max_len"]), 
        batch_size=config["batch_size"], 
        shuffle=True, 
        collate_fn=collate_fn
    )
    valid_loader = DataLoader(
        Full2SummaryDataset(valid_df, sp, config["max_len"]), 
        batch_size=config["batch_size"], 
        shuffle=False, 
        collate_fn=collate_fn
    )
    test_loader = DataLoader(
        Full2SummaryDataset(test_df, sp, config["max_len"]), 
        batch_size=config["batch_size"], 
        shuffle=False, 
        collate_fn=collate_fn
    )

    if config.get("verbose", 0) > 0:
        print("\nDataLoader Summary")
        print("─────────────────────────────")
        for name, loader in zip(["Train", "Valid", "Test"], [train_loader, valid_loader, test_loader]):
            sample_count = len(loader.dataset)
            batch_count = len(loader)
            print(f"[{name}] Samples: {sample_count} | Batches: {batch_count}")
            batch = next(iter(loader))
            for k, v in batch.items():
                print(f"    {k:<12} shape: {tuple(v.shape)}")
        print("─────────────────────────────\n")
    
    return train_loader, valid_loader, test_loader