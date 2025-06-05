# 🧪 스프린트 미션 15

## 🎯 미션 소개

파트4에 오신 여러분들을 환영합니다!  
이번 미션은 두 명의 연구자가 협업하는 아래 시나리오를 참고하여 도커 기반 워크플로우를 설계하고, 필요한 도커파일을 작성하는 미션입니다.

각 연구자에게 부여된 역할은 다음과 같습니다.

- **연구자 1**: 데이터 전처리, 탐색적 데이터 분석(EDA), 모델링 및 모델 파일 추출  
- **연구자 2**: 추출된 모델을 활용한 추론  

---

## 📂 사용 데이터셋

이번 미션의 데이터는 캐글에서 제공하는 학생 성적 데이터를 스프린트 미션 전용으로 후처리한 데이터입니다.
(https://www.kaggle.com/datasets/nikhil7280/student-performance-multiple-linear-regression)
아래 두 데이터를 다운로드 받아주세요:

- `train.csv`
- `test.csv`

| 변수명 | 설명 |
|--------|------|
| Hours Studied | 각 학생이 공부에 소요한 총 시간 |
| Previous Scores | 학생들이 이전 시험에서 얻은 점수 |
| Extracurricular Activities | 학생이 과외 활동에 참여하는지 여부 (예 또는 아니오) |
| Sleep Hours | 학생이 하루 평균 수면 시간 |
| Sample Question Papers Practiced | 학생이 연습한 모의고사 수 |
| Performance Index | 목표변수. 각 학생의 전반적인 성취도를 나타내는 지표. 성취도 지수는 학생의 학업 성취도를 나타내며, 가장 가까운 정수로 반올림됩니다. 지수는 10에서 100까지이며, 값이 높을수록 더 나은 성취도를 나타냅니다. |

---

## 🤝 협업 시나리오

- **연구자 1**
  - `train.csv` 데이터를 기반으로 Jupyter Notebook(`.ipynb`)에서 데이터 전처리, EDA, 회귀 모델링 수행
  - `scikit-learn`을 사용하여 회귀 모델링, 성능 평가는 RMSE 기준
  - 최종 모델은 `model.pkl`로 저장
  - 전처리, 모델링, 모델 저장 과정을 하나의 `.py` 스크립트로 정리
  - 위 작업을 자동화하는 도커 이미지를 구축하여 Docker Hub에 업로드

- **연구자 2**
  - 연구자 1이 생성한 도커 이미지와 별도의 Jupyter Notebook 도커 이미지를 `docker-compose`로 구성
  - 연구자 1의 도커 컨테이너에서 생성된 `model.pkl` 파일과 컨테이너 내부의 `test.csv`를 활용하여 Jupyter Notebook에서 추론 수행
  - 결과를 `result.csv`로 저장
  - 전체 추론 과정은 `inference.ipynb` 파일에 별도 저장

> 참고: 연구자 2는 사전에 데이터나 모델 파일을 보유하지 않은 상태이며,  
> 연구자 1의 Docker Hub 이미지를 통해 필요한 파일을 가져와야 한다.

---

## 📤 제출 안내

미션 15 폴더 하위에 `{팀명}_{이름}`으로 폴더를 생성하고, 그 안에 아래 항목을 제출하세요:

- `코드 폴더 (mission-result)` : 실제 작성한 코드 제출
- `보고서 PDF (2페이지 이내)` : 다음 항목 포함
  - Docker Hub URL
  - 연구자 1의 데이터 전처리 및 모델링 결과 요약
  - 코드 아키텍처 도식 및 설명

---

## 📌 참고 사항

- 두 연구자의 Python 버전과 패키지 버전을 동일하게 유지하는 방안
- 연구자 1의 컨테이너에 있는 데이터와 `model.pkl` 파일을 연구자 2의 컨테이너로 전달하는 전략  
  > 💡 힌트: 두 컨테이너와 호스트 간 볼륨을 공유하고, `docker cp` 명령어를 활용한다.

---

## 🧪 연구자 실험 수행 순서

### 📁 1. Researcher 1 (모델 학습 및 이미지 생성)

```bash
# Docker 이미지 빌드
docker build -t ys2357/re1-train:latest .

# 컨테이너 실행 (모델 학습 수행 확인)
docker run --name trainer_container ys2357/re1-train:latest python train_model.py

# 컨테이너 종료 상태 확인 (Exited 0)
docker ps -a

# shared 디렉토리 생성 및 모델 복사 (.pkl 혹인)
mkdir ./shared
docker cp trainer_container:/app/shared/model.pkl ../shared/model.pkl

# 컨테이너 제거
docker rm trainer_container

# DockerHub 로그인 및 이미지 푸시
docker login
docker tag ys2357/re1-train:latest your_dockerhub_id/re1-train:latest
docker push ys2357/re1-train:latest
```

---

### 📁 2. Researcher 2 (모델 다운로드 및 Jupyter 환경 설정)

```bash
# trainer 컨테이너 실행 (모델 재생성)
docker-compose up trainer

# shared 디렉토리 생성 및 모델/테스트셋 복사
mkdir ./shared
docker cp trainer_container:/app/shared/model.pkl ./shared/model.pkl
docker cp trainer_container:/app/shared/test.csv ./shared/test.csv

# trainer 컨테이너 제거
docker rm trainer_container

# Jupyter Notebook 서버 실행
docker-compose up -d jupyter

# 접속 URL(token) 확인
docker logs jupyter_container
```

> 🔗 브라우저에서 http://localhost:8888 접속 후 token 입력