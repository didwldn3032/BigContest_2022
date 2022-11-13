# -*- coding: utf-8 -*-
"""modeling_돌린버전.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JNUtijc3cXugvLLusG5kuKepK47ZVA-N
"""

# 한글출력
# !sudo apt-get install -y fonts-nanum
# !sudo fc-cache -fv
# !rm ~/.cache/matplotlib -rf

import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import numpy as np
import os

"""### 전처리 """

loan = pd.read_csv("/content/drive/MyDrive/Hype Money/raw/loan_result.csv")
imp = pd.read_csv('/content/drive/MyDrive/Hype Money/preprocess/data_impute_fin.csv') # 유저스펙 결측치처리 완료 
imp = imp.drop(['Unnamed: 0'],axis = 1)

#병합
data = pd.merge(loan, imp, how='left' ,left_on='application_id', right_on = 'application_id')

#loan_limit이 결측치인 경우는 제외 + gender가 결측치인 경우도 제외 
data = data.dropna(subset=['loan_limit','gender'])

# loan_limit 100억 이상인 값은 100억 미만 값 중 최대값으로 대체 
data.loc[data['loan_limit']>=1.0e+10,'loan_limit'] = 2337000000

#loan_limit값이 0인경우 5만으로 대체 
data.loc[data['loan_limit']==0,'loan_limit'] = 50000

# existing_loan_amt 절댓값 
data['existing_loan_amt'] = abs(data['existing_loan_amt'])

# loanapply_insert_time 제거
data = data.drop(['loanapply_insert_time'],axis = 1)

list_ = ['gender','bank_id','product_id','gender','income_type', 'employment_type','houseown_type','purpose','personal_rehabilitation']

  for i in list_:
    data[i] = data[i].astype('int')
    data[i] = data[i].astype('category')

"""#### 데이터 용량 줄이기 
[출처](https://data-newbie.tistory.com/472)
"""







## 데이터 크기 확인
def mem_usage(pandas_obj):
    if isinstance(pandas_obj,pd.DataFrame):
        usage_b = pandas_obj.memory_usage(deep=True).sum()
    else: # we assume if not a df it's a series
        usage_b = pandas_obj.memory_usage(deep=True)
    usage_mb = usage_b / 1024 ** 2 # convert bytes to megabytes
    return "{:03.2f} MB".format(usage_mb)

## 타입별 평균 크기 확인
def type_memory(data) :
    for dtype in ['float','int','object']:
        selected_dtype = data.select_dtypes(include=[dtype])
        mean_usage_b = selected_dtype.memory_usage(deep=True).mean()
        mean_usage_mb = mean_usage_b / 1024 ** 2
        print("Average memory usage for {} columns: {:03.2f} MB".format(dtype,mean_usage_mb))

## 이산형
def int_memory_reduce(data) :
    data_int = data.select_dtypes(include=['int'])
    converted_int = data_int.apply(pd.to_numeric,downcast='unsigned')
    print(f"Before : {mem_usage(data_int)} -> After : {mem_usage(converted_int)}")
    data[converted_int.columns] = converted_int
    return data

## 연속형
def float_memory_reduce(data) :
    data_float = data.select_dtypes(include=['float'])
    converted_float = data_float.apply(pd.to_numeric,downcast='float')
    print(f"Before : {mem_usage(data_float)} -> After : {mem_usage(converted_float)}")
    data[converted_float.columns] = converted_float
    return data

## 문자형
def object_memory_reduce(data) :
    gl_obj = data.select_dtypes(include=['object']).copy()
    converted_obj = pd.DataFrame()
    for col in gl_obj.columns:
        num_unique_values = len(gl_obj[col].unique())
        num_total_values = len(gl_obj[col])
        if num_unique_values / num_total_values < 0.5:
            converted_obj.loc[:,col] = gl_obj[col].astype('category')
        else:
            converted_obj.loc[:,col] = gl_obj[col]
    print(f"Before : {mem_usage(gl_obj)} -> After : {mem_usage(converted_obj)}")
    data[converted_obj.columns] = converted_obj
    return data




list_ = ['gender','bank_id','product_id','gender','income_type', 'employment_type','houseown_type','purpose','personal_rehabilitation']

for i in list_:
  data[i] = data[i].astype('int')
  data[i] = data[i].astype('object')

object_memory_reduce(data)
float_memory_reduce(data)
int_memory_reduce(data)

list_ = ['gender','bank_id','product_id','gender','income_type', 'employment_type','houseown_type','purpose','personal_rehabilitation']

for i in list_:
  data[i] = data[i].astype('int')
  data[i] = data[i].astype('category')

# train, test 나누기 
train = data[data['is_applied'].notna()]
test = data[data['is_applied'].isna()]

# 큰수들 (가격변수들) 로그스케일링 
train['loan_limit'] = np.log1p(train['loan_limit'])
train['yearly_income'] = np.log1p(train['yearly_income'])
train['desired_amount'] = np.log1p(train['desired_amount'])
train['existing_loan_amt'] = np.log1p(train['existing_loan_amt'])

test['loan_limit'] = np.log1p(test['loan_limit'])
test['yearly_income'] = np.log1p(test['yearly_income'])
test['desired_amount'] = np.log1p(test['desired_amount'])
test['existing_loan_amt'] = np.log1p(test['existing_loan_amt'])

#나머지는 로버스트 스케일링 
numerical_feature = ['age','credit_score','desired_amount','existing_loan_amt','loan_limit','loan_rate','loan_rate','working_years','yearly_income']
from sklearn.preprocessing import RobustScaler

rob = RobustScaler()

rob_data = rob.fit_transform(train[numerical_feature])
rob_train = train.copy()
for i,c in enumerate(numerical_feature):
    rob_train[c] = rob_data.T[i]

