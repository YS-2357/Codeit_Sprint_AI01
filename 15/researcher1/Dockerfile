FROM python:3.10-slim

WORKDIR /app

COPY train_model.py ./
COPY train.csv ./
COPY test.csv ./

RUN pip install --no-cache-dir pandas numpy scikit-learn

CMD ["python", "train_model.py"]