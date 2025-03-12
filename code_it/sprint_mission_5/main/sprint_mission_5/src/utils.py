import argparse
import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import cv2
from PIL import Image, ImageEnhance, ImageFilter
from torch.utils.data import Dataset, DataLoader, random_split
from sklearn.datasets import fetch_20newsgroups
import matplotlib.pyplot as plt
from torchvision import transforms
from torchvision.transforms import v2
import math
import torchvision.transforms.functional as TF
import torch.nn.functional as F
from torchinfo import summary
import kaggle
import zipfile



def parse_args():
    """
    파싱 인자 설정
    """
    parser = argparse.ArgumentParser(description="Model Training & Evaluation")
    parser.add_argument("--model", type=str, choices=["dae", "unet"], required=True, help="Choose the model: dae (Denoising Autoencoder) or unet (U-Net Autoencoder)")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size for training")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--save_path", type=str, default="models/", help="Directory to save trained models")
    return parser.parse_args()


def check_kaggle_auth():
    """
    Kaggle API 인증 확인 함수
    """
    kaggle_path = os.path.expanduser("~/.kaggle/kaggle.json")
    if not os.path.exists(kaggle_path):
        print("[ERROR] Kaggle API Token (`kaggle.json`)이 설정되지 않았습니다.\n")
        print("   해결 방법:\n1. Kaggle 계정에서 `kaggle.json` 다운로드\n2. 다음 명령어를 실행하여 설정:\n")
        print("   mkdir -p ~/.kaggle")
        print("   mv kaggle.json ~/.kaggle/")
        print("   chmod 600 ~/.kaggle/kaggle.json")
        print("\n설정 후 다시 실행하세요.")
        exit(1)


def extract_zip_files(raw_data_path):
    """
    data/raw/ 디렉토리의 zip 파일들을 압축 해제하는 함수
    """
    zip_files = [f for f in os.listdir(raw_data_path) if f.endswith(".zip")]

    # 압축 해제
    for zip_file in zip_files:
        zip_path = os.path.join(raw_data_path, zip_file)
        extract_path = raw_data_path

        if os.path.exists(zip_path):
            print(f"[INFO] {zip_file} 압축 해제 중...")
            os.makedirs(extract_path, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
            os.remove(zip_path)
            print(f"[INFO] {zip_file} 압축 해제 완료:", extract_path)
        else:
            print(f"[INFO] {zip_file} 파일이 존재하지 않습니다.")
            continue

def download_kaggle_data():
    """
    Kaggle에서 다운로드하여 data/raw 디렉토리에 저장하는 함수
    """
    dataset_name = "denoising-dirty-documents"
    raw_data_path = "data/raw"

    # Kaggle API 인증 확인
    check_kaggle_auth()

    # 저장 경로 생성
    os.makedirs(raw_data_path, exist_ok=True)

    # 데이터 다운로드
    print("[INFO] 데이터 다운로드 중...")
    kaggle.api.competition_download_files(dataset_name, path=raw_data_path, quiet=False)

    # denoising-dirty-documents 압축 해제
    extract_zip_files(raw_data_path)
    
    # train, train_cleaned, test, sampleSubmission 압축 해제
    extract_zip_files(raw_data_path)

    print("[INFO] 데이터 다운로드 및 압축 해제 완료:", raw_data_path)


# 모델 저장 함수
def save_model(model, model_name=None):
    """
    모델 저장 함수
    """
    os.makedirs("models", exist_ok=True)

    # 모델 이름
    if model_name is None:
        model_name = model.__class__.__name__
    
    # 확장자 변경
    if not model_name.endswith(".pth"):
        model_name += ".pth"

    save_path = os.path.join("models", model_name)
    torch.save(model.state_dict(), save_path)
    print(f"Model saved at {save_path}")

# 모델 불러오기 함수
def load_model(model, model_name=None):
    """
    모델 불러오기 함수
    """
    if model_name is None:
        model_name = model.__class__.__name__

    # 확장자 변경
    if not model_name.endswith(".pth"):
        model_name += ".pth"
    
    load_path = os.path.join("models", model_name)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if os.path.exists(load_path):
        model.load_state_dict(torch.load(load_path, weights_only=True, map_location=device))
        print(f"Model loaded from {load_path}")

        # 가중치 업데이트 확인
        # for name, param in model.named_parameters():
        #     if param.requires_grad:
        #         print(f"Parameter: {name} | Size: {param.size()} | Requires Grad: {param.requires_grad}")

    else:
        print(f"No saved model found at {load_path}")
    return model



# 실행
if __name__ == "__main__":
    download_kaggle_data()