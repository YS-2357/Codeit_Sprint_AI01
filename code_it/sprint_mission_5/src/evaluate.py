import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import argparse
from dataset import get_dataloaders
from models import DenoisingAutoencoder, UNetAutoEncoder
from utils import load_model
from visualization import visualize_test_images
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from torchvision import transforms

# 디바이스 설정
device = "cuda" if torch.cuda.is_available() else "cpu"

# 이미지 저장 함수
def save_image(output_dir, predictions, file_names):
    """
    예측 이미지를 저장하는 함수
    """
    # 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    to_pil = transforms.ToPILImage()

    for idx, (pred, filename) in enumerate(zip(predictions, file_names)):
        pred = pred.clamp(0, 1)     # 이미지 픽셀 값을 0~1 사이로 제한
        pred_path = os.path.join(output_dir, f"{idx}_{filename}.png")

        # 텐서를 PIL 이미지로 변환 후 저장
        to_pil(pred).save(pred_path)
        print(f"Saved {pred_path}")

# 모델 평가 함수
def evaluate_model(model, dataloaders, output_dir, device=device):
    """
    테스트 데이터에 대해 모델을 평가하고 예측 결과를 반환하는 함수
    """
    model.eval()
    print(f"Evaluating {model.__class__.__name__} on {device}")

    original_images = []
    predictions = []

    # 저장용 리스트
    file_names = sorted([os.path.splitext(f)[0] for f in os.listdir("data/raw/test") if f.endswith(".png")])

    with torch.no_grad():
        test_progress = tqdm(dataloaders['test'], desc="Test", unit="batch", leave=False)
        for images in test_progress:
            images = images.to(device)
            outputs = model(images)
            original_images.append(images.cpu())    # 원본 이미지 저장
            predictions.append(outputs.cpu())       # 예측 이미지지 저장
    
    # 모든 배치 결과를 하나의 텐서로 결합
    original_images = torch.cat(original_images, dim=0)
    predictions = torch.cat(predictions, dim=0)

    # 저장 디렉토리
    model_output_dir = os.path.join(output_dir, model.__class__.__name__)
    save_image(model_output_dir, predictions, file_names)

    return original_images, predictions


# 실행 코드
if __name__ == "__main__":
    # Argument Parser
    parser = argparse.ArgumentParser(description="Evaluate trained models on test data")
    parser.add_argument("--batch_size", type=int, default=16, 
                        help="Batch size for DataLoader")
    parser.add_argument("--model", type=str, choices=["dae", "unet"], required=True, 
                        help="Choose the model: dae (Denoising Autoencoder) or unet (U-Net Autoencoder)")
    parser.add_argument("--num_samples", type=int, default=3, 
                        help="Number of test images to visualize")
    parser.add_argument("--output_dir", type=str, default="data/outputs",
                        help="Directory to save output images")
    
    # 파싱
    args = parser.parse_args()

    # 데이터 로더 생설
    dataloaders = get_dataloaders(batch_size=args.batch_size)

    # 모델 선택
    if args.model == "dae":
        model = DenoisingAutoencoder().to(device)
    elif args.model == "unet":
        model = UNetAutoEncoder().to(device)
    else:
        raise ValueError("Invalid model choice. Choose from 'dae' or 'unet'.")
    
    # 모델 가중치 불러오기
    model_path = f"{model.__class__.__name__}.pth"
    model = load_model(model, model_path)

    # 모델 평가
    original_images, predictions = evaluate_model(model, dataloaders, output_dir=args.output_dir) 

    # 샘플 시각화
    visualize_test_images(original_images, predictions, num_samples=args.num_samples, title="Test Results")