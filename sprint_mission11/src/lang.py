import pickle
from tqdm import tqdm
import os

class Lang:
    def __init__(self, name):
        self.name = name
        self.word2index = {}
        self.index2word = {}
        self.word2count = {}
        self.n_words = 0
        self.add_special_tokens()

    def add_special_tokens(self):
        for idx, tok in enumerate(["<sos>", "<eos>", "<pad>", "<unk>"]):
            self.word2index[tok] = self.n_words
            self.index2word[self.n_words] = tok
            self.n_words += 1

    def addSentence(self, sentence, tokenizer):
        for word in tokenizer(sentence):
            self.addWord(word)

    def addWord(self, word):
        if word in self.word2index:
            self.word2count[word] += 1
        else:
            idx = self.n_words
            self.word2index[word] = idx
            self.index2word[idx] = word
            self.word2count[word] = 1
            self.n_words += 1

    def save_vocab(self, filepath):
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load_vocab(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)

def build_and_save_lang(df, name, tokenizer, path, config):
    lang = Lang(name)
    for sentence in tqdm(df[name], desc=f"[{name}] vocab 구축"):
        lang.addSentence(sentence, tokenizer)

    if config.get("verbose", 0) > 0:
        word_freq = sorted(lang.word2count.items(), key = lambda x: x[1], reverse=True)
        print(f"[{name}] 총 단어 수: {lang.n_words}")
        print(f"[{name}] 가장 많이 등장한 단어 10개")
        for word, freq in word_freq[:10]:
            print(f"    {word}: {freq}")

    lang.save_vocab(path)
    print(f"'{name}' vocab saved at: {path}")
    return lang

def load_or_build_lang(df, name, tokenizer, path, config):
    force_reload = config.get("force_rebuild_vocab", False)

    if not force_reload and os.path.exists(path):
        print(f"'{name}' vocab 로드 중... ({path})")
        return Lang.load_vocab(path)
    else:
        print(f"'{name}' vocab {'재생성' if force_reload else '없음. 새로 구축'} 중...")
        return build_and_save_lang(df, name, tokenizer, path, config)