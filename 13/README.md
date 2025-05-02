# 프로젝트 개요: 감성 분류 모델 튜닝 및 성능 비교

본 프로젝트는 한국어 리뷰 데이터를 기반으로 일반 감성 분류(General Polarity Classification) 및 세부 항목 감성 분류(Aspect-based Sentiment Classification)를 수행하기 위한 일련의 실험을 포함합니다. 다양한 Parameter-Efficient Fine-Tuning(PEFT) 기법을 적용하여 학습 파라미터 수, 정확도, 편향성 등의 관점에서 성능을 비교하였습니다.

## ✅ 실험 결과 요약

## ① General Sentiment Classification 기준 (1–4일차)

| 모델 | 튜닝 방식 | 학습 파라미터 비율 | 테스트 정확도 | 주요 특징 |
| --- | --- | --- | --- | --- |
| **beomi/KcELECTRA-base** | Full Fine-tuning | 100.00% | **89.25%** | 전체 학습 대비 Layer-wise와 큰 차이 없음 |
| 〃 | Layer-wise (`layer.9` 이상) | 20.04% | 89.36% | 중상위 계층만 학습해도 성능 확보 |
| 〃 | Layer-wise (`classifier`만) | 0.54% | 89.13% | 거의 동등한 성능 |
| 〃 | LoRA | 0.64% | 84.42% | attention 중심 학습, 표현 조정 한계 |
| 〃 | PromptTuning | 0.007% | 19.27% | 모든 예측이 neutral |
| 〃 | PrefixTuning | 0.17% | 68.76% | positive 편향향 |
| 〃 | AdaLoRA | 0.74% | 68.78% | positive 편향향, classifier 영향 미미 |
| 〃 | PromptEncoder | 0.21% | 12.34% | negative 편향향, 거의 무작위 |
| 〃 | IA3 (2 epoch) | 0.62% | **81.18%** | FFN scaling 적용으로 개선됨 |
| **google/electra-base-discriminator** | LoRA | 0.64% | 68.78% | 한국어 미학습, positive 편향 |
| **bert-base-multilingual-cased** | LoRA | 0.06% | 73.41% | shallow 표현 한계로 감성 구분 어려움 |

---

## ② Aspect-based Sentiment Classification 기준 (5일차)

| 모델 | 튜닝 방식 | 학습 파라미터 비율 | 테스트 정확도 | 주요 특징 |
| --- | --- | --- | --- | --- |
| **beomi/KcELECTRA-small-v2022** | Full Fine-tuning | 100.00% | **90.17%** | Aspect 감정 분류에서 가장 뛰어난 성능 |
| 〃 | LoRA | 0.62% | 77.80% | neutral 감성 미분류, 긍/부정 편향 |
| 〃 | AdaLoRA + classifier 추가 학습 | 0.84% | 69.61% | positive 편향 지속 |

---

## 📆 실험 일지

1. 1일차
    - 토큰화된 데이터셋 구현
    - 완디비 로깅
    - 모델 학습 및 평가가 정상적으로 작동됨을 확인
    - GPU제약으로 인해 CPU로만 구동함. 1에폭에 대략 4~5시간 정도 걸림
    
    → CPU 기반 환경으로 인해 전체 파라미터를 업데이트하는 Full Fine-tuning의 학습 속도가 매우 느림. 따라서 이후 실험에서는 부분 학습이나 파라미터 효율적 튜닝이 중심이 됨.
