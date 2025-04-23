from gensim.models import Word2Vec, FastText
from sklearn.datasets import fetch_20newsgroups
from sklearn.model_selection import train_test_split
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import urllib.request
import numpy as np
import zipfile
import os

# 현재 파일 기준이 아니라 루트 기준으로 이동
# 예: .../Codeit_sprint_AI01/code_it/sprint_mission10/data
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
NLTK_DATA_DIR = os.path.join(DATA_DIR, "nltk_data")

# 폴더 생성
os.makedirs(NLTK_DATA_DIR, exist_ok=True)

# NLTK 경로 등록
nltk.data.path.append(NLTK_DATA_DIR)

# 경로 유틸 함수
def get_data_path(filename):
    return os.path.join(DATA_DIR, filename)

# 필요한 리소스 다운로드 (지정된 디렉토리로)
nltk.download('punkt', download_dir=NLTK_DATA_DIR)
nltk.download('punkt_tab', download_dir=NLTK_DATA_DIR)
nltk.download('stopwords', download_dir=NLTK_DATA_DIR)

def load_dataset(config):
    remove_items = []
    if config.get("remove_headers", False):
        remove_items.append("headers")
    if config.get("remove_footers", False):
        remove_items.append("footers")
    if config.get("remove_quotes", False):
        remove_items.append("quotes")

    news_data = fetch_20newsgroups(
        subset='all',
        remove=tuple(remove_items),
        data_home=DATA_DIR
    )
    texts, labels = news_data.data, news_data.target
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts, labels, test_size=config["test_split"], random_state=42
    )
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        train_texts, train_labels, test_size=config["val_split"], random_state=42
    )
    return train_texts, val_texts, test_texts, train_labels, val_labels, test_labels

def clean_texts(texts):
    stop_words = set(stopwords.words('english'))
    def clean_text(text):
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = text.split()
        tokens = [word for word in tokens if word not in stop_words]
        return ' '.join(tokens)
    return [clean_text(text) for text in texts]

def remove_empty(texts, labels):
    filtered_texts, filtered_labels = [], []
    for t, l in zip(texts, labels):
        if t.strip():
            filtered_texts.append(t)
            filtered_labels.append(l)
    return filtered_texts, filtered_labels

def tokenize_texts(texts):
    return [word_tokenize(text) for text in texts]


import numpy as np
from gensim.models import Word2Vec, FastText

def build_word2vec(sentences, config):
    model = Word2Vec(
        sentences=sentences,
        vector_size=config["embedding_dim"],
        window=5,
        min_count=1,
        sg=1
    )
    word2idx = {word: idx + 1 for idx, word in enumerate(model.wv.index_to_key)}
    embedding_matrix = np.zeros((len(word2idx) + 1, config["embedding_dim"]))
    for word, idx in word2idx.items():
        embedding_matrix[idx] = model.wv[word]
    return model, word2idx, embedding_matrix


def build_fasttext(sentences, config):
    model = FastText(
        sentences=sentences,
        vector_size=config["embedding_dim"],
        window=5,
        min_count=1,
        sg=1
    )
    word2idx = {word: idx + 1 for idx, word in enumerate(model.wv.index_to_key)}
    embedding_matrix = np.zeros((len(word2idx) + 1, config["embedding_dim"]))
    for word, idx in word2idx.items():
        embedding_matrix[idx] = model.wv[word]
    return model, word2idx, embedding_matrix


# GloVe 다운로드 및 추출 함수
def download_and_extract_glove(dim):
    glove_zip_path = get_data_path("glove.6B.zip")
    glove_txt_filename = f"glove.6B.{dim}d.txt"
    glove_txt_path = get_data_path(glove_txt_filename)
    glove_url = "https://nlp.stanford.edu/data/glove.6B.zip"

    if not os.path.exists(glove_txt_path):
        print("Downloading GloVe embeddings...")
        urllib.request.urlretrieve(glove_url, glove_zip_path)
        with zipfile.ZipFile(glove_zip_path, 'r') as zip_ref:
            zip_ref.extract(glove_txt_filename, DATA_DIR)
        print("GloVe embeddings downloaded and extracted.")
    else:
        print("GloVe embeddings already available.")

    return glove_txt_path


def load_glove_embeddings(config):
    dim = config["embedding_dim"]
    glove_file = download_and_extract_glove(dim)

    embeddings = {}
    with open(glove_file, 'r', encoding='utf-8') as f:
        for line in f:
            values = line.strip().split()
            word = values[0]
            vector = np.asarray(values[1:], dtype='float32')
            embeddings[word] = vector

    word2idx = {word: idx + 1 for idx, word in enumerate(embeddings.keys())}
    embedding_matrix = np.zeros((len(word2idx) + 1, dim))
    for word, idx in word2idx.items():
        embedding_vector = embeddings.get(word)
        if embedding_vector is not None:
            embedding_matrix[idx] = embedding_vector

    return None, word2idx, embedding_matrix


import torch
from torch.utils.data import Dataset
from nltk.tokenize import word_tokenize

class TextEmbeddingDataset(Dataset):
    def __init__(self, texts, labels, word2idx, max_len):
        self.texts = texts
        self.labels = labels
        self.word2idx = word2idx
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        tokens = word_tokenize(self.texts[idx])
        encoded = [self.word2idx.get(word, 0) for word in tokens]
        if len(encoded) < self.max_len:
            encoded += [0] * (self.max_len - len(encoded))
        else:
            encoded = encoded[:self.max_len]
        return torch.tensor(encoded, dtype=torch.long), torch.tensor(self.labels[idx], dtype=torch.long)


import numpy as np
from torch.utils.data import DataLoader

def build_datasets(train_texts, val_texts, test_texts,
                   train_labels, val_labels, test_labels,
                   word2idx, max_len):
    train_dataset = TextEmbeddingDataset(train_texts, train_labels, word2idx, max_len)
    val_dataset   = TextEmbeddingDataset(val_texts, val_labels, word2idx, max_len)
    test_dataset  = TextEmbeddingDataset(test_texts, test_labels, word2idx, max_len)
    return train_dataset, val_dataset, test_dataset

def build_loaders(train_dataset, val_dataset, test_dataset, config):
    train_loader = DataLoader(train_dataset, batch_size=config["batch_size"], shuffle=True)
    val_loader   = DataLoader(val_dataset, batch_size=config["batch_size"], shuffle=False)
    test_loader  = DataLoader(test_dataset, batch_size=config["batch_size"], shuffle=False)
    return train_loader, val_loader, test_loader