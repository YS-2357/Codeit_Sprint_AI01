1️⃣ Kaggle API 인증 필요 여부
✅ Kaggle Datasets → 누구나 다운로드 가능 (토큰 불필요)
❌ Kaggle Competitions → 로그인 후 토큰 인증 필요 (denoising-dirty-documents는 Competition 데이터)

즉, 현재 데이터는 Kaggle 로그인 후 다운로드해야 하므로, API 토큰이 반드시 필요합니다.

2️⃣ README.md 또는 실행 메시지에 인증 설정 방법 명시
📌 Kaggle 인증 설정 (필수)
사용자가 자신의 kaggle.json을 설정해야 한다는 안내를 명확히 제공해야 합니다.

설정 방법
Kaggle 계정에서 API 토큰 (kaggle.json) 다운로드

Kaggle 로그인 후, API 페이지에서 Create New API Token 클릭
kaggle.json 파일 다운로드
~/.kaggle/ 폴더에 저장

bash
코드 복사
mkdir -p ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
데이터 다운로드 실행

bash
코드 복사
python src/download_data.py
3️⃣ download_data.py 수정하여 Kaggle 인증 필요 메시지 추가
현재 download_data.py에 Kaggle API 토큰이 없을 경우 오류 메시지를 출력하는 기능을 추가하겠습니다.

Edited Download Data
✅ download_data.py를 수정하여 Kaggle API 토큰이 없을 경우 오류 메시지를 출력하도록 했습니다.
이제 실행하면 토큰이 없는 경우 설정 방법을 안내합니다.

📌 최종 실행 방법
1️⃣ Kaggle API 토큰 설정 (필수)

Kaggle API 페이지에서 kaggle.json 다운로드
아래 명령어 실행:
bash
코드 복사
mkdir -p ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
2️⃣ 데이터 다운로드 실행

bash
코드 복사
python src/download_data.py
이제 데이터 다운로드 후, dataset.py를 실행하여 정상적으로 로드되는지 확인하면 됩니다.
데이터 다운로드가 끝나면 알려주세요.
