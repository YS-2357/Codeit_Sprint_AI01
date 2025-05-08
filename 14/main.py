import yaml
from src.loader import load_and_split
from src.embedder import build_vector_store
from src.llm_setup import load_llm
from src.prompt import get_prompt
from src.rag_chain import build_rag_chain

with open("config/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

docs = load_and_split(config["file_path"], config["chunk"]["size"], config["chunk"]["overlap"])
retriever = build_vector_store(docs, config["embedding_model"]["name"])
llm = load_llm(config["llm_model"]["name"], config["generation"], config["llm_model"]["quantization"])
prompt = get_prompt()
rag_chain = build_rag_chain(retriever, prompt, llm)

questions = [
    "연말 정산 때 비거주자가 주의할 점을 알려 줘.",
    "2024년 개정 세법 중에 월세와 관련한 내용이 있을까?",
    "기부금 공제 때 주의할 점은?"
]

for q in questions:
    print(f"\n질문: {q}")
    print("답변:", rag_chain.invoke(q))