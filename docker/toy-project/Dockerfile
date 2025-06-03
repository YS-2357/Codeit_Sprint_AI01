FROM python:3.9.22-alpine3.22
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY run.py /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
CMD ["python", "run.py"]