# 📘 문서 요약 모델 구현 - 정영선 팀

## ✅ 프로젝트 개요
- Hugging Face Transformers를 활용한 한국어 문서 요약 모델 구현
- 데이터 전처리 → 모델 구성 및 학습 → 요약 생성 및 평가 전 과정을 포함하는 파이프라인 구축

## ✅ 사용 데이터셋
- **출처**: AI Hub 한국어 문서요약 텍스트
- **도메인**: 법률 (train_original_law.json / valid_original_law.json)
- **크기**: 학습 약 24,000개 / 검증 약 3,000개
- **전처리 방식**:
  - 문장 병합하여 전체 문서(`full`) 생성
  - 요약문(`summary`)은 추상적 요약의 첫 문장 사용
  - 특수 전처리 없음
  - SentencePiece BPE tokenizer 사용

## ✅ 모델 구성 및 학습
- Transformer 기반 Encoder-Decoder 구조 (MiniBART 커스텀 구조)
- PositionalEncoding, TransformerEncoder, TransformerDecoder, Gated FFN 적용
- SentencePiece tokenizer로 입력 전처리
- 입력: `[BOS] full [EOS]`, 출력: `[BOS] summary [EOS]`
- Optimizer: AdamW
- Scheduler: CosineAnnealingLR
- Loss: CrossEntropyLoss / NLLLoss
- 정규화, 드롭아웃, gradient clipping 적용

## ✅ 평가 방식
- 평가 지표: Accuracy, Perplexity, Loss
- Sample-level 및 Corpus-level 평가 모두 병행
- 검증 도중 `NaN loss` 방지를 위해 `safe_validate_one_epoch` 함수 적용

## ✅ 실험 기록 및 로깅
- `wandb`를 사용한 학습 및 평가 로깅
- 하이퍼파라미터 스윕(Bayesian 포함) 수행: learning rate, dropout, num_layers 등
- 모델 학습 속도, 에폭당 처리량, 추론 시간 등도 기록

## ✅ 주요 이슈 및 해결 전략
- `NaN` loss 발생 → logits 확인 (`logits.has_nan` 체크)
- Loss 안정화를 위한 gradient clipping, dropout, label smoothing 고려
- SentencePiece 모델 성능 비교 및 tokenizer 훈련 corpus 튜닝

## ✅ 정리
- LLM 사전학습이 잘 되어 있을 경우, 파인튜닝은 소수 파라미터(예: projection)만으로도 성능 확보 가능
- RAG 구조, LangChain 프레임워크 등과의 연동 가능성도 실험 중 고려
- 향후 법률 QA 태스크에 응용할 수 있는 기초 구조 확보