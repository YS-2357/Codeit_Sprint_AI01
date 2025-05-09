from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_clean_pdf(file_path):
    """
    PDF 파일을 로드하고 페이지별 텍스트를 정제하여 반환합니다.

    Args:
        file_path (str): 로컬 PDF 파일 경로

    Returns:
        List[Document]: 정제된 LangChain Document 객체 리스트
    """
    from langchain_community.document_loaders import PyPDFLoader
    import re

    def clean_text(text):
        text = re.sub(r"[\ue000-\uf8ff]", "", text)  # 이상 유니코드 제거
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)  # 줄바꿈 하나는 띄어쓰기로 치환
        text = re.sub(r"[·•・∙ㆍ]+", " ", text)        # 불필요한 점 제거
        return text.strip()

    loader = PyPDFLoader(file_path)
    pages = loader.load()

    for page in pages:
        page.page_content = clean_text(page.page_content)

    return pages


def split_documents(pages, strategy="recursive", chunk_size=500, chunk_overlap=100):
    """
    문서 페이지를 청크로 분할합니다. 전략에 따라 문자 기반 또는 토큰 기반 분할이 가능합니다.

    Args:
        pages (List[Document]): LangChain Document 객체 리스트
        strategy (str): "recursive" 또는 "token" 청킹 전략
        chunk_size (int): 청크 최대 길이
        chunk_overlap (int): 청크 간 중첩 길이

    Returns:
        List[Document]: 청크 단위로 분할된 문서 리스트
    """
    from langchain_text_splitters import (
        RecursiveCharacterTextSplitter,
        TokenTextSplitter,
    )

    if strategy == "recursive":
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    elif strategy == "token":
        splitter = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            model_name="gpt2"  # 기본 tokenizer
        )
    else:
        raise ValueError("Unknown strategy: choose 'recursive' or 'token'")

    return splitter.split_documents(pages)

def load_and_split(file_path, chunk_size=500, chunk_overlap=100, strategy="recursive"):
    """
    PDF 파일을 불러오고 텍스트를 정제한 후, 지정된 전략에 따라 문서를 청크로 분할합니다.

    Args:
        file_path (str): PDF 파일 경로
        chunk_size (int): 청크 크기 (기본값 500)
        chunk_overlap (int): 청크 중첩 크기 (기본값 100)
        strategy (str): 청킹 전략 ("recursive" 또는 "token")

    Returns:
        List[Document]: 청크로 분할된 문서 리스트
    """
    pages = load_and_clean_pdf(file_path)
    splits = split_documents(pages, strategy=strategy, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splits