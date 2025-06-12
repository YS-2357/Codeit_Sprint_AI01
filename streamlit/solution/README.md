# 몇가지 안내

0. docs : https://docs.streamlit.io/
1. gallery : https://streamlit.io/gallery?category=favorites
2. 직접 타이핑 하며 연습하기 위하여
   vscode에서 command(ctrl) + shift + p -> copilot completions disable 설정하기

3. vscode에 인터넷창 띄우기
   command(ctrl) + shift + p -> simple browser:show

4. solution 폴더는 답안 코드 있음, practice는 최소한의 가이드만 존재

5. 환경설정

   - 설치 : `pip install streamlit`
   - 동작확인 :

     - `streamlit hello` # 이메일 입력안해도 됨
     - `python3 -m streamlit run app.py` # 작성한 코드확인
     - `streamlit run app.py` # 작성한 코드확인

   - 실행 코드 종료 : command + c
   - 파이썬 환경 관련 (별도 설치해야하는 경우)
     - venv 이용
     - python -m venv .venv
     - source .venv/bin/activate (윈도우 : myenv\Scripts\activate)
     - (.venv) pip install -r requirements
     - (.venv) python -m streamlit run streamlit_app.py
     - deactivate (비활성화)
   - 포트 관련 (linux/mac):

     - 실행시킬 떄 마다 포트가 누적됨
     - 포트확인 `lsof -i:{port}`
     - 포트종료 'kill -9 {pid}`
     - stream 관련 모든 pid 종료
       - `pkill -f "streamlit run"`
       - `kill -9 $(lsof -t -i :{Port})`

   - 포트 관련 (window)

     - 포트 확인 `netstat -aon | findstr :{port}`
     - 마지막 숫자 pid `Stop-Process -Id {pid} -Force`
     - `$pid = (netstat -aon | findstr :{port} | Select-String "LISTENING" | ForEach-Object { $_ -split "\s+" } | Select-Object -Last 1); if ($pid) { Stop-Process -Id $pid -Force }`

   - 포트관련 실행시 포트 고정
     - 불필요하게 포트 늘리지 말고 고정해서 사용하기
     - streamlit run app.py --server.port 8502

6. 기본