2. 2일차
    - LoRA Config 없이 수동 파라미터 고정 학습방식 추가
    - 모델 저장 및 불러오기 추가
    - 모델 중간층부터 하위로 점진적으로 파라미터를 고정하며 학습하는 Layer-wise Fine-tuning 전략 시도
    - GPT는 Layer-wise Unfreezing 전략이라 소개함
        - Layer-wise Fine-tuning 또는 Progressive Unfreezing
        - ULMFiT (Howard & Ruder, 2018)에서 처음 체계적으로 소개됨
        - 일반적으로는 가장 하위 레이어부터 상위로 점진적으로 학습하는 구조지만, 상위부터 내려가는 전략도 가능
    - 7번 레이어부터 분류기까지 순차적으로 Freeze
        - "encoder.layer.7":
            - trainable params: 36,032,259 || all params: 109,083,651 || trainable%: 33.0318
            - 테스트 정확도: 88.61%
        - "encoder.layer.8":
            - trainable params: 28,944,387 || all params: 109,083,651 || trainable%: 26.5341
            - 테스트 정확도: 89.27%
        - "encoder.layer.9":
            - trainable params: 21,856,515 || all params: 109,083,651 || trainable%: 20.0365
            - 테스트 정확도: 89.36%
        - "encoder.layer.10"
            - trainable params: 14,768,643 || all params: 109,083,651 || trainable%: 13.5388
            - 테스트 정확도: 89.25%
        - "encoder.layer.11"
            - trainable params: 7,680,771 || all params: 109,083,651 || trainable%: 7.0412
            - 테스트 정확도: 89.21%
        - "classifier"
            - trainable params: 592,899 || all params: 109,083,651 || trainable%: 0.5435
            - 테스트 정확도: 89.13%
        
        → beomi/KcELECTRA-base는 encoder.layer.9 이상부터 classifier와 연결이 강하게 형성됨. 해당 계층까지만 학습해도 테스트 정확도 상한선에 거의 도달. 하위 계층은 한국어 토크나이즈에 특화된 pretraining feature를 포함하고 있어 고정해도 성능 손실이 거의 없음.
    - LoRA방식
        - trainable params: 703,491 || all params: 109,787,142 || trainable%: 0.6408
        - 테스트 정확도: 84.42%
    
        → LoRA는 attention query/key/value projection에만 랭크 분해된 학습 가능한 저차 파라미터를 삽입함. classification head와 직접 연결되지 않으며, feature representation의 세밀한 수정이 어려워 상대적으로 낮은 성능을 보임.
3. 3일차
    - Full Fine-tuning(3 epochs)
        - trainable params: 109,083,651 || all params: 109,083,651 || trainable%: 100.0000
        - 테스트 정확도: 89.25%

        → 전체 파라미터를 학습함에도 layer-wise 방식과 비교해 테스트 정확도 차이가 없음. 이미 중상위 계층만 업데이트해도 충분히 분류 경계가 조정되는 구조임을 의미.
    - 다른 모델 실험/ google/electra-base-discriminator
        - trainable params: 703,491 || all params: 110,188,038 || trainable%: 0.6384
        - 테스트 정확도: 68.78%
        - 모든 데이터를 Postive로 분류함. 성능이 좋지 않음을 확인함

        → 사전학습시 한국어 데이터가 포함되지 않음. 문법적/형태소 처리에 실패하고, class imbalance처럼 작동.
    - 다른 모델 실험/ google-bert/bert-base-multilingual-cased
        - trainable params: 112,899 || all params: 177,968,646 || trainable%: 0.0634
        - 테스트 정확도: 73.41%

        → mBERT는 각 언어에 대한 shallow한 표현을 갖고 있어 세밀한 감성 차이를 포착하지 못함.
    - 다른 튜닝/ PromptTuningConfig
        - trainable params: 7,680 || all params: 109,091,331 || trainable%: 0.0070     
        - 테스트 정확도: 19.27%
        - 모든 데이터를 Neutral로 분류함. 성능이 좋지 않음.

        → 매우 작은 가상 프롬프트만 학습됨. backbone은 freeze된 채라 기존 모델의 편향을 극복할 수 없음.
    - 다른 튜닝/ PrefixTuningConfig
        - trainable params: 184,320 || all params: 109,267,971 || trainable%: 0.1687
        - 테스트 정확도: 68.76%
        - 모든 데이터를 Postive로 분류함. 성능이 좋지 않음

        → 입력 전 위치에 prefix embedding만 삽입되므로, 분류 경계 이동이 제한적. 사전학습된 긍정 편향을 유지함.
