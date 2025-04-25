import os
import json
import pandas as pd

def get_df(data_dir):
    # json 파일 모으기
    json_paths = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".json"):
                json_paths.append(os.path.join(root, file))

    # 제이슨 데이터에서 원하는 속성만 수집
    data = []
    for path in json_paths:
        with open(path, 'r', encoding='utf-8') as f:
            try:
                items = json.load(f)
                for item in items:
                    polarity = item.get("GeneralPolarity", None)
                    text = item.get("RawText", None)

                    if polarity is not None and text:  # 둘 다 있어야 추가
                        polarity = int(polarity)
                        if polarity in [-1, 0, 1]:
                            data.append({
                                "text": text,
                                "label": polarity + 1  # -1 → 0, 0 → 1, 1 → 2
                            })
            except Exception:
                continue  # 형식 이상한 파일은 무시하고 넘어감

    # 데이터프레임 만들기
    df = pd.DataFrame(data)
    df = df.dropna().drop_duplicates()
    return df