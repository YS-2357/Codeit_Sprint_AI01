import faiss
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

def build_vector_store(docs, embedding_model_name: str):
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
    dim = len(embeddings.embed_query("테스트"))
    index = faiss.IndexFlatL2(dim)
    vector_store = FAISS(embedding_function=embeddings, index=index, docstore=InMemoryDocstore(), index_to_docstore_id={})
    vector_store.add_documents(docs)
    return vector_store.as_retriever()