4. 4일차
    - 다른 튜닝/ AdaLoraConfig
        - trainable params: 814,227 || all params: 109,897,914 || trainable%: 0.7409
        - 테스트 정확도: 68.78%
        - 모든 데이터를 Postive로 분류함. 성능이 좋지 않음

        → 적응적 dropout 기반 가중치 조절이지만, attention 중심 구조에 치우침. 분류기 head까지 영향을 주지 못함.
    - 다른 튜닝/ PromptEncoderConfig
        - trainable params: 229,376 || all params: 109,313,027 || trainable%: 0.2098
        - 테스트 정확도: 12.34%
        - 모든 데이터를 Negative로 분류함. 성능이 좋지 않음

        → 프롬프트 인코더 embedding이 backbone 구조와 제대로 통합되지 못했거나 학습 불안정. 거의 무작위에 가까운 결과.
    - 다른 튜닝/ IA3Config
        - trainable params: 676,611 || all params: 109,761,030 || trainable%: 0.6164
        - 테스트 정확도: 76.79%
        - 2 epochs/ 테스트 정확도: 81.18%

        → 각 layer의 FFN에 스케일링 벡터를 추가함으로써 비교적 효과적으로 조정됨. 그러나 Full Fine-tuning에는 미치지 못함.
5. 5일차
    - GeneralPolarity가 아닌 Aspects별 SentimentPolarity로 분류를 시도
        - | 겨울에는 가루 보다는 이런 액체가 좋기는 하더라구요. 세탁이 더 깨끗하게 된다는 느낌이 없어서 실망이네요. [SEP] 제형 | 2 |

        → 입력 구조가 단순한 전체 문장에서, 특정 Aspect에 주의를 집중하는 형태로 변경됨. 입력 문장 길이는 비슷하지만, 의미 해석은 더 복잡함. 모델이 attention head나 classifier에서 세밀한 의미 구분을 수행해야 하므로 난이도 증가.
    - 모델: beomi/KcELECTRA-small-v2022/ 튜닝: LoraConfig
        - trainable params: 103,427 || all params: 16,702,086 || trainable%: 0.6192
        - 테스트 정확도: 77.80%
        - neutral이 없는 오직 긍정/부정만을 예측함.

        → LoRA는 attention projection에만 low-rank 파라미터를 삽입하는 구조로 표현 공간 조정 범위가 좁음. Aspect-level에서의 중립 감성 구분처럼 섬세한 decision boundary 조정이 어렵고, 결국 긍정/부정에 쏠리는 결과가 발생.
    - 모델: beomi/KcELECTRA-small-v2022/ 튜닝: AdaLoraConfig + classifier 추가 학습
        - trainable params: 140,435 || all params: 16,739,130 || trainable%: 0.8390
        - 테스트 정확도: 69.61%
        - 대부분의 데이터를 Positive로 분류하며 편향 발생

        → classifier 학습을 포함했음에도 backbone 레이어 학습 부족으로 인해 감성 표현 구분력이 충분히 개선되지 못함.
    - 모델: beomi/KcELECTRA-small-v2022/ Full Fine-tuning
        - trainable params: 16,598,659 || all params: 16,598,659 || trainable%: 100.0000
        - 테스트 정확도: 90.17%

        → 전체 모델 파라미터를 학습한 결과 가장 높은 정확도 달성. backbone 전체를 학습함으로써 Aspect 감성 분류 태스크에서 필요한 섬세한 표현 조정까지 가능한 상태가 됨.

---

## 폴더 구조

```
13/
├── data/           # 원본 및 전처리된 리뷰 데이터 저장 디렉터리
├── notebooks/      # 실험용 Jupyter 노트북 파일
├── results/        # 결과 파일 및 시각화 자료
├── src/            # 주요 코드 모듈 (데이터 로더, 모델, 학습 루프 등)
│   ├── loader.py       # 데이터프레임 생성 및 HuggingFace Datasets 구성
│   ├── model.py        # 사전학습 모델 불러오기 및 분류기 헤드 설정
│   ├── train.py        # 학습 및 평가 함수
│   └── uitils.py       # 설정, 로깅, 시드 고정 등 유틸리티 함수
├── wandb/          # W&B 로그 파일 저장 디렉터리
├── .gitignore      # Git 무시 설정
└── main.py         # 전체 학습 파이프라인을 실행하는 메인 스크립트
```

## 주요 내용

### 1. 태스크 유형
- General Sentiment Classification (전체 문장 기준 감성)
- Aspect-based Sentiment Classification (문장 내 세부 항목 기준 감성)

### 2. 실험 모델
- `beomi/KcELECTRA-small-v2022`
- `google/electra-base-discriminator`
- `google-bert/bert-base-multilingual-cased`

### 3. 튜닝 기법 비교
- Full Fine-tuning
- Layer-wise Freezing
- LoRA, AdaLoRA, IA3, Prompt/Prefix Tuning

