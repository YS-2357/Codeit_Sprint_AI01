# RAG 기반 연말정산 문서 질의응답 시스템

이 프로젝트는 LangChain과 Hugging Face 모델을 활용하여,
국세청 연말정산 안내 문서를 기반으로 질의응답이 가능한 Retrieval-Augmented Generation(RAG) 시스템을 구현합니다.

---

## 프로젝트 구조

```
.
├── config/
│   └── config.yaml
├── data/
│   └── 2024년_연말정산_안내.pdf
├── src/
│   ├── loader.py
│   ├── embedder.py
│   ├── llm_setup.py
│   ├── prompt.py
│   └── rag_chain.py
└── main.py
```

---

## 설치 방법

```bash
git clone <repository-url>
cd <project-directory>
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 실행 방법

```bash
python main.py
```

---

## 설정 (경로: config/config.yaml)

```yaml
file_path: "data/2024년_연말정산_안내.pdf"

chunk:
  size: 500
  overlap: 100

embedding_model:
  name: "nlpai-lab/KoE5"

llm_model:
  name: "beomi/KcGPT-2"
  quantization:
    load_in_4bit: true
    use_double_quant: true
    quant_type: "nf4"
    compute_dtype: "float16"
    enable_fp32_offload: true

generation:
  temperature: 0.1
  repetition_penalty: 1.2
  max_new_tokens: 1000
```

---

## 예시 질문

* 연말 정산 때 비거주자가 주의해야 할 점을 알려 줄 수 있어?
* 2024년 개정 세법 중에 월세와 관련한 내용이 있을까?
* 기부금 공제 때 주의해야 할 점은?

---

## 주요 라이브러리

* langchain
* langchain-community
* langchain-core
* langchain-text-splitters
* langchain-huggingface
* transformers
* torch
* sentencepiece
* faiss-cpu
* PyYAML

---