rob_data = rob.fit_transform(test[numerical_feature])
rob_test = test.copy()
for i,c in enumerate(numerical_feature):
    rob_test[c] = rob_data.T[i]

train_x = rob_train.drop(['is_applied'], axis = 1)
train_y = rob_train['is_applied']

#########################################1:4 undersampling
! pip install -U imbalanced-learn

from imblearn.under_sampling import *
X_samp, y_samp = RandomUnderSampler(random_state=777,sampling_strategy = 0.25).fit_resample(train_x, train_y)

X = X_samp.drop(['application_id','user_id'], axis = 1)
y = y_samp
y = y.astype(int)

!pip install optuna -q

# Optuna Libraries
import optuna
from optuna import Trial
from optuna.samplers import TPESampler

# LGBM Classifier
from lightgbm import LGBMClassifier
#from catboost import CatBoostClassifier


# train_test_split
from sklearn.model_selection import train_test_split

from sklearn.metrics import f1_score

from time import time
from datetime import timedelta

"""#### lgbm - personal_rehabilitation"""

X = X.drop(['personal_rehabilitation'],axis = 1)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state = 777)

from optuna.samplers import TPESampler

def objective(trial):
    param = {
        'boosting_type' : 'gbdt',
        "n_estimators" : trial.suggest_int("n_estimators", 1000, 10000),
        'max_depth':trial.suggest_int('max_depth', 4, 16),
        'random_state': 777,
        'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 8, 24),
        'reg_lambda': trial.suggest_loguniform('reg_lambda', 1e-8, 10.0),
        'num_leaves': trial.suggest_int('num_leaves', 8, 32),
        'learning_rate': trial.suggest_loguniform('learning_rate', 0.01, 0.03)
    }

    model = LGBMClassifier(**param)
    cat_features = X_train[['bank_id','product_id','gender','income_type','employment_type','houseown_type','purpose']].columns.tolist()
    lgb_model = model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=0, early_stopping_rounds=25,categorical_feature =cat_features)
    f1 = f1_score(y_val, lgb_model.predict(X_val))
    return f1
        
# study_lgb = optuna.create_study(direction='maximize', sampler=sampler)
# study_lgb.optimize(objective, n_trials=100)


start = time()
study_lgb = optuna.create_study(direction='maximize', sampler= TPESampler(seed=777))
study_lgb.optimize(objective, n_trials=10)
print("Best Score:",study_lgb.best_value)
print("Best trial",study_lgb.best_trial.params)
end = time()
print("RUN TIME : ", timedelta(seconds=end-start))

lgb_trial = study_lgb.best_trial
lgb_trial_params = lgb_trial.params
print('Best Trial: score {},\nparams {}'.format(lgb_trial.value, lgb_trial_params))

optuna.visualization.plot_param_importances(study_lgb)

start = time()
lgb_model = LGBMClassifier(**lgb_trial_params)
lgb_model.fit(X_train, y_train)

preds_class = lgb_model.predict(X_val)
preds_proba = lgb_model.predict_proba(X_val)
f1 = f1_score(y_val, preds_class)

print("f1 score : " , f1)
end = time()
print("RUN TIME : ", timedelta(seconds=end-start))

! pip install shap

#너무 데이터가 많아 오래걸려서 + 램이 터져서 0.001만큼만 가져옴 
X_train2, X_val2, y_train2, y_val2 = train_test_split(X, y, test_size=0.001, random_state = 777)

start = time()
import shap
explainer = shap.TreeExplainer(lgb_model) # Tree model Shap Value 확인 객체 지정
shap_values = explainer.shap_values(X_val2) # Shap Values 계산
end = time()
print("RUN TIME : ", timedelta(seconds=end-start))

shap.summary_plot(shap_values, X_val2, plot_type = "bar")

# summary
shap.summary_plot(shap_values, X_val2)

shap.summary_plot(shap_values[1], X_val2, feature_names = X_val2.columns)

new_shap_values = np.vstack((shap_values[0][:1000000],shap_values[1][:1000000]))
shap.initjs()
shap.force_plot(explainer.expected_value[0], new_shap_values[0],feature_names =  X_val2.columns)

shap.initjs()
shap.force_plot(explainer.expected_value[0], shap_values[0])

shap.initjs()
shap.force_plot(explainer.expected_value[0], shap_values[0], X_val2.values, feature_names = X_val2.columns)

############################## predict
# personal_rehabiliatation, user_id 삭제 
rob_test = rob_test.drop(['personal_rehabilitation','user_id'],axis = 1)

#application_id 식별자로 빼두기 
rob_test_id = rob_test[['application_id']]
rob_test_2 = rob_test.drop(['application_id'],axis = 1)

X_test = rob_test_2.drop(['is_applied'],axis = 1)
y_test = rob_test_2[['is_applied']]
y_test = lgb_model.predict_proba(X_test)

####################################
threshold = 0.4

#f1score 비교용
# pred = lgb_model.predict_proba(X_val)[:,1]
# pred = np.where(pred >= threshold , 1, 0)
# score = f1_score(y_val,pred)
# print(score)
pred = y_test[:,1]
pred = np.where(pred >= threshold , 1, 0)
# print(pred)

# 0.4일때 > 채택 
import collections, numpy
collections.Counter(pred)

rob_test_2['is_applied'] = pred
test3 = pd.concat([rob_test_id,rob_test_2],axis=1)

submission = pd.read_csv('데이터분석분야_퓨처스부문_평가데이터.csv')
submit = pd.merge(submission[['application_id','product_id']], test3[['application_id','product_id','is_applied']], how='left', left_on=['application_id', 'product_id'], right_on=['application_id', 'product_id'])
submit.to_csv('submission.csv',index=False)