### 4. 실험 환경
- CPU 기반 제한된 연산 환경에서 수행
- 평균 에폭당 4~5시간 소요
- Weights & Biases(wandb) 로깅 사용

## 실행 방법

```bash
python main.py
```

설정값은 `data_config`, `model_config`, `train_config` 등 별도의 설정 딕셔너리 또는 YAML 파일로 관리되며, `src/` 내 모듈에서 불러옵니다.

## 결과 요약
- Full Fine-tuning이 가장 높은 정확도(90.17%) 기록
- 중립 감성 분류는 일부 PEFT 모델에서 제대로 수행되지 않음
- Layer-wise Fine-tuning은 파라미터 수를 대폭 줄이면서도 유사한 성능 확보 가능

## 참고
- 사전학습 모델: Hugging Face Transformers
- 데이터셋 구조: JSON 기반 사용자 리뷰
- 평가 기준: 정확도 및 클래스 편향 분석

---

본 프로젝트는 파인튜닝 및 프롬프트 최적화 없이 다양한 튜닝 기법이 실제로 성능에 미치는 영향을 비교 분석함으로써, 자원이 제한된 환경에서도 효율적인 감성 분류 모델을 구현하는 방법을 탐색합니다.

---

## src 내용

```
loader.py 구조 요약

📁 src/
└── 📄 loader.py
    ├── 🔧 get_df(data_dir, task_type="general")
    │   ├── 역할: JSON 파일에서 리뷰 데이터를 불러와 `text`, `label`을 구성한 DataFrame 생성
    │   ├── 입력: 
    │   │   ├── data_dir (str): JSON 파일들이 저장된 디렉토리 경로
    │   │   └── task_type (str): "general" 또는 "aspect" 감성 분류 방식 선택
    │   └── 출력: pd.DataFrame (text, label 컬럼 포함)
    │       └── label: [-1, 0, 1] → [0, 1, 2] 정규화
    │
    ├── 🔧 get_datasets(df, config)
    │   ├── 역할: DataFrame을 Hugging Face Dataset 형식으로 분할(train/val/test)
    │   ├── 입력:
    │   │   ├── df (pd.DataFrame): 전체 데이터프레임
    │   │   └── config (dict): 분할 비율 및 seed 설정
    │   └── 출력: dict of Dataset → {"train", "val", "test"}
    │
    ├── 🔧 get_tokenizer(config)
    │   ├── 역할: Hugging Face 모델 이름을 기반으로 토크나이저 로드
    │   ├── 입력: config["model_name"] (str)
    │   └── 출력: AutoTokenizer 객체
    │
    └── 🔧 tokenize_datasets(datasets, tokenizer, config)
        ├── 역할: Dataset 객체를 토크나이즈하고 PyTorch 텐서로 변환
        ├── 입력:
        │   ├── datasets (dict): {"train", "val", "test"} Dataset
        │   ├── tokenizer: 사전학습된 토크나이저 객체
        │   └── config (dict): 입력/라벨 컬럼명, max_length 등
        └── 출력: dict of Tokenized Dataset → PyTorch 텐서 형식 + 선택적 text 유지
```

---

```
model.py 구조 요약

📁 src/
└── 📄 model.py
    ├── 🔧 get_model(config, peft_config=None)
    │   ├── 역할: 사전학습된 분류 모델 로드 및 선택적 파인튜닝 레이어 설정, PEFT(LoRA) 적용
    │   ├── 입력:
    │   │   ├── config["model_name"]: 사용할 Hugging Face 모델 이름
    │   │   ├── config["train_layers"]: 학습할 파라미터 이름 포함 리스트 (선택)
    │   │   └── peft_config: LoRA 설정 객체 (선택)
    │   └── 출력: PEFT가 적용된 분류용 모델 객체
    │
    ├── 🔧 get_training_args(config)
    │   ├── 역할: Hugging Face Trainer를 위한 학습 인자(TrainingArguments) 생성
    │   ├── 입력:
    │   │   ├── output_dir, batch_size, num_epochs, grad_accum 등 config 요소
    │   └── 출력: transformers.TrainingArguments 객체
    │
    ├── 🔧 create_trainer(model, training_args, tokenized_datasets, mode='train')
    │   ├── 역할: Trainer 객체 생성 (학습 또는 평가 모드에 따라 동작)
    │   ├── 입력:
    │   │   ├── model: 분류 모델
    │   │   ├── training_args: 학습 설정
    │   │   ├── tokenized_datasets: train/val/test로 나뉜 Dataset 딕셔너리
    │   │   └── mode: 'train' 또는 'eval'
    │   └── 출력: transformers.Trainer 객체
    │       └── accuracy, precision, recall, f1 등 macro-average 평가 지표 포함
    │
    └── 🔧 get_device()
        ├── 역할: 현재 사용 가능한 연산 디바이스 확인
        └── 출력: torch.device 객체 ("cuda" 또는 "cpu")
```

