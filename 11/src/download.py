import nltk
import os

# 현재 실행 중인 파일의 절대 경로 기준으로 상대경로 설정
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
NLTK_DIR = os.path.join(DATA_DIR, "nltk_data")

# 디렉토리 없으면 생성
os.makedirs(NLTK_DIR, exist_ok=True)

# NLTK 리소스 다운로드 (상대경로)
nltk.download('punkt', download_dir=NLTK_DIR)
nltk.download('punkt_tab', download_dir=NLTK_DIR)

# NLTK가 이 경로에서 리소스를 찾도록 추가
import nltk.data
nltk.data.path.append(NLTK_DIR)