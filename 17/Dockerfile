# base image
FROM python:3.12-slim

# set working directory
WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy all files
COPY . . 

# expose port
EXPOSE 8501

# run app
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]