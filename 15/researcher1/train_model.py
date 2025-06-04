import pandas as pd
import numpy as np
import sys
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pickle
import shutil
import os
import traceback

try: 
    # 1. 데이터 로드
    train_csv_path = "train.csv"
    df = pd.read_csv(train_csv_path)
    print("✅ train.csv 로드 완료")

    # 2. 데이터프레임 정보 출력
    df.info(buf=sys.stdout)
    print("✅ DataFrame 정보 출력 완료")

    # 3. 고유값 출력
    print("✅ 각 컬럼의 고유값:")
    for col in df.columns:
        print(f"  - {col}: {np.sort(df[col].dropna().unique())}")
    print("-" * 40)

    # 4. 결측치 처리
    if df.isna().sum().sum() > 0:
        print(f"⚠️ 결측치 존재:\n{df.isna().sum()}")
        df.dropna(inplace=True)
        print("✅ 결측치 제거 완료")
    else:
        print("✅ 결측치 없음")

    # 5. 중복값 처리
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        print(f"⚠️ 중복값 존재: {dup_count}개")
        df.drop_duplicates(inplace=True)
        print("✅ 중복값 제거 완료")
    else:
        print("✅ 중복값 없음")

    # 6. 이상치 탐지 및 제거 (IQR 기준)
    print("✅ 이상치 탐지 및 제거 시작:")
    for col in df.columns:
        if isinstance(df[col].iloc[0], str):
            continue
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower) | (df[col] > upper)].index

        outlier_count = len(outliers)
        if outlier_count > 0:
            print(f"⚠️ {col}: {outlier_count}개 이상치 제거됨")
            df.drop(index=outliers, inplace=True)
            df.reset_index(drop=True, inplace=True)
        else:
            print(f"✅ {col}: 이상치 없음")

    # 7. 데이터 분리 및 전처리
    X_data = df.drop('Performance Index', axis=1).reset_index(drop=True)
    y_data = df['Performance Index'].reset_index(drop=True)

    X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2, random_state=42)

    num_cols = X_data.drop('Extracurricular Activities', axis=1).columns.tolist()
    cat_cols = ['Extracurricular Activities']

    ct = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_cols),
            ('cat', OneHotEncoder(), cat_cols)
        ]
    )

    X_train_trans = ct.fit_transform(X_train)
    X_test_trans = ct.transform(X_test)

    feature_names = ct.get_feature_names_out()
    X_train = pd.DataFrame(X_train_trans, columns=feature_names, index=X_train.index)
    X_test = pd.DataFrame(X_test_trans, columns=feature_names, index=X_test.index)

    # 8. 모델 학습 및 평가
    model = LinearRegression()
    model.fit(X_train, y_train)
    print("✅ 모델 학습 완료")

    y_pred = model.predict(X_test)
    rmse_score = mean_squared_error(y_test, y_pred)
    r2_score = model.score(X_test, y_test)

    print(f"✅ RMSE Score: {rmse_score:.4f}")
    print(f"✅ R² Score: {r2_score:.4f}")
    print(f"⚠️ 회귀 계수: {model.coef_}")
    print(f"⚠️ 절편: {model.intercept_}")

    # 9. 모델 저장
    shared_dir = "shared"
    os.makedirs(shared_dir, exist_ok=True)

    with open(os.path.join(shared_dir, "model.pkl"), "wb") as f:
        pickle.dump((ct, model), f)
    
    shutil.copy("test.csv", os.path.join(shared_dir, "test.csv"))
    print("✅ 모델 저장 완료 (model.pkl)")

except Exception as e:
    print(f"❌ 에러 발생: {e}")
    traceback.print_exc()