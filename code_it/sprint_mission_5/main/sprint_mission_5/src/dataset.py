import os
import torch
import argparse
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from torchvision import transforms
from torchvision.transforms import v2
from sklearn.model_selection import train_test_split
from visualization import visualize_dataset_images

####################################################################################################
# 1. 이미지 무결성 검사
def is_valid_image(image_path):
    """
    이미지 무결성 검사 함수
    """
    try:
        with Image.open(image_path) as img:
            img.verify()    # 이미지 무결성 검사
        return True
    except Exception:
        return False

####################################################################################################
# 2. 사용자 정의 데이터셋 클래스
class CustomDataset(Dataset):
    """
    기본 이미지 데이터셋 클래스 (train: paired, val: paired, test: unpaired)
    """
    def __init__(self, input_images, cleaned_images=None, transform=None, phase="train"):
        """
        Args:
            input_images (list): 입력 이미지 파일 리스트
            cleaned_images (list, optional): 타겟 이미지 파일 리스트
            transform (callable, optional): 이미지 변환 함수
        """
        self.input_images = [img for img in input_images if is_valid_image(img)]
        self.cleaned_images = [img for img in cleaned_images if is_valid_image(img)] if cleaned_images else None
        self.transform = transform
        self.phase = phase

        # 변환된 이미지 저장용 디렉토리
        self.processed_dir = f"data/processed/{self.phase}"
        os.makedirs(self.processed_dir, exist_ok=True)

        # 이미지 변환 후 저장
        self.processed_images = []
        for idx, img_path in enumerate(self.input_images):
            save_path = os.path.join(self.processed_dir, f"{idx}_{os.path.basename(img_path)}")

            # 중복 방지
            if os.path.exists(save_path):
                self.processed_images.append(save_path)
                continue

            input_image = Image.open(img_path).convert("RGB")

            # 이미지 변환환
            if self.transform:
                input_image = self.transform(input_image)

            input_image_pil = transforms.ToPILImage()(input_image)
            input_image_pil.save(save_path)

            self.processed_images.append(save_path)

    def __len__(self):
        return len(self.input_images)
    
    def __getitem__(self, idx):
        """
        변환된 이미지 및 타겟 이미지 반환
        """
        input_image = Image.open(self.input_images[idx]).convert("RGB")
        cleaned_image = Image.open(self.cleaned_images[idx]).convert("RGB") if self.cleaned_images else None

        if self.transform:
            input_image = self.transform(input_image)
            cleaned_image = self.transform(cleaned_image) if cleaned_image is not None else None
        
        return (input_image, cleaned_image) if cleaned_image is not None else input_image


####################################################################################################
# 3. 데이터 로더 생성 함수

# 훈련 데이터와 검증 데이터로 분할
def train_val_split(input_dir, target_dir, val_size=2/9, random_state=42):
    """
    훈련 데이터와 검증 데이터로 분할하는 함수
    """
    input_images = sorted(
        [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".png")]
    )
    target_images = sorted(
        [os.path.join(target_dir, f) for f in os.listdir(target_dir) if f.endswith(".png")]
    )
    
    train_files, val_files, cleaned_train, cleaned_val = train_test_split(
        input_images, target_images, test_size=val_size, random_state=random_state
    )
    
    return train_files, val_files, cleaned_train, cleaned_val     



# 학습용 트랜스폼 설정
train_transforms = v2.Compose([
    v2.ToImage(),
    v2.Resize((420, 540)),  
    v2.RandomApply([v2.GaussianBlur(kernel_size=3)], p=0.4),                # 가우시안 블러 (40% 확률 적용)
    v2.RandomApply([v2.ColorJitter(brightness=0.3, contrast=0.3)], p=0.5),  # 밝기 & 대비 조절 (30% 확률 적용)
    v2.Grayscale(num_output_channels=1),  
    v2.ToDtype(torch.float32, scale=True),
])

# 검증용 트랜스폼 설정
val_transforms = v2.Compose([
    v2.ToImage(),
    v2.Resize((420, 540)),  
    v2.Grayscale(num_output_channels=1),
    v2.ToDtype(torch.float32, scale=True),
])

# 시험용 트랜스폼 설정
test_transforms = v2.Compose([
    v2.ToImage(),
    v2.Resize((420, 540)),  
    v2.Grayscale(num_output_channels=1),
    v2.ToDtype(torch.float32, scale=True),
])


# 배치 데이터 변환 함수 (collate_fn)
def collate_fn(batch):
    """
    DataLoader의 배치 데이터 변환 함수
    """
    if isinstance(batch[0], tuple):  # (original, cleaned) 형태인지 확인
        original, cleaned = zip(*batch)
        original = torch.stack(original)
        cleaned = torch.stack(cleaned) if cleaned[0] is not None else None
        return original, cleaned
    else:  # 단일 이미지만 반환되는 경우 (테스트 데이터셋)
        return torch.stack(batch)



# 데이터 로더 설정
def get_dataloaders(batch_size=16, num_workers=0):
    """
    훈련, 검증, 테스트용 DataLoader를 생성하는 함수
    딕셔너리로 반환
    """
    # 학습 데이터셋과 검증 데이터셋 생성
    train_files, val_files, cleaned_train, cleaned_val = train_val_split(
        "data/raw/train", "data/raw/train_cleaned", val_size=2/9
    )

    # 데이터셋 생성
    train_dataset = CustomDataset(train_files, cleaned_train, transform=train_transforms, phase="train")
    val_dataset = CustomDataset(val_files, cleaned_val, transform=val_transforms, phase="val")
    test_files = sorted([os.path.join("data/raw/test", f) for f in os.listdir("data/raw/test") if f.endswith(".png")])
    test_dataset = CustomDataset(test_files, transform=test_transforms, phase="test")

    # DataLoader 생성
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, collate_fn=collate_fn)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, collate_fn=collate_fn)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    return {"train": train_loader, "val": val_loader, "test": test_loader}


####################################################################################################
# 4. 데이터 크기 확인 함수
def check_dataloader_size(dataloaders):
    """
    DataLoader의 데이터 크기 확인 함수
    """
    for phase, loader in dataloaders.items():
        print(f"[INFO] {phase.upper()} Loader size: {len(loader)}")
        batch = next(iter(loader))  # 데이터 로더에서 첫 번째 배치를 가져옴

        # 배치가 튜플이면 (original, cleaned) 형식
        if isinstance(batch, tuple):
            original, cleaned = batch
            print(f"[INFO] {phase.upper()} - Batch size: {original.shape[0]}")
            print(f"[INFO] {phase.upper()} - Original image size: {original.shape}")
            print(f"[INFO] {phase.upper()} - Cleaned image size: {cleaned.shape}")
        else:  # 배치가 단일 텐서 (테스트 데이터셋)
            print(f"[INFO] {phase.upper()} - Batch size: {batch.shape[0]}")
            print(f"[INFO] {phase.upper()} - Image size: {batch.shape}")


####################################################################################################
# 5. dataset.py 실행
if __name__ == "__main__":
    # 데이터 로더 생성
    dataloaders = get_dataloaders(batch_size=16)
    
    # 데이터 크기 확인
    check_dataloader_size(dataloaders)

    # 데이터 시각화
    visualize_dataset_images(dataloaders["train"].dataset, num_images=3, title="Train")
    visualize_dataset_images(dataloaders["val"].dataset, num_images=3, title="Validation")
    visualize_dataset_images(dataloaders["test"].dataset, num_images=3, title="Test")