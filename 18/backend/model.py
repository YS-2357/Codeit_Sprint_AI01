from transformers import pipeline

def load_model():
    sentiment_model = pipeline(
        "sentiment-analysis",
        model="sangrimlee/bert-base-multilingual-cased-nsmc"
    )
    return sentiment_model


# https://huggingface.co/sangrimlee/bert-base-multilingual-cased-nsmc
# from transformers import pipeline
# classifier = pipeline(
# classifier("흠...포스터보고 초딩영화줄....오버연기조차 가볍지 않구나.")
# classifier("액션이 없는데도 재미 있는 몇안되는 영화")