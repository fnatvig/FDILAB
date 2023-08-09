import pandas as pd
import numpy as np
from Preprocessor import *
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Model
# from tensorflow.keras.models import load_model

@tf.keras.saving.register_keras_serializable('my_package')
class AutoEncoder(Model):
  def __init__(self):
    super(AutoEncoder, self).__init__()
    self.encoder = tf.keras.Sequential([
       
                  tf.keras.layers.Dense(27, activation="relu"),
                  tf.keras.layers.Dense(24, activation="relu"),
                  tf.keras.layers.Dense(18, activation="relu"),
              ])
    self.decoder = tf.keras.Sequential([
                  tf.keras.layers.Dense(18, activation="relu"),
                  tf.keras.layers.Dense(24, activation="relu"),
                  tf.keras.layers.Dense(27, activation="sigmoid")
              ])
    self.threshold = None
    self.max_arr = None
    self.min_arr = None

  def call(self, x):
    encoded = self.encoder(x)
    decoded = self.decoder(encoded)
    return decoded
  

  def train(self):
    # raw_data = pd.read_excel("data_exports/scenario2_attacked_9bus.xlsx")
    # pre = Preprocessor(pd.DataFrame())
    # data = pre.disassemble(raw_data)
    # print(data)
    raw_data = pd.read_excel("data_exports/scenario2_attacked_9bus.xlsx")
    df_normal = raw_data[raw_data["label"] == "no_attack"]
    df_attacked = raw_data[raw_data["label"] == "attack"]

    df_normal = df_normal.iloc[:][df_normal.columns[1:]]
    # preprocessing df_normal
    pre = Preprocessor(pd.DataFrame())
    # data_attack = pre.disassemble_df(df_attacked)
    data, max_arr, min_arr = pre.disassemble_df(df_normal)
    data = pd.DataFrame(data)
    # plt.plot(data.iloc[:][data.columns[4]])
    # plt.show()
    # input = tf.random.normal((32,27))
    # output = self(input)

    early_stopping = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=300, mode="min")
    opt = tf.keras.optimizers.Adam(learning_rate=0.0004)
    self.compile(optimizer=opt, loss="mse")
    # second_layer_weights = self.get_layer('sequential_1').get_weights()[0]
    normal_train_data = data.iloc[0:int(len(data)*0.8)][data.columns[:]].reset_index(drop=True)
    normal_val_data = data.iloc[int(len(data)*0.8):][data.columns[:]].reset_index(drop=True)
    # tf.convert_to_tensor(normal_train_data)
    # tf.convert_to_tensor(normal_val_data)
    history = self.fit(normal_train_data.to_numpy(), normal_train_data.to_numpy(), epochs=10000, batch_size=32,
                    shuffle=True,
                    validation_data=(normal_val_data.to_numpy(), normal_val_data.to_numpy()), callbacks=[early_stopping])
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.show()
    encoder_out = self.encoder(normal_val_data.to_numpy()) #8 unit representation of data
    decoder_out = self.decoder(encoder_out)
    # decoder_out = tf.transpose(decoder_out)
    plt.plot(tf.transpose(decoder_out)[5], 'r')
    plt.plot(normal_val_data.iloc[:][normal_val_data.columns[5]], 'b')
    plt.show()
    max_mse = 0
    for i in range(len(normal_val_data)):
      real_data = normal_val_data.iloc[i][normal_val_data.columns[:]].to_numpy()
      # print(real_data)
      mse = (np.square(real_data - decoder_out[i])).mean(axis=0)
      if mse>max_mse:
        max_mse = mse 
    print("max_mse = ", max_mse)
    with open("scripts/detection_models/autoencoder_9bus_threshold.txt", "w") as f:
      print(str(max_mse), file=f)
    
    with open("scripts/detection_models/autoencoder_9bus_max.txt", "w") as f:
      for value in max_arr:
        print(value, file=f)

    with open("scripts/detection_models/autoencoder_9bus_min.txt", "w") as f:
      for value in min_arr:
        print(value, file=f)

    self.save('scripts/detection_models/autoencoder_9bus.keras')


def filter(model, raw_data):
  pre = Preprocessor(pd.DataFrame())
  data = pre.disassemble_single(model, raw_data)
  data = pd.DataFrame([data], columns=[str(i) for i in range(len(data))])
  # # model = AutoEncoder()
  # print(raw_data)
  # print(data)
  # model = tf.keras.models.load_model("scripts/detection_models/autoencoder_9bus.keras")
  encoder_out = model.encoder(data.to_numpy()) #8 unit representation of data
  decoder_out = model.decoder(encoder_out)
  se = (np.square(data.to_numpy() - decoder_out))
  mse = se[0].mean(axis=0)
  # print("MSE = ", mse)
  # print("threshold = ", model.threshold)
  if mse > model.threshold:
      # print("attack detected!")
      return "attack"
  else: 
      return "no attack"

  
  # if raw_data.iloc[0]["label"] == "attack":
  #     return "attack"
  # else: 
  #     return "no attack"


  


    
# model = AutoEncoder()
# model.train()