import tensorflow as tf
from joblib import load

import scripts.autoencoder_30bus as ae
import scripts.gmm as gmm
import scripts.perfect_classifier as pc

class Defense:
    def __init__(self):
        self.script = "" 
        self.active = False
        self.threshold = None
        self.model = None
        
    def set_script(self, script):
        self.script = script
        if script == "autoencoder_30bus.py":
            self.model = tf.keras.models.load_model("scripts/detection_models/autoencoder_30bus_train.keras")

            with open("scripts/detection_models/autoencoder_30bus_threshold_train.txt", "r") as f:
                self.model.threshold = float(f.read()[:-1])

            with open("scripts/detection_models/autoencoder_30bus_max_train.txt", "r") as f:
                self.model.max_arr = [float(line.rstrip()) for line in f]

            with open("scripts/detection_models/autoencoder_30bus_min_train.txt", "r") as f:
                self.model.min_arr = [float(line.rstrip()) for line in f]
        if script == "gmm.py":
            self.model = load('scripts/detection_models/gmm.joblib')
            max_arr, min_arr = [], []
            with open("scripts/detection_models/scenario12_min.txt", "r") as f:
                min_arr = [float(line.rstrip()) for line in f]
            with open("scripts/detection_models/scenario12_max.txt", "r") as f:
                max_arr = [float(line.rstrip()) for line in f]

            setattr(self.model, 'max_arr', max_arr)
            setattr(self.model, 'min_arr', min_arr)
            setattr(self.model, 'threshold', float(load('scripts/detection_models/gmm_threshold.joblib')))

    def set_active(self, active):
        self.active = active

    def filter(self, data, memory):
        if self.active == False:
            return "no_attack"
        else:        
            if self.script == "autoencoder_30bus.py":
                return ae.filter(self.model, data)
            if self.script == "gmm.py":
                return gmm.filter(self.model, data)
            elif self.script == "perfect_classifier.py":
                return pc.filter(self.model, data)

        