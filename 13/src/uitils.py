import torch
import wandb

def get_predictions_and_labels(trainer, dataset):
    """
    Hugging Face Trainer를 이용해 예측 결과와 실제 라벨을 반환합니다.

    Args:
        trainer (transformers.Trainer): 평가에 사용할 Trainer 객체
        dataset (datasets.Dataset): 평가할 데이터셋

    Returns:
        Tuple[torch.Tensor, numpy.ndarray]: 예측된 라벨(pred_labels), 실제 라벨(true_labels)
    """
    predictions = trainer.predict(dataset)
    pred_labels = torch.argmax(torch.tensor(predictions.predictions), dim=1)
    true_labels = predictions.label_ids

    return pred_labels, true_labels


from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

def print_acc_and_confusion_matrix(true_labels, pred_labels):
    """
    정확도와 혼동 행렬(Confusion Matrix)을 출력합니다.

    Args:
        true_labels (array-like): 실제 라벨 목록
        pred_labels (array-like): 예측된 라벨 목록

    Returns:
        None
    """
    test_accuracy = accuracy_score(true_labels, pred_labels)
    print(f"🎯 테스트 정확도: {test_accuracy * 100:.2f}%")

    cm = confusion_matrix(true_labels, pred_labels)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["negative", "neutral", "positive"])

    # Plot and capture figure
    fig, ax = plt.subplots(figsize=(6, 6))
    disp.plot(cmap="Blues", values_format='d', ax=ax)
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.show()

    # WandB 이미지로 로깅
    wandb.log({"confusion_matrix": wandb.Image(fig)})
    plt.close(fig)  # 리소스 해제


def print_samples(dataset, true_labels, pred_labels, num_samples=5):
    """
    정답/예측 샘플 및 오분류 샘플을 출력합니다.

    Args:
        dataset (datasets.Dataset): 원본 텍스트가 포함된 테스트 데이터셋
        true_labels (array-like): 실제 라벨 목록
        pred_labels (torch.Tensor): 예측된 라벨 목록
        num_samples (int): 출력할 샘플 수

    Returns:
        None
    """
    label_to_text = {0: "negative", 1: "neutral", 2: "positive"}

    print("\n✅ 예측 결과 샘플:")
    for i in range(num_samples):
        print("📝 원문:", dataset[i]["text"])
        print("✅ 실제:", label_to_text[dataset[i]["label"]], "🔮 예측:", label_to_text[pred_labels[i].item()])
        print("-" * 40)

    print("\n\n❌ 예측이 틀린 샘플:")
    wrong_indices = [i for i, (pred, true) in enumerate(zip(pred_labels, true_labels)) if pred != true]
    for i in wrong_indices[:num_samples]:
        print("📝 원문:", dataset[i]["text"])
        print("✅ 실제:", label_to_text[dataset[i]["label"]], "🔮 예측:", label_to_text[pred_labels[i].item()])
        print("-" * 40)