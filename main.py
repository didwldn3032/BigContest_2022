# -*- coding: utf-8 -*-
"""main.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bP27DMcmgWcj6mfl0QremRZFhURgQDwd

## ECO 제주 음식물 쓰레기 예측모델 실행 파일
#### Hype Money
빅콘테스트 2022 데이터분석 분야 퓨처스 부문 - 앱 사용성 데이터를 통한 대출신청 예측분석의 실행파일입니다.

### Step0. 환경설정
전처리부터 데이터 예측까지의 과정에서 필요한 라이브러리 환경을 구축합니다.
"""

def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)

"""### Step1. EDA
데이터 EDA를 위한 EDA.py을 실행하기 위해 preprocessing 폴더로 이동합니다.
"""

# Commented out IPython magic to ensure Python compatibility.
# %cd preprocess

"""#### Step1-1. EDA.py 파일을 실행합니다."""

!python EDA.py

"""### Step2. Preprocessing
모델 구축에 사용되는 내부 데이터와 외부 데이터에 대한 데이터 전처리를 실행합니다.

#### Stemp2-1. 이상치 처리
"""

!python outlier.py

"""#### Stemp2-2. 결측치 처리
pycaret과 random forest를 활용해 데이터 결측치를 채웁니다.
"""

install_and_import('pycaret')

!python preprocess.py



"""### Step3. Modeling & Predict
모델링 및 데이터 예측을 위한 model.py을 실행하기 위해 model 폴더로 이동합니다. 
"""

# Commented out IPython magic to ensure Python compatibility.
# %cd ../model

"""#### Step3-1. modeling.py 파일을 실행합니다.
lgbm모델을 이용해 예측을 진행합니다.
"""

install_and_import('shap')

install_and_import('optuna')

install_and_import('lightgbm')

!python modeling.py

"""### Step5. Clustering
k-means를 이용해 군집화를 진행합니다.
"""

!python clustering.py