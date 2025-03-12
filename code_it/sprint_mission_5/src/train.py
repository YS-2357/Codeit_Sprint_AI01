import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import argparse
from dataset import get_dataloaders
from models import DenoisingAutoencoder, UNetAutoEncoder
from utils import save_model, load_model
from visualization import visualize_train_results
from tqdm import tqdm

# RMSE Loss 정의
class RMSELoss(nn.Module):
    def __init__(self):
        super(RMSELoss, self).__init__()

    def forward(self, pred, target):
        return torch.sqrt(F.mse_loss(pred, target))

# Hybrid Loss 정의
class HybridLoss(nn.Module):
    def __init__(self, lambda_rmse=0.8, lambda_l1=0.2):
        super(HybridLoss, self).__init__()
        self.lambda_rmse = lambda_rmse
        self.lambda_l1 = lambda_l1
        self.rmse_loss = RMSELoss()
        self.l1_loss = nn.L1Loss()

    def forward(self, pred, target):
        return self.lambda_rmse * self.rmse_loss(pred, target) + self.lambda_l1 * self.l1_loss(pred, target)

# 디바이스 설정
device = "cuda" if torch.cuda.is_available() else "cpu"

# 훈련 함수 정의
def train_model(model, dataloaders, num_epochs=50, patience=7, lr=1e-2, weight_decay=1e-3, num_samples=3 ,device=device):
    """
    모델을 훈련하는 함수
    """
    model = model.to(device)
    criterion = HybridLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)

    # 초기 설정
    early_stop_counter = 0
    best_val_loss = float('inf')
    best_model_state = None
    print(f"Training {model.__class__.__name__} on {device}")

    for epoch in range(num_epochs):
        # Training Step
        model.train()
        train_loss = 0.0
        train_progress = tqdm(enumerate(dataloaders['train']), total=len(dataloaders['train']), desc=f"Epoch {epoch+1}/{num_epochs}", unit="batch", leave=False)
        for idx, (train_images, train_cleaned_images) in train_progress:
            train_images, train_cleaned_images = train_images.to(device), train_cleaned_images.to(device)
            optimizer.zero_grad()
            outputs = model(train_images)
            loss = criterion(outputs, train_cleaned_images)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        train_loss /= len(dataloaders['train'])
        print(f"Epoch [{epoch+1}/{num_epochs}], Train Loss: {train_loss:.4f}")

        # Validation Step
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            val_progress = tqdm(enumerate(dataloaders['val']), total=len(dataloaders['val']), desc="Validation", unit="batch", leave=False)
            for idx, (val_images, val_cleaned_images) in val_progress:
                val_images, val_cleaned_images = val_images.to(device), val_cleaned_images.to(device)
                outputs = model(val_images)
                loss = criterion(outputs, val_cleaned_images)
                val_loss += loss.item()

        val_loss /= len(dataloaders['val'])

        # 스케쥴러 적용
        prev_lr = optimizer.param_groups[0]['lr']
        scheduler.step(val_loss)
        current_lr = optimizer.param_groups[0]['lr']

        # 러닝 레이트 변경 시
        if current_lr != prev_lr:
            print(f"Learning Rate updated: {current_lr:.6f}\n")
            early_stop_counter -= 1

        # Best Model 갱신
        if val_loss < best_val_loss:
            print(f"New best validation loss: {val_loss:.4f} (Previous: {best_val_loss:.4f})")
            best_val_loss = val_loss
            best_model_state = model.state_dict()
            early_stop_counter = 0
        else:
            early_stop_counter += 1
            print(f"Validation loss increased! Early stopping counter: {early_stop_counter}/{patience}")

        # 시각화
        if (epoch+1) % max(5, num_epochs // 5) == 0:
            sample_images, sample_cleaned = next(iter(dataloaders['val']))
            sample_images, sample_cleaned = sample_images.to(device), sample_cleaned.to(device)
            sample_outputs = model(sample_images)

            visualize_train_results(sample_images, sample_cleaned, sample_outputs, num_samples=num_samples, title=f"Epoch {epoch+1} - Sample Images")


        # Early Stopping
        if early_stop_counter >= patience:
            print(f"Early stopping triggered after {epoch+1} epochs")
            model.load_state_dict(best_model_state)
            print(f"Best model loaded with val_loss = {best_val_loss:.4f}")
            break

    # Best 모델 저장
    if best_model_state is not None:
        save_model(model, f"{model.__class__.__name__}")
    else:
        print("No best model was saved.")

    return model

# 실행 코드
if __name__ == "__main__":
    # Argument Parser
    parser = argparse.ArgumentParser(description="Train a Denoising Model")

    # 모델 선택
    parser.add_argument("--model", type=str, choices=["dae", "unet"], required=True, help="Choose the model: dae (Denoising Autoencoder) or unet (U-Net Autoencoder)")

    # 하이퍼파라미터 설정
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size for training")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--patience", type=int, default=7, help="Early stopping patience")
    parser.add_argument("--lr", type=float, default=1e-2, help="Learning rate")
    parser.add_argument("--weight_decay", type=float, default=1e-3, help="Weight decay for optimizer")
    parser.add_argument("--num_samples", type=int, default=3, help="Number of sample images to visualize")

    args = parser.parse_args()


    dataloaders = get_dataloaders(batch_size=args.batch_size)

    # 학습할 모델 선택 (DenoisingAutoencoder 또는 UNetAutoEncoder)
    if args.model == "dae":
        model = DenoisingAutoencoder()
    elif args.model == "unet":
        model = UNetAutoEncoder()
    else:
        raise ValueError("Invalid model choice. Choose either 'dae' or 'unet'.")

    trained_model = train_model(
        model=model,
        dataloaders=dataloaders,
        num_epochs=args.epochs,
        patience=args.patience,
        lr=args.lr,
        weight_decay=args.weight_decay,
        num_samples=args.num_samples
    )