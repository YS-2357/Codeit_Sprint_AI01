# 🧠 Text Classification with Custom Embeddings (Sprint Mission 10)

이 프로젝트는 **20 Newsgroups 데이터셋**을 활용한 뉴스 텍스트 분류 모델을 구현하는 NLP 미션입니다.  
사용자가 선택한 임베딩 방식 (`Word2Vec`, `FastText`, `GloVe`)과 모델 구조 (`EmbeddingLSTM`, `AttnBiLSTM`, `FinalBiLSTM`)에 따라 유연하게 실험을 구성할 수 있도록 설계되어 있습니다.

---

## 📌 주요 기능

- ✅ 20 Newsgroups 데이터 자동 다운로드 및 전처리
- ✅ Word2Vec, FastText, GloVe 임베딩 지원
- ✅ LSTM 기반 분류 모델 구조 선택 가능
- ✅ `wandb`를 통한 학습 모니터링 및 성능 로깅
- ✅ 모든 실험은 재현 가능하도록 설정 가능 (`config` 기반 제어)

---

## 📁 프로젝트 구조

```
sprint_mission10/
├── data/                # 데이터 및 임베딩 저장 (깃에서 무시됨)
├── models/              # 학습된 모델 저장 경로
├── src/                 # 주요 모듈 코드
│   ├── data.py          # 데이터 로딩 및 전처리
│   ├── model.py         # 모델 아키텍처 정의
│   ├── train.py         # 학습 및 평가 루프
│   ├── utils.py         # 유틸리티 함수
│   └── log.py           # wandb 로깅 관련
├── main.py              # 메인 실행 스크립트
└── requirements.txt     # 필요 라이브러리 명세
```

---

## 🚀 실행 방법

1. **패키지 설치**

```bash
pip install -r requirements.txt
```

2. **NLTK 리소스 다운로드 자동 처리됨**

프로그램이 처음 실행되면 필요한 `nltk` 리소스 (`stopwords`, `punkt`)는 자동으로 `data/nltk_data`에 다운로드됩니다.

3. **모델 실행 (기본 설정)**

```bash
python main.py
```

- 기본 설정은 Word2Vec + EmbeddingLSTM 입니다.
- 학습 완료 모델은 `models/` 디렉토리에 저장됩니다.

4. **모델/임베딩 설정 바꾸기**

`main.py` 하단에서 다음 변수만 바꾸면 됩니다:

```python
embedding_name = "GloVe"           # Word2Vec, FastText, GloVe
model_name = "AttnBiLSTM"          # EmbeddingLSTM, AttnBiLSTM, FinalBiLSTM
```

---

## 🧪 예시 결과 (WandB 없이 실행 가능)

```bash
[Data Ready] Train: 13173 | Val: 1466 | Test: 3663
[Epoch 1/10] Train Loss: 0.74 | Train Acc: 0.82 | Val Acc: 0.84
[Final Evaluation] Test Acc: 0.86 | Test Precision: 0.85 | Test Recall: 0.85 | Test F1: 0.85
```

---

## ✅ 참고 사항

- `data/`, `models/`, `wandb/` 디렉토리는 `.gitignore`에 의해 Git 업로드에서 제외됩니다.
- Windows 환경에서 symlink 권한 오류가 발생할 수 있으므로, wandb 저장은 제외됩니다.

---

## 🙋‍♀️ 기여자

- 정영선 (프로젝트 매니저 및 전체 시스템 통합 설계)