from transformers import AutoTokenizer, BertForSequenceClassification
from fastapi import FastAPI

app = FastAPI()

# KoBERT의 원래 토크나이저 사용
# https://huggingface.co/jeonghyeon97/koBERT-Senti5
'''
0: Angry
1: Fear
2: Happy
3: Tender
4: Sad
'''

tokenizer = AutoTokenizer.from_pretrained('monologg/kobert',trust_remote_code=True)
model = BertForSequenceClassification.from_pretrained('jeonghyeon97/koBERT-Senti5')


@app.post("/predict")
async def predict(text: str):
    # 입력 텍스트 토큰화
    inputs = tokenizer([text], return_tensors='pt', padding=True, truncation=True)

    # 예측
    outputs = model(**inputs)
    predictions = outputs.logits.argmax().item()
    mapper = {  0: 'Angry',
                1: 'Fear',
                2: 'Happy',
                3: 'Tender',
                4: 'Sad'
            }
    
    sentiment = mapper[predictions]
    return {"sentiment": sentiment}