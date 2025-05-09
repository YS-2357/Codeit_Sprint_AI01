import faiss
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

def build_vector_store(splits, embedding_model_name="nlpai-lab/KoE5"):
    """
    문서 청크에 대한 임베딩을 생성하고 FAISS 벡터 데이터베이스에 저장하여 retriever를 반환합니다.

    Args:
        splits (List[Document]): 청크로 분할된 문서 리스트
        embedding_model_name (str): Hugging Face의 사전학습 임베딩 모델 이름

    Returns:
        VectorStoreRetriever: 검색을 수행할 수 있는 LangChain retriever 객체
    """
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
    dim = len(embeddings.embed_query("hello world"))  # 임베딩 차원 수 추론
    index = faiss.IndexFlatL2(dim)

    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    vector_store.add_documents(splits)
    return vector_store.as_retriever()