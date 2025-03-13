import os
import matplotlib.pyplot as plt
import torch


# 데이터셋 이미지 시각화 함수 (훈련, 검증, 테스트 데이터셋)
def visualize_dataset_images(dataset, num_images=3, title="Sample Images"):
    """
    주어진 데이터셋에서 샘플 이미지를 출력하는 함수
    """
    fig, axes = plt.subplots(num_images, 2 if isinstance(dataset[0], tuple) else 1, figsize=(10, num_images * 3))

    for i in range(num_images):
        if isinstance(dataset[i], tuple):   # 훈련/검증 데이터 (입력 + 정답)
            input_image, target_image = dataset[i]
            axes[i, 0].imshow(input_image.squeeze(0), cmap="gray")
            axes[i, 0].set_title(f"{title} - Input {i+1}")
            axes[i, 0].axis("off")

            axes[i, 1].imshow(target_image.squeeze(0), cmap="gray")
            axes[i, 1].set_title(f"{title} - Target {i+1}")
            axes[i, 1].axis("off")
        else:                               # 테스트 데이터 (입력만)
            axes[i].imshow(dataset[i].squeeze(0), cmap="gray")
            axes[i].set_title(f"{title} {i+1}")
            axes[i].axis("off")

    plt.tight_layout()
    plt.show()


# 훈련 결과 시각화 함수
def visualize_train_results(original, cleaned, outputs, num_samples=5, title="Sample Images"):
    """
    검증 데이터 원본, 정답, 모델 출력을 비교하는 시각화 함수
    """
    num_samples = min(num_samples, original.shape[0])
    fig, axes = plt.subplots(num_samples, 3, figsize=(15, num_samples * 3))

    for i in range(num_samples):
        # 첫 번째 열: 원본 이미지
        axes[i, 0].imshow(original[i].cpu().numpy().squeeze(), cmap='gray')
        axes[i, 0].set_title(f"Original {i+1}", fontsize=10)
        axes[i, 0].axis('off')

        # 두 번째 열: 정답 이미지
        axes[i, 1].imshow(cleaned[i].cpu().numpy().squeeze(), cmap='gray')
        axes[i, 1].set_title(f"Cleaned {i+1}", fontsize=10)
        axes[i, 1].axis('off')

        # 세 번째 열: 모델 출력 이미지
        axes[i, 2].imshow(outputs[i].detach().cpu().numpy().squeeze(), cmap='gray')
        axes[i, 2].set_title(f"Output {i+1}", fontsize=10)
        axes[i, 2].axis('off')
    
    plt.tight_layout()
    plt.show()


# 시험 결과 시각화 함수
def visualize_test_images(images, outputs, num_samples=5, title="Sample Images"):
    """
    테스트 데이터 원본과 모델 출력을 비교하는 시각화 함수
    """
    num_samples = min(num_samples, images.shape[0])
    fig, axes = plt.subplots(num_samples, 2, figsize=(10, num_samples * 3))

    for i in range(num_samples):
        # 첫 번째 열: 원본 테스트 이미지
        axes[i, 0].imshow(images[i].cpu().numpy().squeeze(), cmap='gray')
        axes[i, 0].set_title(f"Original {i+1}", fontsize=10)
        axes[i, 0].axis('off')

        # 두 번째 열: 모델 출력 이미지
        axes[i, 1].imshow(outputs[i].cpu().numpy().squeeze(), cmap='gray')
        axes[i, 1].set_title(f"Output {i+1}", fontsize=10)
        axes[i, 1].axis('off')
    
    plt.tight_layout()
    plt.show()