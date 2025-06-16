import os
import requests
import onnxruntime as ort
import streamlit as st
import numpy as np
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from PIL import Image 

st.set_page_config(
    page_title="MNIST App",
    page_icon="🔢",
    layout="wide"
)

# 모델 로드
@st.cache_resource
def load_model():
    model_url = "https://github.com/onnx/models/raw/main/validated/vision/classification/mnist/model/mnist-8.onnx"
    model_path = "data/mnist-12.onnx"

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(model_path):
        with st.spinner("Downloading model..."):
            r = requests(model_url)
            with open(model_path, "wb") as f:
                f.write(r.content)

    return ort.InferenceSession(model_path)

# 이미지 전처리
def process_image(image_data):
    if image_data is None:
        return None
    
    # PIL image
    img = Image.fromarray(image_data.astype('uint8')).convert('L')

    # resize & normalize
    img_resized = img.resize((28, 28), Image.Resampling.LANCZOS)
    img_array = np.array(img_resized)
    img_normalized = img_array.astype(np.float32) / 255.0
    img_reshaped = img_normalized.reshape(1, 1, 28, 28)
    return img_reshaped
    
    
def predict_digit(model, image):
    if image is None:
        return None, None
    
    # predict
    input_name = model.get_inputs()[0].name
    result = model.run(None, {input_name: image})
    logits = result[0][0]

    def softmax(x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()
    
    probs = softmax(logits)
    pred_label = int(np.argmax(probs))

    return pred_label, probs

try:
    model = load_model()
    st.success("Model loaded Successfully!", icon="✅")
except Exception as e:
    st.error(f"Error as {str(e)}", icon="❌")
    st.stop


st.title("MNIST App")

col1, col2= st.columns([1, 1])

with col1:
    st.header("Draw a number", divider='blue')

    # canvas
    canvas_image = st_canvas(
        stroke_width=20,
        stroke_color="#000000",
        background_color= "#FFFFFF",
        width=280,
        height=280,
        drawing_mode="freedraw",
        key='canvas'
    )

with col2:
    st.header("Processing...", divider='green')

    if canvas_image.image_data is not None:
        processed_image = process_image(canvas_image.image_data)
        if processed_image is not None:
            processed_image_display = processed_image.reshape(28, 28)
            st.image(processed_image_display, caption="Processed image", width=280)
        else:
            st.info("Processing image...")
    else:
        st.info("Draw a number")

st.header("Predicted number!", divider="red")

if canvas_image.image_data is not None:
    processed_image = process_image(canvas_image.image_data)
    if processed_image is not None:
        pred_label, probs = predict_digit(model, processed_image)
        
        if pred_label is not None and probs is not None:
            df = pd.DataFrame([probs], columns=[str(i) for i in range(10)], index=['Probability'])

            def highlight_probabilities_row(row):
                max_index = int(np.argmax(row))
                max_prob = row.iloc[max_index]

                def get_color(p):
                    # 비율로 색상 농도 결정
                    ratio = p / max_prob if max_prob > 0 else 0
                    if ratio < 0.2:
                        return "#eaf8f0"
                    elif ratio < 0.4:
                        return "#c9f2da"
                    elif ratio < 0.6:
                        return "#a6ecc2"
                    elif ratio < 0.8:
                        return "#7fe6a6"
                    elif ratio < 1.0:
                        return "#4bdc83"
                    else:
                        return "#00cc66"

                return [f"background-color: {get_color(p)}" for p in row]

            st.subheader(f"Prediction: {pred_label}")

            styled_df = df.style.apply(highlight_probabilities_row, axis=1)
            styled_df = styled_df.format("{:.2%}")

            # 왼쪽에 'Label' 인덱스를 추가해 표 형식 강조
            df_with_labels = df.copy()
            df_with_labels.index.name = "Row"
            
            st.dataframe(styled_df)
        else:
            st.error("Failed to predict")
    else:
        st.info("Processing image...")
else:
    st.info("Draw a number")