const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

document.getElementById("fileInput").addEventListener("change", handleImageUpload);

function handleImageUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    const img = new Image();
    img.onload = function () {
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function preprocessCanvas() {
  const tempCanvas = document.createElement("canvas");
  tempCanvas.width = 28;
  tempCanvas.height = 28;
  const tempCtx = tempCanvas.getContext("2d");

  // 280x280 → 28x28 축소
  tempCtx.drawImage(canvas, 0, 0, 28, 28);
  const imageData = tempCtx.getImageData(0, 0, 28, 28).data;

  const input = new Float32Array(1 * 1 * 28 * 28);
  for (let i = 0; i < 28 * 28; i++) {
    const r = imageData[i * 4];  // R 값만 사용
    input[i] = ((255 - r) / 255.0 - 0.5) / 0.5;  // Normalize: 흰색→0, 검정→1
  }
  return input;
}

async function predict() {
  const input = preprocessCanvas();
  const tensor = new ort.Tensor("float32", input, [1, 1, 28, 28]);
  const session = await ort.InferenceSession.create("mnist_cnn.onnx");

  const feeds = { input: tensor };  // input 이름 확인 필요
  const results = await session.run(feeds);
  const output = results.output.data;

  const prediction = output.indexOf(Math.max(...output));
  document.getElementById("result").innerText = `결과: ${prediction}`;
}