---

```
utils.py 구조 요약

📁 src/
└── 📄 utils.py
    ├── 🔧 check_trainable_parameters(model)
    │   ├── 역할: 모델의 각 파라미터가 학습 가능한지 여부를 출력
    │   ├── 입력: model (transformers.PreTrainedModel)
    │   └── 출력: 콘솔 출력 (이름, requires_grad 상태)

    ├── 🔧 get_predictions_and_labels(trainer, dataset)
    │   ├── 역할: Trainer를 사용해 예측값과 실제 정답값 반환
    │   ├── 입력:
    │   │   ├── trainer: Hugging Face Trainer 객체
    │   │   └── dataset: 평가용 Dataset
    │   └── 출력:
    │       ├── pred_labels (torch.Tensor): 예측된 라벨
    │       └── true_labels (np.ndarray): 실제 라벨

    ├── 🔧 print_acc_and_confusion_matrix(true_labels, pred_labels)
    │   ├── 역할: 테스트 정확도 및 혼동 행렬(Confusion Matrix) 시각화
    │   ├── 입력:
    │   │   ├── true_labels: 정답 라벨
    │   │   └── pred_labels: 예측 라벨
    │   └── 출력:
    │       ├── 정확도 출력
    │       ├── matplotlib로 혼동 행렬 시각화
    │       └── wandb에 confusion matrix 이미지 로깅

    └── 🔧 print_samples(dataset, true_labels, pred_labels, num_samples=5)
        ├── 역할: 예측/실제 라벨 비교 샘플 및 오분류 샘플 출력
        ├── 입력:
        │   ├── dataset: 평가 대상 Dataset (원문 텍스트 포함)
        │   ├── true_labels: 실제 라벨
        │   ├── pred_labels: 예측 라벨
        │   └── num_samples: 출력할 샘플 개수
        └── 출력:
            ├── 맞춘 샘플 일부 출력
            └── 틀린 샘플 일부 출력
```

---

```
train.py 구조 요약

📁 src/
└── 📄 train.py
    └── 🔧 run_train_and_eval(data_config, trainer_config, module_config=None)
        ├── 역할:
        │   ├── 데이터 불러오기, 토크나이즈, 모델 로딩, 학습 및 평가까지 전체 파이프라인 수행
        │   ├── LoRA 또는 기타 PEFT 설정 및 resume checkpoint 기능 포함
        │   ├── W&B 로깅 및 모델 저장/재개 지원
        │
        ├── 입력:
        │   ├── data_config (dict): 데이터 및 모델 관련 설정
        │   ├── trainer_config (dict): 학습 관련 설정 (output_dir, epochs 등)
        │   └── module_config (LoRAConfig 또는 dict, optional): PEFT 설정 또는 layer freezing 등 추가 설정
        │
        ├── 주요 단계:
        │   ├── ✅ 데이터 로딩 및 전처리
        │   │   ├── get_df() → get_datasets() → get_tokenizer() → tokenize_datasets()
        │   ├── ✅ 저장 경로 및 W&B 초기화
        │   ├── ✅ 모델 로딩 및 선택적 checkpoint 불러오기
        │   ├── ✅ 파라미터 요약 출력 (trainable/all 비율 계산)
        │   ├── ✅ TrainingArguments 생성 → Trainer 객체 생성
        │   ├── ✅ 학습 시작 (`trainer.train()`)
        │   ├── ✅ 모델 저장 (`trainer.save_model()`)
        │   ├── ✅ 평가 수행
        │   │   ├── create_trainer(mode='eval') → get_predictions_and_labels()
        │   │   ├── print_acc_and_confusion_matrix()
        │   │   └── print_samples()  
        │
        └── 출력:
            └── model: 학습 완료된 모델 객체
```

---