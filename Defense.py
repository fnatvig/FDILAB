import tensorflow as tf
import scripts.autoencoder_9bus as ae
import scripts.perfect_classifier as pc

class Defense:
    def __init__(self):
        self.script = "" 
        self.active = False
        self.model = None
        
    def set_script(self, script):
        self.script = script
        if script == "autoencoder_9bus.py":
            self.model = tf.keras.models.load_model("scripts/detection_models/autoencoder_9bus.keras")

            with open("scripts/detection_models/autoencoder_9bus_threshold.txt", "r") as f:
                self.model.threshold = float(f.read()[:-1])

            with open("scripts/detection_models/autoencoder_9bus_max.txt", "r") as f:
                self.model.max_arr = [float(line.rstrip()) for line in f]

            with open("scripts/detection_models/autoencoder_9bus_min.txt", "r") as f:
                self.model.min_arr = [float(line.rstrip()) for line in f]

    def set_active(self, active):
        self.active = active

    def filter(self, data):
        if self.active == False:
            return "no_attack"
        else:        
            if self.script == "autoencoder_9bus.py":
                return ae.filter(self.model, data)
            elif self.script == "perfect_classifier.py":
                return pc.filter(self.model, data)

        