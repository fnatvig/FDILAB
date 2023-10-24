import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
from joblib import dump, load
from sklearn.mixture import GaussianMixture

from Preprocessor import *


def train():
    raw_data = pd.read_excel("data_exports/scenario13_modified.xlsx")
    # df_normal = raw_data[raw_data["label"] == "no_attack"]
    # df_attacked = raw_data[raw_data["label"] == "attack"]
    df = raw_data.iloc[:][raw_data.columns[1:]]

    pre = Preprocessor(pd.DataFrame())

    data, max_arr, min_arr = pre.disassemble_df(df)
    data = pd.DataFrame(data)
 
    gmm = GaussianMixture(n_components=4, n_init=10, random_state=5)
    y_gmm = gmm.fit_predict(data)

    score = gmm.score_samples(data)
    print(data)
    df['score'] = score
    
    pct_threshold = np.percentile(score, 4)

    df['anomaly_gmm_pct'] = df['score'].apply(lambda  x: 1 if x < pct_threshold else 0)

    TP = 0
    FP = 0
    FN = 0
    for i in range(len(df['anomaly_gmm_pct'])):
        if df.iloc[i]['anomaly_gmm_pct'] == 1:
            if df.iloc[i]['label']=='attack':
                # print(f"attack detected at t = {i}")
                TP +=1
            else:
                # print(f"no_attack misclassified as attack at t={i}")
                FP +=1
        else:
            if df.iloc[i]['label']=='attack':
                FN +=1

    print("Precision = ", TP/(TP+FP))
    print("Recall = ", TP/(TP+FN))
    # with open("scripts/detection_models/autoencoder_9bus_threshold.txt", "w") as f:
    #   print(str(max_mse), file=f)
    
    with open("scripts/detection_models/scenario12_max.txt", "w") as f:
      for value in max_arr:
          print(value, file=f)

    with open("scripts/detection_models/scenario12_min.txt", "w") as f:
      for value in min_arr:
          print(value, file=f)

    dump(gmm, 'scripts/detection_models/gmm.joblib') 
    dump(pct_threshold, 'scripts/detection_models/gmm_threshold.joblib') 
    return gmm, pct_threshold

def filter(model, raw_data):
    pre = Preprocessor(pd.DataFrame())
    data = pre.disassemble_single(model, raw_data)
    data = np.array(data).reshape(1,-1)
    model.predict(data)

    if model.score_samples(data)[-1] < model.threshold:
        return "attack"   
    else: 
        return "no_attack"
    

def filter_draft(model, raw_data):

    df = raw_data.iloc[:][raw_data.columns[1:]]

    pre = Preprocessor(pd.DataFrame())


    if len(raw_data)>4:
        data, max_arr, min_arr = pre.disassemble_df(df)
        data = pd.DataFrame(data)
        model.fit_predict(data)
        if model.score_samples(data)[-1] < model.threshold:
            return "attack"   
        else: 
            return "no_attack"
    else: 
        data = pre.disassemble_single(model, raw_data)
        data = np.array(data).reshape(1,-1)
        model.predict(data)
        if model.score_samples(data)[-1] < model.threshold:
            return "attack"   
        else: 
            return "no_attack"






# model, threshold = train()
# X = np.array([random.random() for i in range(90)]).reshape(1,-1)
# model = load('scripts/detection_models/gmm.joblib')
# print(model.predict(X))
# plt.plot(y_gmm)
# plt.plot()
# plt.show()


    