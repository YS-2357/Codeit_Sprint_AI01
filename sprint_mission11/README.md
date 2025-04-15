# 🧐 Korean-to-English Neural Machine Translation (K2E NMT)

이 프로젝트는 한국어 문장을 영어로 번역하는 RNN 기반 Seq2Seq 모델을 구현하고, BLEU 점수 기반 성능을 평가합니다. 학원에는 Bahdanau Attention이 적용되었고, Optuna로 하이퍼파리터 튜닝이 가능합니다.

---

## 📁 프로젝트 구조

```
.
├── data/                    # 원시 및 전처리 데이터, vocab 저장
├── checkpoints/            # 모델 체크포인트 저장
├── src/                    # 주요 코드 파일
│   ├── train.py            # 학원 및 평가 룰티
│   ├── model.py            # Encoder/Decoder 및 Attention
│   ├── dataset.py          # DataLoader 및 전처리
│   └── utils.py            # 보조 유틸리티 함수
├── main.py                 # 실행 짹짹점
├── requirements.txt        # 필요 라이브러리 목록
└── README.md               # 프로젝트 문서
```

---

## 🚀 실행 방법

### 1. 환경 설정
```bash
pip install -r requirements.txt
```

### 2. 데이터 준비
- `config["train_json_path"]` 및 `valid_json_path` 위치에 JSON 파일 배치
- 각 항목에 `ko`, `en`, `domain`, `subdomain`, `word_count_ko`, `word_count_en` 필드들 포함

### 3. 실행
```bash
python main.py
```

---

## ⚙️ 모델 설정

- Encoder: GRU 기반, multi-layer, bidirectional 아니면
- Decoder: GRU + Bahdanau Attention
- Tokenizer: `Okt` (ko), `nltk.word_tokenize` (en)
- Loss: CrossEntropyLoss (ignore_index=PAD)
- Evaluation: BLEU Score (nltk, smoothing 없이)

---

## 🔍 주요 기능

- ✅ Bahdanau Attention 기반 Seq2Seq 모델
- ✅ 데이터 전처리 자동화 (길이 기반 필터링 포함)
- ✅ Stratified Split + Weighted Sampling 지원
- ✅ wandb 연동으로 로그 및 번역 샘플 기록 가능
- ✅ Optuna 기반 하이퍼파리터 탐색 가능
- ✅ 학원 후 BLEU 점수 및 예제 문장 Í9c력

---

## 🧪 사용 라이브러리

- PyTorch
- konlpy
- nltk
- tqdm
- optuna
- wandb

---

## 👤 작성자

정영선 (Youngsun Joung)  
📧 joungyoungsun20@gmail.com