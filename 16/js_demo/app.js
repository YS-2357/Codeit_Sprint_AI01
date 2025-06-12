const canvas = document.getElementById("canvas");  // HTML에서 canvas 요소 가져오기
const ctx = canvas.getContext("2d");  // 2D 그래픽을 위한 context 얻기

document.getElementById("fileInput").addEventListener("change", handleImageUpload);  // 파일 입력 시 handleImageUpload 실행

function handleImageUpload(event) {  // 이미지 파일 업로드 처리 함수
  const file = event.target.files[0];  // 업로드된 첫 번째 파일 가져오기
  if (!file) return;  // 파일이 없으면 종료

  const reader = new FileReader();  // 파일을 읽기 위한 FileReader 생성
  reader.onload = function (e) {  // 파일 읽기가 완료되었을 때 실행되는 함수
    const img = new Image();  // 새로운 이미지 객체 생성
    img.onload = function () {  // 이미지 로드 완료 시 캔버스에 그리기
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);  // 캔버스에 이미지 그림
    };
    img.src = e.target.result;  // 이미지 소스를 읽은 데이터로 설정 (base64 형식)
  };
  reader.readAsDataURL(file);  // 파일을 base64 형식으로 읽음
}

function preprocessCanvas() {  // 캔버스 이미지를 28x28로 전처리하는 함수
  const tempCanvas = document.createElement("canvas");  // 임시 캔버스 생성
  tempCanvas.width = 28;  // 너비 28 설정
  tempCanvas.height = 28;  // 높이 28 설정
  const tempCtx = tempCanvas.getContext("2d");  // 임시 캔버스의 context 가져오기

  tempCtx.drawImage(canvas, 0, 0, 28, 28);  // 기존 캔버스의 이미지를 28x28로 축소해서 그리기
  const imageData = tempCtx.getImageData(0, 0, 28, 28).data;  // 이미지 픽셀 데이터 가져오기

  const input = new Float32Array(1 * 1 * 28 * 28);  // ONNX 모델 입력용 1D 배열 생성
  for (let i = 0; i < 28 * 28; i++) {  // 픽셀 수만큼 반복
    const r = imageData[i * 4];  // R 값만 사용 (그레이스케일 기반)
    input[i] = ((255 - r) / 255.0 - 0.5) / 0.5;  // Normalize: 흰색→0, 검정→1 범위 조정
  }
  return input;  // 전처리된 입력 반환
}

async function predict() {  // 예측 함수 (비동기)
  const input = preprocessCanvas();  // 캔버스 전처리 수행
  const tensor = new ort.Tensor("float32", input, [1, 1, 28, 28]);  // ONNX용 텐서로 변환
  const session = await ort.InferenceSession.create("mnist_cnn.onnx");  // ONNX 세션 생성 및 모델 로드

  const feeds = { input: tensor };  // 입력 텐서를 세션에 연결 (input 이름 확인 필요)
  const results = await session.run(feeds);  // 모델 실행
  const output = results.output.data;  // 결과에서 출력 벡터 추출

  const prediction = output.indexOf(Math.max(...output));  // 가장 높은 확률의 인덱스를 예측값으로 선택
  document.getElementById("result").innerText = `결과: ${prediction}`;  // 결과 출력
}