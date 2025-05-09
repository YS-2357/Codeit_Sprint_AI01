import yaml
from src.loader import load_and_split
from src.embedder import build_vector_store
from src.llm_setup import load_llm
from src.prompt import get_prompt
from src.rag_chain import build_rag_chain

# Config 불러오기
with open("config/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Prompt 템플릿 정의
prompt_template = """
아래에 주어진 맥락을 이용해 질문에 대해 답변해 줘.
주어진 맥락으로 답변이 어려운 상황이라면, 그냥 모른다고 답하면 되고 억지로 답변을 꾸며 내지 마.
최대한 자세하게 답변해 줘.
반드시 한국어로 답변해야 해.

맥락:
{context}

질문:
{question}
"""

# 구성 요소 생성
docs = load_and_split(config["file_path"], config["chunk"]["size"], config["chunk"]["overlap"])
retriever = build_vector_store(docs, config["embedding_model"]["name"])
llm = load_llm(config["llm_model"]["name"], config["generation"], config["llm_model"]["quantization"])
rag_chain = build_rag_chain(retriever=retriever, llm=llm, prompt_template=prompt_template)

# 질문 실행
questions = [
    "연말 정산 때 비거주자가 주의할 점을 알려 줘.",
    "2024년 개정 세법 중에 월세와 관련한 내용이 있을까?",
    "기부금 공제 때 주의할 점은?"
]

for q in questions:
    print(f"\n질문: {q}")
    print("답변:", rag_chain.invoke(q))